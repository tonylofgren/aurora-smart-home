"""Data integrity tests for LilyGo T-Display S3 board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "special" / "lilygo-t-display-s3.json"


@pytest.fixture(scope="module")
def lilygo():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_lilygo_chip_is_esp32_s3(lilygo):
    assert lilygo["chip"] == "ESP32-S3"


def test_lilygo_has_onboard_tft_display(lilygo):
    display = lilygo["onboard_components"]["display"]
    assert "ST7789" in display
    assert "170x320" in display


def test_lilygo_has_battery_connector(lilygo):
    assert lilygo["power"]["battery_connector"] == "JST-PH 2.0"
    assert lilygo["power"]["vbat_monitor_pin"] == 4


def test_lilygo_has_psram(lilygo):
    """LilyGo T-Display S3 has 8MB OPI PSRAM, enabling voice assistant use cases."""
    assert lilygo["memory"]["psram_mb"] == 8
    assert lilygo["smart_home_capabilities"]["voice_assistant"] is True


def test_lilygo_warns_about_display_reservations(lilygo):
    warnings_text = " ".join(lilygo["limitations"]["strapping_conflict_warnings"])
    assert "Display reserves" in warnings_text


def test_lilygo_valid_pins_exclude_display_pins(lilygo):
    """Display-reserved pins (5,6,7,8,9,13,15,17,18,40,41,42,45,46) should NOT be in valid_pins."""
    valid = set(lilygo["gpio"]["valid_pins"])
    display_reserved = {5, 6, 7, 8, 9, 13, 15, 17, 18, 40, 41, 42, 45, 46}
    overlap = valid & display_reserved
    assert overlap == set(), f"valid_pins must not include display-reserved pins, found: {overlap}"
