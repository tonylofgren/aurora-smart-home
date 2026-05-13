"""Data integrity tests for PIR AM312 motion sensor component profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "components" / "motion" / "pir-am312.json"


@pytest.fixture(scope="module")
def pir_am312():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_protocol_is_digital_io(pir_am312):
    """AM312 outputs a simple digital HIGH/LOW signal — no UART or I2C."""
    assert pir_am312["protocol"] == "digital_io"


def test_type_is_motion(pir_am312):
    """AM312 is a passive infrared motion detector."""
    assert pir_am312["type"] == "motion"


def test_requires_one_pin(pir_am312):
    """AM312 only needs one GPIO pin for the digital output."""
    assert pir_am312["pin_requirements"]["count"] == 1


def test_no_calibration_required(pir_am312):
    """AM312 has no user calibration procedure."""
    assert pir_am312["calibration"]["required"] is False


def test_input_only_pin_acceptable(pir_am312):
    """AM312 output is read-only; an input-only GPIO is sufficient."""
    assert pir_am312["pin_requirements"]["input_only_ok"] is True


def test_easily_confused_with_hc_sr501(pir_am312):
    """HC-SR501 is the common larger PIR; AM312 is compact and 3.3V native."""
    confused = pir_am312["variants"]["easily_confused_with"]
    assert any(c["component_id"] == "hc-sr501" for c in confused)
