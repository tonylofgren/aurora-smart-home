"""Integration test for Volt's Iron Law 6 validation workflow.

This test does not invoke Claude. It encodes the same checks that Volt must
perform, using the same reference data, to ensure the data is consistent
with the rules.
"""
import json
from pathlib import Path
import pytest

REF_DIR = Path(__file__).resolve().parents[1] / "references"


@pytest.fixture(scope="module")
def s3():
    with (REF_DIR / "boards/esp32/esp32-s3-devkitc-1.json").open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def bme280():
    with (REF_DIR / "components/temperature/bme280.json").open(encoding="utf-8") as f:
        return json.load(f)


def run_pin_validator(board, pin_assignments, config_flags):
    """Simulates the pin-validator rules from pin-validator.md."""
    failures = []
    warnings = []
    valid = set(board["gpio"]["valid_pins"])
    reserved_usb = set(board["gpio"].get("reserved_for_usb", []))
    reserved_flash = set(board["gpio"].get("reserved_for_flash", []))
    strapping = set(board["gpio"].get("strapping_pins", []))
    psram_blocks = set(board.get("limitations", {}).get("psram_blocks_gpio", []))
    for component, pins in pin_assignments.items():
        for n in pins:
            if n not in valid:
                failures.append(f"GPIO {n} does not exist on {board['display_name']}.")
                continue
            if config_flags.get("usb_cdc_enabled") and n in reserved_usb:
                failures.append(f"GPIO {n} is used by USB CDC on {board['display_name']}.")
            if config_flags.get("psram_used") and n in psram_blocks:
                failures.append(f"GPIO {n} is reserved for PSRAM on {board['display_name']}.")
            if n in reserved_flash:
                failures.append(f"GPIO {n} is hardwired to SPI flash.")
            if n in strapping:
                warnings.append(f"GPIO {n} is a strapping pin on {board['display_name']}.")
    return {"failures": failures, "warnings": warnings}


def run_conflict_validator(board, component_assignments):
    """Simulates the conflict-validator rules from conflict-validator.md."""
    failures = []
    i2c_addr_seen = {}
    pin_owners = {}
    for entry in component_assignments:
        comp_id = entry["component_id"]
        profile = entry["component_profile"]
        for pin in entry["pins"]:
            if pin in pin_owners and profile["protocol"] not in {"i2c", "onewire"}:
                failures.append(
                    f"GPIO {pin} is claimed by both {pin_owners[pin]} and {comp_id}."
                )
            pin_owners.setdefault(pin, comp_id)
        if profile["protocol"] == "i2c" and entry.get("i2c_address"):
            addr = entry["i2c_address"]
            if addr in i2c_addr_seen:
                failures.append(
                    f"{i2c_addr_seen[addr]} and {comp_id} both use I2C address {addr}."
                )
            else:
                i2c_addr_seen[addr] = comp_id
        if not profile["power"]["tolerates_5v"] and board["power"]["operating_voltage"] >= 5:
            failures.append(
                f"{comp_id} max voltage is {profile['power']['voltage_max']}V but the board is 5V."
            )
    return {"failures": failures}


def test_happy_path_bme280_on_esp32_s3_passes(s3, bme280):
    """The canonical example: BME280 on ESP32-S3 DevKit C-1 with default I2C pins."""
    pin_result = run_pin_validator(
        s3,
        pin_assignments={"bme280": [s3["gpio"]["i2c_default"]["sda"], s3["gpio"]["i2c_default"]["scl"]]},
        config_flags={"usb_cdc_enabled": True, "psram_used": True, "wifi_enabled": True},
    )
    assert pin_result["failures"] == []

    conflict_result = run_conflict_validator(
        s3,
        component_assignments=[
            {"component_id": "bme280", "component_profile": bme280,
             "pins": [s3["gpio"]["i2c_default"]["sda"], s3["gpio"]["i2c_default"]["scl"]],
             "i2c_address": "0x76"}
        ],
    )
    assert conflict_result["failures"] == []


def test_gpio_19_with_usb_cdc_fails(s3):
    """Using a USB pin while USB CDC is enabled must fail."""
    result = run_pin_validator(
        s3,
        pin_assignments={"sensor": [19]},
        config_flags={"usb_cdc_enabled": True},
    )
    assert any("USB CDC" in msg for msg in result["failures"])


def test_gpio_outside_valid_range_fails(s3):
    """A GPIO number that does not exist on the board must fail."""
    result = run_pin_validator(
        s3,
        pin_assignments={"sensor": [99]},
        config_flags={},
    )
    assert any("does not exist" in msg for msg in result["failures"])


def test_strapping_pin_emits_warning_not_failure(s3):
    """Strapping pins are warnings, not failures."""
    result = run_pin_validator(
        s3,
        pin_assignments={"sensor": [0]},
        config_flags={},
    )
    assert result["failures"] == []
    assert any("strapping pin" in msg for msg in result["warnings"])


def test_two_bme280_same_address_fails(s3, bme280):
    """Two BME280 on the same I2C address must collide."""
    result = run_conflict_validator(
        s3,
        component_assignments=[
            {"component_id": "bme280_a", "component_profile": bme280,
             "pins": [8, 9], "i2c_address": "0x76"},
            {"component_id": "bme280_b", "component_profile": bme280,
             "pins": [8, 9], "i2c_address": "0x76"},
        ],
    )
    assert any("I2C address 0x76" in msg for msg in result["failures"])


def test_two_bme280_different_addresses_pass(s3, bme280):
    """Two BME280 on distinct I2C addresses must share the bus cleanly."""
    result = run_conflict_validator(
        s3,
        component_assignments=[
            {"component_id": "bme280_a", "component_profile": bme280,
             "pins": [8, 9], "i2c_address": "0x76"},
            {"component_id": "bme280_b", "component_profile": bme280,
             "pins": [8, 9], "i2c_address": "0x77"},
        ],
    )
    assert result["failures"] == []
