"""Data integrity tests for BMP280 component profile — key disambiguation from BME280."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "components" / "temperature" / "bmp280.json"


@pytest.fixture(scope="module")
def bmp280():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_chip_id_is_0x58_not_0x60(bmp280):
    """BMP280 chip ID is 0x58; BME280 is 0x60. Verification method must state this."""
    method = bmp280["variants"]["verification_method"].lower()
    assert "0x58" in method
    assert "0x60" in method


def test_type_does_not_include_humidity(bmp280):
    """BMP280 has no humidity sensor — type must NOT contain 'humidity'."""
    assert "humidity" not in bmp280["type"]


def test_easily_confused_with_bme280(bmp280):
    """BME280 is the primary confusion risk since boards look physically identical."""
    confused = bmp280["variants"]["easily_confused_with"]
    assert any(c["component_id"] == "bme280" for c in confused)


def test_does_not_tolerate_5v(bmp280):
    """BMP280 max voltage is 3.6V; a level shifter is required on 5V boards."""
    assert bmp280["power"]["tolerates_5v"] is False
    assert bmp280["power"]["level_shifter_required_on_5v_board"] is True


def test_i2c_addresses_are_0x76_or_0x77(bmp280):
    """BMP280 I2C address is selectable between 0x76 and 0x77 via SDO pin."""
    addresses = bmp280["i2c"]["default_addresses"]
    assert "0x76" in addresses
    assert "0x77" in addresses


def test_no_calibration_required(bmp280):
    """BMP280 is factory calibrated."""
    assert bmp280["calibration"]["required"] is False
