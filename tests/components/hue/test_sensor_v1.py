"""Philips Hue sensors platform tests."""
import asyncio
from unittest.mock import Mock

import aiohue
from freezegun.api import FrozenDateTimeFactory

from homeassistant.components import hue
from homeassistant.components.hue.const import ATTR_HUE_EVENT
from homeassistant.components.hue.v1 import sensor_base
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get

from .conftest import create_mock_bridge, setup_platform

from tests.common import async_capture_events, async_fire_time_changed

PRESENCE_SENSOR_1_PRESENT = {
    "state": {"presence": True, "lastupdated": "2019-01-01T01:00:00"},
    "swupdate": {"state": "noupdates", "lastinstall": "2019-01-01T00:00:00"},
    "config": {
        "on": True,
        "battery": 100,
        "reachable": True,
        "alert": "none",
        "ledindication": False,
        "usertest": False,
        "sensitivity": 2,
        "sensitivitymax": 2,
        "pending": [],
    },
    "name": "Living room sensor",
    "type": "ZLLPresence",
    "modelid": "SML001",
    "manufacturername": "Philips",
    "productname": "Hue motion sensor",
    "swversion": "6.1.1.27575",
    "uniqueid": "00:11:22:33:44:55:66:77-02-0406",
    "capabilities": {"certified": True},
}
LIGHT_LEVEL_SENSOR_1 = {
    "state": {
        "lightlevel": 1,
        "dark": True,
        "daylight": True,
        "lastupdated": "2019-01-01T01:00:00",
    },
    "swupdate": {"state": "noupdates", "lastinstall": "2019-01-01T00:00:00"},
    "config": {
        "on": True,
        "battery": 100,
        "reachable": True,
        "alert": "none",
        "tholddark": 12467,
        "tholdoffset": 7000,
        "ledindication": False,
        "usertest": False,
        "pending": [],
    },
    "name": "Hue ambient light sensor 1",
    "type": "ZLLLightLevel",
    "modelid": "SML001",
    "manufacturername": "Philips",
    "productname": "Hue ambient light sensor",
    "swversion": "6.1.1.27575",
    "uniqueid": "00:11:22:33:44:55:66:77-02-0400",
    "capabilities": {"certified": True},
}
TEMPERATURE_SENSOR_1 = {
    "state": {"temperature": 1775, "lastupdated": "2019-01-01T01:00:00"},
    "swupdate": {"state": "noupdates", "lastinstall": "2019-01-01T01:00:00"},
    "config": {
        "on": True,
        "battery": 100,
        "reachable": True,
        "alert": "none",
        "ledindication": False,
        "usertest": False,
        "pending": [],
    },
    "name": "Hue temperature sensor 1",
    "type": "ZLLTemperature",
    "modelid": "SML001",
    "manufacturername": "Philips",
    "productname": "Hue temperature sensor",
    "swversion": "6.1.1.27575",
    "uniqueid": "00:11:22:33:44:55:66:77-02-0402",
    "capabilities": {"certified": True},
}
PRESENCE_SENSOR_2_NOT_PRESENT = {
    "state": {"presence": False, "lastupdated": "2019-01-01T00:00:00"},
    "swupdate": {"state": "noupdates", "lastinstall": "2019-01-01T01:00:00"},
    "config": {
        "on": True,
        "battery": 100,
        "reachable": True,
        "alert": "none",
        "ledindication": False,
        "usertest": False,
        "sensitivity": 2,
        "sensitivitymax": 2,
        "pending": [],
    },
    "name": "Kitchen sensor",
    "type": "ZLLPresence",
    "modelid": "SML001",
    "manufacturername": "Philips",
    "productname": "Hue motion sensor",
    "swversion": "6.1.1.27575",
    "uniqueid": "00:11:22:33:44:55:66:88-02-0406",
    "capabilities": {"certified": True},
}
LIGHT_LEVEL_SENSOR_2 = {
    "state": {
        "lightlevel": 10001,
        "dark": True,
        "daylight": True,
        "lastupdated": "2019-01-01T01:00:00",
    },
    "swupdate": {"state": "noupdates", "lastinstall": "2019-01-01T00:00:00"},
    "config": {
        "on": True,
        "battery": 100,
        "reachable": True,
        "alert": "none",
        "tholddark": 12467,
        "tholdoffset": 7000,
        "ledindication": False,
        "usertest": False,
        "pending": [],
    },
    "name": "Hue ambient light sensor 2",
    "type": "ZLLLightLevel",
    "modelid": "SML001",
    "manufacturername": "Philips",
    "productname": "Hue ambient light sensor",
    "swversion": "6.1.1.27575",
    "uniqueid": "00:11:22:33:44:55:66:88-02-0400",
    "capabilities": {"certified": True},
}
TEMPERATURE_SENSOR_2 = {
    "state": {"temperature": 1875, "lastupdated": "2019-01-01T01:00:00"},
    "swupdate": {"state": "noupdates", "lastinstall": "2019-01-01T01:00:00"},
    "config": {
        "on": True,
        "battery": 100,
        "reachable": True,
        "alert": "none",
        "ledindication": False,
        "usertest": False,
        "pending": [],
    },
    "name": "Hue temperature sensor 2",
    "type": "ZLLTemperature",
    "modelid": "SML001",
    "manufacturername": "Philips",
    "productname": "Hue temperature sensor",
    "swversion": "6.1.1.27575",
    "uniqueid": "00:11:22:33:44:55:66:88-02-0402",
    "capabilities": {"certified": True},
}
PRESENCE_SENSOR_3_PRESENT = {
    "state": {"presence": True, "lastupdated": "2019-01-01T01:00:00"},
    "swupdate": {"state": "noupdates", "lastinstall": "2019-01-01T00:00:00"},
    "config": {
        "on": True,
        "battery": 100,
        "reachable": True,
        "alert": "none",
        "ledindication": False,
        "usertest": False,
        "sensitivity": 2,
        "sensitivitymax": 2,
        "pending": [],
    },
    "name": "Bedroom sensor",
    "type": "ZLLPresence",
    "modelid": "SML001",
    "manufacturername": "Philips",
    "productname": "Hue motion sensor",
    "swversion": "6.1.1.27575",
    "uniqueid": "00:11:22:33:44:55:66:99-02-0406",
    "capabilities": {"certified": True},
}
LIGHT_LEVEL_SENSOR_3 = {
    "state": {
        "lightlevel": 1,
        "dark": True,
        "daylight": True,
        "lastupdated": "2019-01-01T01:00:00",
    },
    "swupdate": {"state": "noupdates", "lastinstall": "2019-01-01T00:00:00"},
    "config": {
        "on": True,
        "battery": 100,
        "reachable": True,
        "alert": "none",
        "tholddark": 12467,
        "tholdoffset": 7000,
        "ledindication": False,
        "usertest": False,
        "pending": [],
    },
    "name": "Hue ambient light sensor 3",
    "type": "ZLLLightLevel",
    "modelid": "SML001",
    "manufacturername": "Philips",
    "productname": "Hue ambient light sensor",
    "swversion": "6.1.1.27575",
    "uniqueid": "00:11:22:33:44:55:66:99-02-0400",
    "capabilities": {"certified": True},
}
TEMPERATURE_SENSOR_3 = {
    "state": {"temperature": 1775, "lastupdated": "2019-01-01T01:00:00"},
    "swupdate": {"state": "noupdates", "lastinstall": "2019-01-01T01:00:00"},
    "config": {
        "on": True,
        "battery": 100,
        "reachable": True,
        "alert": "none",
        "ledindication": False,
        "usertest": False,
        "pending": [],
    },
    "name": "Hue temperature sensor 3",
    "type": "ZLLTemperature",
    "modelid": "SML001",
    "manufacturername": "Philips",
    "productname": "Hue temperature sensor",
    "swversion": "6.1.1.27575",
    "uniqueid": "00:11:22:33:44:55:66:99-02-0402",
    "capabilities": {"certified": True},
}
UNSUPPORTED_SENSOR = {
    "state": {"status": 0, "lastupdated": "2019-01-01T01:00:00"},
    "config": {"on": True, "reachable": True},
    "name": "Unsupported sensor",
    "type": "CLIPGenericStatus",
    "modelid": "PHWA01",
    "manufacturername": "Philips",
    "swversion": "1.0",
    "uniqueid": "arbitrary",
    "recycle": True,
}
HUE_TAP_REMOTE_1 = {
    "state": {"buttonevent": 17, "lastupdated": "2019-06-22T14:43:50"},
    "swupdate": {"state": "notupdatable", "lastinstall": None},
    "config": {"on": True},
    "name": "Hue Tap",
    "type": "ZGPSwitch",
    "modelid": "ZGPSWITCH",
    "manufacturername": "Philips",
    "productname": "Hue tap switch",
    "diversityid": "d8cde5d5-0eef-4b95-b0f0-71ddd2952af4",
    "uniqueid": "00:00:00:00:00:44:23:08-f2",
    "capabilities": {"certified": True, "primary": True, "inputs": []},
}
HUE_DIMMER_REMOTE_1 = {
    "state": {"buttonevent": 4002, "lastupdated": "2019-12-28T21:58:02"},
    "swupdate": {"state": "noupdates", "lastinstall": "2019-10-13T13:16:15"},
    "config": {"on": True, "battery": 100, "reachable": True, "pending": []},
    "name": "Hue dimmer switch 1",
    "type": "ZLLSwitch",
    "modelid": "RWL021",
    "manufacturername": "Philips",
    "productname": "Hue dimmer switch",
    "diversityid": "73bbabea-3420-499a-9856-46bf437e119b",
    "swversion": "6.1.1.28573",
    "uniqueid": "00:17:88:01:10:3e:3a:dc-02-fc00",
    "capabilities": {"certified": True, "primary": True, "inputs": []},
}
SENSOR_RESPONSE = {
    "1": PRESENCE_SENSOR_1_PRESENT,
    "2": LIGHT_LEVEL_SENSOR_1,
    "3": TEMPERATURE_SENSOR_1,
    "4": PRESENCE_SENSOR_2_NOT_PRESENT,
    "5": LIGHT_LEVEL_SENSOR_2,
    "6": TEMPERATURE_SENSOR_2,
    "7": HUE_TAP_REMOTE_1,
    "8": HUE_DIMMER_REMOTE_1,
}


def add_sensor_response(mock_bridge, sensor_data):
    """Add a sensor response to the mock bridge.

    Example:
        add_sensor_response(
        mock_bridge_2,
        {
            "1": PRESENCE_SENSOR_3_PRESENT,
            "2": LIGHT_LEVEL_SENSOR_3,
            "3": TEMPERATURE_SENSOR_3,
        },
    ).
    """
    mock_bridge.mock_sensor_responses.append(sensor_data)


async def setup_hue_platform(hass, mock_bridge, platforms):
    """Asynchronous setting up the Philips Hue platform for testing.

    Example:
        await setup_hue_platform(hass, mock_bridge_v1, ["binary_sensor", "sensor"]).

    This setting up the v1 bridge with the binary sensor and normal sensor
    """
    await setup_platform(hass, mock_bridge, platforms)


def assert_sensor_state(hass, entity_id, expected_state, expected_name):
    """Assert the state and name of a sensor."""
    sensor = hass.states.get(entity_id)
    assert sensor is not None
    assert sensor.state == expected_state
    assert sensor.name == expected_name


def assert_length(checker, length):
    """Assert the length of a sequence.

    Example:
        Assert that the length of `checker` is equal to `length`.
    """
    assert len(checker) == length


async def test_no_sensors(hass: HomeAssistant, mock_bridge_v1) -> None:
    """Test the update_items function when no sensors are found."""
    add_sensor_response(mock_bridge_v1, {})
    await setup_hue_platform(hass, mock_bridge_v1, ["binary_sensor", "sensor"])
    assert_length(mock_bridge_v1.mock_request, 1)
    assert_length(hass.states.async_all(), 0)


async def test_sensors_with_multiple_bridges(
    hass: HomeAssistant, mock_bridge_v1
) -> None:
    """Test the update_items function with some sensors."""
    mock_bridge_2 = create_mock_bridge(hass)
    add_sensor_response(
        mock_bridge_2,
        {
            "1": PRESENCE_SENSOR_3_PRESENT,
            "2": LIGHT_LEVEL_SENSOR_3,
            "3": TEMPERATURE_SENSOR_3,
        },
    )
    add_sensor_response(mock_bridge_v1, SENSOR_RESPONSE)
    await setup_hue_platform(hass, mock_bridge_v1, ["binary_sensor", "sensor"])
    await setup_platform(
        hass, mock_bridge_2, ["binary_sensor", "sensor"], "mock-bridge-2"
    )
    assert_length(mock_bridge_v1.mock_requests, 1)
    assert_length(mock_bridge_2.mock_requests, 1)
    # 3 "physical" sensors with 3 virtual sensors each + 1 battery sensor
    assert_length(hass.states.async_all(), 10)


async def test_sensors(hass: HomeAssistant, mock_bridge_v1) -> None:
    """Test the update_items function with some sensors."""
    add_sensor_response(mock_bridge_v1, SENSOR_RESPONSE)
    await setup_hue_platform(hass, mock_bridge_v1, ["binary_sensor", "sensor"])
    assert_length(mock_bridge_v1.mock_requests, 1)
    # 2 "physical" sensors with 3 virtual sensors each
    assert_length(hass.states.async_all(), 7)

    assert_sensor_state(
        hass,
        "binary_sensor.living_room_sensor_motion",
        "on",
        "Living room sensor motion",
    )
    assert_sensor_state(
        hass,
        "sensor.living_room_sensor_light_level",
        "1.0",
        "Living room sensor light level",
    )
    assert_sensor_state(
        hass,
        "sensor.living_room_sensor_temperature",
        "17.75",
        "Living room sensor temperature",
    )

    assert_sensor_state(
        hass, "binary_sensor.kitchen_sensor_motion", "off", "Kitchen sensor motion"
    )
    assert_sensor_state(
        hass,
        "sensor.kitchen_sensor_light_level",
        "10.0",
        "Kitchen sensor light level",
    )
    assert_sensor_state(
        hass,
        "sensor.kitchen_sensor_temperature",
        "18.75",
        "Kitchen sensor temperature",
    )

    assert_sensor_state(
        hass,
        "sensor.hue_dimmer_switch_1_battery_level",
        "100",
        "Hue dimmer switch 1 battery level",
    )

    ent_reg = async_get(hass)
    assert (
        ent_reg.async_get("sensor.hue_dimmer_switch_1_battery_level").entity_category
        == EntityCategory.DIAGNOSTIC
    )


async def test_unsupported_sensors(hass: HomeAssistant, mock_bridge_v1) -> None:
    """Test that unsupported sensors don't get added and don't fail."""
    response_with_unsupported = dict(SENSOR_RESPONSE)
    response_with_unsupported["7"] = UNSUPPORTED_SENSOR
    add_sensor_response(mock_bridge_v1, response_with_unsupported)
    await setup_hue_platform(hass, mock_bridge_v1, ["binary_sensor", "sensor"])
    assert_length(mock_bridge_v1.mock_requests, 1)
    # 2 "physical" sensors with 3 virtual sensors each + 1 battery sensor
    assert_length(hass.states.async_all(), 7)


async def test_new_sensor_discovered(hass: HomeAssistant, mock_bridge_v1) -> None:
    """Test if 2nd update has a new sensor."""
    add_sensor_response(mock_bridge_v1, SENSOR_RESPONSE)

    await setup_hue_platform(hass, mock_bridge_v1, ["binary_sensor", "sensor"])
    assert_length(mock_bridge_v1.mock_requests, 1)
    assert_length(hass.states.async_all(), 7)

    new_sensor_response = dict(SENSOR_RESPONSE)
    new_sensor_response.update(
        {
            "9": PRESENCE_SENSOR_3_PRESENT,
            "10": LIGHT_LEVEL_SENSOR_3,
            "11": TEMPERATURE_SENSOR_3,
        }
    )

    add_sensor_response(mock_bridge_v1, new_sensor_response)

    # Force updates to run again
    await mock_bridge_v1.sensor_manager.coordinator.async_refresh()
    await hass.async_block_till_done()

    assert_length(mock_bridge_v1.mock_requests, 2)
    assert_length(hass.states.async_all(), 10)

    assert_sensor_state(
        hass, "binary_sensor.bedroom_sensor_motion", "on", "Bedroom sensor motion"
    )
    assert_sensor_state(
        hass,
        "sensor.bedroom_sensor_temperature",
        "17.75",
        "Bedroom sensor temperature",
    )


async def test_sensor_removed(hass: HomeAssistant, mock_bridge_v1) -> None:
    """Test if 2nd update has removed sensor."""
    add_sensor_response(mock_bridge_v1, SENSOR_RESPONSE)

    await setup_hue_platform(hass, mock_bridge_v1, ["binary_sensor", "sensor"])
    assert_length(mock_bridge_v1.mock_requests, 1)
    assert_length(hass.states.async_all(), 7)
    mock_bridge_v1.mock_sensor_responses.clear()
    keys = ("1", "2", "3")
    mock_bridge_v1.mock_sensor_responses.append({k: SENSOR_RESPONSE[k] for k in keys})

    # Force updates to run again
    await mock_bridge_v1.sensor_manager.coordinator.async_refresh()

    # To flush out the service call to update the group
    await hass.async_block_till_done()
    assert_length(mock_bridge_v1.mock_requests, 2)
    assert_length(hass.states.async_all(), 3)
    assert_sensor_state(
        hass,
        "binary_sensor.living_room_sensor_motion",
        "on",
        "Living room sensor motion",
    )
    removed_sensor = hass.states.get("binary_sensor.kitchen_sensor_motion")
    assert removed_sensor is None


async def test_update_timeout(hass: HomeAssistant, mock_bridge_v1) -> None:
    """Test bridge marked as not available if timeout error during update."""
    mock_bridge_v1.api.sensors.update = Mock(side_effect=asyncio.TimeoutError)
    await setup_hue_platform(hass, mock_bridge_v1, ["binary_sensor", "sensor"])
    assert len(mock_bridge_v1.mock_requests) == 0
    assert len(hass.states.async_all()) == 0


async def test_update_unauthorized(hass: HomeAssistant, mock_bridge_v1) -> None:
    """Test bridge marked as not authorized if unauthorized during update."""
    mock_bridge_v1.api.sensors.update = Mock(side_effect=aiohue.Unauthorized)
    await setup_hue_platform(hass, mock_bridge_v1, ["binary_sensor", "sensor"])
    assert_length(mock_bridge_v1.mock_requests, 0)
    assert_length(hass.states.async_all(), 0)
    assert_length(mock_bridge_v1.handle_unauthorized_error.mock_calls, 1)


async def test_hue_events(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, mock_bridge_v1, device_reg
) -> None:
    """Test that hue remotes fire events when pressed."""
    add_sensor_response(mock_bridge_v1, SENSOR_RESPONSE)

    events = async_capture_events(hass, ATTR_HUE_EVENT)

    await setup_hue_platform(hass, mock_bridge_v1, ["binary_sensor", "sensor"])

    assert_length(mock_bridge_v1.mock_requests, 1)
    assert_length(hass.states.async_all(), 7)
    assert_length(events, 0)

    hue_tap_device = device_reg.async_get_device(
        identifiers={(hue.DOMAIN, "00:00:00:00:00:44:23:08")}
    )

    mock_bridge_v1.api.sensors["7"].last_event = {"type": "button"}
    mock_bridge_v1.api.sensors["8"].last_event = {"type": "button"}

    new_sensor_response = dict(SENSOR_RESPONSE)
    new_sensor_response["7"] = dict(new_sensor_response["7"])
    new_sensor_response["7"]["state"] = {
        "buttonevent": 18,
        "lastupdated": "2019-12-28T22:58:03",
    }
    add_sensor_response(mock_bridge_v1, new_sensor_response)

    # Force updates to run again
    freezer.tick(sensor_base.SensorManager.SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert_length(mock_bridge_v1.mock_requests, 2)
    assert_length(hass.states.async_all(), 7)
    assert_length(events, 1)
    assert events[-1].data == {
        "device_id": hue_tap_device.id,
        "id": "hue_tap",
        "unique_id": "00:00:00:00:00:44:23:08-f2",
        "event": 18,
        "last_updated": "2019-12-28T22:58:03",
    }

    hue_dimmer_device = device_reg.async_get_device(
        identifiers={(hue.DOMAIN, "00:17:88:01:10:3e:3a:dc")}
    )

    new_sensor_response = dict(new_sensor_response)
    new_sensor_response["8"] = dict(new_sensor_response["8"])
    new_sensor_response["8"]["state"] = {
        "buttonevent": 3002,
        "lastupdated": "2019-12-28T22:58:03",
    }
    add_sensor_response(mock_bridge_v1, new_sensor_response)

    # Force updates to run again
    freezer.tick(sensor_base.SensorManager.SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert_length(mock_bridge_v1.mock_requests, 3)
    assert_length(hass.states.async_all(), 7)
    assert_length(events, 2)
    assert events[-1].data == {
        "device_id": hue_dimmer_device.id,
        "id": "hue_dimmer_switch_1",
        "unique_id": "00:17:88:01:10:3e:3a:dc-02-fc00",
        "event": 3002,
        "last_updated": "2019-12-28T22:58:03",
    }

    # Fire old event, it should be ignored
    new_sensor_response = dict(new_sensor_response)
    new_sensor_response["8"] = dict(new_sensor_response["8"])
    new_sensor_response["8"]["state"] = {
        "buttonevent": 18,
        "lastupdated": "2019-12-28T22:58:02",
    }
    add_sensor_response(mock_bridge_v1, new_sensor_response)

    # Force updates to run again
    freezer.tick(sensor_base.SensorManager.SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert_length(mock_bridge_v1.mock_requests, 4)
    assert_length(hass.states.async_all(), 7)
    assert_length(events, 2)

    # Add a new remote. In discovery, the new event is registered **but not fired**
    new_sensor_response = dict(new_sensor_response)
    new_sensor_response["21"] = {
        "state": {
            "rotaryevent": 2,
            "expectedrotation": 208,
            "expectedeventduration": 400,
            "lastupdated": "2020-01-31T15:56:19",
        },
        "swupdate": {"state": "noupdates", "lastinstall": "2019-11-26T03:35:21"},
        "config": {"on": True, "battery": 100, "reachable": True, "pending": []},
        "name": "Lutron Aurora 1",
        "type": "ZLLRelativeRotary",
        "modelid": "Z3-1BRL",
        "manufacturername": "Lutron",
        "productname": "Lutron Aurora",
        "diversityid": "2c3a75ff-55c4-4e4d-8c44-82d330b8eb9b",
        "swversion": "3.4",
        "uniqueid": "ff:ff:00:0f:e7:fd:bc:b7-01-fc00-0014",
        "capabilities": {
            "certified": True,
            "primary": True,
            "inputs": [
                {
                    "repeatintervals": [400],
                    "events": [
                        {"rotaryevent": 1, "eventtype": "start"},
                        {"rotaryevent": 2, "eventtype": "repeat"},
                    ],
                }
            ],
        },
    }
    add_sensor_response(mock_bridge_v1, new_sensor_response)

    # Force updates to run again
    freezer.tick(sensor_base.SensorManager.SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert_length(mock_bridge_v1.mock_requests, 5)
    assert_length(hass.states.async_all(), 8)
    assert_length(events, 2)

    # A new press fires the event
    new_sensor_response["21"]["state"]["lastupdated"] = "2020-01-31T15:57:19"
    add_sensor_response(mock_bridge_v1, new_sensor_response)

    # Force updates to run again
    freezer.tick(sensor_base.SensorManager.SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    hue_aurora_device = device_reg.async_get_device(
        identifiers={(hue.DOMAIN, "ff:ff:00:0f:e7:fd:bc:b7")}
    )

    assert_length(mock_bridge_v1.mock_requests, 6)
    assert_length(hass.states.async_all(), 8)
    assert_length(events, 3)
    assert events[-1].data == {
        "device_id": hue_aurora_device.id,
        "id": "lutron_aurora_1",
        "unique_id": "ff:ff:00:0f:e7:fd:bc:b7-01-fc00-0014",
        "event": 2,
        "last_updated": "2020-01-31T15:57:19",
    }
