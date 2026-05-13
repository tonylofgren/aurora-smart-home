"""Data integrity tests for Heltec WiFi LoRa 32 V3 board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "special" / "heltec-wifi-lora32-v3.json"


@pytest.fixture(scope="module")
def heltec():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_heltec_has_lora_radio(heltec):
    """Heltec WiFi LoRa 32 V3 has an SX1262 LoRa transceiver."""
    lora = heltec["wireless"]["lora"]
    assert lora is not None
    assert "SX1262" in lora


def test_heltec_has_ipex_connector(heltec):
    """The LoRa antenna uses an IPEX U.FL connector."""
    assert heltec["form_factor"]["ipex_connector"] is True


def test_heltec_has_battery_support(heltec):
    assert heltec["power"]["battery_connector"] == "JST-PH 2.0"
    assert heltec["power"]["charging_ic"] == "TP4054 LiPo charger"


def test_heltec_has_oled(heltec):
    assert "SSD1306" in heltec["onboard_components"]["display"]
    assert "128x64" in heltec["onboard_components"]["display"]


def test_heltec_warns_about_lora_pin_reservations(heltec):
    warnings_text = " ".join(heltec["limitations"]["strapping_conflict_warnings"])
    assert "LoRa SX1262 reserves" in warnings_text


def test_heltec_warns_about_no_antenna_transmit(heltec):
    """The warning about damaging the PA without antenna must be present."""
    warnings_text = " ".join(heltec["limitations"]["strapping_conflict_warnings"])
    assert "antenna" in warnings_text.lower()
