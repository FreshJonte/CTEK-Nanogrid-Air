"""Small asynchronous client for the local Nanogrid API."""

from aiohttp import BasicAuth, ClientError, ClientSession, ClientTimeout
from yarl import URL

from .const import DEFAULT_TIMEOUT

_AUTH_CHALLENGE = object()


class CannotConnect(Exception):
    """The device could not provide a valid response."""


class InvalidAuth(Exception):
    """The device rejected the credentials."""


class NanogridApi:
    """Read API endpoints using Home Assistant's shared HTTP session."""

    def __init__(
        self,
        session: ClientSession,
        host: str,
        port: int,
        username: str | None = None,
        password: str | None = None,
    ):
        self.session = session
        self.base_url = URL.build(scheme="http", host=host, port=port)
        self.auth = BasicAuth(username, password) if username and password else None
        self._auth_required_endpoints = set()

    async def async_get(self, endpoint: str):
        """Fetch and validate one response without logging credentials or payloads."""
        needs_auth = endpoint in self._auth_required_endpoints
        data = await self._async_request(endpoint, self.auth if needs_auth else None)
        if data is _AUTH_CHALLENGE:
            if self.auth is None or needs_auth:
                raise InvalidAuth
            data = await self._async_request(endpoint, self.auth)
            if data is _AUTH_CHALLENGE:
                raise InvalidAuth
            self._auth_required_endpoints.add(endpoint)

        expected_type = list if endpoint == "/evse" else dict
        if not isinstance(data, expected_type):
            raise CannotConnect("Unexpected response structure")
        if endpoint == "/status" and not isinstance(data.get("deviceInfo"), dict):
            raise CannotConnect("Missing device information")
        return data

    async def _async_request(self, endpoint: str, auth: BasicAuth | None):
        """Return a sentinel for an authentication challenge; never follow redirects."""
        try:
            async with self.session.get(
                self.base_url.with_path(f"{endpoint}/"),
                auth=auth,
                timeout=ClientTimeout(total=DEFAULT_TIMEOUT),
                allow_redirects=False,
            ) as response:
                if response.status in (401, 403):
                    return _AUTH_CHALLENGE
                if response.status != 200:
                    raise CannotConnect(f"HTTP {response.status}")
                return await response.json()
        except (ClientError, TimeoutError, ValueError) as err:
            raise CannotConnect("Invalid response or connection failure") from err


def extract_value(data, json_path):
    """Safely traverse dictionaries and arrays, including incomplete responses."""
    for key in json_path.split("."):
        if isinstance(data, dict):
            data = data.get(key)
        elif isinstance(data, list) and key.isdigit() and int(key) < len(data):
            data = data[int(key)]
        else:
            return None
    return data
