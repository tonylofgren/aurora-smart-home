"""Bluetooth Device Integration.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home

This template demonstrates:
- Bluetooth device discovery
- Passive BLE scanning
- Active BLE connections
- Coordinator pattern for Bluetooth data
"""
from __future__ import annotations

import logging

from homeassistant.components.bluetooth import (
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
    async_ble_device_from_address,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import MyBluetoothCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

type MyConfigEntry = ConfigEntry[MyBluetoothCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Set up Bluetooth device from a config entry."""
    address: str = entry.data["address"]

    # Get the BLE device from Home Assistant's Bluetooth manager
    ble_device = async_ble_device_from_address(
        hass, address, connectable=True
    )

    if not ble_device:
        raise ConfigEntryNotReady(
            f"Could not find Bluetooth device with address {address}"
        )

    # Create coordinator
    coordinator = MyBluetoothCoordinator(
        hass,
        entry,
        ble_device,
    )

    # Start listening for advertisements
    entry.async_on_unload(
        coordinator.async_start()
    )

    # Initial data fetch
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
