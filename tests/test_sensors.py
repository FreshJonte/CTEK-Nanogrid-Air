"""Protect sensor identities, availability and statistics from regressions."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from yarl import URL

from custom_components.ctek_nanogrid_air.const import DOMAIN
from custom_components.ctek_nanogrid_air.sensor import CTEKSensor, async_setup_entry


def make_sensor(
    value, sensor_id="active_power_in_watt", unit="W", transform=lambda x: x * 1000
):
    coordinator = MagicMock()
    coordinator.data = {"/meter": {"value": value}}
    coordinator.last_update_success = True
    coordinator.api.base_url = URL("http://device.local:8080")
    sensor = CTEKSensor(
        coordinator,
        "device.local",
        8080,
        sensor_id,
        "Test",
        "/meter",
        "value",
        unit_of_measurement=unit,
        transform=transform,
        device_key="device.local:8080",
    )
    return sensor, coordinator


@pytest.mark.parametrize(
    "raw,expected",
    [
        (1.5, 1500),
        ("1.5", 1500),
        (0, 0),
        (None, None),
        (True, None),
        ("bad", None),
        ("nan", None),
        (float("inf"), None),
        ({}, None),
        ([], None),
        (1e308, None),
    ],
)
def test_numeric_readings(raw, expected):
    sensor, _ = make_sensor(raw)
    assert sensor.native_value == expected
    assert sensor.native_unit_of_measurement == "W"
    assert sensor.should_poll is False


def test_energy_zero_after_outage():
    sensor, coordinator = make_sensor(
        12000, "chargebox_outlet_1_energy", "kWh", lambda x: x / 1000
    )
    assert sensor.native_value == 12
    for raw, expected in [(None, None), (0, 12), (13000, 13)]:
        coordinator.data["/meter"] = {"value": raw}
        sensor._update_value()
        assert sensor.native_value == expected


def test_endpoint_availability_and_recovery():
    sensor, coordinator = make_sensor(1)
    assert sensor.available
    coordinator.data["/meter"] = None
    assert not sensor.available
    coordinator.data["/meter"] = {"value": 2}
    assert sensor.available
    coordinator.last_update_success = False
    assert not sensor.available


@pytest.mark.parametrize(
    "state,expected",
    [(2, "Charging"), ("0", "Available"), (None, None), ({}, None), (99, None)],
)
def test_outlet_state(state, expected):
    sensor, _ = make_sensor(state, "chargebox_outlet_1_state", None, None)
    assert sensor.native_value == expected


async def test_all_sensor_ids_preserved():
    hass = MagicMock()
    coordinator = MagicMock()
    coordinator.data = {}
    hass.data = {DOMAIN: {"entry": coordinator}}
    entry = SimpleNamespace(
        entry_id="entry", data={"host": "device.local", "port": 8080}
    )
    add_entities = MagicMock()
    await async_setup_entry(hass, entry, add_entities)
    sensors = add_entities.call_args.args[0]
    assert len(sensors) == 31
    assert len({sensor.unique_id for sensor in sensors}) == 31
    assert all(
        sensor.unique_id == f"{DOMAIN}_device.local:8080_{sensor._sensor_id}"
        for sensor in sensors
    )
    assert all(not sensor.should_poll for sensor in sensors)


def test_device_link_includes_port():
    sensor, _ = make_sensor(1)
    assert sensor.device_info["configuration_url"] == "http://device.local:8080"
