"""Contract tests for aurora/references/validators/entity-id-validator.md.

These do NOT execute the validator (the validator is a markdown spec that
agents read and apply, not a Python module). They assert that the doc
contains the contract the agents rely on: the two modes, the format check,
the snapshot integration, and the QUICK fallback. If a future edit removes
or weakens any of those, agents will silently lose the ability to validate
entity IDs and the snapshot system stops being load-bearing.
"""
import re
from pathlib import Path

import pytest

AURORA_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = AURORA_ROOT / "references" / "validators" / "entity-id-validator.md"
VOLT_SOUL_PATH = AURORA_ROOT / "souls" / "volt.md"


@pytest.fixture(scope="module")
def doc_text():
    assert VALIDATOR_PATH.is_file(), (
        f"entity-id-validator.md missing at {VALIDATOR_PATH}"
    )
    return VALIDATOR_PATH.read_text(encoding="utf-8")


def test_doc_has_title(doc_text):
    """The validator must declare itself with a clear h1."""
    assert re.search(r"^#\s+Entity\s+ID\s+Validator", doc_text, re.MULTILINE), (
        "entity-id-validator.md does not start with '# Entity ID Validator'."
    )


def test_doc_has_required_sections(doc_text):
    """Match the structure used by pin-validator.md and conflict-validator.md
    so agents that consume validator docs see a consistent shape."""
    required_sections = ["When to Run", "Inputs", "Checks", "Output", "Examples"]
    missing = [
        s for s in required_sections
        if not re.search(rf"^##\s+{re.escape(s)}", doc_text, re.MULTILINE)
    ]
    assert not missing, (
        f"entity-id-validator.md is missing required sections: {missing}. "
        "Other validator docs follow the same structure — keep them aligned."
    )


def test_doc_documents_both_modes(doc_text):
    """Producer mode (Volt/Ada/Sage creating IDs) and consumer mode
    (Sage/Iris/Mira/River referencing IDs) must both be specified."""
    text_lower = doc_text.lower()
    assert "producer mode" in text_lower, (
        "Producer mode is not documented; agents that own entity_ids_generated "
        "will not know how to validate IDs they create."
    )
    assert "consumer mode" in text_lower, (
        "Consumer mode is not documented; downstream agents will not know "
        "how to validate IDs they reference."
    )


def test_doc_specifies_format_regex(doc_text):
    """A concrete regex must be present so the format check is unambiguous.
    Look for the characteristic shape of an entity-id regex: anchored
    `^[a-z...` at the start, a literal dot in the middle, anchored `...$`
    at the end."""
    pattern = re.compile(r"`\^\[a-z[^`]+\$`")
    assert pattern.search(doc_text), (
        "entity-id-validator.md must specify the exact regex for valid IDs "
        "(starting with ^[a-z, ending with $, wrapped in backticks). Without "
        "a concrete regex, every agent will invent its own validation rule."
    )


def test_doc_references_snapshot_entity_ids_field(doc_text):
    """The validator must hook into the snapshot's entity_ids_generated field
    — that is what makes Phase 1's snapshot system load-bearing."""
    assert "entity_ids_generated" in doc_text, (
        "entity-id-validator.md does not reference the snapshot's "
        "entity_ids_generated field; the consumer-mode existence check has "
        "nothing to validate against."
    )


def test_doc_documents_quick_mode_fallback(doc_text):
    """Single-agent (QUICK) tasks have no snapshot. The validator must say
    what to do then, so consumer-mode calls don't crash on a null snapshot."""
    text_lower = doc_text.lower()
    assert "quick" in text_lower, (
        "entity-id-validator.md does not address QUICK mode (no snapshot). "
        "Consumer-mode invocations would have no fallback."
    )
    assert re.search(
        r"(skip|warning|cannot verify|null|missing)",
        text_lower,
    ), (
        "entity-id-validator.md does not document the QUICK-mode behavior "
        "for the consumer-mode existence check."
    )


def test_doc_names_authorized_producer_agents(doc_text):
    """The ownership check must enumerate which agents are allowed to produce
    entity IDs (Volt, Ada, Sage), so unauthorized writes get blocked."""
    for agent in ("volt", "ada", "sage"):
        assert re.search(rf"\b{agent}\b", doc_text, re.IGNORECASE), (
            f"entity-id-validator.md does not mention '{agent}' in the "
            f"producer-ownership context."
        )


def test_doc_includes_at_least_one_failure_and_one_success_example(doc_text):
    """Examples make the contract concrete. Need at least one failing example
    so agents see what failure output looks like, and one passing example
    so they know what success looks like."""
    examples_block_match = re.search(
        r"##\s+Examples(.+)$",
        doc_text,
        re.DOTALL,
    )
    assert examples_block_match, "Examples section missing"
    examples = examples_block_match.group(1)
    assert re.search(r"Failures:\s*\n\s*-", examples), (
        "Examples section has no failing example. Agents will not know what "
        "a failure looks like."
    )
    assert re.search(r"Failures:\s*\[\]", examples), (
        "Examples section has no passing example. Agents will not know what "
        "a clean validation looks like."
    )


def test_volt_iron_law_6_references_entity_id_validator():
    """Volt produces sensor entity IDs, so its Iron Law 6 must point at the
    entity-id-validator. Without this reference Volt will not invoke the
    validator when generating IDs, and the snapshot may accumulate
    malformed entries."""
    volt_text = VOLT_SOUL_PATH.read_text(encoding="utf-8")
    assert "entity-id-validator" in volt_text, (
        "volt.md does not reference entity-id-validator. Volt owns sensor "
        "entity IDs in entity_ids_generated; without invoking the validator "
        "in producer mode, malformed or duplicate IDs can land in the snapshot."
    )


def test_doc_uses_lowercase_snake_case_phrasing(doc_text):
    """Sanity check: the doc itself must call out lowercase snake_case so
    the rule is unambiguous to any agent that reads it."""
    assert re.search(r"lowercase\s+snake_case", doc_text, re.IGNORECASE), (
        "entity-id-validator.md does not explicitly state the lowercase "
        "snake_case rule. The regex alone is easy to misread."
    )
