"""Domain-specific data integrity tests for the Sonoff Mini R3 board profile."""
import json
from pathlib import Path

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "smart-home" / "sonoff-mini-r3.json"


import pytest


@pytest.fixture(scope="module")
def sonoff_mini_r3():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_sonoff_mini_r3_has_ble(sonoff_mini_r3):
    """Sonoff Mini R3 uses ESP32-C3 which has BLE 5.0."""
    assert sonoff_mini_r3["wireless"]["bluetooth"] == "BLE 5.0"


def test_sonoff_mini_r3_chip_is_esp32_c3(sonoff_mini_r3):
    """Sonoff Mini R3 uses the ESP32-C3 (single-core RISC-V) chip."""
    assert sonoff_mini_r3["chip"] == "ESP32-C3"


def test_sonoff_mini_r3_relay_pin_is_4(sonoff_mini_r3):
    """Sonoff Mini R3 relay control is hardwired to GPIO 4."""
    assert 4 in sonoff_mini_r3["gpio"]["valid_pins"]


def test_sonoff_mini_r3_external_switch_pin_is_5(sonoff_mini_r3):
    """Sonoff Mini R3 external detect-switch input is GPIO 5."""
    assert 5 in sonoff_mini_r3["gpio"]["valid_pins"]


def test_sonoff_mini_r3_bluetooth_proxy_and_ble_tracker(sonoff_mini_r3):
    """ESP32-C3 BLE enables bluetooth_proxy and ble_tracker."""
    caps = sonoff_mini_r3["smart_home_capabilities"]
    assert caps["bluetooth_proxy"] is True
    assert caps["ble_tracker"] is True


def test_sonoff_mini_r3_matter_device_true(sonoff_mini_r3):
    """Sonoff Mini R3 supports Matter over WiFi."""
    assert sonoff_mini_r3["smart_home_capabilities"]["matter_device"] is True


def test_sonoff_mini_r3_no_bluetooth_classic(sonoff_mini_r3):
    """ESP32-C3 has BLE only, no Bluetooth Classic."""
    assert sonoff_mini_r3["wireless"]["bluetooth_classic"] is False


def test_sonoff_mini_r3_lifecycle_is_active(sonoff_mini_r3):
    """Sonoff Mini R3 is a current product."""
    assert sonoff_mini_r3["lifecycle"]["status"] == "active"


def test_sonoff_mini_r3_esphome_variant_is_esp32c3(sonoff_mini_r3):
    """ESPHome variant must be ESP32C3 for correct chip targeting."""
    assert sonoff_mini_r3["esphome"]["variant"] == "ESP32C3"
    assert sonoff_mini_r3["esphome"]["platform"] == "esp32"


def test_sonoff_mini_r3_strapping_pins_include_2_8_9(sonoff_mini_r3):
    """ESP32-C3 strapping pins 2, 8, 9 must be listed."""
    strapping = set(sonoff_mini_r3["gpio"]["strapping_pins"])
    assert {2, 8, 9}.issubset(strapping)
