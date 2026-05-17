"""Data integrity tests for M5Stack Atom Lite board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "special" / "m5stack-atom-lite.json"


@pytest.fixture(scope="module")
def atom():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_atom_chip_is_esp32(atom):
    assert "ESP32" in atom["chip"]


def test_atom_board_type_is_specialty(atom):
    assert atom["board_type"] == "specialty_board"


def test_atom_esphome_board_id_present(atom):
    assert atom["esphome"]["board"] is not None


def test_atom_has_bluetooth_proxy(atom):
    assert atom["smart_home_capabilities"]["bluetooth_proxy"] is True


def test_atom_lifecycle_active(atom):
    assert atom["lifecycle"]["status"] == "active"
