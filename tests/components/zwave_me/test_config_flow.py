"""Test the zwave_me config flow."""
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.components.zwave_me.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult, FlowResultType

from .const import ASYNC_SETUP_ENTRY_FUNCTION, FAKE_UUID
from .helpers import patch_uuid

from tests.common import MockConfigEntry

FAKE_IP = "192.168.1.14"
WRONG_FAKE_IP = "192.168.1.15"
FAKE_WS = f"ws://{FAKE_IP}"
MOCK_ZEROCONF_DATA = zeroconf.ZeroconfServiceInfo(
    host=FAKE_WS,
    hostname="mock_hostname",
    name="mock_name",
    addresses=[FAKE_IP],
    port=1234,
    properties={
        "deviceid": "aa:bb:cc:dd:ee:ff",
        "manufacturer": "fake_manufacturer",
        "model": "fake_model",
        "serialNumber": "fake_serial",
    },
    type="mock_type",
)


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    with patch(
        ASYNC_SETUP_ENTRY_FUNCTION,
        return_value=True,
    ) as mock_setup_entry, patch_uuid():
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {}
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "url": FAKE_IP,
                "token": "test-token",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == FAKE_WS
    assert result2["data"] == {
        "url": FAKE_WS,
        "token": "test-token",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_zeroconf(hass: HomeAssistant) -> None:
    """Test starting a flow from zeroconf."""
    with patch(
        ASYNC_SETUP_ENTRY_FUNCTION,
        return_value=True,
    ) as mock_setup_entry, patch_uuid():
        result: FlowResult = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_ZEROCONF},
            data=MOCK_ZEROCONF_DATA,
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "token": "test-token",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == FAKE_WS
    assert result2["data"] == {
        "url": FAKE_WS,
        "token": "test-token",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_error_handling_zeroconf(hass: HomeAssistant) -> None:
    """Test getting proper errors from no uuid."""
    with patch_uuid(return_value=None):
        result: FlowResult = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_ZEROCONF},
            data=MOCK_ZEROCONF_DATA,
        )
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "no_valid_uuid_set"


async def test_handle_error_user(hass: HomeAssistant) -> None:
    """Test getting proper errors from no uuid."""
    with patch_uuid(return_value=None):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {}
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "url": WRONG_FAKE_IP,
                "token": "test-token",
            },
        )
        assert result2["errors"] == {"base": "no_valid_uuid_set"}


async def test_duplicate_user(hass: HomeAssistant) -> None:
    """Test getting proper errors from duplicate uuid."""
    entry: MockConfigEntry = MockConfigEntry(
        domain=DOMAIN,
        title="ZWave_me",
        data={
            "url": FAKE_WS,
            "token": "test-token",
        },
        unique_id=FAKE_UUID,
    )
    entry.add_to_hass(hass)
    with patch_uuid():
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {}
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "url": FAKE_IP,
                "token": "test-token",
            },
        )
        assert result2["type"] == FlowResultType.ABORT
        assert result2["reason"] == "already_configured"


async def test_duplicate_zeroconf(hass: HomeAssistant) -> None:
    """Test getting proper errors from duplicate uuid."""
    entry: MockConfigEntry = MockConfigEntry(
        domain=DOMAIN,
        title="ZWave_me",
        data={
            "url": FAKE_WS,
            "token": "test-token",
        },
        unique_id=FAKE_UUID,
    )
    entry.add_to_hass(hass)

    with patch_uuid():
        result: FlowResult = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_ZEROCONF},
            data=MOCK_ZEROCONF_DATA,
        )
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "already_configured"
