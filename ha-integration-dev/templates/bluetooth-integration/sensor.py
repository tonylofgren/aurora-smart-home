"""Sensor platform for Bluetooth Device integration.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home

This demonstrates:
- Bluetooth device sensors using EntityDescription
- Proper device info for Bluetooth devices
- Coordinator-based entity updates
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import (
    CONNECTION_BLUETOOTH,
    DeviceInfo,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MyConfigEntry
from .const import DOMAIN
from .coordinator import MyBluetoothCoordinator


@dataclass(frozen=True, kw_only=True)
class MyBluetoothSensorDescription(SensorEntityDescription):
    """Describes a Bluetooth device sensor."""

    value_fn: Callable[[dict], Any]
    available_fn: Callable[[dict], bool] = lambda data: True


SENSOR_DESCRIPTIONS: tuple[MyBluetoothSensorDescription, ...] = (
    MyBluetoothSensorDescription(
        key="battery",
        name="Battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("battery"),
        available_fn=lambda data: "battery" in data,
    ),
    MyBluetoothSensorDescription(
        key="temperature",
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("temperature"),
        available_fn=lambda data: "temperature" in data,
    ),
    MyBluetoothSensorDescription(
        key="rssi",
        name="Signal Strength",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,  # Disabled by default
        value_fn=lambda data: data.get("rssi"),
        available_fn=lambda data: "rssi" in data,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bluetooth device sensors."""
    coordinator = entry.runtime_data

    async_add_entities(
        MyBluetoothSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class MyBluetoothSensor(
    CoordinatorEntity[MyBluetoothCoordinator],
    SensorEntity,
):
    """Representation of a Bluetooth device sensor."""

    entity_description: MyBluetoothSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MyBluetoothCoordinator,
        entry: MyConfigEntry,
        description: MyBluetoothSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description

        # Unique ID based on address and sensor key
        self._attr_unique_id = f"{coordinator.address}_{description.key}"

        # Device info for Bluetooth device
        self._attr_device_info = DeviceInfo(
            # Connection via Bluetooth
            connections={(CONNECTION_BLUETOOTH, coordinator.address)},
            # Identifiers
            identifiers={(DOMAIN, coordinator.address)},
            # Device metadata
            name=entry.data.get("name", f"Device {coordinator.address[-8:]}"),
            manufacturer="Unknown",  # Update with actual manufacturer
            model="Unknown",  # Update with actual model
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not super().available:
            return False
        if self.coordinator.data is None:
            return False
        return self.entity_description.available_fn(self.coordinator.data)

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
