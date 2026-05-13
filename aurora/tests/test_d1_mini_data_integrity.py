"""Domain-specific data integrity tests for the Wemos D1 Mini (ESP8266) board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "esp8266" / "d1-mini.json"


@pytest.fixture(scope="module")
def d1_mini():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_d1_mini_chip_is_esp8266(d1_mini):
    assert d1_mini["chip"] == "ESP8266EX"


def test_d1_mini_has_no_bluetooth(d1_mini):
    """ESP8266 has no Bluetooth radio at all."""
    assert d1_mini["wireless"]["bluetooth"] is None
    assert d1_mini["wireless"]["bluetooth_classic"] is False


def test_d1_mini_has_no_thread_or_zigbee(d1_mini):
    """ESP8266 has no 802.15.4 radio."""
    assert d1_mini["wireless"]["thread"] is False
    assert d1_mini["wireless"]["zigbee"] is False


def test_d1_mini_lifecycle_is_legacy(d1_mini):
    """ESP8266 is marked legacy in favor of the ESP32-C3 Super Mini for new projects."""
    assert d1_mini["lifecycle"]["status"] == "legacy"
    assert d1_mini["lifecycle"]["successor"] == "esp32-c3-mini"


def test_d1_mini_capabilities_reflect_no_ble(d1_mini):
    """All BLE-dependent capabilities must be false."""
    caps = d1_mini["smart_home_capabilities"]
    assert caps["bluetooth_proxy"] is False
    assert caps["ble_tracker"] is False
    assert caps["matter_controller"] is False
    assert caps["matter_device"] is False
    assert caps["voice_assistant"] is False


def test_d1_mini_flash_pins_reserved(d1_mini):
    """ESP8266 flash uses GPIO 6-11. They must be reserved."""
    reserved_flash = set(d1_mini["gpio"]["reserved_for_flash"])
    assert {6, 7, 8, 9, 10, 11}.issubset(reserved_flash)


def test_d1_mini_only_one_adc_pin(d1_mini):
    """ESP8266 has a single ADC channel exposed as A0 (GPIO 17 in our mapping)."""
    assert d1_mini["gpio"]["adc1_pins"] == [17]
    assert d1_mini["gpio"]["adc2_pins"] == []


def test_d1_mini_esphome_uses_arduino_framework(d1_mini):
    """ESPHome on ESP8266 only supports the Arduino framework, not esp-idf."""
    assert d1_mini["esphome"]["framework"] == "arduino"
    assert d1_mini["esphome"]["platform"] == "esp8266"
