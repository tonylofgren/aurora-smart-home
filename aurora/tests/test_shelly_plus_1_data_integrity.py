"""Domain-specific data integrity tests for the Shelly Plus 1 board profile."""
import json
from pathlib import Path

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "smart-home" / "shelly-plus-1.json"


import pytest


@pytest.fixture(scope="module")
def shelly_plus_1():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_shelly_plus_1_relay_pin_is_26(shelly_plus_1):
    """Shelly Plus 1 relay output is hardwired to GPIO 26."""
    assert 26 in shelly_plus_1["gpio"]["valid_pins"]


def test_shelly_plus_1_button_pin_is_4(shelly_plus_1):
    """Shelly Plus 1 SW input (optocoupler) is hardwired to GPIO 4."""
    assert 4 in shelly_plus_1["gpio"]["valid_pins"]


def test_shelly_plus_1_valid_pins_limited(shelly_plus_1):
    """Only 3 pins are exposed on Shelly Plus 1: GPIO 0, 4, 26."""
    assert set(shelly_plus_1["gpio"]["valid_pins"]) == {0, 4, 26}


def test_shelly_plus_1_no_usb(shelly_plus_1):
    """Shelly Plus 1 is mains-powered. No USB port."""
    assert shelly_plus_1["power"]["usb_type"] is None


def test_shelly_plus_1_mains_input_voltage(shelly_plus_1):
    """Input voltage is AC mains, not USB or battery."""
    assert "mains" in shelly_plus_1["power"]["input_voltage_range"].lower()


def test_shelly_plus_1_bluetooth_proxy_and_ble_tracker(shelly_plus_1):
    """Shelly Plus 1 ESP32 supports BLE, enabling bluetooth_proxy and ble_tracker."""
    caps = shelly_plus_1["smart_home_capabilities"]
    assert caps["bluetooth_proxy"] is True
    assert caps["ble_tracker"] is True


def test_shelly_plus_1_matter_device_true(shelly_plus_1):
    """Shelly Plus 1 supports Matter device role via ESPHome or Shelly firmware."""
    assert shelly_plus_1["smart_home_capabilities"]["matter_device"] is True


def test_shelly_plus_1_no_voice_assistant(shelly_plus_1):
    """Shelly Plus 1 has no audio hardware and cannot serve as voice assistant."""
    assert shelly_plus_1["smart_home_capabilities"]["voice_assistant"] is False


def test_shelly_plus_1_lifecycle_is_active(shelly_plus_1):
    """Shelly Plus 1 is a current product."""
    assert shelly_plus_1["lifecycle"]["status"] == "active"


def test_shelly_plus_1_chip_is_esp32_wroom32(shelly_plus_1):
    """Shelly Plus 1 uses the classic ESP32-WROOM-32 module."""
    assert shelly_plus_1["chip"] == "ESP32-WROOM-32"
