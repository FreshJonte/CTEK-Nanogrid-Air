"""Configuration and credential recovery for Nanogrid Air."""

import ipaddress
import re

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import CannotConnect, InvalidAuth, NanogridApi
from .const import DEFAULT_PORT, DOMAIN


def normalize_host(value):
    """Accept a hostname or IP address, never a URL or embedded credentials."""
    host = value.strip().lower().rstrip(".")
    if host.startswith("[") and host.endswith("]"):
        host = host[1:-1]
    try:
        return str(ipaddress.ip_address(host))
    except ValueError:
        if not re.fullmatch(r"(?=.{1,253}\Z)[a-z0-9](?:[a-z0-9._-]*[a-z0-9])?", host):
            raise vol.Invalid("Enter a hostname or IP address") from None
        return host


def input_schema(defaults):
    """Preserve non-secret values when redisplaying the form."""
    return vol.Schema(
        {
            vol.Required("host", default=defaults.get("host", "")): str,
            vol.Optional("port", default=defaults.get("port", DEFAULT_PORT)): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=65535)
            ),
            vol.Optional("username"): str,
            vol.Optional("password"): str,
        }
    )


class CTEKNanogridAirConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Validate connectivity before creating or updating a config entry."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        return await self._async_form("user", user_input)

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        return await self._async_form("reauth_confirm", user_input)

    async def _async_form(self, step_id, user_input):
        errors = {}
        defaults = self._get_reauth_entry().data if step_id == "reauth_confirm" else {}
        if user_input is not None:
            defaults = user_input
            try:
                user_input = input_schema(defaults)(user_input)
                user_input["host"] = normalize_host(user_input["host"])
                username = user_input.get("username", "").strip()
                password = user_input.get("password", "")
                if bool(username) != bool(password) or ":" in username:
                    raise vol.Invalid("A Basic Auth username cannot contain a colon")
                user_input.pop("username", None)
                user_input.pop("password", None)
                if username:
                    user_input["username"] = username
                    user_input["password"] = password
            except vol.Invalid:
                errors["base"] = "invalid_input"
            else:
                if step_id == "reauth_confirm":
                    reauth_entry = self._get_reauth_entry()
                    if user_input["host"] != normalize_host(
                        reauth_entry.data["host"]
                    ) or user_input["port"] != reauth_entry.data.get(
                        "port", DEFAULT_PORT
                    ):
                        return self.async_show_form(
                            step_id=step_id,
                            data_schema=input_schema(reauth_entry.data),
                            errors={"base": "address_changed"},
                        )
                for entry in self._async_current_entries():
                    if (
                        step_id == "reauth_confirm"
                        and entry.entry_id == self.context["entry_id"]
                    ):
                        continue
                    try:
                        existing_host = normalize_host(entry.data["host"])
                    except vol.Invalid:
                        # Older releases accepted malformed host strings.
                        continue
                    if (
                        existing_host == user_input["host"]
                        and entry.data.get("port", DEFAULT_PORT) == user_input["port"]
                    ):
                        return self.async_abort(reason="already_configured")
                api = NanogridApi(async_get_clientsession(self.hass), **user_input)
                try:
                    await api.async_get("/status")
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                else:
                    if step_id == "reauth_confirm":
                        # Keep the address and existing entity IDs on reauth.
                        return self.async_update_reload_and_abort(
                            reauth_entry,
                            data_updates={
                                "username": user_input.get("username", ""),
                                "password": user_input.get("password", ""),
                            },
                        )
                    else:
                        return self.async_create_entry(
                            title="CTEK Nanogrid Air", data=user_input
                        )
        return self.async_show_form(
            step_id=step_id,
            data_schema=input_schema(defaults),
            errors=errors,
        )
