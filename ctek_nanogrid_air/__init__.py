from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "ctek_nanogrid_air"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CTEK Nanogrid Air from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Forward the config entry to the sensor platform (awaiting the setup)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
