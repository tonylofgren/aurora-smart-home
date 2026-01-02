"""Config flow for LLM Conversation Agent.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_API_KEY,
    CONF_API_URL,
    CONF_LLM_PROVIDER,
    CONF_MAX_HISTORY,
    CONF_MODEL,
    CONF_TEMPERATURE,
    DEFAULT_MAX_HISTORY,
    DEFAULT_MODEL_ANTHROPIC,
    DEFAULT_MODEL_OLLAMA,
    DEFAULT_MODEL_OPENAI,
    DEFAULT_OLLAMA_URL,
    DEFAULT_TEMPERATURE,
    DOMAIN,
    PROVIDER_ANTHROPIC,
    PROVIDER_OLLAMA,
    PROVIDER_OPENAI,
)

_LOGGER = logging.getLogger(__name__)


class LLMConversationConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LLM Conversation Agent."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._provider: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle initial step - select provider."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._provider = user_input[CONF_LLM_PROVIDER]

            if self._provider == PROVIDER_OLLAMA:
                return await self.async_step_ollama()
            elif self._provider == PROVIDER_OPENAI:
                return await self.async_step_openai()
            elif self._provider == PROVIDER_ANTHROPIC:
                return await self.async_step_anthropic()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LLM_PROVIDER, default=PROVIDER_OLLAMA): vol.In(
                        {
                            PROVIDER_OLLAMA: "Ollama (Local)",
                            PROVIDER_OPENAI: "OpenAI",
                            PROVIDER_ANTHROPIC: "Anthropic Claude",
                        }
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_ollama(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure Ollama."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Test connection
            if await self._test_ollama(user_input[CONF_API_URL]):
                return self.async_create_entry(
                    title="LLM Assistant (Ollama)",
                    data={
                        CONF_LLM_PROVIDER: PROVIDER_OLLAMA,
                        CONF_API_URL: user_input[CONF_API_URL],
                        CONF_MODEL: user_input[CONF_MODEL],
                    },
                )
            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="ollama",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_URL, default=DEFAULT_OLLAMA_URL): str,
                    vol.Required(CONF_MODEL, default=DEFAULT_MODEL_OLLAMA): str,
                }
            ),
            errors=errors,
        )

    async def async_step_openai(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure OpenAI."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Test API key
            if await self._test_openai(user_input[CONF_API_KEY]):
                return self.async_create_entry(
                    title="LLM Assistant (OpenAI)",
                    data={
                        CONF_LLM_PROVIDER: PROVIDER_OPENAI,
                        CONF_API_KEY: user_input[CONF_API_KEY],
                        CONF_MODEL: user_input[CONF_MODEL],
                    },
                )
            errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="openai",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Required(CONF_MODEL, default=DEFAULT_MODEL_OPENAI): str,
                }
            ),
            errors=errors,
        )

    async def async_step_anthropic(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure Anthropic."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Test API key
            if await self._test_anthropic(user_input[CONF_API_KEY]):
                return self.async_create_entry(
                    title="LLM Assistant (Anthropic)",
                    data={
                        CONF_LLM_PROVIDER: PROVIDER_ANTHROPIC,
                        CONF_API_KEY: user_input[CONF_API_KEY],
                        CONF_MODEL: user_input[CONF_MODEL],
                    },
                )
            errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="anthropic",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Required(CONF_MODEL, default=DEFAULT_MODEL_ANTHROPIC): str,
                }
            ),
            errors=errors,
        )

    async def _test_ollama(self, url: str) -> bool:
        """Test Ollama connection."""
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(f"{url}/api/tags", timeout=5) as resp:
                return resp.status == 200
        except (aiohttp.ClientError, TimeoutError):
            return False

    async def _test_openai(self, api_key: str) -> bool:
        """Test OpenAI API key."""
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5,
            ) as resp:
                return resp.status == 200
        except (aiohttp.ClientError, TimeoutError):
            return False

    async def _test_anthropic(self, api_key: str) -> bool:
        """Test Anthropic API key."""
        # Anthropic doesn't have a simple validation endpoint
        # Just check key format
        return api_key.startswith("sk-ant-")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get options flow."""
        return LLMConversationOptionsFlow(config_entry)


class LLMConversationOptionsFlow(OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_TEMPERATURE,
                        default=self.config_entry.options.get(
                            CONF_TEMPERATURE, DEFAULT_TEMPERATURE
                        ),
                    ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=2.0)),
                    vol.Optional(
                        CONF_MAX_HISTORY,
                        default=self.config_entry.options.get(
                            CONF_MAX_HISTORY, DEFAULT_MAX_HISTORY
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=50)),
                }
            ),
        )
