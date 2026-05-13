"""Data integrity tests for M5Stack Atom Lite board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "special" / "m5stack-atom-lite.json"


@pytest.fixture(scope="module")
def atom():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_atom_lite_chip_is_pico_d4(atom):
    assert atom["chip"] == "ESP32-PICO-D4"


def test_atom_lite_has_onboard_rgb_led(atom):
    assert atom["onboard_components"]["led_gpio"] == 27
    assert "SK6812" in atom["onboard_components"]["led_type"]


def test_atom_lite_has_ir_blaster_capability(atom):
    """Atom Lite has onboard IR LED on GPIO 12 making it an ideal IR blaster."""
    assert atom["smart_home_capabilities"]["ir_blaster"] is True
    warnings_text = " ".join(atom["limitations"]["strapping_conflict_warnings"])
    assert "IR LED" in warnings_text


def test_atom_lite_has_bluetooth_classic(atom):
    """ESP32-PICO-D4 has Bluetooth Classic (legacy ESP32 chip family)."""
    assert atom["wireless"]["bluetooth_classic"] is True


def test_atom_lite_no_battery_connector(atom):
    """Atom Lite (vs other Atom variants) does not have a battery connector."""
    assert atom["power"]["battery_connector"] is None
    assert atom["smart_home_capabilities"]["battery_powered"] is False


def test_atom_lite_compact_gpio_count(atom):
    """Atom Lite only exposes ~9 GPIO on edge and Grove connectors."""
    assert len(atom["gpio"]["valid_pins"]) <= 10
