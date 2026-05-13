"""Data integrity tests for individual voltage level shifter profiles."""
import json
from pathlib import Path
import pytest

AURORA_ROOT = Path(__file__).resolve().parents[1]
VOLTAGE_SHIFTERS_DIR = AURORA_ROOT / "references" / "voltage-shifters"


def load_shifter(name):
    path = VOLTAGE_SHIFTERS_DIR / f"{name}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def test_txs0108e_is_bidirectional():
    """TXS0108E direction must be bidirectional."""
    profile = load_shifter("txs0108e")
    assert profile["direction"] == "bidirectional"


def test_txs0108e_has_8_channels():
    """TXS0108E must have exactly 8 channels."""
    profile = load_shifter("txs0108e")
    assert profile["channels"] == 8


def test_txs0108e_warns_against_i2c():
    """TXS0108E must flag auto_direction_can_oscillate_on_i2c and prefer_bss138_for_i2c."""
    profile = load_shifter("txs0108e")
    assert profile["limitations"]["auto_direction_can_oscillate_on_i2c"] is True
    assert profile["limitations"]["prefer_bss138_for_i2c"] is True


def test_txs0108e_voltage_a_range():
    """TXS0108E VCCA range must cover 1.4V to 3.6V."""
    profile = load_shifter("txs0108e")
    assert profile["voltage_a_range"] == "1.4V to 3.6V"


def test_bss138_is_bidirectional():
    """BSS138 direction must be bidirectional."""
    profile = load_shifter("bss138")
    assert profile["direction"] == "bidirectional"


def test_bss138_is_single_channel():
    """BSS138 is a single-channel device."""
    profile = load_shifter("bss138")
    assert profile["channels"] == 1


def test_bss138_safe_for_i2c():
    """BSS138 must NOT flag auto_direction_can_oscillate_on_i2c (safe for I2C)."""
    profile = load_shifter("bss138")
    assert profile["limitations"]["auto_direction_can_oscillate_on_i2c"] is False


def test_bss138_voltage_b_range():
    """BSS138 VCCB range must cover 2.0V to 5.5V."""
    profile = load_shifter("bss138")
    assert profile["voltage_b_range"] == "2.0V to 5.5V"
