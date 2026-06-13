"""Replay test for the DEEP-mode snapshot protocol.

Per-soul snapshot awareness is unit-tested in test_soul_snapshot_awareness.py
(do the souls carry the Iron Law). This test proves the protocol end to end
on a real snapshot: it validates the schema and then "replays" the lifecycle,
asserting the invariants that must hold for a finished DEEP-mode project.

"Replay" here means: walk agents_completed in order and verify the final
snapshot is consistent with each agent only ever touching fields it owns,
that every populated field traces to an agent that actually ran, that the
pipeline drained cleanly, that conflicts were resolved, and that every
referenced artifact exists on disk.

Runs against every examples/**/aurora-project.json, so future DEEP demos
are covered automatically. The shipped subject is examples/deep-mode-co2-demo.
"""
import json
import re
from datetime import datetime
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads(
    (REPO_ROOT / "aurora" / "references" / "schemas" / "project-snapshot.schema.json")
    .read_text(encoding="utf-8")
)
BOARDS_DIR = REPO_ROOT / "aurora" / "references" / "boards"
COMPONENTS_DIR = REPO_ROOT / "aurora" / "references" / "components"

# Which agent is allowed to be the first writer of each optional field.
# If a field is populated, at least one of these agents must have run.
FIELD_PROVENANCE = {
    "selected_board": {"volt"},
    "selected_components": {"volt"},
    "gpio_allocation": {"volt"},
    "esphome_filename": {"volt"},
    "entity_ids_generated": {"volt", "sage", "ada", "mira"},
    "ha_yaml_files": {"sage", "iris", "ada", "mira"},
}

SNAPSHOTS = sorted((REPO_ROOT / "examples").rglob("aurora-project.json"))


def board_ids() -> set[str]:
    return {p.stem for p in BOARDS_DIR.rglob("*.json")}


def component_ids() -> set[str]:
    return {p.stem for p in COMPONENTS_DIR.rglob("*.json")}


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_at_least_one_demo_snapshot_exists():
    assert SNAPSHOTS, "expected at least one examples/**/aurora-project.json demo"


@pytest.mark.parametrize("path", SNAPSHOTS, ids=lambda p: p.parent.name)
class TestSnapshotReplay:
    @pytest.fixture
    def snap(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_validates_against_schema(self, snap):
        jsonschema.validate(snap, SCHEMA)

    def test_pipeline_drained_cleanly(self, snap):
        completed = snap["agents_completed"]
        assert len(completed) == len(set(completed)), "agents_completed has duplicates"
        assert not (set(completed) & set(snap["agents_pending"])), (
            "an agent is in both agents_completed and agents_pending"
        )
        # A snapshot shipped as a demo represents a finished project.
        assert snap["agents_pending"] == [], "demo snapshot should be fully drained"

    def test_every_completed_agent_recorded_a_result(self, snap):
        for agent in snap["agents_completed"]:
            assert agent in snap["validation_results"], (
                f"{agent} is in agents_completed but recorded no validation_results"
            )
            assert "status" in snap["validation_results"][agent]

    def test_no_orphan_validation_results(self, snap):
        for agent in snap["validation_results"]:
            assert agent in snap["agents_completed"], (
                f"validation_results has {agent} but it never appears in agents_completed"
            )

    def test_populated_fields_trace_to_an_agent_that_ran(self, snap):
        completed = set(snap["agents_completed"])
        for field, owners in FIELD_PROVENANCE.items():
            value = snap.get(field)
            populated = bool(value) and value not in (None, [], {})
            if populated:
                assert owners & completed, (
                    f"{field} is populated but none of its possible writers "
                    f"{owners} ran (completed: {completed})"
                )

    def test_conflicts_are_resolved_and_reference_known_agents(self, snap):
        known = set(snap["agents_completed"]) | set(snap["agents_pending"])
        for entry in snap.get("conflict_log", []):
            assert entry["resolution"] and entry["resolved_at"], (
                f"unresolved conflict in a finished project: {entry['message']}"
            )
            assert entry["raised_by"] in known, "conflict raised_by an unknown agent"
            assert entry["blocks_agent"] in known, "conflict blocks an unknown agent"
            assert ts(entry["resolved_at"]) >= ts(entry["raised_at"])

    def test_referential_integrity_of_artifacts(self, snap, path):
        project = path.parent
        if snap.get("esphome_filename"):
            matches = list(project.rglob(snap["esphome_filename"]))
            assert matches, f"esphome_filename {snap['esphome_filename']} not found on disk"
        for rel in snap.get("ha_yaml_files", []):
            assert (project / rel).is_file(), f"ha_yaml_files path missing: {rel}"

    def test_board_and_components_match_profiles(self, snap):
        if snap.get("selected_board"):
            assert snap["selected_board"] in board_ids(), (
                f"selected_board {snap['selected_board']} has no profile"
            )
        for cid in snap.get("selected_components", []):
            assert cid in component_ids(), f"selected_component {cid} has no profile"

    def test_entity_ids_well_formed(self, snap):
        for eid in snap.get("entity_ids_generated", []):
            assert re.match(r"^[a-z_]+\.[a-z0-9_]+$", eid), f"malformed entity_id: {eid}"

    def test_timestamps_are_ordered(self, snap):
        created, updated = ts(snap["created_at"]), ts(snap["updated_at"])
        assert created <= updated
        last = created
        for agent in snap["agents_completed"]:
            done = snap["validation_results"][agent].get("completed_at")
            if done:
                assert created <= ts(done) <= updated, f"{agent} completed_at out of range"
                assert ts(done) >= last, (
                    f"{agent} completed before the previous agent in the pipeline order"
                )
                last = ts(done)
