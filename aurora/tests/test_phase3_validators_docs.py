"""Contract tests for Plan 5 Phase 3 D+ validator docs.

Covers: ota-safety, i2c-address, voltage-level, version, async-correctness.

These do NOT execute the validators (they are markdown specs, not Python
modules). They assert the docs are structurally sound and that the unique
contract of each validator is intact: which data fields it consumes, what
failure messages it produces, and how it integrates with the agent that
runs it.
"""
import re
from pathlib import Path

import pytest

AURORA_ROOT = Path(__file__).resolve().parents[1]
VALIDATORS_DIR = AURORA_ROOT / "references" / "validators"
VOLT_SOUL_PATH = AURORA_ROOT / "souls" / "volt.md"
ADA_SOUL_PATH = AURORA_ROOT / "souls" / "ada.md"

NEW_VALIDATORS = {
    "ota-safety": {
        "title": "OTA Safety Validator",
        "owner_agents": ["volt"],
        "key_fields": ["ota_safety", "factory_reset_pin", "usb_cdc_recovery"],
        "must_mention": ["external programmer", "factory reset", "AP fallback"],
    },
    "i2c-address": {
        "title": "I2C Address Validator",
        "owner_agents": ["volt"],
        "key_fields": ["default_addresses", "address_strap_pin"],
        "must_mention": ["multiplexer", "TCA9548A", "reserved range"],
    },
    "voltage-level": {
        "title": "Voltage Level Validator",
        "owner_agents": ["volt"],
        "key_fields": ["operating_voltage", "gpio_5v_tolerant", "level_shifter_required_on_5v_board"],
        "must_mention": ["BSS138", "TXS0108E", "level shifter"],
    },
    "version": {
        "title": "Version Validator",
        "owner_agents": ["volt", "sage"],
        "key_fields": ["min_version", "target_version", "platform-versions.md"],
        "must_mention": ["semver", "deprecated", "experimental"],
    },
    "async-correctness": {
        "title": "Async Correctness Validator",
        "owner_agents": ["ada"],
        "key_fields": ["datetime.now()", "requests", "time.sleep"],
        "must_mention": ["aiohttp", "dt_util.now()", "asyncio.sleep"],
    },
}

REQUIRED_SECTIONS = ["When to Run", "Inputs", "Output", "Examples"]


@pytest.fixture(scope="module", params=list(NEW_VALIDATORS.keys()))
def validator(request):
    name = request.param
    path = VALIDATORS_DIR / f"{name}-validator.md"
    assert path.is_file(), f"{name}-validator.md missing at {path}"
    return name, path.read_text(encoding="utf-8"), NEW_VALIDATORS[name]


def test_validator_doc_has_title(validator):
    name, text, spec = validator
    expected = re.escape(spec["title"])
    assert re.search(rf"^#\s+{expected}", text, re.MULTILINE), (
        f"{name}-validator.md does not start with '# {spec['title']}'."
    )


def test_validator_doc_has_required_sections(validator):
    name, text, _ = validator
    missing = [
        s for s in REQUIRED_SECTIONS
        if not re.search(rf"^##\s+{re.escape(s)}", text, re.MULTILINE)
    ]
    assert not missing, (
        f"{name}-validator.md is missing required sections: {missing}. "
        "Other validator docs follow the same structure."
    )


def test_validator_doc_lists_key_fields(validator):
    name, text, spec = validator
    missing = [f for f in spec["key_fields"] if f not in text]
    assert not missing, (
        f"{name}-validator.md does not reference required key fields: {missing}. "
        "The validator needs these data sources to be actionable."
    )


def test_validator_doc_mentions_required_concepts(validator):
    name, text, spec = validator
    missing = [m for m in spec["must_mention"] if m.lower() not in text.lower()]
    assert not missing, (
        f"{name}-validator.md does not mention required concepts: {missing}. "
        "These are the load-bearing terms for this validator's contract."
    )


def test_validator_doc_includes_failing_example(validator):
    name, text, _ = validator
    examples_match = re.search(r"##\s+Examples(.+)$", text, re.DOTALL)
    assert examples_match, f"{name}-validator.md is missing Examples section"
    examples = examples_match.group(1)
    assert re.search(r"Failures:\s*\n\s*-", examples), (
        f"{name}-validator.md has no failing example. Agents will not know "
        "what a failure looks like."
    )


def test_validator_doc_includes_passing_example(validator):
    name, text, _ = validator
    examples_match = re.search(r"##\s+Examples(.+)$", text, re.DOTALL)
    assert examples_match, f"{name}-validator.md is missing Examples section"
    examples = examples_match.group(1)
    assert re.search(r"Failures:\s*\[\]", examples), (
        f"{name}-validator.md has no passing example. Agents will not know "
        "what a clean run looks like."
    )


# Targeted per-validator contract checks beyond the shared structure.

def test_ota_safety_addresses_min_required_features():
    """OTA-safety must enforce the min_required_features_for_unbricking list
    from the board profile — the validator's most load-bearing check."""
    text = (VALIDATORS_DIR / "ota-safety-validator.md").read_text(encoding="utf-8")
    assert "min_required_features_for_unbricking" in text, (
        "ota-safety-validator.md does not reference "
        "min_required_features_for_unbricking. The unbrickability contract "
        "from board profiles would not be enforced."
    )


def test_i2c_address_addresses_reserved_range():
    """I2C-address must call out the I2C-reserved address range (0x00-0x07,
    0x78-0x7F). Without this check, components mis-keyed into reserved
    addresses go unflagged."""
    text = (VALIDATORS_DIR / "i2c-address-validator.md").read_text(encoding="utf-8")
    assert "0x00" in text and "0x7F" in text.upper().replace("X", "x"), (
        "i2c-address-validator.md does not call out the I2C-reserved range "
        "(0x00-0x07 / 0x78-0x7F)."
    )


def test_voltage_level_recommends_specific_shifters():
    """When the validator recommends adding a level shifter, it must name
    concrete parts so Volt can update the BOM. Both BSS138 and TXS0108E
    must appear."""
    text = (VALIDATORS_DIR / "voltage-level-validator.md").read_text(encoding="utf-8")
    assert "BSS138" in text, "voltage-level-validator.md does not recommend BSS138"
    assert "TXS0108E" in text, "voltage-level-validator.md does not recommend TXS0108E"


def test_version_handles_semver_comparison():
    """Version validator must define how to compare date-style versions
    (e.g. 2026.4.5 vs 2026.5.0). Without an explicit rule, two agents
    could compare differently."""
    text = (VALIDATORS_DIR / "version-validator.md").read_text(encoding="utf-8")
    text_lower = text.lower()
    assert "version comparison" in text_lower or "semver" in text_lower, (
        "version-validator.md does not document how to compare version "
        "strings. Behaviour will diverge between agents."
    )


def test_async_correctness_lists_forbidden_patterns():
    """async-correctness must enumerate the specific forbidden patterns
    rather than describing them in prose. Vague guidance produces vague
    enforcement."""
    text = (VALIDATORS_DIR / "async-correctness-validator.md").read_text(encoding="utf-8")
    required = ["datetime.now()", "time.sleep", "requests.get", "subprocess"]
    missing = [p for p in required if p not in text]
    assert not missing, (
        f"async-correctness-validator.md is missing forbidden patterns: "
        f"{missing}."
    )
    # The validator must also call out the docstring/comment exemption so
    # references inside documentation strings don't false-positive.
    text_lower = text.lower()
    assert "docstring" in text_lower or "comment" in text_lower, (
        "async-correctness-validator.md does not document the "
        "docstring/comment exemption. Agents will get false positives."
    )


def test_async_correctness_exempts_imports():
    """`import requests` is fine; only the call site matters. The validator
    must document this exemption explicitly."""
    text = (VALIDATORS_DIR / "async-correctness-validator.md").read_text(encoding="utf-8")
    text_lower = text.lower()
    assert re.search(r"import.{0,40}exempt", text_lower), (
        "async-correctness-validator.md does not exempt 'import' lines from "
        "the pattern check. Every legitimate import would be flagged."
    )
