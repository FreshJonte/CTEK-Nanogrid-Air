"""Connection validation and credential recovery using real HA flow classes."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import voluptuous as vol
import voluptuous_serialize

from custom_components.ctek_nanogrid_air.api import CannotConnect, InvalidAuth
from custom_components.ctek_nanogrid_air.config_flow import (
    CTEKNanogridAirConfigFlow,
    input_schema,
    normalize_host,
)

INPUT = {"host": "device.local", "port": 80, "username": "ctek", "password": "secret"}
MODULE = "custom_components.ctek_nanogrid_air.config_flow"


@pytest.mark.parametrize(
    "host,expected",
    [
        (" DEVICE.local. ", "device.local"),
        ("[2001:db8::1]", "2001:db8::1"),
        ("192.168.1.2", "192.168.1.2"),
    ],
)
def test_normalize_host(host, expected):
    assert normalize_host(host) == expected


@pytest.mark.parametrize(
    "host",
    ["", " ", "http://device", "device:8080", "user@device", "device/path", "a b"],
)
def test_invalid_host(host):
    with pytest.raises(vol.Invalid):
        normalize_host(host)


@pytest.mark.parametrize("port", [0, -1, 65536, "no"])
def test_invalid_port(port):
    with pytest.raises(vol.Invalid):
        input_schema({})({**INPUT, "port": port})


def test_form_serializable():
    assert voluptuous_serialize.convert(input_schema({}))


@pytest.fixture
def flow():
    flow = CTEKNanogridAirConfigFlow()
    flow.hass = MagicMock()
    flow.context = {"source": "user"}
    flow.hass.config_entries.async_entries.return_value = []
    return flow


@pytest.mark.parametrize(
    "error,expected",
    [
        (InvalidAuth(), "invalid_auth"),
        (CannotConnect(), "cannot_connect"),
        (None, None),
    ],
)
async def test_validate_before_save(flow, error, expected):
    with (
        patch(f"{MODULE}.async_get_clientsession"),
        patch(f"{MODULE}.NanogridApi.async_get", new_callable=AsyncMock) as get,
    ):
        get.side_effect = error
        result = await flow.async_step_user(INPUT.copy())
    if expected:
        assert result["type"] == "form"
        assert result["errors"]["base"] == expected
    else:
        assert result["type"] == "create_entry"
        assert result["data"] == INPUT
    get.assert_awaited_once_with("/status")


async def test_duplicate(flow):
    flow.hass.config_entries.async_entries.return_value = [
        SimpleNamespace(entry_id="old", data=INPUT)
    ]
    result = await flow.async_step_user({**INPUT, "host": "DEVICE.local."})
    assert result["reason"] == "already_configured"


@pytest.mark.parametrize(
    "changes", [{"host": "http://device"}, {"username": "user:name"}, {"port": 65536}]
)
async def test_invalid_input_does_not_connect(flow, changes):
    with patch(f"{MODULE}.NanogridApi") as api:
        result = await flow.async_step_user({**INPUT, **changes})
    assert result["errors"] == {"base": "invalid_input"}
    api.assert_not_called()


async def test_invalid_legacy_entry_does_not_block_new_setup(flow):
    flow.hass.config_entries.async_entries.return_value = [
        SimpleNamespace(entry_id="old", data={**INPUT, "host": "http://invalid"})
    ]
    with (
        patch(f"{MODULE}.async_get_clientsession"),
        patch(f"{MODULE}.NanogridApi.async_get", new_callable=AsyncMock),
    ):
        result = await flow.async_step_user(INPUT.copy())
    assert result["type"] == "create_entry"


async def test_reauth_cannot_change_address(flow):
    entry = SimpleNamespace(entry_id="old", title="CTEK Nanogrid Air", data=INPUT)
    flow.context = {"source": "reauth", "entry_id": "old"}
    flow.hass.config_entries.async_get_known_entry.return_value = entry
    with patch(f"{MODULE}.NanogridApi") as api:
        result = await flow.async_step_reauth_confirm(
            {**INPUT, "host": "different.local"}
        )
    assert result["errors"] == {"base": "address_changed"}
    api.assert_not_called()


async def test_reauth_preserves_address(flow):
    entry = SimpleNamespace(entry_id="old", data={**INPUT, "host": "DEVICE.local"})
    flow.context = {"source": "reauth", "entry_id": "old"}
    flow.hass.config_entries.async_get_known_entry.return_value = entry
    with (
        patch(f"{MODULE}.async_get_clientsession"),
        patch(f"{MODULE}.NanogridApi.async_get", new_callable=AsyncMock),
        patch.object(
            flow, "async_update_reload_and_abort", return_value={"type": "abort"}
        ) as update,
    ):
        await flow.async_step_reauth_confirm({**INPUT, "password": "new"})
    update.assert_called_once_with(
        entry, data_updates={"username": "ctek", "password": "new"}
    )
