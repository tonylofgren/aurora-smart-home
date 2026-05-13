"""Domain-specific data integrity tests for the ESP32-C3 Super Mini board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "esp32" / "esp32-c3-mini.json"


@pytest.fixture(scope="module")
def c3():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_c3_is_riscv_single_core(c3):
    """ESP32-C3 uses a RISC-V core, not Xtensa."""
    assert c3["chip"] == "ESP32-C3"


def test_c3_has_ble_no_bt_classic(c3):
    """ESP32-C3 has BLE 5.0 but no Bluetooth Classic."""
    assert c3["wireless"]["bluetooth"] == "BLE 5.0"
    assert c3["wireless"]["bluetooth_classic"] is False


def test_c3_no_thread_no_zigbee(c3):
    """ESP32-C3 has no 802.15.4 radio."""
    assert c3["wireless"]["thread"] is False
    assert c3["wireless"]["zigbee"] is False


def test_c3_no_dac_no_touch(c3):
    """ESP32-C3 has no DAC and no capacitive touch pins."""
    assert c3["gpio"]["dac_pins"] == []
    assert c3["gpio"]["touch_pins"] == []
    assert c3["limitations"]["no_dac"] is True


def test_c3_bluetooth_proxy_and_matter_controller(c3):
    """C3 has BLE, so bluetooth_proxy and matter_controller must be true."""
    caps = c3["smart_home_capabilities"]
    assert caps["bluetooth_proxy"] is True
    assert caps["matter_controller"] is True


def test_c3_voice_assistant_false(c3):
    """Single-core C3 with limited RAM is insufficient for voice assistant."""
    assert c3["smart_home_capabilities"]["voice_assistant"] is False


def test_c3_flash_reserved_11_to_17(c3):
    """GPIO 11-17 are reserved for internal SPI flash on ESP32-C3."""
    flash_reserved = set(c3["gpio"]["reserved_for_flash"])
    assert {11, 12, 13, 14, 15, 16, 17}.issubset(flash_reserved)


def test_c3_gpio_max_21(c3):
    """ESP32-C3 valid GPIO stops at 21, no GPIO 22+ exposed."""
    valid = c3["gpio"]["valid_pins"]
    assert all(pin <= 21 for pin in valid)
