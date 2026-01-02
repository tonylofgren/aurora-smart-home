"""Sensor platform for Webhook Integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_SENSORS, DOMAIN, WEBHOOK_ID_KEY

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from config entry."""
    entities = [
        WebhookSensor(hass, entry, sensor_key)
        for sensor_key in DEFAULT_SENSORS
    ]
    async_add_entities(entities)


class WebhookSensor(SensorEntity):
    """Sensor entity for webhook data."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        sensor_key: str,
    ) -> None:
        """Initialize sensor."""
        self.hass = hass
        self._entry = entry
        self._sensor_key = sensor_key
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"
        self._attr_translation_key = sensor_key

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.data[CONF_NAME],
            manufacturer="Webhook",
            model="Webhook Receiver",
            configuration_url=self._webhook_url,
        )

    @property
    def _webhook_url(self) -> str:
        """Return webhook URL."""
        webhook_id = self._entry.data[WEBHOOK_ID_KEY]
        return f"/api/webhook/{webhook_id}"

    @property
    def name(self) -> str:
        """Return sensor name."""
        return self._sensor_key.replace("_", " ").title()

    @property
    def native_value(self) -> Any | None:
        """Return sensor value."""
        data = self.hass.data[DOMAIN].get(self._entry.entry_id, {}).get("data", {})
        return data.get(self._sensor_key)

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_{self._entry.entry_id}_update",
                self._handle_update,
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle data update."""
        self.async_write_ha_state()
