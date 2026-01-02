"""Media Player platform for My Media Player Integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MediaPlayerCoordinator

_LOGGER = logging.getLogger(__name__)

# Map device states to HA states
STATE_MAP = {
    "playing": MediaPlayerState.PLAYING,
    "paused": MediaPlayerState.PAUSED,
    "stopped": MediaPlayerState.IDLE,
    "idle": MediaPlayerState.IDLE,
    "off": MediaPlayerState.OFF,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up media player from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([MyMediaPlayer(coordinator, entry)])


class MyMediaPlayer(CoordinatorEntity[MediaPlayerCoordinator], MediaPlayerEntity):
    """Media player entity."""

    _attr_has_entity_name = True
    _attr_name = None  # Uses device name
    _attr_device_class = MediaPlayerDeviceClass.SPEAKER

    # Define supported features
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.SELECT_SOURCE
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
    )

    def __init__(
        self,
        coordinator: MediaPlayerCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize media player."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = entry.data[CONF_HOST]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.data[CONF_HOST])},
            name=self._entry.data.get(CONF_NAME, "My Media Player"),
            manufacturer="My Company",
            model="Media Player Model",
        )

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the state of the player."""
        if self.coordinator.data is None:
            return None
        device_state = self.coordinator.data.get("state", "idle")
        return STATE_MAP.get(device_state, MediaPlayerState.IDLE)

    @property
    def volume_level(self) -> float | None:
        """Return volume level (0.0 to 1.0)."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("volume")

    @property
    def is_volume_muted(self) -> bool | None:
        """Return if volume is muted."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("muted", False)

    @property
    def media_title(self) -> str | None:
        """Return current media title."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("media_title")

    @property
    def media_artist(self) -> str | None:
        """Return current media artist."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("media_artist")

    @property
    def media_album_name(self) -> str | None:
        """Return current media album."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("media_album")

    @property
    def media_duration(self) -> int | None:
        """Return media duration in seconds."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("media_duration")

    @property
    def media_position(self) -> int | None:
        """Return media position in seconds."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("media_position")

    @property
    def source(self) -> str | None:
        """Return current source."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("source")

    @property
    def source_list(self) -> list[str] | None:
        """Return list of available sources."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("source_list")

    async def async_turn_on(self) -> None:
        """Turn on the player."""
        await self.coordinator.async_send_command("power_on")

    async def async_turn_off(self) -> None:
        """Turn off the player."""
        await self.coordinator.async_send_command("power_off")

    async def async_media_play(self) -> None:
        """Play media."""
        await self.coordinator.async_send_command("play")

    async def async_media_pause(self) -> None:
        """Pause media."""
        await self.coordinator.async_send_command("pause")

    async def async_media_stop(self) -> None:
        """Stop media."""
        await self.coordinator.async_send_command("stop")

    async def async_media_previous_track(self) -> None:
        """Previous track."""
        await self.coordinator.async_send_command("previous")

    async def async_media_next_track(self) -> None:
        """Next track."""
        await self.coordinator.async_send_command("next")

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level (0.0 to 1.0)."""
        await self.coordinator.async_send_command("set_volume", volume=volume)

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute/unmute volume."""
        await self.coordinator.async_send_command("mute", muted=mute)

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        await self.coordinator.async_send_command("select_source", source=source)
