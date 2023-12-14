"""Tests for the music light switch."""
from unittest.mock import patch

from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.components.music_light_switch.const import DOMAIN
from homeassistant.components.music_light_switch.switch import color_extractor
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from tests.common import MockConfigEntry, async_mock_service
from tests.components.media_player.common import async_media_next_track


def load_test_image():
    """Load a monochromatic test image."""
    with open("testimage.png", "rb") as image_file:
        image = image_file.read()
        return image


async def test_music_switch(hass: HomeAssistant):
    """Test for the music switcher."""
    await async_setup_component(hass, domain="music_light_switch", config={})

    # Assert 3 because it uses http, mediaplayer and music light switch
    assert len(hass.config_entries.hass.data.get("integrations")) == 3


async def test_light(hass: HomeAssistant):
    """Test color extractor."""
    assert color_extractor(load_test_image()) == (252, 68, 4)


async def test_song_changes(hass: HomeAssistant):
    """Test that the lights change when the song changes."""
    with patch(
        "homeassistant.components.demo.media_player.DemoMusicPlayer.async_get_media_image",
        return_value=(load_test_image(), "image/png"),
    ):
        await async_setup_component(hass, "homeassistant", {})
        await async_setup_component(
            hass, "media_player", {"media_player": {"platform": "demo"}}
        )
        MEDIA_PLAYER_ENTITY_ID = "media_player.kitchen"
        # Synchronize because the light component is loaded as a dependency
        # (inteferes with the SERVICE_TURN_ON mock)
        await hass.async_block_till_done()

        LIGHT_ENTITY_ID = "light.test"
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            options={
                "media_player_entity_id": MEDIA_PLAYER_ENTITY_ID,
                "light_ids": [LIGHT_ENTITY_ID],
            },
        )
        await hass.config_entries.async_add(config_entry)
        SWITCH_ENTITY_ID = "switch.music_light_switch_enabled"

        light_service_calls = async_mock_service(hass, LIGHT_DOMAIN, SERVICE_TURN_ON)
        await hass.async_block_till_done()

        # If the switch is off, song changes do not trigger light changes
        assert hass.states.get(SWITCH_ENTITY_ID).state == STATE_OFF
        await async_media_next_track(hass)
        await hass.async_block_till_done()
        assert len(light_service_calls) == 0

        # Turn the switch on (also triggers light changes)
        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: SWITCH_ENTITY_ID},
        )
        await hass.async_block_till_done()
        assert len(light_service_calls) == 1

        # If the switch is on, song changes trigger light changes
        await async_media_next_track(hass)
        await hass.async_block_till_done()
        assert len(light_service_calls) == 2

        # Turn the switch off again
        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: SWITCH_ENTITY_ID},
        )
        assert len(light_service_calls) == 2

        # If the switch is off, song changes do not trigger light changes
        await async_media_next_track(hass)
        await hass.async_block_till_done()
        assert len(light_service_calls) == 2
