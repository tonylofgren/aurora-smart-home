"""Tests that all voltage shifter profile JSON files conform to the voltage-shifter schema."""
import jsonschema
import pytest


def test_voltage_shifter_schema_loads(voltage_shifter_schema):
    """The voltage shifter profile schema itself must be valid JSON Schema."""
    jsonschema.Draft202012Validator.check_schema(voltage_shifter_schema)


def test_all_voltage_shifter_profiles_validate(all_voltage_shifter_profiles, voltage_shifter_schema):
    """Every voltage shifter profile JSON must validate against the schema."""
    if not all_voltage_shifter_profiles:
        pytest.skip("No voltage shifter profiles found yet")
    validator = jsonschema.Draft202012Validator(voltage_shifter_schema, format_checker=jsonschema.FormatChecker())
    for path, profile in all_voltage_shifter_profiles:
        errors = list(validator.iter_errors(profile))
        assert not errors, f"{path} failed validation: {[e.message for e in errors]}"


def test_invalid_voltage_shifter_profile_is_rejected(voltage_shifter_schema):
    """A voltage shifter profile missing required fields must fail validation."""
    bad_profile = {"schema_version": "1.0", "shifter_id": "broken"}
    validator = jsonschema.Draft202012Validator(voltage_shifter_schema, format_checker=jsonschema.FormatChecker())
    errors = list(validator.iter_errors(bad_profile))
    assert errors, "Schema accepted a profile that is missing required fields"
