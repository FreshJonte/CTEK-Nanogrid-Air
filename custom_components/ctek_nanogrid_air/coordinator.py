"""Shared API update coordinator for CTEK Nanogrid Air."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from aiohttp import BasicAuth, ClientError, ClientSession
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10


class CTEKNanogridCoordinator(DataUpdateCoordinator[Any]):
    """Fetch and share data from one Nanogrid API endpoint."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        session: ClientSession,
        auth: BasicAuth,
        host: str,
        port: int,
        endpoint: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize the endpoint coordinator."""
        self._session = session
        self._auth = auth
        self._url = f"http://{host}:{port}{endpoint}/"

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{endpoint.strip('/')}",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> Any:
        """Fetch the latest response for this endpoint."""
        try:
            async with self._session.get(
                self._url,
                auth=self._auth,
                timeout=DEFAULT_TIMEOUT,
            ) as response:
                if response.status != 200:
                    raise UpdateFailed(
                        f"Request to {self._url} returned status {response.status}"
                    )
                return await response.json()
        except asyncio.TimeoutError as err:
            raise UpdateFailed(f"Timeout while requesting {self._url}") from err
        except ClientError as err:
            raise UpdateFailed(f"Client error while requesting {self._url}: {err}") from err

