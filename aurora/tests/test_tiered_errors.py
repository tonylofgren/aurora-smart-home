"""Contract tests for the tiered-errors output format.

Every validator under aurora/references/validators/ must reference the
shared `_tiered-errors.md` format spec so the agent output is consistent
across the suite. Beginners get a short problem + concrete fix; curious
users get the full four-tier breakdown.
"""
import re
from pathlib import Path

import pytest

AURORA_ROOT = Path(__file__).resolve().parents[1]
VALIDATORS_DIR = AURORA_ROOT / "references" / "validators"
SPEC_PATH = VALIDATORS_DIR / "_tiered-errors.md"


def _all_validator_docs():
    """Return all *-validator.md docs (excluding the spec itself and other
    underscore-prefixed meta docs)."""
    return sorted(
        p for p in VALIDATORS_DIR.glob("*-validator.md")
        if not p.name.startswith("_")
    )


def test_tiered_errors_spec_exists():
    """The shared format spec must exist."""
    assert SPEC_PATH.is_file(), (
        f"_tiered-errors.md missing at {SPEC_PATH}. The shared format spec "
        "is the single source of truth for validator output format."
    )


@pytest.fixture(scope="module")
def spec_text():
    return SPEC_PATH.read_text(encoding="utf-8")


def test_spec_defines_four_tiers(spec_text):
    """All four tiers must be defined explicitly."""
    for tier in ["Problem", "Explanation", "Fix", "Deeper"]:
        assert tier in spec_text, (
            f"_tiered-errors.md does not define the '{tier}' tier."
        )


def test_spec_specifies_emoji_prefixes(spec_text):
    """The exact emoji prefixes must be enumerated so agents can parse the
    output without language detection."""
    for emoji in ["❌", "⚠️", "📚", "🔧", "💡"]:
        assert emoji in spec_text, (
            f"_tiered-errors.md does not specify the '{emoji}' emoji prefix."
        )


def test_spec_declares_mandatory_tiers(spec_text):
    """Tiers 1 and 3 must be marked mandatory; tier 4 must be optional."""
    text_lower = spec_text.lower()
    assert "mandatory" in text_lower, (
        "_tiered-errors.md does not say which tiers are mandatory. "
        "Validators will skip tiers silently otherwise."
    )
    assert "optional" in text_lower, (
        "_tiered-errors.md does not call out optional tiers (tier 4 should "
        "be optional)."
    )


def test_spec_includes_at_least_one_complete_example(spec_text):
    """Without a concrete example, validators may interpret the format
    differently. Spec must demonstrate the four-tier shape end-to-end."""
    # A complete example uses all four emoji prefixes in proximity.
    pattern = re.compile(
        r"❌[^❌]*?\U0001f4da[^❌]*?\U0001f527[^❌]*?\U0001f4a1",
        re.DOTALL,
    )
    assert pattern.search(spec_text), (
        "_tiered-errors.md does not include a complete four-tier example. "
        "Without an example, validators may emit incomplete output."
    )


@pytest.fixture(scope="module", params=_all_validator_docs(), ids=lambda p: p.name)
def validator_doc(request):
    return request.param.read_text(encoding="utf-8"), request.param.name


def test_every_validator_references_tiered_format(validator_doc):
    """Each validator doc must point at _tiered-errors.md so agents that
    read just one validator still see the shared output contract."""
    text, name = validator_doc
    assert "_tiered-errors.md" in text, (
        f"{name} does not reference _tiered-errors.md. Validators emit "
        "output in isolation; without the reference, agents lose the "
        "shared format contract."
    )


def test_every_validator_links_tiered_format_in_output_block(validator_doc):
    """The reference must live in the Output section so it is the last
    thing an agent reads before producing output."""
    text, name = validator_doc
    output_match = re.search(r"##\s+Output(.+?)(?=\n##\s|\Z)", text, re.DOTALL)
    assert output_match, f"{name} is missing an Output section"
    assert "_tiered-errors.md" in output_match.group(1), (
        f"{name} mentions _tiered-errors.md but not inside the Output "
        "section. Move the reference under '## Output' so it sits next to "
        "the failure-list and warning-list contract."
    )


def test_validator_count_meets_minimum():
    """Sanity check: we expect at least 9 validators (the post-1.6.2 count)."""
    docs = _all_validator_docs()
    assert len(docs) >= 9, (
        f"Expected at least 9 validators, found {len(docs)}: "
        f"{[p.name for p in docs]}. If validators were removed, update "
        "this test together with the removal."
    )
