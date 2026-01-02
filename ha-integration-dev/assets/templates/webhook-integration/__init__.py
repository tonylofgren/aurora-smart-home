"""Webhook Integration.

Custom integration that receives data via webhooks.
"""
from __future__ import annotations

import logging
from typing import Any

from aiohttp import web

from homeassistant.components import webhook
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DOMAIN, WEBHOOK_ID_KEY

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "data": {},
    }

    # Register webhook
    webhook_id = entry.data[WEBHOOK_ID_KEY]
    webhook.async_register(
        hass,
        DOMAIN,
        "My Webhook",
        webhook_id,
        async_handle_webhook,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    # Unregister webhook
    webhook_id = entry.data[WEBHOOK_ID_KEY]
    webhook.async_unregister(hass, webhook_id)

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_handle_webhook(
    hass: HomeAssistant,
    webhook_id: str,
    request: web.Request,
) -> web.Response:
    """Handle incoming webhook."""
    try:
        data = await request.json()
    except ValueError:
        _LOGGER.warning("Received invalid JSON in webhook")
        return web.Response(status=400, text="Invalid JSON")

    _LOGGER.debug("Received webhook data: %s", data)

    # Find the config entry for this webhook
    for entry_id, entry_data in hass.data[DOMAIN].items():
        entry = hass.config_entries.async_get_entry(entry_id)
        if entry and entry.data.get(WEBHOOK_ID_KEY) == webhook_id:
            # Update stored data
            entry_data["data"] = data

            # Notify entities to update
            async_dispatcher_send(hass, f"{DOMAIN}_{entry_id}_update")

            # Fire event for automations
            hass.bus.async_fire(
                f"{DOMAIN}_received",
                {
                    "webhook_id": webhook_id,
                    "data": data,
                },
            )

            return web.Response(text="OK")

    return web.Response(status=404, text="Webhook not found")
