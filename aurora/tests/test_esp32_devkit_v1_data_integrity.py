"""Domain-specific data integrity tests for the ESP32 DevKit V1 board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "esp32" / "esp32-devkit-v1.json"


@pytest.fixture(scope="module")
def devkit_v1():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_chip_has_bluetooth_classic(devkit_v1):
    """ESP32 classic is the only ESP32 variant with both BLE and Bluetooth Classic."""
    assert devkit_v1["wireless"]["bluetooth_classic"] is True
    assert devkit_v1["wireless"]["bluetooth"] == "BLE 4.2 + BT Classic"


def test_no_thread_no_zigbee(devkit_v1):
    """ESP32 classic has no 802.15.4 radio, so Thread and Zigbee must be false."""
    assert devkit_v1["wireless"]["thread"] is False
    assert devkit_v1["wireless"]["zigbee"] is False


def test_has_dac_pins(devkit_v1):
    """ESP32 classic has two DAC pins (GPIO 25 and 26) unlike S2/S3."""
    dac = devkit_v1["gpio"]["dac_pins"]
    assert 25 in dac
    assert 26 in dac
    assert devkit_v1["limitations"]["no_dac"] is False


def test_input_only_pins_34_35_36_39(devkit_v1):
    """GPIO 34, 35, 36, 39 are input-only on ESP32 classic (no output driver)."""
    input_only = set(devkit_v1["gpio"]["input_only"])
    assert {34, 35, 36, 39}.issubset(input_only)


def test_flash_reserved_6_to_11(devkit_v1):
    """GPIO 6-11 are used by the internal SPI flash and must never be used."""
    flash_reserved = set(devkit_v1["gpio"]["reserved_for_flash"])
    assert {6, 7, 8, 9, 10, 11}.issubset(flash_reserved)


def test_strapping_pins_include_0_2_5_12_15(devkit_v1):
    """ESP32 classic strapping pins are 0, 2, 5, 12, 15."""
    strapping = set(devkit_v1["gpio"]["strapping_pins"])
    assert {0, 2, 5, 12, 15}.issubset(strapping)


def test_no_psram_by_default(devkit_v1):
    """ESP32 DevKit V1 has no PSRAM by default."""
    assert devkit_v1["memory"]["psram_mb"] == 0
    assert devkit_v1["memory"]["psram_type"] is None


def test_adc2_blocked_when_wifi(devkit_v1):
    """ADC2 is unavailable while WiFi radio is active on ESP32 classic."""
    assert devkit_v1["limitations"]["adc2_blocked_when_wifi_active"] is True
