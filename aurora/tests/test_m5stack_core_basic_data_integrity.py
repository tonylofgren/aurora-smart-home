"""Data integrity tests for M5Stack Core Basic board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "special" / "m5stack-core-basic.json"


@pytest.fixture(scope="module")
def core():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_core_has_320x240_tft(core):
    assert "320x240" in core["onboard_components"]["display"]
    assert "ILI9342C" in core["onboard_components"]["display"]


def test_core_has_imu(core):
    assert "MPU6886" in core["onboard_components"]["imu"]


def test_core_has_speaker_via_dac(core):
    """Core Basic has 1W speaker on GPIO 25 DAC via NS4168."""
    buzzer = core["onboard_components"]["buzzer"]
    assert "1W speaker" in buzzer
    assert "GPIO 25" in buzzer


def test_core_has_internal_battery(core):
    assert core["power"]["battery_connector"] == "Built-in 150mAh LiPo"
    assert core["smart_home_capabilities"]["battery_powered"] is True


def test_core_has_psram_for_voice(core):
    assert core["memory"]["psram_mb"] == 4
    assert core["smart_home_capabilities"]["voice_assistant"] is True


def test_core_is_not_ir_blaster(core):
    """M5Stack Core Basic does not have onboard IR LED (unlike Atom)."""
    assert core["smart_home_capabilities"]["ir_blaster"] is False
