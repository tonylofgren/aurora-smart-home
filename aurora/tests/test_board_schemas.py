"""Tests that all board profile JSON files conform to the board-profile schema."""
import jsonschema
import pytest


def test_board_schema_loads(board_schema):
    """The board profile schema itself must be valid JSON Schema."""
    jsonschema.Draft202012Validator.check_schema(board_schema)


def test_all_board_profiles_validate(all_board_profiles, board_schema):
    """Every board profile JSON must validate against the schema."""
    if not all_board_profiles:
        pytest.skip("No board profiles found yet")
    validator = jsonschema.Draft202012Validator(board_schema, format_checker=jsonschema.FormatChecker())
    for path, profile in all_board_profiles:
        errors = list(validator.iter_errors(profile))
        assert not errors, f"{path} failed validation: {[e.message for e in errors]}"


def test_invalid_board_profile_is_rejected(board_schema):
    """A board profile missing required fields must fail validation."""
    bad_profile = {"schema_version": "1.0", "board_id": "broken-board"}
    validator = jsonschema.Draft202012Validator(board_schema, format_checker=jsonschema.FormatChecker())
    errors = list(validator.iter_errors(bad_profile))
    assert errors, "Schema accepted a profile that is missing every required field except two"
