"""Domain-specific data integrity tests for the ESP32-S3 board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "esp32" / "esp32-s3-devkitc-1.json"


@pytest.fixture(scope="module")
def s3_profile():
    """Load the ESP32-S3 DevKit C-1 profile."""
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_gpio_19_and_20_reserved_for_usb(s3_profile):
    """ESP32-S3 USB OTG uses GPIO 19 and 20. They must be marked reserved."""
    reserved = s3_profile["gpio"]["reserved_for_usb"]
    assert 19 in reserved
    assert 20 in reserved


def test_strapping_pins_include_0_3_45_46(s3_profile):
    """ESP32-S3 strapping pins are GPIO 0, 3, 45, 46 per Espressif datasheet."""
    strapping = set(s3_profile["gpio"]["strapping_pins"])
    assert {0, 3, 45, 46}.issubset(strapping)


def test_chip_has_ble_5(s3_profile):
    """ESP32-S3 has BLE 5.0 (no BT Classic)."""
    assert s3_profile["wireless"]["bluetooth"] == "BLE 5.0"
    assert s3_profile["wireless"]["bluetooth_classic"] is False


def test_chip_has_no_thread(s3_profile):
    """ESP32-S3 does not have 802.15.4, so no Thread or Zigbee."""
    assert s3_profile["wireless"]["thread"] is False
    assert s3_profile["wireless"]["zigbee"] is False


def test_smart_home_caps_consistent_with_chip(s3_profile):
    """ESP32-S3 supports bluetooth_proxy (has BLE) but not zigbee_coordinator (no 802.15.4)."""
    caps = s3_profile["smart_home_capabilities"]
    assert caps["bluetooth_proxy"] is True
    assert caps["zigbee_coordinator"] is False


def test_no_dac_on_s3(s3_profile):
    """ESP32-S3 has no DAC pins (removed compared to ESP32 classic)."""
    assert s3_profile["limitations"]["no_dac"] is True
    assert s3_profile["gpio"]["dac_pins"] == []


def test_valid_gpio_range_for_s3(s3_profile):
    """ESP32-S3 valid GPIO are 0-21 and 26-48 (22-25 are reserved for SPI flash)."""
    valid = set(s3_profile["gpio"]["valid_pins"])
    expected = set(range(0, 22)) | set(range(26, 49))
    assert valid == expected


def test_psram_blocks_gpio_26_to_32(s3_profile):
    """When PSRAM is active, GPIO 26-32 are unusable."""
    psram_blocks = set(s3_profile["limitations"]["psram_blocks_gpio"])
    assert {26, 27, 28, 29, 30, 31, 32}.issubset(psram_blocks)


def test_lifecycle_is_active(s3_profile):
    """ESP32-S3 DevKit C-1 is a current product, status must be active."""
    assert s3_profile["lifecycle"]["status"] == "active"
