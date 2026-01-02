"""Config flow for Bluetooth Device integration.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home

This demonstrates:
- Bluetooth device discovery via config flow
- User selection from discovered devices
- Manual address entry fallback
"""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS

from .const import DOMAIN, DEVICE_NAME_PREFIX, MANUFACTURER_ID

_LOGGER = logging.getLogger(__name__)


class MyBluetoothConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bluetooth device."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle a Bluetooth discovery."""
        _LOGGER.debug(
            "Discovered Bluetooth device: %s (%s)",
            discovery_info.name,
            discovery_info.address,
        )

        # Check if this is our device
        if not self._is_supported_device(discovery_info):
            return self.async_abort(reason="not_supported")

        # Set unique ID based on Bluetooth address
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        # Store for user confirmation
        self._discovered_devices[discovery_info.address] = discovery_info

        # Show confirmation dialog
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm Bluetooth device setup."""
        if user_input is not None:
            # User confirmed - create entry
            address = list(self._discovered_devices.keys())[0]
            discovery_info = self._discovered_devices[address]

            return self.async_create_entry(
                title=discovery_info.name or f"Device {address[-8:]}",
                data={
                    CONF_ADDRESS: address,
                    "name": discovery_info.name,
                },
            )

        # Show confirmation form
        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={
                "name": list(self._discovered_devices.values())[0].name
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle user-initiated config flow."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS]

            # Validate address format
            if not self._is_valid_address(address):
                errors["base"] = "invalid_address"
            else:
                await self.async_set_unique_id(address)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Device {address[-8:]}",
                    data={
                        CONF_ADDRESS: address,
                    },
                )

        # Discover nearby devices
        discovered = await self._async_get_discovered_devices()

        if discovered:
            # Show picker for discovered devices
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_ADDRESS): vol.In(discovered),
                    }
                ),
                errors=errors,
            )

        # No devices found - allow manual entry
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "no_devices": "No devices found. Enter address manually."
            },
        )

    async def _async_get_discovered_devices(self) -> dict[str, str]:
        """Get discovered Bluetooth devices."""
        devices: dict[str, str] = {}

        for discovery_info in async_discovered_service_info(self.hass):
            if self._is_supported_device(discovery_info):
                # Already configured?
                if discovery_info.address in self._async_current_ids():
                    continue

                display_name = (
                    discovery_info.name
                    or f"Unknown ({discovery_info.address[-8:]})"
                )
                devices[discovery_info.address] = display_name

        return devices

    def _is_supported_device(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> bool:
        """Check if the discovered device is supported."""
        # Option 1: Check by name prefix
        if discovery_info.name and discovery_info.name.startswith(DEVICE_NAME_PREFIX):
            return True

        # Option 2: Check by manufacturer data
        if MANUFACTURER_ID in discovery_info.manufacturer_data:
            return True

        # Option 3: Check by service UUID
        # if SERVICE_UUID in discovery_info.service_uuids:
        #     return True

        return False

    def _is_valid_address(self, address: str) -> bool:
        """Validate Bluetooth address format."""
        # Format: XX:XX:XX:XX:XX:XX
        parts = address.upper().split(":")
        if len(parts) != 6:
            return False
        return all(
            len(part) == 2 and all(c in "0123456789ABCDEF" for c in part)
            for part in parts
        )
