"""Tests that all component profile JSON files conform to the component-profile schema."""
import jsonschema
import pytest


def test_component_schema_loads(component_schema):
    """The component profile schema itself must be valid JSON Schema."""
    jsonschema.Draft202012Validator.check_schema(component_schema)


def test_all_component_profiles_validate(all_component_profiles, component_schema):
    """Every component profile JSON must validate against the schema."""
    if not all_component_profiles:
        pytest.skip("No component profiles found yet")
    validator = jsonschema.Draft202012Validator(component_schema, format_checker=jsonschema.FormatChecker())
    for path, profile in all_component_profiles:
        errors = list(validator.iter_errors(profile))
        assert not errors, f"{path} failed validation: {[e.message for e in errors]}"


def test_invalid_component_profile_is_rejected(component_schema):
    """A component profile missing required fields must fail validation."""
    bad_profile = {"schema_version": "1.0", "component_id": "broken"}
    validator = jsonschema.Draft202012Validator(component_schema, format_checker=jsonschema.FormatChecker())
    errors = list(validator.iter_errors(bad_profile))
    assert errors, "Schema accepted a profile that is missing required fields"
