"""Constants for CTEK Nanogrid Air."""

from datetime import timedelta

DOMAIN = "ctek_nanogrid_air"
DEFAULT_PORT = 80
DEFAULT_TIMEOUT = 10
UPDATE_INTERVAL = timedelta(seconds=30)
ENDPOINTS = ("/status", "/meter", "/evse")
