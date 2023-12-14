"""Tests for the music light switch."""
from homeassistant.components.music_light_switch.switch import color_extractor
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component


async def test_music_switch(hass: HomeAssistant):
    """Test for the music switcher."""
    await async_setup_component(hass, domain="music_light_switch", config={})

    # Assert 3 because it uses http, mediaplayer and music light switch
    assert len(hass.config_entries.hass.data.get("integrations")) == 3


def test_light(hass: HomeAssistant):
    """Test color extractor."""
    with open("testimage.png", "rb") as image_file:
        image = image_file.read()
        # bytes= binascii.hexlify(image).decode("utf-8")

    assert color_extractor(image) == (252, 68, 4)
