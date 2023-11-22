"""Support for enabling and disabling the music syncing."""
from __future__ import annotations

from collections import Counter
import io
import random
from typing import Any

from PIL import Image, UnidentifiedImageError

from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
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

from .const import DOMAIN


class MusicLightSwitchEnabledEntity(SwitchEntity):
    """Enabled state of a light switcher."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_is_on = False
    _remove_music_listener: CALLBACK_TYPE | None = None

    def __init__(self, config_entry) -> None:
        """Initialize the entity."""
        self._attr_unique_id = config_entry.entry_id
        self.entity_id = f"{DOMAIN}.music_light_switch_enabled"
        self._media_player_entity_id = config_entry.options["media_player_entity_id"]
        self._light_ids = config_entry.options["light_ids"]

    async def _update_lights_music(
        self, event: EventType[EventStateChangedData]
    ) -> None:
        """Set the lights based on the current cover art."""
        if event.data["new_state"] is not None:
            domain = event.data["new_state"].domain
            entity_id = event.data["new_state"].entity_id
        else:
            return

        component: EntityComponent[MediaPlayerEntity] = self.hass.data[domain]
        media_player: MediaPlayerEntity | None = component.get_entity(entity_id)
        if media_player is not None:
            image = await media_player.async_get_media_image()
        else:
            return

        # Convert bytes to stream (file-like object in memory)
        image_bytes: bytes | None = image[0]
        if image_bytes is not None:
            picture_stream: io.BytesIO = io.BytesIO(image_bytes)
        else:
            return

        # Create a PIL Image,
        try:
            picture = Image.open(picture_stream)
        except UnidentifiedImageError:
            return

        # make sure that image is RGB based
        if picture.mode == "RGB":
            # Get the pixels from the image
            pixels = list(picture.getdata())

            # Count amount of times each pixel/color occurs
            color_counts = Counter(pixels)

            # Get the color that appears the most
            dominant_color = color_counts.most_common(1)[0][0]
        else:
            dominant_color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
        for light_id in self._light_ids:
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
        self._remove_music_listener = async_track_state_change_event(
            self.hass, [self._media_player_entity_id], self._update_lights_music
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self._attr_is_on = False
        if self._remove_music_listener is not None:
            self._remove_music_listener()
            self._remove_music_listener = None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up light entities."""
    async_add_entities([MusicLightSwitchEnabledEntity(config_entry)])
