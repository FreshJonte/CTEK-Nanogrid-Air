from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from aiohttp import BasicAuth, ClientError
import asyncio
import logging

DOMAIN = "ctek_nanogrid_air"

_LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10  # Timeout for API calls

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors for CTEK Nanogrid Air integration."""
    config = entry.data
    host = config["host"]
    port = config["port"]
    username = config["username"]
    password = config["password"]

    session = async_get_clientsession(hass)
    auth = BasicAuth(username, password)
    
    device_key = f"{host}:{port}"

    # Define the sensors to be added
    sensors = [
        # Status endpoint entities
        CTEKSensor(session, host, port, auth, "device_serial", "Device Serial", "/status", "deviceInfo.serial", device_key=device_key, entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:numeric"),
        CTEKSensor(session, host, port, auth, "device_firmware", "Device Firmware", "/status", "deviceInfo.firmware", device_key=device_key, entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:update"),
        CTEKSensor(session, host, port, auth, "device_mac", "Device MAC", "/status", "deviceInfo.mac", device_key=device_key, entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:router"),
        CTEKSensor(session, host, port, auth, "wifi_ssid", "WiFi SSID", "/status", "wifiInfo.ssid", device_key=device_key, entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:wifi"),
        CTEKSensor(session, host, port, auth, "wifi_rssi", "WiFi Signal Strength", "/status", "wifiInfo.rssi", unit_of_measurement="dBm", device_key=device_key, entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:signal"),

        # Meter endpoint entities
        CTEKSensor(session, host, port, auth, "active_power_in_watt", "Active Power In Watt", "/meter", "activePowerIn", unit_of_measurement="W", device_key=device_key, icon="mdi:meter-electric", transform=lambda x: x * 1000),
        CTEKSensor(session, host, port, auth, "active_power_in_kw", "Active Power In Kw", "/meter", "activePowerIn", unit_of_measurement="kW", device_key=device_key, icon="mdi:meter-electric"),
        CTEKSensor(session, host, port, auth, "active_power_out", "Active Power Out", "/meter", "activePowerOut", unit_of_measurement="W", device_key=device_key, icon="mdi:flash-off"),
        CTEKSensor(session, host, port, auth, "current_phase_1", "Current Phase 1", "/meter", "current.0", unit_of_measurement="A", device_key=device_key, icon="mdi:current-ac"),
        CTEKSensor(session, host, port, auth, "current_phase_2", "Current Phase 2", "/meter", "current.1", unit_of_measurement="A", device_key=device_key, icon="mdi:current-ac"),
        CTEKSensor(session, host, port, auth, "current_phase_3", "Current Phase 3", "/meter", "current.2", unit_of_measurement="A", device_key=device_key, icon="mdi:current-ac"),
        CTEKSensor(session, host, port, auth, "voltage_phase_1", "Voltage Phase 1", "/meter", "voltage.0", unit_of_measurement="V", device_key=device_key, icon="mdi:flash"),
        CTEKSensor(session, host, port, auth, "voltage_phase_2", "Voltage Phase 2", "/meter", "voltage.1", unit_of_measurement="V", device_key=device_key, icon="mdi:flash"),
        CTEKSensor(session, host, port, auth, "voltage_phase_3", "Voltage Phase 3", "/meter", "voltage.2", unit_of_measurement="V", device_key=device_key, icon="mdi:flash"),
        CTEKSensor(session, host, port, auth, "total_energy_import", "Total Energy Import", "/meter", "totalEnergyActiveImport", unit_of_measurement="kWh", device_key=device_key, icon="mdi:flash"),
        CTEKSensor(session, host, port, auth, "total_energy_export", "Total Energy Export", "/meter", "totalEnergyActiveExport", unit_of_measurement="kWh", device_key=device_key, icon="mdi:flash-off"),
        CTEKSensor(session, host, port, auth, "meter_vendor", "Meter Vendor", "/status", "meterInfo.vendor", device_key=device_key, entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:meter-electric"),
        CTEKSensor(session, host, port, auth, "meter_type", "Meter Type", "/status", "meterInfo.type", device_key=device_key, entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:meter-electric"),
        CTEKSensor(session, host, port, auth, "meter_id", "Meter ID", "/status", "meterInfo.id", device_key=device_key, entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:meter-electric"),

        # EVSE endpoint entities
        CTEKSensor(session, host, port, auth, "chargebox_connection_status", "Chargebox Network Connection Status", "/evse", "0.connection_status", device_key=device_key, entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:lan"),
        CTEKSensor(session, host, port, auth, "chargebox_outlet_1_state", "Chargebox Outlet 1 State", "/evse", "0.evse.0.state", device_key=device_key, icon="mdi:ev-plug-type2"),
        CTEKSensor(session, host, port, auth, "chargebox_outlet_1_energy", "Chargebox Outlet 1 Energy", "/evse", "0.evse.0.energy", unit_of_measurement="kWh", device_key=device_key, icon="mdi:ev-plug-type2", transform=lambda x: x / 1000), #Total energy used when charging, in kWh
        CTEKSensor(session, host, port, auth, "chargebox_outlet_1_power", "Chargebox Outlet 1 Power", "/evse", "0.evse.0.power", unit_of_measurement="kW", device_key=device_key, icon="mdi:ev-plug-type2", transform=lambda x: x / 1000), # Current kW usage
        CTEKSensor(session, host, port, auth, "chargebox_outlet_1_current_phase_1", "Chargebox Outlet 1 Current Phase 1", "/evse", "0.evse.0.current.0", unit_of_measurement="A", device_key=device_key, icon="mdi:ev-plug-type2"),
        CTEKSensor(session, host, port, auth, "chargebox_outlet_1_current_phase_2", "Chargebox Outlet 1 Current Phase 2", "/evse", "0.evse.0.current.1", unit_of_measurement="A", device_key=device_key, icon="mdi:ev-plug-type2"),
        CTEKSensor(session, host, port, auth, "chargebox_outlet_1_current_phase_3", "Chargebox Outlet 1 Current Phase 3", "/evse", "0.evse.0.current.2", unit_of_measurement="A", device_key=device_key, icon="mdi:ev-plug-type2"),

        # Chargebox endpoint entities
        CTEKSensor(session, host, port, auth, "chargebox_serial", "Chargebox Serial", "/status", "chargeboxInfo.serial", device_key=device_key, entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:numeric"),
        CTEKSensor(session, host, port, auth, "chargebox_firmware", "Chargebox Firmware", "/status", "chargeboxInfo.firmware", device_key=device_key, entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:update"),
        CTEKSensor(session, host, port, auth, "chargebox_endpoint", "Chargebox Endpoint", "/status", "chargeboxInfo.endpoint", device_key=device_key, entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:link"),
        CTEKSensor(session, host, port, auth, "chargebox_port", "Chargebox Endpoint TCP Port", "/status", "chargeboxInfo.port", device_key=device_key, entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:lan"),
        CTEKSensor(session, host, port, auth, "chargebox_state", "Chargebox State", "/status", "chargeboxInfo.state", device_key=device_key, entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:lan"),

    ]

    async_add_entities(sensors, True)


class CTEKSensor(SensorEntity):
    """Representation of a single CTEK Nanogrid Air sensor."""

    def __init__(
        self,
        session,
        host,
        port,
        auth,
        sensor_id,
        name,
        endpoint,
        json_path,
        unit_of_measurement=None,
        icon=None,
        transform=None,
        device_key=None,
        device_name=None,
        entity_category=None,
    ):
        self._session = session
        self._host = host
        self._port = port
        self._auth = auth
        self._sensor_id = sensor_id
        self._name = name
        self._endpoint = endpoint
        self._json_path = json_path
        self._unit_of_measurement = unit_of_measurement
        self._icon = icon
        self._state = None
        self.transform = transform  
        self._entity_category = entity_category

        # device grouping info: supply the same device_key for sensors that should be grouped.
        # device_key should be unique for each physical device.
        self._device_key = device_key or f"{DOMAIN}_{host}:{port}"
        self._device_name = device_name or f"CTEK Nanogrid ({host})"

    def _extract_value(self, data, json_path):
        """Extract a value from a nested JSON object using a dotted path."""
        keys = json_path.split(".")
        value = data
        for key in keys:
            if isinstance(value, list):
                try:
                    value = value[int(key)] if key.isdigit() else None
                except (IndexError, ValueError):
                    _LOGGER.warning(f"Index {key} out of range while parsing JSON for {self._name}.")
                    return None
            else:
                value = value.get(key)
            if value is None:
                _LOGGER.debug(f"Key {key} not found while parsing JSON for {self._name}.")
                return None
        return value

    @property
    def name(self):
        return self._name

    @property
    def entity_category(self):
        return self._entity_category

    @property
    def entity_registry_enabled_default(self):
        return True

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        # include device key so IDs are unique across multiple devices/hosts
        return f"{DOMAIN}_{self._device_key}_{self._sensor_id}"

    @property
    def state(self):
        """Return the current state of the sensor."""
        if self._sensor_id == "chargebox_outlet_1_state":
            state_mapping = {
                "0": "Available",
                0: "Available",
                "1": "Preparing",
                1: "Preparing",
                "2": "Charging",
                2: "Charging",
                "3": "Suspended by charger",
                3: "Suspended by charger",
                "4": "Suspended by vehicle",
                4: "Suspended by vehicle",
                "5": "Finishing",
                5: "Finishing",
                "6": "Reserved",
                6: "Reserved",
                "7": "Unavailable",
                7: "Unavailable",
                "8": "Faulted",
                8: "Faulted",
            }
            if self._state not in state_mapping:
                _LOGGER.warning(f"Unexpected state for {self._name}: {self._state}")
            return state_mapping.get(self._state, "Unknown")
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def icon(self):
        return self._icon

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        if self._sensor_id in ["total_energy_import", "total_energy_export", "chargebox_outlet_1_energy"]:
            return "energy"
        if self._sensor_id in ["active_power_in", "active_power_out"]:
            return "power"
        return None

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        if self._sensor_id in ["total_energy_import", "total_energy_export", "chargebox_outlet_1_energy"]:
            return "total_increasing"
        if self._sensor_id in ["active_power_in", "active_power_out"]:
            return "measurement"
        return None

    @property
    def device_info(self):
        """Provide device info so Home Assistant groups entities under a device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_key)},
            name=self._device_name,
            manufacturer="CTEK",
            model="Nanogrid Air",
            configuration_url=f"http://{self._host}",
        )

    async def async_update(self):
        """Fetch data from the API and update the state."""
        url = f"http://{self._host}:{self._port}{self._endpoint}/"
        try:
            async with self._session.get(url, auth=self._auth, timeout=DEFAULT_TIMEOUT) as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to fetch data for {self._name}, status: {response.status}")
                    self._state = None
                    return

                data = await response.json()
                raw_value = self._extract_value(data, self._json_path)
                if self.transform and raw_value is not None:
                    self._state = self.transform(raw_value)
                else:
                    self._state = raw_value

                _LOGGER.debug(f"Updated state for {self._name}: {self._state}")

        except asyncio.TimeoutError:
            _LOGGER.error(f"Timeout fetching data for {self._name} from {url}. Please check your network and device.")
            self._state = None

        except ClientError as e:
            _LOGGER.error(f"Client error for {self._name} while accessing {url}: {e}")
            self._state = None

        except Exception as e:
            _LOGGER.error(f"Unexpected error for {self._name}: {e}. Check device compatibility and logs for details.")
            self._state = None
