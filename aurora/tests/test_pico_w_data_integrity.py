"""Data integrity tests for Raspberry Pi Pico W and Pico 2 W board profiles."""
import json
from pathlib import Path
import pytest

PICO_W_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "rp" / "pico-w.json"
PICO_2W_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "rp" / "pico-2-w.json"


@pytest.fixture(scope="module")
def pico_w():
    with PICO_W_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def pico_2w():
    with PICO_2W_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_pico_w_chip_is_rp2040(pico_w):
    assert pico_w["chip"] == "RP2040"


def test_pico_2w_chip_is_rp2350(pico_2w):
    assert pico_2w["chip"] == "RP2350"


def test_both_use_cyw43439_wifi(pico_w, pico_2w):
    """Both Pico W variants share the same CYW43439 WiFi/BLE chip."""
    assert "CYW43439" in pico_w["wireless"]["bluetooth"]
    assert "CYW43439" in pico_2w["wireless"]["bluetooth"]


def test_both_lack_thread_and_zigbee(pico_w, pico_2w):
    """Neither Pico has 802.15.4 radio."""
    for pico in (pico_w, pico_2w):
        assert pico["wireless"]["thread"] is False
        assert pico["wireless"]["zigbee"] is False


def test_pico_w_is_active(pico_w):
    """Pico W has stable ESPHome support."""
    assert pico_w["lifecycle"]["status"] == "active"


def test_pico_2w_is_experimental(pico_2w):
    """Pico 2 W has only preliminary ESPHome support."""
    assert pico_2w["lifecycle"]["status"] == "experimental"


def test_both_use_rp2040_platform(pico_w, pico_2w):
    """ESPHome groups RP2350 under the rp2040 platform name."""
    assert pico_w["esphome"]["platform"] == "rp2040"
    assert pico_2w["esphome"]["platform"] == "rp2040"


def test_pico_2w_has_more_ram_than_pico_w(pico_w, pico_2w):
    """RP2350 has 520KB RAM vs RP2040's 264KB."""
    assert pico_2w["memory"]["ram_kb"] > pico_w["memory"]["ram_kb"]


def test_both_have_3_adc_channels(pico_w, pico_2w):
    """Both expose GPIO 26-28 as ADC channels."""
    for pico in (pico_w, pico_2w):
        assert set(pico["gpio"]["adc1_pins"]) == {26, 27, 28}


def test_both_have_high_deep_sleep_current(pico_w, pico_2w):
    """Both Pico W variants have higher deep sleep current than ESP32 due to CYW43439."""
    for pico in (pico_w, pico_2w):
        assert pico["power"]["deep_sleep_current_ua"] >= 1000
