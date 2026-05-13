"""Data integrity tests for MH-Z19B CO2 sensor component profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "components" / "air-quality" / "mh-z19b.json"


@pytest.fixture(scope="module")
def mhz19b():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_protocol_is_uart(mhz19b):
    """MH-Z19B communicates over UART (TX/RX), not I2C."""
    assert mhz19b["protocol"] == "uart"


def test_calibration_is_required(mhz19b):
    """MH-Z19B requires manual zero-point calibration — this distinguishes it from MH-Z19C."""
    assert mhz19b["calibration"]["required"] is True


def test_calibration_type_is_zero_point_400ppm_outdoors(mhz19b):
    """Zero-point calibration must be done outdoors at ~400ppm ambient CO2."""
    assert mhz19b["calibration"]["type"] == "zero_point_400ppm_outdoors"


def test_vcc_requires_5v(mhz19b):
    """MH-Z19B VCC must be 5V; 3.3V is insufficient for the sensor."""
    assert mhz19b["power"]["voltage_min"] == 4.5
    assert mhz19b["power"]["voltage_max"] == 5.5


def test_easily_confused_with_mhz19c(mhz19b):
    """MH-Z19C is the most common mix-up due to different calibration behavior."""
    confused = mhz19b["variants"]["easily_confused_with"]
    assert any(c["component_id"] == "mh-z19c" for c in confused)


def test_requires_two_pins(mhz19b):
    """UART requires TX and RX, so pin count must be 2."""
    assert mhz19b["pin_requirements"]["count"] == 2
