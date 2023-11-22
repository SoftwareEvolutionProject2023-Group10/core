"""Registers listeners for state change events."""
import io
import random

from PIL import Image, UnidentifiedImageError

from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.event import (
    EventStateChangedData,
    async_track_state_change_event,
)
from homeassistant.helpers.typing import ConfigType, EventType

from .const import DOMAIN

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register event listeners during startup of Home Assistant."""

    async def get_media_img(entity_id: str, domain: str) -> None:
        component: EntityComponent[MediaPlayerEntity] = hass.data[domain]
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
            pixels = list(picture.getdata())
            rand_color = random.choice(pixels)
        else:
            rand_color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
        await hass.services.async_call(
            "light",
            "turn_on",
            {"entity_id": "light.fake_light", "rgb_color": rand_color},
        )

    @callback
    def update_lights_music(event: EventType[EventStateChangedData]) -> None:
        if event.data["new_state"] is not None:
            domain = event.data["new_state"].domain
            entity_id = event.data["new_state"].entity_id
        else:
            return

        hass.add_job(get_media_img, entity_id, domain)

    async_track_state_change_event(
        hass, ["media_player.spotify_erik_bengtsson"], update_lights_music
    )

    return True
