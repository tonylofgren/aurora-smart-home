"""Conversation platform for LLM Conversation Agent.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home

This provides the ConversationEntity that appears in the Assist pipeline.
"""
from __future__ import annotations

from homeassistant.components.conversation import ConversationEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MyConfigEntry
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up conversation entity."""
    async_add_entities([LLMConversationEntity(config_entry)])


class LLMConversationEntity(ConversationEntity):
    """Entity representation for the LLM conversation agent."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the entity."""
        self._config_entry = config_entry
        self._attr_unique_id = config_entry.entry_id

        provider = config_entry.data.get("llm_provider", "unknown")
        model = config_entry.data.get("model", "unknown")

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=f"LLM Assistant ({provider.title()})",
            manufacturer=provider.title(),
            model=model,
            entry_type="service",
        )

    @property
    def supported_languages(self) -> list[str]:
        """Return supported languages."""
        return ["*"]  # All languages via LLM
