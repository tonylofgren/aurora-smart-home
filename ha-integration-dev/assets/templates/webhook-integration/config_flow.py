"""Config flow for Webhook Integration."""
from __future__ import annotations

import secrets
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import webhook
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, WEBHOOK_ID_KEY

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="My Webhook"): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self._webhook_id: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            # Generate unique webhook ID
            webhook_id = secrets.token_hex(16)

            # Create entry
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={
                    CONF_NAME: user_input[CONF_NAME],
                    WEBHOOK_ID_KEY: webhook_id,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
        )

    async def async_step_import(self, import_data: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_data)
