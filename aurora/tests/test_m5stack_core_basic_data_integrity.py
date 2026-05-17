"""Data integrity tests for M5Stack Core Basic board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "special" / "m5stack-core-basic.json"


@pytest.fixture(scope="module")
def core():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_core_chip_is_esp32(core):
    assert "ESP32" in core["chip"]


def test_core_board_type_is_specialty(core):
    assert core["board_type"] == "specialty_board"


def test_core_esphome_board_id_present(core):
    assert core["esphome"]["board"] is not None


def test_core_has_onboard_display(core):
    assert core["onboard_components"]["display"] is not None, "M5Stack Core Basic has a built-in display"


def test_core_lifecycle_active(core):
    assert core["lifecycle"]["status"] == "active"
