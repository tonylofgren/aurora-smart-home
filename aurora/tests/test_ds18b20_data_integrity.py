"""Data integrity tests for DS18B20 OneWire temperature sensor profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "components" / "temperature" / "ds18b20.json"


@pytest.fixture(scope="module")
def ds18b20():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_protocol_is_onewire(ds18b20):
    """DS18B20 uses the OneWire protocol, not I2C or single_wire_digital."""
    assert ds18b20["protocol"] == "onewire"


def test_requires_one_pin(ds18b20):
    """DS18B20 shares one data pin across all sensors on the bus."""
    assert ds18b20["pin_requirements"]["count"] == 1


def test_requires_external_pullup_4700_ohm(ds18b20):
    """4.7kΩ pullup is required on the OneWire bus line."""
    pullup = ds18b20["external_components"]["pullup_resistor"]
    assert pullup["required"] is True
    assert pullup["value_ohm"] == 4700


def test_no_calibration_required(ds18b20):
    """DS18B20 is factory calibrated to +/- 0.5C."""
    assert ds18b20["calibration"]["required"] is False


def test_multi_drop_on_single_pin(ds18b20):
    """Multiple DS18B20 sensors can share one pin on the OneWire bus."""
    assert ds18b20["limitations"]["multi_drop_on_single_pin"] is True


def test_esphome_platform_is_dallas_temp(ds18b20):
    """ESPHome uses the dallas_temp platform (renamed from dallas in 2023.12)."""
    assert ds18b20["esphome"]["platform"] == "dallas_temp"
    assert ds18b20["esphome"]["min_version"] == "2023.12.0"
