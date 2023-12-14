"""Support for enabling and disabling the music syncing."""
from __future__ import annotations

import io
from typing import Any

from colorthief import ColorThief

from homeassistant.components.media_player import (
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    MediaPlayerEntity,
    MediaPlayerState,
)
from homeassistant.components.switch import (
    DOMAIN as SWITCH_DOMAIN,
    SwitchDeviceClass,
    SwitchEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    EventStateChangedData,
    async_track_state_change_event,
)
from homeassistant.helpers.typing import EventType


class MusicLightSwitchEnabledEntity(SwitchEntity):
    """Enabled state of a light switcher."""

    entity_id = f"{SWITCH_DOMAIN}.music_light_switch_enabled"
    _attr_name = "Music light switch"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_is_on = False
    _remove_music_listener: CALLBACK_TYPE | None = None

    def __init__(self, config_entry) -> None:
        """Initialize the entity."""
        self._attr_unique_id = config_entry.entry_id
        self._config_entry = config_entry
        config_entry.async_on_unload(
            config_entry.add_update_listener(self._on_config_entry_update)
        )
        config_entry.async_on_unload(self.async_turn_off)

    async def _on_config_entry_update(
        self, hass: HomeAssistant, config_entry: ConfigEntry
    ) -> None:
        if self.is_on:
            await self.async_turn_off()
            await self.async_turn_on()

    async def _update_lights(
        self, event: EventType[EventStateChangedData] | None = None
    ) -> None:
        """Set the lights based on the current cover art."""
        component: EntityComponent[MediaPlayerEntity] = self.hass.data[
            MEDIA_PLAYER_DOMAIN
        ]
        media_player: MediaPlayerEntity | None = component.get_entity(
            self.media_player_entity_id
        )
        if media_player is None or media_player.state != MediaPlayerState.PLAYING:
            return

        image = await media_player.async_get_media_image()
        image_bytes = image[0]

        dominant_color = color_extractor(image_bytes)

        for light_id in self.light_ids:
            await self.hass.services.async_call(
                "light",
                "turn_on",
                {"entity_id": light_id, "rgb_color": dominant_color},
            )

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self._attr_is_on = True
        await self._update_lights()
        self._remove_music_listener = async_track_state_change_event(
            self.hass, [self.media_player_entity_id], self._update_lights
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self._attr_is_on = False
        if self._remove_music_listener is not None:
            self._remove_music_listener()
            self._remove_music_listener = None

    @property
    def media_player_entity_id(self):
        """Getter for media_player_entity_id."""
        return self._config_entry.options["media_player_entity_id"]

    @property
    def light_ids(self):
        """Getter for light_ids."""
        return self._config_entry.options["light_ids"]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up light entities."""
    async_add_entities([MusicLightSwitchEnabledEntity(config_entry)])


def color_extractor(image_bytes):
    """Extract color from image."""
    if image_bytes is None:
        return

    color_thief = ColorThief(io.BytesIO(image_bytes))
    dominant_color = color_thief.get_color(quality=5)
    return dominant_color
