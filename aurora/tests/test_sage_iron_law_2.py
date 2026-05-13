"""Contract tests for Sage's Iron Law 2 (Validate Before Generating).

Sage is the second specialist to gain a per-agent validation Iron Law
(after Volt's Iron Law 6). The pattern mirrors Volt: name the shipped
validators, document the failure path, document the graceful fallback
when reference data is missing. These tests assert that wiring stays
intact across future edits.
"""
import re
from pathlib import Path

import pytest

AURORA_ROOT = Path(__file__).resolve().parents[1]
SAGE_SOUL_PATH = AURORA_ROOT / "souls" / "sage.md"


@pytest.fixture(scope="module")
def sage_text():
    assert SAGE_SOUL_PATH.is_file(), f"sage.md missing at {SAGE_SOUL_PATH}"
    return SAGE_SOUL_PATH.read_text(encoding="utf-8")


def test_sage_has_iron_law_2(sage_text):
    """Iron Law 2 must be present with the 'Validate Before Generating' label."""
    assert re.search(
        r"\*\*Iron\s+Law\s+2\s+—\s+Validate\s+Before\s+Generating", sage_text
    ), (
        "sage.md does not declare 'Iron Law 2 — Validate Before Generating'. "
        "Without it Sage has no contract to run the entity-id and secrets "
        "validators before delivering YAML."
    )


def test_sage_iron_law_2_invokes_entity_id_validator(sage_text):
    """Sage references entity IDs in triggers, conditions, and actions, so
    its validation Iron Law MUST invoke entity-id-validator in consumer mode."""
    assert "entity-id-validator" in sage_text, (
        "sage.md does not invoke entity-id-validator. Without it, Sage can "
        "reference entity IDs that do not exist in the snapshot."
    )
    text_lower = sage_text.lower()
    assert "consumer mode" in text_lower, (
        "sage.md does not specify consumer mode for entity-id-validator. "
        "Sage references existing IDs, it does not produce them on its own."
    )


def test_sage_iron_law_2_invokes_secrets_validator(sage_text):
    """Sage generates YAML with notify integrations, webhook secrets, and
    other credential-bearing keys, so the secrets-validator MUST be invoked."""
    assert "secrets-validator" in sage_text, (
        "sage.md does not invoke secrets-validator. Sage commonly writes "
        "notify integrations, webhook triggers, and rest service configs "
        "that carry credentials — literal values can leak without the check."
    )


def test_sage_iron_law_2_documents_quick_fallback(sage_text):
    """QUICK mode has no snapshot; the entity-id existence check must have
    a documented fallback so single-agent invocations do not crash."""
    text_lower = sage_text.lower()
    assert "quick mode" in text_lower, (
        "sage.md Iron Law 2 does not address QUICK mode. The entity-id "
        "consumer-mode check would have no fallback path."
    )
    assert re.search(
        r"(warning|fallback|flag|cannot verify)",
        text_lower,
    ), (
        "sage.md Iron Law 2 does not document the QUICK-mode behavior "
        "(graceful warning rather than failure)."
    )


def test_sage_iron_law_2_documents_failure_behaviour(sage_text):
    """Failures must block delivery, not be silently ignored or rationalised."""
    text_lower = sage_text.lower()
    assert re.search(r"(do\s+not\s+deliver|block\s+delivery)", text_lower), (
        "sage.md Iron Law 2 does not explicitly say validator failures block "
        "YAML delivery. Sage might still ship offending output."
    )


def test_sage_iron_law_2_notes_missing_yaml_syntax_validator(sage_text):
    """yaml-syntax and version validators are spec'd in Plan 5 §3.14 but
    not yet shipped. Iron Law 2 must acknowledge them as planned so a
    future edit does not 'fix' the missing reference by deleting the note."""
    text_lower = sage_text.lower()
    assert re.search(r"yaml-syntax", text_lower), (
        "sage.md Iron Law 2 does not mention yaml-syntax as a planned "
        "future validator. The roadmap context will be lost."
    )


def test_sage_iron_law_2_handles_producer_mode_for_helpers(sage_text):
    """Sage produces helper entity IDs (input_boolean, template sensors).
    The Iron Law must invoke entity-id-validator in producer mode for
    helpers it creates."""
    text_lower = sage_text.lower()
    assert "producer mode" in text_lower, (
        "sage.md Iron Law 2 does not invoke entity-id-validator in producer "
        "mode for Sage-created helpers. Helper IDs added to the snapshot "
        "would not be format-checked."
    )


def test_sage_iron_law_1_still_present(sage_text):
    """Adding Iron Law 2 must not remove Iron Law 1 (snapshot awareness)."""
    assert re.search(r"\*\*Iron\s+Law\s+1\s+—\s+Snapshot-Aware", sage_text), (
        "sage.md is missing Iron Law 1 (Snapshot-Aware Coordination). "
        "Adding Law 2 should not have displaced Law 1."
    )


def test_sage_iron_laws_are_unique(sage_text):
    """Each Iron Law label should appear exactly once."""
    for n in (1, 2):
        pattern = rf"\*\*Iron\s+Law\s+{n}\s+—"
        count = len(re.findall(pattern, sage_text))
        assert count == 1, (
            f"sage.md declares 'Iron Law {n}' {count} times; expected 1."
        )
