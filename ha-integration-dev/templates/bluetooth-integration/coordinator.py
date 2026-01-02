"""DataUpdateCoordinator for Bluetooth Device.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home

This demonstrates:
- Passive Bluetooth data collection (advertisements)
- Active Bluetooth connections for reading characteristics
- Proper async handling for Bluetooth operations
"""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice

from homeassistant.components.bluetooth import (
    BluetoothCallbackMatcher,
    BluetoothChange,
    BluetoothServiceInfoBleak,
    async_register_callback,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CHAR_BATTERY_LEVEL,
    CHAR_TEMPERATURE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

if TYPE_CHECKING:
    from . import MyConfigEntry

_LOGGER = logging.getLogger(__name__)


class MyBluetoothCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator for Bluetooth device data."""

    config_entry: MyConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: MyConfigEntry,
        ble_device: BLEDevice,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.ble_device = ble_device
        self.address = entry.data["address"]
        self._cancel_bluetooth_callback: callable | None = None

        # Cached data from advertisements
        self._advertisement_data: dict = {}

    def async_start(self) -> callable:
        """Start listening for Bluetooth advertisements."""
        @callback
        def _async_bluetooth_callback(
            service_info: BluetoothServiceInfoBleak,
            change: BluetoothChange,
        ) -> None:
            """Handle Bluetooth advertisement."""
            _LOGGER.debug(
                "Received advertisement from %s: RSSI=%s",
                service_info.address,
                service_info.rssi,
            )

            # Parse advertisement data
            self._advertisement_data = self._parse_advertisement(service_info)

            # Update coordinator data
            self.async_set_updated_data({
                **self.data or {},
                **self._advertisement_data,
                "rssi": service_info.rssi,
            })

        # Register for advertisements from this device
        self._cancel_bluetooth_callback = async_register_callback(
            self.hass,
            _async_bluetooth_callback,
            BluetoothCallbackMatcher(address=self.address),
            BluetoothScanningMode.PASSIVE,
        )

        return self._cancel_bluetooth_callback

    async def _async_update_data(self) -> dict:
        """Fetch data from the Bluetooth device.

        This method is called periodically by the coordinator.
        Use this for active connections when you need to read
        characteristics that aren't broadcast in advertisements.
        """
        try:
            # Option 1: Just return advertisement data (passive)
            if self._advertisement_data:
                return {
                    **self._advertisement_data,
                    "last_seen": self.hass.loop.time(),
                }

            # Option 2: Active connection to read characteristics
            return await self._async_read_device_data()

        except BleakError as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout connecting to device") from err

    async def _async_read_device_data(self) -> dict:
        """Read data from device via active BLE connection.

        Use this pattern when you need to read characteristics
        that aren't available in advertisements.
        """
        data: dict = {}

        # Get fresh BLE device reference
        ble_device = async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )

        if not ble_device:
            raise UpdateFailed("Device not found")

        async with BleakClient(ble_device) as client:
            # Read battery level
            try:
                battery_data = await client.read_gatt_char(CHAR_BATTERY_LEVEL)
                data["battery"] = battery_data[0]
            except BleakError:
                _LOGGER.debug("Could not read battery level")

            # Read temperature (if available)
            try:
                temp_data = await client.read_gatt_char(CHAR_TEMPERATURE)
                # Parse temperature (format depends on device)
                data["temperature"] = int.from_bytes(temp_data[:2], "little") / 100
            except BleakError:
                _LOGGER.debug("Could not read temperature")

        return data

    def _parse_advertisement(
        self, service_info: BluetoothServiceInfoBleak
    ) -> dict:
        """Parse manufacturer data from advertisement.

        Customize this based on your device's advertisement format.
        """
        data: dict = {}

        # Example: Parse manufacturer data
        # Format varies by device - check your device's documentation
        if manufacturer_data := service_info.manufacturer_data:
            for manufacturer_id, payload in manufacturer_data.items():
                _LOGGER.debug(
                    "Manufacturer %04x data: %s",
                    manufacturer_id,
                    payload.hex(),
                )

                # Example parsing (customize for your device):
                # if len(payload) >= 4:
                #     data["battery"] = payload[0]
                #     data["temperature"] = int.from_bytes(payload[1:3], "little") / 10

        return data


# Import needed for async_ble_device_from_address
from homeassistant.components.bluetooth import (
    async_ble_device_from_address,
    BluetoothScanningMode,
)
