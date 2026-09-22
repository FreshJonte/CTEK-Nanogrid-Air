"""Set up the CTEK Nanogrid Air integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NanogridApi
from .const import DEFAULT_PORT, DOMAIN
from .coordinator import NanogridCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CTEK Nanogrid Air from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    config = entry.data
    api = NanogridApi(
        async_get_clientsession(hass),
        config["host"],
        config.get("port", DEFAULT_PORT),
        config["username"],
        config["password"],
    )
    coordinator = NanogridCoordinator(hass, api, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
