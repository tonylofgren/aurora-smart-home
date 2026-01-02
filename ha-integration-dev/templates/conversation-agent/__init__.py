"""LLM Conversation Agent Integration.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home

This template demonstrates:
- Conversation agent registration
- LLM integration (Ollama, OpenAI, Anthropic)
- Conversation history management
- Home Assistant context injection
"""
from __future__ import annotations

import logging

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .conversation_agent import LLMConversationAgent

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CONVERSATION]

type MyConfigEntry = ConfigEntry[LLMConversationAgent]


async def async_setup_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Set up LLM Conversation Agent from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create conversation agent
    agent = LLMConversationAgent(hass, entry)

    # Register as conversation agent
    conversation.async_set_agent(hass, entry, agent)

    # Store reference
    entry.runtime_data = agent
    hass.data[DOMAIN][entry.entry_id] = agent

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info("LLM Conversation Agent configured successfully")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Unload a config entry."""
    # Unregister conversation agent
    conversation.async_unset_agent(hass, entry)

    # Clean up
    hass.data[DOMAIN].pop(entry.entry_id, None)

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
