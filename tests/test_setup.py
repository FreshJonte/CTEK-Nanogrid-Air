"""Verify setup and unload use a single shared coordinator."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.ctek_nanogrid_air import async_setup_entry, async_unload_entry
from custom_components.ctek_nanogrid_air.const import DOMAIN

MODULE = "custom_components.ctek_nanogrid_air"


async def test_setup_and_unload():
    hass = MagicMock()
    hass.data = {}
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    entry = SimpleNamespace(
        entry_id="entry",
        data={"host": "device", "username": "ctek", "password": "test"},
    )
    with (
        patch(f"{MODULE}.async_get_clientsession"),
        patch(f"{MODULE}.NanogridCoordinator") as cls,
    ):
        coordinator = cls.return_value
        coordinator.async_config_entry_first_refresh = AsyncMock()
        assert await async_setup_entry(hass, entry)
        coordinator.async_config_entry_first_refresh.assert_awaited_once()
        assert hass.data[DOMAIN]["entry"] is coordinator
    hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(
        entry, ["sensor"]
    )
    hass.config_entries.async_unload_platforms.return_value = False
    assert not await async_unload_entry(hass, entry)
    assert "entry" in hass.data[DOMAIN]
    hass.config_entries.async_unload_platforms.return_value = True
    assert await async_unload_entry(hass, entry)
    assert "entry" not in hass.data[DOMAIN]


async def test_failed_setup_does_not_forward_platforms():
    hass = MagicMock()
    hass.data = {}
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    entry = SimpleNamespace(
        entry_id="entry",
        data={"host": "device", "username": "ctek", "password": "test"},
    )
    with (
        patch(f"{MODULE}.async_get_clientsession"),
        patch(f"{MODULE}.NanogridCoordinator") as cls,
    ):
        cls.return_value.async_config_entry_first_refresh = AsyncMock(
            side_effect=ConfigEntryNotReady
        )
        with pytest.raises(ConfigEntryNotReady):
            await async_setup_entry(hass, entry)
    assert not hass.data[DOMAIN]
    hass.config_entries.async_forward_entry_setups.assert_not_awaited()


async def test_setup_without_credentials():
    hass = MagicMock()
    hass.data = {}
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    entry = SimpleNamespace(entry_id="anonymous", data={"host": "device"})
    with (
        patch(f"{MODULE}.async_get_clientsession"),
        patch(f"{MODULE}.NanogridApi") as api,
        patch(f"{MODULE}.NanogridCoordinator") as cls,
    ):
        cls.return_value.async_config_entry_first_refresh = AsyncMock()
        assert await async_setup_entry(hass, entry)
    assert api.call_args.args[3:] == (None, None)
