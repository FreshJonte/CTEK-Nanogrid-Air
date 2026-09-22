"""Sensors backed by shared Nanogrid API updates."""

import math

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import extract_value
from .const import DEFAULT_PORT, DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors for CTEK Nanogrid Air integration."""
    config = entry.data
    host = config["host"]
    port = config.get("port", DEFAULT_PORT)
    coordinator = hass.data[DOMAIN][entry.entry_id]

    device_key = f"{host}:{port}"

    # Define the sensors to be added
    sensors = [
        # Status endpoint entities
        CTEKSensor(
            coordinator,
            host,
            port,
            "device_serial",
            "Device Serial",
            "/status",
            "deviceInfo.serial",
            device_key=device_key,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:numeric",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "device_firmware",
            "Device Firmware",
            "/status",
            "deviceInfo.firmware",
            device_key=device_key,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:update",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "device_mac",
            "Device MAC",
            "/status",
            "deviceInfo.mac",
            device_key=device_key,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:router",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "wifi_ssid",
            "WiFi SSID",
            "/status",
            "wifiInfo.ssid",
            device_key=device_key,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:wifi",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "wifi_rssi",
            "WiFi Signal Strength",
            "/status",
            "wifiInfo.rssi",
            unit_of_measurement="dBm",
            device_key=device_key,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:signal",
        ),
        # Meter endpoint entities
        CTEKSensor(
            coordinator,
            host,
            port,
            "active_power_in_watt",
            "Active Power In Watt",
            "/meter",
            "activePowerIn",
            unit_of_measurement="W",
            device_key=device_key,
            icon="mdi:meter-electric",
            transform=lambda x: x * 1000,
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "active_power_in_kw",
            "Active Power In Kw",
            "/meter",
            "activePowerIn",
            unit_of_measurement="kW",
            device_key=device_key,
            icon="mdi:meter-electric",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "active_power_out",
            "Active Power Out",
            "/meter",
            "activePowerOut",
            unit_of_measurement="W",
            device_key=device_key,
            icon="mdi:flash-off",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "current_phase_1",
            "Current Phase 1",
            "/meter",
            "current.0",
            unit_of_measurement="A",
            device_key=device_key,
            icon="mdi:current-ac",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "current_phase_2",
            "Current Phase 2",
            "/meter",
            "current.1",
            unit_of_measurement="A",
            device_key=device_key,
            icon="mdi:current-ac",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "current_phase_3",
            "Current Phase 3",
            "/meter",
            "current.2",
            unit_of_measurement="A",
            device_key=device_key,
            icon="mdi:current-ac",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "voltage_phase_1",
            "Voltage Phase 1",
            "/meter",
            "voltage.0",
            unit_of_measurement="V",
            device_key=device_key,
            icon="mdi:flash",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "voltage_phase_2",
            "Voltage Phase 2",
            "/meter",
            "voltage.1",
            unit_of_measurement="V",
            device_key=device_key,
            icon="mdi:flash",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "voltage_phase_3",
            "Voltage Phase 3",
            "/meter",
            "voltage.2",
            unit_of_measurement="V",
            device_key=device_key,
            icon="mdi:flash",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "total_energy_import",
            "Total Energy Import",
            "/meter",
            "totalEnergyActiveImport",
            unit_of_measurement="kWh",
            device_key=device_key,
            icon="mdi:flash",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "total_energy_export",
            "Total Energy Export",
            "/meter",
            "totalEnergyActiveExport",
            unit_of_measurement="kWh",
            device_key=device_key,
            icon="mdi:flash-off",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "meter_vendor",
            "Meter Vendor",
            "/status",
            "meterInfo.vendor",
            device_key=device_key,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:meter-electric",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "meter_type",
            "Meter Type",
            "/status",
            "meterInfo.type",
            device_key=device_key,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:meter-electric",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "meter_id",
            "Meter ID",
            "/status",
            "meterInfo.id",
            device_key=device_key,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:meter-electric",
        ),
        # EVSE endpoint entities
        CTEKSensor(
            coordinator,
            host,
            port,
            "chargebox_connection_status",
            "Chargebox Network Connection Status",
            "/evse",
            "0.connection_status",
            device_key=device_key,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:lan",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "chargebox_outlet_1_state",
            "Chargebox Outlet 1 State",
            "/evse",
            "0.evse.0.state",
            device_key=device_key,
            icon="mdi:ev-plug-type2",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "chargebox_outlet_1_energy",
            "Chargebox Outlet 1 Energy",
            "/evse",
            "0.evse.0.energy",
            unit_of_measurement="kWh",
            device_key=device_key,
            icon="mdi:ev-plug-type2",
            transform=lambda x: x / 1000,
        ),  # Total energy used when charging, in kWh
        CTEKSensor(
            coordinator,
            host,
            port,
            "chargebox_outlet_1_power",
            "Chargebox Outlet 1 Power",
            "/evse",
            "0.evse.0.power",
            unit_of_measurement="kW",
            device_key=device_key,
            icon="mdi:ev-plug-type2",
            transform=lambda x: x / 1000,
        ),  # Current kW usage
        CTEKSensor(
            coordinator,
            host,
            port,
            "chargebox_outlet_1_current_phase_1",
            "Chargebox Outlet 1 Current Phase 1",
            "/evse",
            "0.evse.0.current.0",
            unit_of_measurement="A",
            device_key=device_key,
            icon="mdi:ev-plug-type2",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "chargebox_outlet_1_current_phase_2",
            "Chargebox Outlet 1 Current Phase 2",
            "/evse",
            "0.evse.0.current.1",
            unit_of_measurement="A",
            device_key=device_key,
            icon="mdi:ev-plug-type2",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "chargebox_outlet_1_current_phase_3",
            "Chargebox Outlet 1 Current Phase 3",
            "/evse",
            "0.evse.0.current.2",
            unit_of_measurement="A",
            device_key=device_key,
            icon="mdi:ev-plug-type2",
        ),
        # Chargebox endpoint entities
        CTEKSensor(
            coordinator,
            host,
            port,
            "chargebox_serial",
            "Chargebox Serial",
            "/status",
            "chargeboxInfo.serial",
            device_key=device_key,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:numeric",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "chargebox_firmware",
            "Chargebox Firmware",
            "/status",
            "chargeboxInfo.firmware",
            device_key=device_key,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:update",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "chargebox_endpoint",
            "Chargebox Endpoint",
            "/status",
            "chargeboxInfo.endpoint",
            device_key=device_key,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:link",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "chargebox_port",
            "Chargebox Endpoint TCP Port",
            "/status",
            "chargeboxInfo.port",
            device_key=device_key,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:lan",
        ),
        CTEKSensor(
            coordinator,
            host,
            port,
            "chargebox_state",
            "Chargebox State",
            "/status",
            "chargeboxInfo.state",
            device_key=device_key,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:lan",
        ),
    ]

    async_add_entities(sensors)


class CTEKSensor(CoordinatorEntity, SensorEntity):
    """Representation of a single CTEK Nanogrid Air sensor."""

    def __init__(
        self,
        coordinator,
        host,
        port,
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
        super().__init__(coordinator)
        self._host = host
        self._port = port
        self._sensor_id = sensor_id
        self._name = name
        self._endpoint = endpoint
        self._json_path = json_path
        self._unit_of_measurement = unit_of_measurement
        self._icon = icon
        self._state = None
        self._last_valid_energy = None
        self.transform = transform
        self._entity_category = entity_category

        # device grouping info: supply the same device_key for sensors that should be grouped.
        # device_key should be unique for each physical device.
        self._device_key = device_key or f"{DOMAIN}_{host}:{port}"
        self._device_name = device_name or f"CTEK Nanogrid ({host})"

        self._update_value()

    @property
    def available(self):
        """Only mark sensors from a failed endpoint unavailable."""
        return (
            super().available and self.coordinator.data.get(self._endpoint) is not None
        )

    def _update_value(self):
        """Validate readings before handing them to Home Assistant statistics."""
        raw_value = extract_value(
            (self.coordinator.data or {}).get(self._endpoint), self._json_path
        )
        if self._unit_of_measurement is not None and raw_value is not None:
            try:
                if isinstance(raw_value, bool):
                    raise ValueError("Boolean is not a measurement")
                raw_value = float(raw_value)
                if not math.isfinite(raw_value):
                    raise ValueError("Non-finite measurement")
                if self.transform:
                    raw_value = self.transform(raw_value)
                if not math.isfinite(raw_value):
                    raise ValueError("Non-finite transformed measurement")
            except (TypeError, ValueError, OverflowError):
                raw_value = None
        elif isinstance(raw_value, (dict, list)):
            raw_value = None

        if self._sensor_id == "chargebox_outlet_1_energy":
            # Preserve the last valid counter across missing readings/outages.
            # A transient zero must not create a false meter reset in statistics.
            if raw_value == 0 and self._last_valid_energy not in (None, 0):
                raw_value = self._last_valid_energy
            elif raw_value is not None:
                self._last_valid_energy = raw_value
        self._state = raw_value

    @callback
    def _handle_coordinator_update(self):
        self._update_value()
        self.async_write_ha_state()

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
    def native_value(self):
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
            return state_mapping.get(self._state)
        return self._state

    @property
    def native_unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def icon(self):
        return self._icon

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        if self._sensor_id in [
            "total_energy_import",
            "total_energy_export",
            "chargebox_outlet_1_energy",
        ]:
            return "energy"
        if self._sensor_id in [
            "active_power_in_watt",
            "active_power_in_kw",
            "active_power_out",
            "chargebox_outlet_1_power",
        ]:
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
        if self._sensor_id in [
            "total_energy_import",
            "total_energy_export",
            "chargebox_outlet_1_energy",
        ]:
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
            configuration_url=str(self.coordinator.api.base_url),
        )
