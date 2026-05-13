"""Contract tests for Iron Law 2 propagation to Ada, Iris, and Atlas.

After Sage (test_sage_iron_law_2.py) gained 'Iron Law 2 — Validate Before
Generating', the same pattern was extended to:

- Ada (full)  — async-correctness + entity-id producer
- Iris (thin) — entity-id consumer only
- Atlas (thin) — secrets-validator on YAML snippets

Mira and River intentionally stay at Iron Law 1 (snapshot-aware) until
their domain validators ship.
"""
import re
from pathlib import Path

import pytest

AURORA_ROOT = Path(__file__).resolve().parents[1]
SOULS_DIR = AURORA_ROOT / "souls"

# soul name → expected validator references in Iron Law 2.
IRON_LAW_2_SOULS = {
    "ada": {
        "must_invoke": ["async-correctness-validator", "entity-id-validator"],
        "must_mention_concepts": ["producer mode", "QUICK mode"],
        "must_acknowledge_planned": ["python-secrets-validator"],
    },
    "iris": {
        "must_invoke": ["entity-id-validator"],
        "must_mention_concepts": ["consumer mode", "QUICK mode", "conflict_log"],
        "must_acknowledge_planned": [],
    },
    "atlas": {
        "must_invoke": ["secrets-validator"],
        "must_mention_concepts": ["!secret"],
        "must_acknowledge_planned": [],
    },
    "mira": {
        "must_invoke": [
            "llm-config-validator",
            "entity-id-validator",
            "secrets-validator",
            "async-correctness-validator",
        ],
        "must_mention_concepts": ["consumer mode", "conflict_log"],
        "must_acknowledge_planned": [],
    },
    "river": {
        "must_invoke": ["node-red-syntax-validator", "entity-id-validator"],
        "must_mention_concepts": ["consumer mode", "conflict_log"],
        "must_acknowledge_planned": [],
    },
}

# Souls that intentionally STAY at Iron Law 1 only. After 1.6.4, every
# DEEP-mode specialist has both laws; the parked list is empty.
PARKED_SOULS = []


@pytest.fixture(scope="module", params=list(IRON_LAW_2_SOULS.keys()))
def soul(request):
    name = request.param
    path = SOULS_DIR / f"{name}.md"
    assert path.is_file(), f"souls/{name}.md missing"
    return name, path.read_text(encoding="utf-8"), IRON_LAW_2_SOULS[name]


def test_soul_has_iron_law_2(soul):
    name, text, _ = soul
    assert re.search(
        r"\*\*Iron\s+Law\s+2\s+—\s+Validate\s+Before\s+Generating", text
    ), (
        f"{name}.md does not declare 'Iron Law 2 — Validate Before Generating'."
    )


def test_soul_iron_law_1_still_present(soul):
    name, text, _ = soul
    assert re.search(r"\*\*Iron\s+Law\s+1\s+—\s+Snapshot-Aware", text), (
        f"{name}.md is missing Iron Law 1 (Snapshot-Aware Coordination). "
        "Adding Law 2 should not have displaced Law 1."
    )


def test_soul_invokes_required_validators(soul):
    name, text, spec = soul
    missing = [v for v in spec["must_invoke"] if v not in text]
    assert not missing, (
        f"{name}.md Iron Law 2 does not invoke required validators: {missing}."
    )


def test_soul_mentions_required_concepts(soul):
    """Concepts must be present; line wrapping (producer\\n  mode) is OK."""
    name, text, spec = soul
    # Collapse runs of whitespace so wrapped phrases still match.
    flat = re.sub(r"\s+", " ", text)
    missing = [c for c in spec["must_mention_concepts"] if c not in flat]
    assert not missing, (
        f"{name}.md Iron Law 2 is missing required concepts: {missing}."
    )


def test_soul_acknowledges_planned_validators(soul):
    """Souls that note planned-but-not-yet-shipped validators must keep the
    forward reference. A future edit deleting it would lose roadmap context."""
    name, text, spec = soul
    if not spec["must_acknowledge_planned"]:
        pytest.skip("No planned validators flagged for this soul")
    missing = [p for p in spec["must_acknowledge_planned"] if p not in text]
    assert not missing, (
        f"{name}.md Iron Law 2 does not acknowledge planned validators: "
        f"{missing}."
    )


def test_soul_documents_failure_blocks_delivery(soul):
    """Validator failures MUST block delivery, otherwise the law is advisory."""
    name, text, _ = soul
    text_lower = text.lower()
    assert re.search(r"(do\s+not\s+deliver|blocks?\s+delivery)", text_lower), (
        f"{name}.md Iron Law 2 does not state validator failures block "
        "delivery. The validator becomes advisory rather than enforceable."
    )


def test_soul_iron_laws_are_unique(soul):
    name, text, _ = soul
    for n in (1, 2):
        pattern = rf"\*\*Iron\s+Law\s+{n}\s+—"
        count = len(re.findall(pattern, text))
        assert count == 1, (
            f"{name}.md declares 'Iron Law {n}' {count} times; expected 1."
        )


# Negative checks — souls that should NOT yet have Iron Law 2.

@pytest.mark.parametrize("soul_name", PARKED_SOULS)
def test_parked_soul_does_not_have_iron_law_2(soul_name):
    """Mira and River explicitly stay at Iron Law 1 until their domain
    validators (llm-config, node-red-syntax) ship. Adding Iron Law 2 to
    these souls before the validators exist would create dead references."""
    text = (SOULS_DIR / f"{soul_name}.md").read_text(encoding="utf-8")
    has_law_2 = bool(re.search(r"\*\*Iron\s+Law\s+2\s+—", text))
    assert not has_law_2, (
        f"{soul_name}.md unexpectedly has an Iron Law 2. Per the Phase 3 plan, "
        f"{soul_name} stays at Iron Law 1 until its domain validators "
        "(llm-config / node-red-syntax) ship. Add the validator first, then "
        "the Iron Law — not the other way around."
    )


def test_iris_law_2_is_read_only():
    """Iris is read-only of entity_ids_generated. Its Iron Law 2 must
    enforce that — never add to or modify the list."""
    text = (SOULS_DIR / "iris.md").read_text(encoding="utf-8")
    text_lower = text.lower()
    assert re.search(r"(produces no entities|read-only|never modif)", text_lower), (
        "iris.md Iron Law 2 does not state the read-only constraint. "
        "Iris could mistakenly add inventions to entity_ids_generated."
    )


def test_ada_law_2_warns_about_python_secret_literals():
    """Ada produces Python, and the YAML-only secrets-validator does not
    cover Python source. Iron Law 2 must warn about Python literal
    credentials manually until python-secrets-validator ships."""
    text = (SOULS_DIR / "ada.md").read_text(encoding="utf-8")
    text_lower = text.lower()
    assert "config_entry" in text_lower or "environment variable" in text_lower, (
        "ada.md Iron Law 2 does not steer credentials to config_entry / "
        "environment variables. Until python-secrets-validator ships, this "
        "is the only guardrail Ada has against hardcoded API keys."
    )
