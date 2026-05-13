"""Data integrity tests for SCD40 CO2/temperature/humidity sensor profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "components" / "air-quality" / "scd40.json"


@pytest.fixture(scope="module")
def scd40():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_protocol_is_i2c(scd40):
    """SCD40 uses I2C for communication."""
    assert scd40["protocol"] == "i2c"


def test_i2c_address_is_0x62_fixed(scd40):
    """SCD40 has a fixed I2C address of 0x62 — no strap pin to change it."""
    assert scd40["i2c"]["default_addresses"] == ["0x62"]
    assert scd40["i2c"]["address_strap_pin"] is None


def test_calibration_not_required(scd40):
    """SCD40 ships factory calibrated; forced recalibration is optional, not required."""
    assert scd40["calibration"]["required"] is False


def test_esphome_platform_is_scd4x(scd40):
    """ESPHome uses the unified scd4x platform for both SCD40 and SCD41."""
    assert scd40["esphome"]["platform"] == "scd4x"


def test_easily_confused_with_scd41(scd40):
    """SCD41 is the main confusion risk; it extends CO2 range and adds single-shot mode."""
    confused = scd40["variants"]["easily_confused_with"]
    assert any(c["component_id"] == "scd41" for c in confused)


def test_voltage_range_supports_3v3_and_5v(scd40):
    """SCD40 operates from 2.4V to 5.5V, compatible with both 3.3V and 5V systems."""
    assert scd40["power"]["voltage_min"] <= 3.3
    assert scd40["power"]["voltage_max"] >= 5.0
