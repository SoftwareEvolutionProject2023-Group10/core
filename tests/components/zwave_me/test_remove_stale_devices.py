"""Test the zwave_me removal of stale devices."""
from unittest.mock import patch
import uuid

import pytest
from zwave_me_ws import ZWaveMeData

from homeassistant.components.zwave_me import ZWaveMePlatform
from homeassistant.components.zwave_me.const import DOMAIN
from homeassistant.const import CONF_TOKEN, CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import MODULE_NAME

from tests.common import MockConfigEntry

DEFAULT_DEVICE_INFO = ZWaveMeData(
    id="DummyDevice",
    deviceType=ZWaveMePlatform.BINARY_SENSOR,
    title="DeviceDevice",
    level=100,
    deviceIdentifier="16-23",
)


async def mock_connection(controller):
    """Mock established connection and setting identifiers."""
    controller.on_new_device(DEFAULT_DEVICE_INFO)
    return True


@pytest.mark.parametrize(
    ("identifier", "should_exist"),
    [
        (DEFAULT_DEVICE_INFO.id, False),
        (DEFAULT_DEVICE_INFO.deviceIdentifier, True),
    ],
)
async def test_remove_stale_devices(
    hass: HomeAssistant, device_registry: dr.DeviceRegistry, identifier, should_exist
) -> None:
    """Test removing devices with old-format ids."""

    config_entry = MockConfigEntry(
        unique_id=uuid.uuid4(),
        domain=DOMAIN,
        data={CONF_TOKEN: "test_token", CONF_URL: "http://test_test"},
    )
    config_entry.add_to_hass(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        connections={("mac", "12:34:56:AB:CD:EF")},
        identifiers={(DOMAIN, f"{config_entry.unique_id}-{identifier}")},
    )
    with patch(
        f"{MODULE_NAME}.ZWaveMe.get_connection",
        mock_connection,
    ), patch(
        f"{MODULE_NAME}.async_setup_platforms",
    ):
        await hass.config_entries.async_setup(config_entry.entry_id)
    assert (
        bool(
            device_registry.async_get_device(
                identifiers={
                    (
                        DOMAIN,
                        f"{config_entry.unique_id}-{identifier}",
                    )
                }
            )
        )
        == should_exist
    )
