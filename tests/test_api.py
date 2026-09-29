"""API regressions using real aiohttp requests to a local test server."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import ClientSession, TCPConnector, web
from aiohttp.resolver import ThreadedResolver

from custom_components.ctek_nanogrid_air.api import (
    CannotConnect,
    InvalidAuth,
    NanogridApi,
    extract_value,
)


@pytest.mark.parametrize(
    "data,path,expected",
    [
        ({"current": [1, 2, 3]}, "current.1", 2),
        ([], "0.evse.0.state", None),
        ({"current": [1]}, "current.2", None),
        ({"current": None}, "current.0", None),
        ({"current": 4}, "current.0", None),
        ({"current": [0]}, "current.0", 0),
        ({"0": "ok"}, "0", "ok"),
    ],
)
def test_extract_value(data, path, expected):
    assert extract_value(data, path) == expected


@pytest.mark.parametrize(
    "status,body,endpoint,error",
    [
        (200, '{"deviceInfo": {"serial": "123"}}', "/status", None),
        (200, "[]", "/evse", None),
        (401, "{}", "/status", InvalidAuth),
        (403, "{}", "/status", InvalidAuth),
        (500, "{}", "/meter", CannotConnect),
        (302, "{}", "/meter", CannotConnect),
        (200, "not json", "/meter", CannotConnect),
        (200, "null", "/meter", CannotConnect),
        (200, "{}", "/status", CannotConnect),
        (200, "{}", "/evse", CannotConnect),
    ],
)
async def test_http_response(status, body, endpoint, error):
    requests = []

    async def handler(request):
        requests.append(request)
        return web.Response(status=status, text=body, content_type="application/json")

    app = web.Application()
    app.router.add_get(endpoint + "/", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = runner.addresses[0][1]
    try:
        async with ClientSession(
            connector=TCPConnector(resolver=ThreadedResolver())
        ) as session:
            api = NanogridApi(session, "127.0.0.1", port, "ctek", "test-password")
            if error:
                with pytest.raises(error):
                    await api.async_get(endpoint)
            else:
                assert await api.async_get(endpoint) is not None
        assert len(requests) == (2 if status in (401, 403) else 1)
        assert "Authorization" not in requests[0].headers
        if status in (401, 403):
            assert requests[1].headers["Authorization"].startswith("Basic ")
    finally:
        await runner.cleanup()


async def test_timeout():
    session = MagicMock()
    session.get.return_value.__aenter__ = AsyncMock(side_effect=TimeoutError)
    with pytest.raises(CannotConnect):
        await NanogridApi(session, "device.local", 80, "ctek", "secret").async_get(
            "/meter"
        )


def test_ipv6_url():
    api = NanogridApi(MagicMock(), "2001:db8::1", 8080, "ctek", "secret")
    assert str(api.base_url) == "http://[2001:db8::1]:8080"


async def test_anonymous_read_ignores_saved_credentials():
    requests = []

    async def handler(request):
        requests.append(request)
        return web.json_response({"deviceInfo": {"serial": "123"}})

    app = web.Application()
    app.router.add_get("/status/", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    try:
        async with ClientSession(
            connector=TCPConnector(resolver=ThreadedResolver())
        ) as session:
            api = NanogridApi(
                session, "127.0.0.1", runner.addresses[0][1], "ctek", "saved"
            )
            await api.async_get("/status")
            await api.async_get("/status")
        assert len(requests) == 2
        assert all("Authorization" not in request.headers for request in requests)
    finally:
        await runner.cleanup()


async def test_auth_fallback_is_cached_after_challenge():
    requests = []

    async def handler(request):
        requests.append(request)
        if "Authorization" not in request.headers:
            return web.Response(status=401)
        return web.json_response({"deviceInfo": {"serial": "123"}})

    app = web.Application()
    app.router.add_get("/status/", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    try:
        async with ClientSession(
            connector=TCPConnector(resolver=ThreadedResolver())
        ) as session:
            api = NanogridApi(
                session, "127.0.0.1", runner.addresses[0][1], "ctek", "secret"
            )
            await api.async_get("/status")
            await api.async_get("/status")
        assert len(requests) == 3
        assert "Authorization" not in requests[0].headers
        assert all("Authorization" in request.headers for request in requests[1:])
    finally:
        await runner.cleanup()


async def test_auth_required_without_credentials():
    session = MagicMock()
    session.get.return_value.__aenter__ = AsyncMock(return_value=MagicMock(status=401))
    with pytest.raises(InvalidAuth):
        await NanogridApi(session, "device.local", 80).async_get("/status")
