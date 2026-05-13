"""Domain-specific data integrity tests for the Sonoff Basic R3 board profile."""
import json
from pathlib import Path

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "smart-home" / "sonoff-basic-r3.json"


import pytest


@pytest.fixture(scope="module")
def sonoff_basic_r3():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_sonoff_basic_r3_is_legacy(sonoff_basic_r3):
    """Sonoff Basic R3 is marked legacy due to the ESP8285 chip limitations."""
    assert sonoff_basic_r3["lifecycle"]["status"] == "legacy"


def test_sonoff_basic_r3_successor_is_mini_r3(sonoff_basic_r3):
    """The recommended successor for Sonoff Basic R3 is the Sonoff Mini R3."""
    assert sonoff_basic_r3["lifecycle"]["successor"] == "sonoff-mini-r3"


def test_sonoff_basic_r3_chip_is_esp8285(sonoff_basic_r3):
    """Sonoff Basic R3 uses the ESP8285 (ESP8266-compatible with integrated 1MB flash)."""
    assert sonoff_basic_r3["chip"] == "ESP8285"


def test_sonoff_basic_r3_relay_pin_is_12(sonoff_basic_r3):
    """Sonoff Basic R3 relay output is hardwired to GPIO 12."""
    assert 12 in sonoff_basic_r3["gpio"]["valid_pins"]


def test_sonoff_basic_r3_led_pin_is_13(sonoff_basic_r3):
    """Sonoff Basic R3 status LED (active-low) is on GPIO 13."""
    assert sonoff_basic_r3["onboard_components"]["led_gpio"] == 13


def test_sonoff_basic_r3_has_no_bluetooth(sonoff_basic_r3):
    """ESP8285 has no Bluetooth radio."""
    assert sonoff_basic_r3["wireless"]["bluetooth"] is None
    assert sonoff_basic_r3["wireless"]["bluetooth_classic"] is False


def test_sonoff_basic_r3_all_ble_caps_false(sonoff_basic_r3):
    """All BLE-dependent capabilities must be false on ESP8285."""
    caps = sonoff_basic_r3["smart_home_capabilities"]
    assert caps["bluetooth_proxy"] is False
    assert caps["ble_tracker"] is False
    assert caps["matter_device"] is False
    assert caps["matter_controller"] is False


def test_sonoff_basic_r3_esphome_uses_esp8266_arduino(sonoff_basic_r3):
    """ESPHome on ESP8285 targets the esp8266 platform with Arduino framework."""
    esphome = sonoff_basic_r3["esphome"]
    assert esphome["platform"] == "esp8266"
    assert esphome["framework"] == "arduino"


def test_sonoff_basic_r3_flash_is_1mb(sonoff_basic_r3):
    """ESP8285 has only 1MB integrated flash."""
    assert sonoff_basic_r3["memory"]["flash_mb"] == 1


def test_sonoff_basic_r3_valid_pins_limited(sonoff_basic_r3):
    """Only the 4 exposed GPIO pads are listed as valid."""
    assert set(sonoff_basic_r3["gpio"]["valid_pins"]) == {0, 12, 13, 14}
