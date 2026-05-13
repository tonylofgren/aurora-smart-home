"""Data integrity tests for DHT22 / AM2302 component profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "components" / "temperature" / "dht22.json"


@pytest.fixture(scope="module")
def dht22():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_protocol_is_single_wire_digital(dht22):
    """DHT22 uses a proprietary single-wire digital protocol, not I2C or SPI."""
    assert dht22["protocol"] == "single_wire_digital"


def test_requires_one_pin(dht22):
    """DHT22 needs exactly one data pin."""
    assert dht22["pin_requirements"]["count"] == 1


def test_requires_external_pullup_4700_ohm(dht22):
    """External 4.7kΩ pullup on the data line is required for reliable operation."""
    pullup = dht22["external_components"]["pullup_resistor"]
    assert pullup["required"] is True
    assert pullup["value_ohm"] == 4700


def test_no_calibration_required(dht22):
    """DHT22 is factory calibrated; no user procedure is needed."""
    assert dht22["calibration"]["required"] is False


def test_min_read_interval_is_2_seconds(dht22):
    """DHT22 cannot be polled faster than once every 2 seconds."""
    assert dht22["limitations"]["min_read_interval_s"] == 2


def test_easily_confused_with_dht11(dht22):
    """DHT11 is the main confusion risk — lower accuracy, same protocol."""
    confused = dht22["variants"]["easily_confused_with"]
    assert any(c["component_id"] == "dht11" for c in confused)
