"""Integration for extracting color from album change on spotify."""

import io
import random

from PIL import Image, UnidentifiedImageError

from homeassistant.components.media_player import (
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    MediaPlayerEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.event import (
    EventStateChangedData,
    async_track_state_change_event,
)
from homeassistant.helpers.typing import ConfigType, EventType

MEDIA_ENTITY = "media_player.spotify_erik_bengtsson"
KEY = "e0d2a815c385d12f19022a9fbd317e1f"


CONFIG_SCHEMA = cv.empty_config_schema(MEDIA_PLAYER_DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Docstring."""

    async def get_media_img() -> None:
        component: EntityComponent[MediaPlayerEntity] = hass.data[MEDIA_PLAYER_DOMAIN]
        entity = list(component.entities)[0].entity_id

        media_player: MediaPlayerEntity = component.get_entity(entity)
        image = await media_player.async_get_media_image()

        # Convert bytes to stream (file-like object in memory)
        picture_stream: io.BytesIO = io.BytesIO(image[0])

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
            {"entity_id": config["music_lights"]["light_id"], "rgb_color": rand_color},
        )

    @callback
    def update_lights_music(event: EventType[EventStateChangedData]) -> None:
        hass.add_job(get_media_img)

    async_track_state_change_event(hass, [MEDIA_ENTITY], update_lights_music)
    return True
