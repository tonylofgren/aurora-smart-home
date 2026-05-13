"""Domain-specific data integrity tests for the ESP32-H2 DevKit board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "esp32" / "esp32-h2-devkit.json"


@pytest.fixture(scope="module")
def h2():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_h2_has_no_wifi(h2):
    """ESP32-H2 has no WiFi radio. The wifi array must be empty."""
    assert h2["wireless"]["wifi"] == []


def test_h2_has_thread_and_zigbee(h2):
    """ESP32-H2 supports 802.15.4 protocols: Thread and Zigbee."""
    assert h2["wireless"]["thread"] is True
    assert h2["wireless"]["zigbee"] is True


def test_h2_has_ble_5(h2):
    """ESP32-H2 has BLE 5.0."""
    assert h2["wireless"]["bluetooth"] == "BLE 5.0"
    assert h2["wireless"]["bluetooth_classic"] is False


def test_h2_supports_zigbee_coordinator_and_thread_border_router(h2):
    """ESP32-H2 is the canonical Thread/Zigbee chip."""
    caps = h2["smart_home_capabilities"]
    assert caps["zigbee_coordinator"] is True
    assert caps["thread_border_router"] is True


def test_h2_does_not_support_voice_assistant(h2):
    """ESP32-H2 lacks the PSRAM and core count for voice assistant pipelines."""
    assert h2["smart_home_capabilities"]["voice_assistant"] is False


def test_h2_chip_is_riscv_single_core(h2):
    assert h2["chip"] == "ESP32-H2"


def test_h2_no_dac_no_touch(h2):
    assert h2["limitations"]["no_dac"] is True
    assert h2["gpio"]["dac_pins"] == []
    assert h2["gpio"]["touch_pins"] == []


def test_h2_warns_about_no_wifi(h2):
    """The strapping warnings list must mention the no-WiFi limitation."""
    warnings_text = " ".join(h2["limitations"]["strapping_conflict_warnings"])
    assert "no WiFi" in warnings_text or "no wifi" in warnings_text.lower()
