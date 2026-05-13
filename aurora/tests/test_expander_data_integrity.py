"""Data integrity tests for individual GPIO expander profiles."""
import json
from pathlib import Path
import pytest

AURORA_ROOT = Path(__file__).resolve().parents[1]
EXPANDERS_DIR = AURORA_ROOT / "references" / "expanders"


def load_expander(name):
    path = EXPANDERS_DIR / f"{name}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def test_pcf8574_is_open_drain_only():
    """PCF8574 must be flagged as open-drain only."""
    profile = load_expander("pcf8574")
    assert profile["limitations"]["open_drain_only"] is True


def test_pcf8574_has_8_channels():
    """PCF8574 must have exactly 8 channels."""
    profile = load_expander("pcf8574")
    assert profile["channels"] == 8


def test_pcf8574_has_interrupt_pin():
    """PCF8574 must advertise an available interrupt pin."""
    profile = load_expander("pcf8574")
    assert profile["limitations"]["interrupt_pin_available"] is True


def test_mcp23017_has_16_channels():
    """MCP23017 must have exactly 16 channels."""
    profile = load_expander("mcp23017")
    assert profile["channels"] == 16


def test_mcp23017_is_not_open_drain_only():
    """MCP23017 supports push-pull, so open_drain_only must be False."""
    profile = load_expander("mcp23017")
    assert profile["limitations"]["open_drain_only"] is False


def test_mcp23017_is_digital_io():
    """MCP23017 channel type must be digital_io."""
    profile = load_expander("mcp23017")
    assert profile["channel_type"] == "digital_io"


def test_pca9685_is_pwm():
    """PCA9685 channel type must be pwm."""
    profile = load_expander("pca9685")
    assert profile["channel_type"] == "pwm"


def test_pca9685_has_16_channels():
    """PCA9685 must have exactly 16 channels."""
    profile = load_expander("pca9685")
    assert profile["channels"] == 16


def test_pca9685_no_interrupt():
    """PCA9685 does not have an interrupt pin."""
    profile = load_expander("pca9685")
    assert profile["limitations"]["interrupt_pin_available"] is False


def test_tca9548a_is_multiplexer():
    """TCA9548A channel type must be i2c_multiplex."""
    profile = load_expander("tca9548a")
    assert profile["channel_type"] == "i2c_multiplex"


def test_tca9548a_has_8_channels():
    """TCA9548A must have exactly 8 downstream bus channels."""
    profile = load_expander("tca9548a")
    assert profile["channels"] == 8


def test_tca9548a_has_8_addresses():
    """TCA9548A must have 8 selectable I2C addresses."""
    profile = load_expander("tca9548a")
    assert len(profile["i2c"]["default_addresses"]) == 8
