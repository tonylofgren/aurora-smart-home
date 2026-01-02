"""Config flow for Media Player Integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_NAME, default="My Media Player"): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]

            # Check if already configured
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            # Validate connection
            try:
                # TODO: Replace with actual connection test
                # await self._test_connection(host)
                pass
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, host),
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def _test_connection(self, host: str) -> bool:
        """Test connection to device."""
        # TODO: Implement actual connection test
        # Example:
        # client = MyMediaPlayerClient(host)
        # await client.async_connect()
        # await client.async_disconnect()
        return True
