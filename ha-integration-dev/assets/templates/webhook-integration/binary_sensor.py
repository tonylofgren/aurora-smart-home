"""Binary Sensor platform for Webhook Integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, WEBHOOK_ID_KEY

_LOGGER = logging.getLogger(__name__)

# Consider webhook "connected" if received data in last 5 minutes
TIMEOUT_SECONDS = 300


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors from config entry."""
    async_add_entities([WebhookConnectivitySensor(hass, entry)])


class WebhookConnectivitySensor(BinarySensorEntity):
    """Binary sensor for webhook connectivity."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_name = "Connected"

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize sensor."""
        self.hass = hass
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_connectivity"
        self._last_update: datetime | None = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.data[CONF_NAME],
            manufacturer="Webhook",
            model="Webhook Receiver",
        )

    @property
    def is_on(self) -> bool:
        """Return True if webhook recently received data."""
        if self._last_update is None:
            return False
        return (datetime.now() - self._last_update).total_seconds() < TIMEOUT_SECONDS

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        webhook_id = self._entry.data[WEBHOOK_ID_KEY]
        return {
            "webhook_url": f"/api/webhook/{webhook_id}",
            "last_update": self._last_update.isoformat() if self._last_update else None,
        }

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        # Listen for webhook updates
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_{self._entry.entry_id}_update",
                self._handle_update,
            )
        )

        # Periodically check connectivity status
        self.async_on_remove(
            async_track_time_interval(
                self.hass,
                self._check_connectivity,
                timedelta(seconds=60),
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle data update."""
        self._last_update = datetime.now()
        self.async_write_ha_state()

    async def _check_connectivity(self, _: datetime) -> None:
        """Check if still connected."""
        self.async_write_ha_state()
