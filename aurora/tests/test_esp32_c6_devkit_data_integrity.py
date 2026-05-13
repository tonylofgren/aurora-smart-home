"""Domain-specific data integrity tests for the ESP32-C6 board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "esp32" / "esp32-c6-devkit.json"


@pytest.fixture(scope="module")
def c6():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_c6_has_thread_and_zigbee(c6):
    """ESP32-C6 has an 802.15.4 radio, enabling both Thread and Zigbee."""
    assert c6["wireless"]["thread"] is True
    assert c6["wireless"]["zigbee"] is True


def test_c6_supports_matter_device(c6):
    """ESP32-C6 has BLE + Thread + WiFi 6, fully supporting Matter device role."""
    assert c6["smart_home_capabilities"]["matter_device"] is True


def test_c6_supports_zigbee_coordinator(c6):
    """ESP32-C6 802.15.4 radio can act as Zigbee coordinator."""
    assert c6["smart_home_capabilities"]["zigbee_coordinator"] is True


def test_c6_supports_thread_border_router(c6):
    """ESP32-C6 can act as a Thread border router (WiFi + 802.15.4)."""
    assert c6["smart_home_capabilities"]["thread_border_router"] is True


def test_c6_chip_is_riscv_single_core(c6):
    """ESP32-C6 uses a single-core RISC-V architecture."""
    assert c6["chip"] == "ESP32-C6"


def test_c6_wifi6(c6):
    """ESP32-C6 supports WiFi 6 (802.11ax)."""
    assert c6["wireless"]["wifi_standard"] == "WiFi 6 (ax)"


def test_c6_no_dac_no_touch(c6):
    """ESP32-C6 has no DAC and no capacitive touch pins."""
    assert c6["gpio"]["dac_pins"] == []
    assert c6["gpio"]["touch_pins"] == []
    assert c6["limitations"]["no_dac"] is True


def test_c6_bluetooth_proxy_true(c6):
    """BLE 5.0 presence means bluetooth_proxy capability is true."""
    assert c6["smart_home_capabilities"]["bluetooth_proxy"] is True
