"""Domain-specific data integrity tests for the ESP32-S2 Mini board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "esp32" / "esp32-s2-mini.json"


@pytest.fixture(scope="module")
def s2():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_s2_has_no_bluetooth(s2):
    """ESP32-S2 has no Bluetooth at all — bluetooth field must be null."""
    assert s2["wireless"]["bluetooth"] is None
    assert s2["wireless"]["bluetooth_classic"] is False


def test_s2_bluetooth_proxy_false(s2):
    """Without BLE, bluetooth_proxy capability must be false."""
    assert s2["smart_home_capabilities"]["bluetooth_proxy"] is False


def test_s2_matter_controller_false(s2):
    """Matter controller requires BLE for commissioning; S2 has none."""
    assert s2["smart_home_capabilities"]["matter_controller"] is False


def test_s2_has_dac_pins_17_18(s2):
    """ESP32-S2 retains DAC on GPIO 17 and 18."""
    dac = s2["gpio"]["dac_pins"]
    assert 17 in dac
    assert 18 in dac


def test_s2_input_only_pin_46(s2):
    """GPIO 46 is input-only on ESP32-S2 (no output capability)."""
    assert 46 in s2["gpio"]["input_only"]


def test_s2_flash_reserved_22_to_25(s2):
    """GPIO 22-25 are reserved for SPI flash on ESP32-S2."""
    flash_reserved = set(s2["gpio"]["reserved_for_flash"])
    assert {22, 23, 24, 25}.issubset(flash_reserved)


def test_s2_adc2_blocked_when_wifi(s2):
    """ADC2 is unavailable while WiFi is active on ESP32-S2."""
    assert s2["limitations"]["adc2_blocked_when_wifi_active"] is True


def test_s2_usb_otg_pins(s2):
    """GPIO 19 and 20 are used by USB OTG and must be reserved."""
    assert 19 in s2["gpio"]["reserved_for_usb"]
    assert 20 in s2["gpio"]["reserved_for_usb"]
