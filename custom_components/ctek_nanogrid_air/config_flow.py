import voluptuous as vol
from homeassistant import config_entries
from . import DOMAIN

class CTEKNanogridAirConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CTEK Nanogrid Air."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the input here if needed
            # Example: Ensure "host" is a valid hostname or IP address
            if not user_input["host"]:
                errors["host"] = "Host is required."
            else:
                # Input seems valid; create the entry
                return self.async_create_entry(title="CTEK Nanogrid Air", data=user_input)

        # Form schema
        data_schema = vol.Schema({
            vol.Required("host"): str,
            vol.Optional("port", default=80): int,
            vol.Required("username", default="ctek"): str,
            vol.Required("password"): str,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
