"""Fetch each API endpoint once per update for all sensors."""

import logging

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CannotConnect, InvalidAuth
from .const import DOMAIN, ENDPOINTS, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class NanogridCoordinator(DataUpdateCoordinator):
    """Share readings while isolating failures to the affected endpoint."""

    def __init__(self, hass, api, entry):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=UPDATE_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self):
        data = {}
        # Sequential requests avoid overloading the embedded device.
        for endpoint in ENDPOINTS:
            try:
                data[endpoint] = await self.api.async_get(endpoint)
            except InvalidAuth as err:
                raise ConfigEntryAuthFailed("Device rejected credentials") from err
            except CannotConnect:
                _LOGGER.debug("Unable to update %s", endpoint)
                data[endpoint] = None
        if all(value is None for value in data.values()):
            raise UpdateFailed("Unable to read any Nanogrid API endpoint")
        return data
