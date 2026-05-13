"""Domain-specific data integrity tests for the BME280 component profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "components" / "temperature" / "bme280.json"


@pytest.fixture(scope="module")
def bme280():
    """Load the BME280 profile."""
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_protocol_is_i2c(bme280):
    """BME280 uses I2C (or SPI, but we expose the I2C variant)."""
    assert bme280["protocol"] == "i2c"


def test_easily_confused_with_bmp280(bme280):
    """BME280 and BMP280 look identical but BMP280 lacks humidity."""
    confused = bme280["variants"]["easily_confused_with"]
    assert any(c["component_id"] == "bmp280" for c in confused)


def test_verification_method_includes_chip_id_check(bme280):
    """Detection must reference the chip ID register since the boards look identical."""
    method = bme280["variants"]["verification_method"].lower()
    assert "0x60" in method and "0x58" in method


def test_i2c_addresses_are_0x76_or_0x77(bme280):
    """BME280 ships as either 0x76 or 0x77 depending on SDO."""
    addresses = bme280["i2c"]["default_addresses"]
    assert "0x76" in addresses
    assert "0x77" in addresses


def test_does_not_tolerate_5v(bme280):
    """BME280 max voltage is 3.6V. On a 5V board it needs a level shifter."""
    assert bme280["power"]["tolerates_5v"] is False
    assert bme280["power"]["level_shifter_required_on_5v_board"] is True


def test_voltage_range(bme280):
    """BME280 operates between 1.8V and 3.6V."""
    assert bme280["power"]["voltage_min"] == 1.8
    assert bme280["power"]["voltage_max"] == 3.6


def test_pin_requirements_count_is_two(bme280):
    """I2C needs exactly SDA and SCL, so count = 2."""
    assert bme280["pin_requirements"]["count"] == 2
    assert bme280["pin_requirements"]["type"] == "i2c"


def test_no_calibration_required(bme280):
    """BME280 is factory calibrated, no user procedure needed."""
    assert bme280["calibration"]["required"] is False
