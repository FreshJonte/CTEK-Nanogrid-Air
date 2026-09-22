"""Test shared polling, outage isolation and Home Assistant retry behavior."""

from unittest.mock import AsyncMock, MagicMock, call

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.ctek_nanogrid_air.api import CannotConnect, InvalidAuth
from custom_components.ctek_nanogrid_air.coordinator import NanogridCoordinator


def make_coordinator(responses):
    api = MagicMock()
    api.async_get = AsyncMock(side_effect=responses)
    hass = MagicMock()
    hass.is_stopping = False
    entry = MagicMock()
    entry.state = ConfigEntryState.SETUP_IN_PROGRESS
    coordinator = NanogridCoordinator(hass, api, entry)
    return coordinator, api


async def test_one_request_per_endpoint():
    coordinator, api = make_coordinator([{"deviceInfo": {}}, {"current": [1]}, []])
    data = await coordinator._async_update_data()
    assert api.async_get.call_args_list == [
        call("/status"),
        call("/meter"),
        call("/evse"),
    ]
    assert data["/meter"]["current"] == [1]
    assert data["/evse"] == []


async def test_partial_outage():
    coordinator, _ = make_coordinator([{}, {"current": [1]}, CannotConnect()])
    data = await coordinator._async_update_data()
    assert data["/evse"] is None
    assert data["/meter"] == {"current": [1]}


async def test_total_outage():
    coordinator, _ = make_coordinator([CannotConnect()] * 3)
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


async def test_initial_outage_retries_setup():
    coordinator, _ = make_coordinator([CannotConnect()] * 3)
    with pytest.raises(ConfigEntryNotReady):
        await coordinator.async_config_entry_first_refresh()


async def test_auth_failure():
    coordinator, api = make_coordinator([InvalidAuth()])
    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()
    assert api.async_get.call_count == 1


async def test_outage_recovery():
    coordinator, api = make_coordinator([CannotConnect()] * 3)
    await coordinator.async_refresh()
    assert not coordinator.last_update_success
    api.async_get.side_effect = [{"deviceInfo": {}}, {}, []]
    await coordinator.async_refresh()
    assert coordinator.last_update_success
    assert coordinator.data["/evse"] == []
