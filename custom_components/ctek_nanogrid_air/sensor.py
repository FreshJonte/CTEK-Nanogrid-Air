"""Sensors for the CTEK Nanogrid Air integration."""

from datetime import timedelta
import logging

from aiohttp import BasicAuth
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .coordinator import CTEKNanogridCoordinator

_LOGGER = logging.getLogger(__name__)

REALTIME_UPDATE_INTERVAL = timedelta(seconds=10)
STATUS_UPDATE_INTERVAL = timedelta(seconds=60)


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

    coordinators = {
        "/status": CTEKNanogridCoordinator(
            hass, entry, session, auth, host, port, "/status", STATUS_UPDATE_INTERVAL
        ),
        "/meter": CTEKNanogridCoordinator(
            hass, entry, session, auth, host, port, "/meter", REALTIME_UPDATE_INTERVAL
        ),
        "/evse": CTEKNanogridCoordinator(
            hass, entry, session, auth, host, port, "/evse", REALTIME_UPDATE_INTERVAL
        ),
    }

    for coordinator in coordinators.values():
        await coordinator.async_config_entry_first_refresh()

    def sensor(sensor_id, name, endpoint, json_path, **kwargs):
        """Create a sensor connected to its endpoint coordinator."""
        return CTEKSensor(
            coordinators[endpoint],
            host,
            port,
            sensor_id,
            name,
            json_path,
            device_key=device_key,
            **kwargs,
        )

    # Define the sensors to be added
    sensors = [
        # Status endpoint entities
        sensor("device_serial", "Device Serial", "/status", "deviceInfo.serial", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:numeric"),
        sensor("device_firmware", "Device Firmware", "/status", "deviceInfo.firmware", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:update"),
        sensor("device_mac", "Device MAC", "/status", "deviceInfo.mac", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:router"),
        sensor("wifi_ssid", "WiFi SSID", "/status", "wifiInfo.ssid", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:wifi"),
        sensor("wifi_rssi", "WiFi Signal Strength", "/status", "wifiInfo.rssi", unit_of_measurement="dBm", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:signal"),

        # Meter endpoint entities
        sensor("active_power_in_watt", "Active Power In Watt", "/meter", "activePowerIn", unit_of_measurement="W", icon="mdi:meter-electric", transform=lambda x: x * 1000),
        sensor("active_power_in_kw", "Active Power In Kw", "/meter", "activePowerIn", unit_of_measurement="kW", icon="mdi:meter-electric"),
        sensor("active_power_out", "Active Power Out", "/meter", "activePowerOut", unit_of_measurement="W", icon="mdi:flash-off"),
        sensor("current_phase_1", "Current Phase 1", "/meter", "current.0", unit_of_measurement="A", icon="mdi:current-ac"),
        sensor("current_phase_2", "Current Phase 2", "/meter", "current.1", unit_of_measurement="A", icon="mdi:current-ac"),
        sensor("current_phase_3", "Current Phase 3", "/meter", "current.2", unit_of_measurement="A", icon="mdi:current-ac"),
        sensor("voltage_phase_1", "Voltage Phase 1", "/meter", "voltage.0", unit_of_measurement="V", icon="mdi:flash"),
        sensor("voltage_phase_2", "Voltage Phase 2", "/meter", "voltage.1", unit_of_measurement="V", icon="mdi:flash"),
        sensor("voltage_phase_3", "Voltage Phase 3", "/meter", "voltage.2", unit_of_measurement="V", icon="mdi:flash"),
        sensor("total_energy_import", "Total Energy Import", "/meter", "totalEnergyActiveImport", unit_of_measurement="kWh", icon="mdi:flash"),
        sensor("total_energy_export", "Total Energy Export", "/meter", "totalEnergyActiveExport", unit_of_measurement="kWh", icon="mdi:flash-off"),
        sensor("meter_vendor", "Meter Vendor", "/status", "meterInfo.vendor", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:meter-electric"),
        sensor("meter_type", "Meter Type", "/status", "meterInfo.type", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:meter-electric"),
        sensor("meter_id", "Meter ID", "/status", "meterInfo.id", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:meter-electric"),

        # EVSE endpoint entities
        sensor("chargebox_connection_status", "Chargebox Network Connection Status", "/evse", "0.connection_status", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:lan"),
        sensor("chargebox_outlet_1_state", "Chargebox Outlet 1 State", "/evse", "0.evse.0.state", icon="mdi:ev-plug-type2"),
        sensor("chargebox_outlet_1_energy", "Chargebox Outlet 1 Energy", "/evse", "0.evse.0.energy", unit_of_measurement="kWh", icon="mdi:ev-plug-type2", transform=lambda x: x / 1000), #Total energy used when charging, in kWh
        sensor("chargebox_outlet_1_power", "Chargebox Outlet 1 Power", "/evse", "0.evse.0.power", unit_of_measurement="kW", icon="mdi:ev-plug-type2", transform=lambda x: x / 1000), # Current kW usage
        sensor("chargebox_outlet_1_current_phase_1", "Chargebox Outlet 1 Current Phase 1", "/evse", "0.evse.0.current.0", unit_of_measurement="A", icon="mdi:ev-plug-type2"),
        sensor("chargebox_outlet_1_current_phase_2", "Chargebox Outlet 1 Current Phase 2", "/evse", "0.evse.0.current.1", unit_of_measurement="A", icon="mdi:ev-plug-type2"),
        sensor("chargebox_outlet_1_current_phase_3", "Chargebox Outlet 1 Current Phase 3", "/evse", "0.evse.0.current.2", unit_of_measurement="A", icon="mdi:ev-plug-type2"),

        # Chargebox endpoint entities
        sensor("chargebox_serial", "Chargebox Serial", "/status", "chargeboxInfo.serial", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:numeric"),
        sensor("chargebox_firmware", "Chargebox Firmware", "/status", "chargeboxInfo.firmware", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:update"),
        sensor("chargebox_endpoint", "Chargebox Endpoint", "/status", "chargeboxInfo.endpoint", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:link"),
        sensor("chargebox_port", "Chargebox Endpoint TCP Port", "/status", "chargeboxInfo.port", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:lan"),
        sensor("chargebox_state", "Chargebox State", "/status", "chargeboxInfo.state", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:lan"),

    ]

    async_add_entities(sensors)


class CTEKSensor(CoordinatorEntity[CTEKNanogridCoordinator], SensorEntity):
    """Representation of a single CTEK Nanogrid Air sensor."""

    def __init__(
        self,
        coordinator,
        host,
        port,
        sensor_id,
        name,
        json_path,
        unit_of_measurement=None,
        icon=None,
        transform=None,
        device_key=None,
        device_name=None,
        entity_category=None,
    ):
        super().__init__(coordinator)
        self._host = host
        self._port = port
        self._sensor_id = sensor_id
        self._name = name
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
        self._update_state_from_coordinator()

    def _update_state_from_coordinator(self):
        """Read this entity's value from the shared endpoint response."""
        raw_value = self._extract_value(self.coordinator.data, self._json_path)
        new_state = (
            self.transform(raw_value)
            if self.transform and raw_value is not None
            else raw_value
        )

        # Ignore transient zero readings after a valid cumulative energy value.
        # Publishing zero would make Home Assistant interpret the next valid
        # reading as a new meter cycle and inflate consumption.
        if (
            self._sensor_id == "chargebox_outlet_1_energy"
            and new_state == 0
            and self._state not in (None, 0)
        ):
            _LOGGER.warning(
                "Ignoring unexpected zero value for %s; keeping the previous value of %s",
                self._name,
                self._state,
            )
            return

        self._state = new_state

    @callback
    def _handle_coordinator_update(self):
        """Update this entity after its coordinator receives new data."""
        self._update_state_from_coordinator()
        self.async_write_ha_state()

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
        if self._sensor_id in ["active_power_in_watt", "active_power_in_kw", "active_power_out", "chargebox_outlet_1_power"]:
            return "power"
        if self._sensor_id in [
            "current_phase_1",
            "current_phase_2",
            "current_phase_3",
            "chargebox_outlet_1_current_phase_1",
            "chargebox_outlet_1_current_phase_2",
            "chargebox_outlet_1_current_phase_3",
        ]:
            return "current"
        if self._sensor_id in [
            "voltage_phase_1",
            "voltage_phase_2",
            "voltage_phase_3",
        ]:
            return "voltage"
        return None

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        if self._sensor_id in ["total_energy_import", "total_energy_export", "chargebox_outlet_1_energy"]:
            return "total_increasing"
        if self._sensor_id in [
            "active_power_in_watt",
            "active_power_in_kw",
            "active_power_out",
            "chargebox_outlet_1_power",
            "current_phase_1",
            "current_phase_2",
            "current_phase_3",
            "chargebox_outlet_1_current_phase_1",
            "chargebox_outlet_1_current_phase_2",
            "chargebox_outlet_1_current_phase_3",
            "voltage_phase_1",
            "voltage_phase_2",
            "voltage_phase_3",
        ]:
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


