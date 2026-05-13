"""Tests that aurora/SKILL.md documents the DEEP-mode hand-off contract.

If these break, the orchestrator side of cross-agent coordination has lost
the wiring that makes the snapshot protocol actually fire. Without these
instructions in SKILL.md, the Iron Law in specialist souls would always hit
its 'no snapshot found' fallback and the protocol would be dead code.
"""
import re
from pathlib import Path

import pytest

AURORA_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = AURORA_ROOT / "SKILL.md"
PROTOCOL_PATH = AURORA_ROOT / "references" / "handoff" / "_protocol.md"
SCHEMA_PATH = AURORA_ROOT / "references" / "schemas" / "project-snapshot.schema.json"


@pytest.fixture(scope="module")
def skill_md_text():
    return SKILL_PATH.read_text(encoding="utf-8")


def test_skill_md_exists():
    assert SKILL_PATH.is_file(), f"SKILL.md missing at {SKILL_PATH}"


def test_skill_md_has_deep_mode_handoff_section(skill_md_text):
    """SKILL.md must have a dedicated DEEP-mode hand-off section."""
    assert re.search(r"##\s+Step\s+7:\s+DEEP\s+Mode\s+Hand", skill_md_text, re.IGNORECASE), (
        "SKILL.md is missing the 'Step 7: DEEP Mode Hand-Off' section. "
        "Without it the orchestrator has no instructions to create the project "
        "snapshot that specialists rely on."
    )


def test_skill_md_references_protocol_doc(skill_md_text):
    """SKILL.md must point at the protocol doc so the orchestrator knows
    where to find the per-field ownership table and lifecycle rules."""
    assert "aurora/references/handoff/_protocol.md" in skill_md_text, (
        "SKILL.md does not link to the hand-off protocol document."
    )


def test_skill_md_references_snapshot_schema(skill_md_text):
    """SKILL.md must point at the snapshot JSON Schema for validation."""
    assert "project-snapshot.schema.json" in skill_md_text, (
        "SKILL.md does not link to the project-snapshot schema."
    )


def test_skill_md_names_default_snapshot_file(skill_md_text):
    """SKILL.md must document the default snapshot filename so every
    orchestrator turn writes to the same place."""
    assert "aurora-project.json" in skill_md_text, (
        "SKILL.md does not document the default snapshot file path "
        "(aurora-project.json at the project root)."
    )


def test_skill_md_lists_required_initial_fields(skill_md_text):
    """The orchestrator instructions must enumerate the fields that need
    to be populated on snapshot creation, otherwise the resulting file
    may fail schema validation on the very first turn."""
    required_field_mentions = [
        "schema_version",
        "project_id",
        "project_name",
        "created_at",
        "updated_at",
        "current_agent",
        "agents_completed",
        "agents_pending",
        "user_requirements",
        "validation_results",
    ]
    missing = [f for f in required_field_mentions if f not in skill_md_text]
    assert not missing, (
        f"Step 7 instructions do not mention required snapshot fields: {missing}. "
        "If the orchestrator omits any of these, the file will fail schema validation."
    )


def test_skill_md_documents_per_field_ownership(skill_md_text):
    """The orchestrator must be told not to overwrite specialist-owned fields."""
    assert re.search(r"per-field\s+ownership", skill_md_text, re.IGNORECASE), (
        "Step 7 does not mention per-field ownership, which means the "
        "orchestrator could overwrite specialist data."
    )


def test_skill_md_documents_conflict_handling(skill_md_text):
    """Conflict handling must be documented so DEEP mode does not silently
    complete with unresolved conflicts."""
    text_lower = skill_md_text.lower()
    assert "conflict_log" in text_lower, (
        "Step 7 does not reference conflict_log — DEEP mode could "
        "complete with unresolved conflicts."
    )
    assert "resolution" in text_lower, (
        "Step 7 does not document the resolution flow for conflicts."
    )


def test_skill_md_says_quick_mode_skips_snapshot(skill_md_text):
    """QUICK mode (single agent) should NOT create a snapshot — otherwise
    every trivial request gets an aurora-project.json artifact it does not need."""
    assert re.search(
        r"QUICK\s+mode\s+does\s+NOT\s+use\s+snapshots",
        skill_md_text,
        re.IGNORECASE,
    ), (
        "Step 7 does not explicitly exempt QUICK mode from snapshot creation. "
        "Without that, the orchestrator may write a snapshot for every single-agent task."
    )


def test_protocol_doc_and_schema_referenced_in_reference_data_section(skill_md_text):
    """The Reference Data section must register handoff/ as an authoritative
    resource alongside boards/, components/, schemas/, validators/."""
    ref_data_match = re.search(
        r"##\s+Reference\s+Data.*?(?=^##\s|\Z)",
        skill_md_text,
        re.DOTALL | re.MULTILINE,
    )
    assert ref_data_match, "Reference Data section missing from SKILL.md"
    ref_data_block = ref_data_match.group(0)
    assert "handoff" in ref_data_block.lower(), (
        "Reference Data section does not list aurora/references/handoff/. "
        "Specialists looking for the protocol via the Reference Data section will miss it."
    )


def test_protocol_doc_and_schema_exist_for_skill_md_to_reference():
    """If SKILL.md references the protocol doc and schema, those files must exist."""
    assert PROTOCOL_PATH.is_file(), f"Protocol doc missing at {PROTOCOL_PATH}"
    assert SCHEMA_PATH.is_file(), f"Snapshot schema missing at {SCHEMA_PATH}"
