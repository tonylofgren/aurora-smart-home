"""Data integrity tests for NTC Thermistor 10K component profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "components" / "temperature" / "ntc-thermistor-10k.json"


@pytest.fixture(scope="module")
def ntc():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_protocol_is_analog(ntc):
    """NTC thermistor is a passive analog component requiring ADC."""
    assert ntc["protocol"] == "analog"


def test_adc_required(ntc):
    """An ADC-capable GPIO is required to read the thermistor voltage divider output."""
    assert ntc["pin_requirements"]["adc_required"] is True


def test_calibration_required(ntc):
    """NTC thermistors require calibration via beta coefficient or two-point reference."""
    assert ntc["calibration"]["required"] is True


def test_calibration_type_includes_beta_coefficient(ntc):
    """Beta coefficient method or two-point reference are the standard calibration approaches."""
    assert ntc["calibration"]["type"] == "beta_coefficient_or_two_point"


def test_requires_voltage_divider(ntc):
    """A 10K series resistor forming a voltage divider is required."""
    pullup = ntc["external_components"]["pullup_resistor"]
    assert pullup["required"] is True
    assert pullup["value_ohm"] == 10000


def test_voltage_max_is_3v3(ntc):
    """NTC thermistor on 3.3V boards; ADC reference voltage is 3.3V."""
    assert ntc["power"]["voltage_max"] == 3.3
