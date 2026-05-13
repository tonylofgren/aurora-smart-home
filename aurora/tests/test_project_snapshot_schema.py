"""Tests for the project snapshot schema and example snapshots."""
import copy
import json
from pathlib import Path

import jsonschema
import pytest

AURORA_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = AURORA_ROOT / "references" / "schemas" / "project-snapshot.schema.json"
HANDOFF_DIR = AURORA_ROOT / "references" / "handoff"
EXAMPLES_DIR = HANDOFF_DIR / "examples"


@pytest.fixture(scope="module")
def snapshot_schema():
    with SCHEMA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def validator(snapshot_schema):
    return jsonschema.Draft202012Validator(
        snapshot_schema,
        format_checker=jsonschema.FormatChecker(),
    )


@pytest.fixture(scope="module")
def example_snapshots():
    snapshots = []
    if EXAMPLES_DIR.exists():
        for path in sorted(EXAMPLES_DIR.glob("*.json")):
            with path.open(encoding="utf-8") as f:
                snapshots.append((path.name, json.load(f)))
    return snapshots


def test_snapshot_schema_loads_and_is_valid(snapshot_schema):
    """The schema itself must be valid JSON Schema Draft 2020-12."""
    jsonschema.Draft202012Validator.check_schema(snapshot_schema)


def test_protocol_doc_exists():
    """The hand-off protocol document must ship alongside the schema."""
    protocol_path = HANDOFF_DIR / "_protocol.md"
    assert protocol_path.is_file(), (
        f"Hand-off protocol doc missing at {protocol_path}. "
        "The schema is meaningless without the protocol that explains how to use it."
    )


def test_at_least_one_example_ships(example_snapshots):
    """Phase 1 requires at least one runnable example snapshot."""
    assert example_snapshots, (
        "No example snapshots found under references/handoff/examples/. "
        "An unverifiable schema is not a deliverable."
    )


def test_all_example_snapshots_validate(example_snapshots, validator):
    """Every example snapshot must pass schema validation."""
    if not example_snapshots:
        pytest.skip("No example snapshots to validate")
    for name, snapshot in example_snapshots:
        errors = list(validator.iter_errors(snapshot))
        assert not errors, (
            f"{name} failed validation: {[e.message for e in errors]}"
        )


def test_snapshot_missing_required_field_is_rejected(validator):
    """A snapshot missing core required fields must fail validation."""
    bad = {"schema_version": "1.0"}
    errors = list(validator.iter_errors(bad))
    assert errors, "Schema accepted a snapshot missing every required field except one"


def test_unknown_top_level_field_is_rejected(validator):
    """The schema must reject unknown top-level fields (additionalProperties: false)."""
    bad = _minimal_valid_snapshot()
    bad["surprise_field"] = "should not be allowed"
    errors = list(validator.iter_errors(bad))
    assert errors, "Schema accepted an unknown top-level field"


def test_invalid_project_id_is_rejected(validator):
    """project_id must be a UUID."""
    bad = _minimal_valid_snapshot()
    bad["project_id"] = "not-a-uuid"
    errors = list(validator.iter_errors(bad))
    assert errors, "Schema accepted a non-UUID project_id"


def test_invalid_entity_id_is_rejected(validator):
    """entity_ids_generated entries must match HA entity_id format domain.object_id."""
    bad = _minimal_valid_snapshot()
    bad["entity_ids_generated"] = ["MissingDomain"]
    errors = list(validator.iter_errors(bad))
    assert errors, "Schema accepted an entity_id without a domain prefix"


def test_validation_status_must_be_in_enum(validator):
    """validation_results[<agent>].status must be one of the documented values."""
    bad = _minimal_valid_snapshot()
    bad["validation_results"]["volt"] = {"status": "kind-of-passed"}
    errors = list(validator.iter_errors(bad))
    assert errors, "Schema accepted an out-of-enum validation status"


def test_conflict_log_entry_requires_core_fields(validator):
    """A conflict_log entry without raised_by/blocks_agent/message/raised_at must fail."""
    bad = _minimal_valid_snapshot()
    bad["conflict_log"] = [{"raised_by": "vera"}]
    errors = list(validator.iter_errors(bad))
    assert errors, "Schema accepted a conflict_log entry missing required fields"


def test_minimal_valid_snapshot_passes(validator):
    """The helper baseline must itself validate, otherwise the negative tests are unreliable."""
    snapshot = _minimal_valid_snapshot()
    errors = list(validator.iter_errors(snapshot))
    assert not errors, (
        f"Minimal valid snapshot should pass but did not: {[e.message for e in errors]}"
    )


def test_example_living_room_sensor_demonstrates_full_workflow(example_snapshots):
    """The shipped example must demonstrate a multi-agent workflow, otherwise the
    protocol is not visibly exercised."""
    examples = dict(example_snapshots)
    assert "living-room-sensor.json" in examples, (
        "living-room-sensor.json missing from examples"
    )
    snapshot = examples["living-room-sensor.json"]
    assert len(snapshot["agents_completed"]) >= 2, (
        "The flagship example should show at least 2 agents having completed work"
    )
    assert snapshot["validation_results"], (
        "The flagship example should record validation_results entries"
    )


def _minimal_valid_snapshot():
    """A baseline snapshot used by negative tests. Mutated copies should fail; the
    baseline itself must pass (verified by test_minimal_valid_snapshot_passes)."""
    return copy.deepcopy({
        "schema_version": "1.0",
        "project_id": "00000000-0000-4000-8000-000000000000",
        "project_name": "Test project",
        "created_at": "2026-05-13T22:00:00Z",
        "updated_at": "2026-05-13T22:00:00Z",
        "current_agent": "volt",
        "agents_completed": [],
        "agents_pending": ["volt"],
        "user_requirements": ["Build something"],
        "validation_results": {
            "volt": {"status": "pending"}
        }
    })
