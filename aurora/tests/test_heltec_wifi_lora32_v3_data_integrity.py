"""Data integrity tests for Heltec WiFi LoRa32 v3 board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "special" / "heltec-wifi-lora32-v3.json"


@pytest.fixture(scope="module")
def heltec():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_heltec_chip_is_esp32(heltec):
    assert "ESP32" in heltec["chip"]


def test_heltec_board_type_is_specialty(heltec):
    assert heltec["board_type"] == "specialty_board"


def test_heltec_has_lora(heltec):
    assert heltec["wireless"]["lora"] is not None, "LoRa radio must be documented"


def test_heltec_esphome_board_id_present(heltec):
    assert heltec["esphome"]["board"] is not None, "esphome.board must be set for specialty boards"


def test_heltec_lifecycle_active(heltec):
    assert heltec["lifecycle"]["status"] == "active"
