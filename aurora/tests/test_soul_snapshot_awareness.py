"""Tests that every multi-agent specialist soul carries the snapshot-aware Iron Law.

These are contract tests. If a future edit removes or weakens the snapshot
clause in any soul, this suite fails. Without snapshot awareness in the soul,
the agent has no instruction to read or update aurora-project.json when
invoked under DEEP mode, and Phase 2A's orchestrator wiring becomes a
half-bridge.
"""
import re
from pathlib import Path

import pytest

AURORA_ROOT = Path(__file__).resolve().parents[1]
SOULS_DIR = AURORA_ROOT / "souls"

# Specialists that participate in DEEP mode and therefore need the Iron Law.
# Each entry: soul name (matches souls/<name>.md and the agents_completed value
# the agent must append to). Support agents (Glitch, Probe, Lens, Manual,
# Scout, Lore, Forge, Grid, Canvas, Echo, Nano, Watt) intentionally omitted —
# they either run transverse to DEEP flows or have not been wired in yet.
DEEP_MODE_SOULS = [
    "volt",
    "ada",
    "sage",
    "iris",
    "vera",
    "atlas",
    "mira",
    "river",
]


@pytest.fixture(scope="module", params=DEEP_MODE_SOULS)
def soul(request):
    soul_name = request.param
    soul_path = SOULS_DIR / f"{soul_name}.md"
    assert soul_path.is_file(), f"Soul file missing: {soul_path}"
    return soul_name, soul_path.read_text(encoding="utf-8")


def test_soul_has_iron_laws_section(soul):
    """Every DEEP-mode specialist must have an explicit Iron Laws section."""
    name, text = soul
    assert re.search(r"^##\s+Iron\s+Laws\b", text, re.MULTILINE), (
        f"{name}.md is missing an '## Iron Laws' section. The snapshot-aware "
        "law has nowhere to live."
    )


def test_soul_mentions_snapshot_filename(soul):
    """The Iron Law must name aurora-project.json so the agent knows what to read."""
    name, text = soul
    assert "aurora-project.json" in text, (
        f"{name}.md does not mention the snapshot file (aurora-project.json). "
        "Without that reference the agent will not know what file to open."
    )


def test_soul_references_handoff_protocol(soul):
    """The Iron Law must point at the protocol doc as the source of truth."""
    name, text = soul
    assert "aurora/references/handoff/_protocol.md" in text, (
        f"{name}.md does not link to _protocol.md. Per-field ownership and "
        "lifecycle rules will not be discoverable from the soul."
    )


def test_soul_documents_quick_mode_fallback(soul):
    """The Iron Law must exempt QUICK mode so single-agent tasks do not
    spawn snapshot files unnecessarily."""
    name, text = soul
    text_lower = text.lower()
    assert "quick mode" in text_lower, (
        f"{name}.md does not exempt QUICK mode from snapshot creation."
    )
    assert re.search(
        r"(missing|does not exist).+(quick|proceed normally)",
        text_lower,
        re.DOTALL,
    ), (
        f"{name}.md does not document the QUICK-mode fallback path "
        "(what to do when no snapshot exists)."
    )


def test_soul_records_its_own_validation_results(soul):
    """Every specialist must record its own validation_results entry, keyed
    by its soul name, so the orchestrator can advance the pipeline."""
    name, text = soul
    expected = f"validation_results.{name}"
    assert expected in text, (
        f"{name}.md does not record `{expected}`. Without this entry the "
        "orchestrator cannot tell whether the agent succeeded."
    )


def test_soul_appends_itself_to_agents_completed(soul):
    """Every specialist must append its own soul name to agents_completed
    so the orchestrator knows it has finished."""
    name, text = soul
    pattern = rf"append\s+`{name}`\s+to\s+`agents_completed`"
    assert re.search(pattern, text, re.IGNORECASE), (
        f"{name}.md does not explicitly say to append `{name}` to "
        "`agents_completed`. Without that step the pipeline cannot advance."
    )


def test_soul_documents_conflict_log_escape_hatch(soul):
    """If the agent cannot make a clean decision, the soul must instruct it
    to raise a conflict_log entry instead of guessing or overwriting peers."""
    name, text = soul
    assert "conflict_log" in text, (
        f"{name}.md does not mention `conflict_log`. Without that escape "
        "hatch the agent may silently overwrite peer fields or invent data."
    )


def test_soul_bumps_updated_at(soul):
    """Every snapshot mutation must bump updated_at so chronology is preserved."""
    name, text = soul
    assert "updated_at" in text, (
        f"{name}.md does not bump `updated_at` when writing. Snapshot "
        "chronology will not survive multi-agent flows."
    )


@pytest.mark.parametrize("soul_name", DEEP_MODE_SOULS)
def test_handoff_iron_law_count_is_one(soul_name):
    """Exactly one 'Snapshot-Aware Coordination' iron law per soul. If a future
    edit duplicates the law (e.g. via copy-paste during expansion), this test
    catches it so the souls do not drift apart."""
    soul_path = SOULS_DIR / f"{soul_name}.md"
    text = soul_path.read_text(encoding="utf-8")
    matches = re.findall(r"Snapshot-Aware\s+Coordination", text)
    assert len(matches) == 1, (
        f"{soul_name}.md has {len(matches)} snapshot-aware iron law(s); "
        "expected exactly 1."
    )
