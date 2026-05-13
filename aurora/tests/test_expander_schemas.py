"""Tests that all GPIO expander profile JSON files conform to the expander-profile schema."""
import jsonschema
import pytest


def test_expander_schema_loads(expander_schema):
    """The expander profile schema itself must be valid JSON Schema."""
    jsonschema.Draft202012Validator.check_schema(expander_schema)


def test_all_expander_profiles_validate(all_expander_profiles, expander_schema):
    """Every expander profile JSON must validate against the schema."""
    if not all_expander_profiles:
        pytest.skip("No expander profiles found yet")
    validator = jsonschema.Draft202012Validator(expander_schema, format_checker=jsonschema.FormatChecker())
    for path, profile in all_expander_profiles:
        errors = list(validator.iter_errors(profile))
        assert not errors, f"{path} failed validation: {[e.message for e in errors]}"


def test_invalid_expander_profile_is_rejected(expander_schema):
    """An expander profile missing required fields must fail validation."""
    bad_profile = {"schema_version": "1.0", "expander_id": "broken"}
    validator = jsonschema.Draft202012Validator(expander_schema, format_checker=jsonschema.FormatChecker())
    errors = list(validator.iter_errors(bad_profile))
    assert errors, "Schema accepted a profile that is missing required fields"
