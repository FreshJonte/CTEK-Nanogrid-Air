"""Small asynchronous client for the local Nanogrid API."""

from aiohttp import BasicAuth, ClientError, ClientSession, ClientTimeout
from yarl import URL

from .const import DEFAULT_TIMEOUT


class CannotConnect(Exception):
    """The device could not provide a valid response."""


class InvalidAuth(Exception):
    """The device rejected the credentials."""


class NanogridApi:
    """Read API endpoints using Home Assistant's shared HTTP session."""

    def __init__(
        self, session: ClientSession, host: str, port: int, username: str, password: str
    ):
        self.session = session
        self.base_url = URL.build(scheme="http", host=host, port=port)
        self.auth = BasicAuth(username, password)

    async def async_get(self, endpoint: str):
        """Fetch and validate one response without logging credentials or payloads."""
        try:
            async with self.session.get(
                self.base_url.with_path(f"{endpoint}/"),
                auth=self.auth,
                timeout=ClientTimeout(total=DEFAULT_TIMEOUT),
                allow_redirects=False,
            ) as response:
                if response.status in (401, 403):
                    raise InvalidAuth
                if response.status != 200:
                    raise CannotConnect(f"HTTP {response.status}")
                data = await response.json()
        except (ClientError, TimeoutError, ValueError) as err:
            raise CannotConnect("Invalid response or connection failure") from err

        expected_type = list if endpoint == "/evse" else dict
        if not isinstance(data, expected_type):
            raise CannotConnect("Unexpected response structure")
        if endpoint == "/status" and not isinstance(data.get("deviceInfo"), dict):
            raise CannotConnect("Missing device information")
        return data


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
