"""Data integrity tests for Capacitive Soil Moisture v1.2 component profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "components" / "moisture" / "capacitive-soil-v1.2.json"


@pytest.fixture(scope="module")
def soil():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_protocol_is_analog(soil):
    """Capacitive soil sensor outputs an analog voltage — requires ADC."""
    assert soil["protocol"] == "analog"


def test_adc_required(soil):
    """An ADC-capable GPIO is mandatory for this sensor."""
    assert soil["pin_requirements"]["adc_required"] is True


def test_calibration_required(soil):
    """Each sensor unit must be calibrated with dry and wet reference readings."""
    assert soil["calibration"]["required"] is True


def test_calibration_type_is_two_point_dry_wet(soil):
    """Two-point calibration using dry and fully-wet soil references is required."""
    assert soil["calibration"]["type"] == "two_point_dry_wet_reference"


def test_easily_confused_with_v1_0(soil):
    """v1.0/v1.1 knockoffs have corrosion issues; v1.2 can be verified by 555 chip and gold plating."""
    confused = soil["variants"]["easily_confused_with"]
    assert any(c["component_id"] == "capacitive-soil-v10" for c in confused)


def test_knockoffs_known(soil):
    """Knockoff versions of this sensor are widely circulated."""
    assert soil["variants"]["knockoffs_known"] is True
