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
    validator = jsonschema.Draft202012Validator(board_schema)
    for path, profile in all_board_profiles:
        errors = list(validator.iter_errors(profile))
        assert not errors, f"{path} failed validation: {[e.message for e in errors]}"
