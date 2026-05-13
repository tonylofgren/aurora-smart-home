"""Data integrity tests for LD2410 mmWave presence radar component profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "components" / "motion" / "ld2410.json"


@pytest.fixture(scope="module")
def ld2410():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_protocol_is_uart(ld2410):
    """LD2410 communicates over UART — unlike PIR sensors which use digital_io."""
    assert ld2410["protocol"] == "uart"


def test_type_is_presence_radar(ld2410):
    """LD2410 detects sub-mm presence (breathing/micro-movement), not just motion."""
    assert ld2410["type"] == "presence_radar"


def test_requires_two_pins(ld2410):
    """UART requires TX and RX pins."""
    assert ld2410["pin_requirements"]["count"] == 2


def test_no_calibration_required(ld2410):
    """LD2410 works out of the box; configuration is optional via Bluetooth/UART commands."""
    assert ld2410["calibration"]["required"] is False


def test_esphome_platform_min_version_2023_11(ld2410):
    """Built-in ESPHome ld2410 platform was added in 2023.11.0."""
    assert ld2410["esphome"]["platform"] == "ld2410"
    assert ld2410["esphome"]["min_version"] == "2023.11.0"


def test_detection_range_up_to_5m(ld2410):
    """LD2410 has a maximum detection range of 5 meters."""
    assert ld2410["limitations"]["detection_range_m"] == 5
