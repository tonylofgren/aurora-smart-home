"""Domain-specific data integrity tests for the Shelly Plus 2PM board profile."""
import json
from pathlib import Path

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "smart-home" / "shelly-plus-2pm.json"


import pytest


@pytest.fixture(scope="module")
def shelly_plus_2pm():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_shelly_plus_2pm_has_two_relays(shelly_plus_2pm):
    """Shelly Plus 2PM has two relay outputs: GPIO 12 and GPIO 13."""
    valid = shelly_plus_2pm["gpio"]["valid_pins"]
    assert 12 in valid
    assert 13 in valid


def test_shelly_plus_2pm_relay_pins_are_12_and_13(shelly_plus_2pm):
    """Relay 1 is GPIO 12, relay 2 is GPIO 13 per Shelly hardware design."""
    valid = set(shelly_plus_2pm["gpio"]["valid_pins"])
    assert {12, 13}.issubset(valid)


def test_shelly_plus_2pm_ade7953_i2c_pins(shelly_plus_2pm):
    """ADE7953 power monitor uses I2C on GPIO 19 (SDA) and GPIO 23 (SCL)."""
    i2c = shelly_plus_2pm["gpio"]["i2c_default"]
    assert i2c["sda"] == 19
    assert i2c["scl"] == 23


def test_shelly_plus_2pm_valid_pins_set(shelly_plus_2pm):
    """Only the 7 functionally exposed pins are listed as valid."""
    assert set(shelly_plus_2pm["gpio"]["valid_pins"]) == {0, 5, 12, 13, 18, 19, 23}


def test_shelly_plus_2pm_no_usb(shelly_plus_2pm):
    """Shelly Plus 2PM is mains-powered. No USB port."""
    assert shelly_plus_2pm["power"]["usb_type"] is None


def test_shelly_plus_2pm_mains_input_voltage(shelly_plus_2pm):
    """Input voltage is AC mains, not USB or battery."""
    assert "mains" in shelly_plus_2pm["power"]["input_voltage_range"].lower()


def test_shelly_plus_2pm_bluetooth_proxy_and_ble_tracker(shelly_plus_2pm):
    """Shelly Plus 2PM ESP32 supports BLE proxy and tracker."""
    caps = shelly_plus_2pm["smart_home_capabilities"]
    assert caps["bluetooth_proxy"] is True
    assert caps["ble_tracker"] is True


def test_shelly_plus_2pm_lifecycle_is_active(shelly_plus_2pm):
    """Shelly Plus 2PM is a current product."""
    assert shelly_plus_2pm["lifecycle"]["status"] == "active"


def test_shelly_plus_2pm_chip_is_esp32_wroom32(shelly_plus_2pm):
    """Shelly Plus 2PM uses the classic ESP32-WROOM-32 module."""
    assert shelly_plus_2pm["chip"] == "ESP32-WROOM-32"


def test_shelly_plus_2pm_no_battery(shelly_plus_2pm):
    """Shelly Plus 2PM is mains-powered only, no battery connector."""
    assert shelly_plus_2pm["power"]["battery_connector"] is None
    assert shelly_plus_2pm["smart_home_capabilities"]["battery_powered"] is False
