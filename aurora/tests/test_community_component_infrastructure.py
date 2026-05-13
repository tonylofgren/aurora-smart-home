"""Contract tests for the Plan 6 community-component infrastructure.

Aurora's catalog of ESPHome external_components and HACS-distributed HA
integrations is intentionally narrow. These tests cover the infrastructure
that handles community components correctly without a populated catalog:

- Two JSON Schemas (external-component, hacs-integration) defining the shape
  of any future catalog entries.
- A markdown validator spec (unknown-component-validator) defining what
  agents do when the user names a component for which no profile exists.
- Two CONTRIBUTING.md files defining the verification floor for adding
  catalog entries.

The catalog itself ships empty by design. The tests verify the schemas
are valid JSON Schema Draft 2020-12 and that the protocol is documented.
"""
import json
import re
from pathlib import Path

import jsonschema
import pytest

AURORA_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = AURORA_ROOT / "references" / "schemas"
VALIDATORS_DIR = AURORA_ROOT / "references" / "validators"
EXTERNAL_DIR = AURORA_ROOT / "references" / "external_components"
HACS_DIR = AURORA_ROOT / "references" / "hacs_integrations"

EXTERNAL_SCHEMA_PATH = SCHEMAS_DIR / "external-component.schema.json"
HACS_SCHEMA_PATH = SCHEMAS_DIR / "hacs-integration.schema.json"
PROTOCOL_PATH = VALIDATORS_DIR / "unknown-component-validator.md"


@pytest.fixture(scope="module")
def external_schema():
    with EXTERNAL_SCHEMA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def hacs_schema():
    with HACS_SCHEMA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


# Schema validity.

def test_external_component_schema_is_valid(external_schema):
    jsonschema.Draft202012Validator.check_schema(external_schema)


def test_hacs_integration_schema_is_valid(hacs_schema):
    jsonschema.Draft202012Validator.check_schema(hacs_schema)


# Required-field coverage.

def test_external_component_schema_has_required_fields(external_schema):
    """The external-component schema must enforce the core fields needed
    for verifiable catalog entries."""
    required = set(external_schema.get("required", []))
    expected = {
        "schema_version",
        "external_component_id",
        "display_name",
        "source",
        "esphome",
        "lifecycle",
        "last_verified",
    }
    missing = expected - required
    assert not missing, f"external-component schema missing required: {missing}"


def test_hacs_integration_schema_has_required_fields(hacs_schema):
    required = set(hacs_schema.get("required", []))
    expected = {
        "schema_version",
        "hacs_integration_id",
        "display_name",
        "source",
        "homeassistant",
        "category",
        "lifecycle",
        "last_verified",
    }
    missing = expected - required
    assert not missing, f"hacs-integration schema missing required: {missing}"


def test_external_component_schema_supports_real_chips(external_schema):
    """supported_chips enum must include every chip family aurora currently
    ships board profiles for. Otherwise a contributor cannot list a chip
    the rest of the catalog already knows about."""
    chips = (
        external_schema["properties"]["esphome"]["properties"]
        ["supported_chips"]["items"]["enum"]
    )
    required_chips = {"esp32", "esp32-s3", "esp32-c3", "esp32-c6", "esp32-h2", "esp8266", "rp2040", "rp2350"}
    missing = required_chips - set(chips)
    assert not missing, (
        f"external-component schema's supported_chips enum is missing: {missing}. "
        "Every chip aurora has a board profile for must be selectable."
    )


def test_hacs_integration_schema_enumerates_categories(hacs_schema):
    """HACS integration categories must be enumerated so contributors cannot
    invent ad-hoc category names that diverge across the catalog."""
    cats = hacs_schema["properties"]["category"]["enum"]
    expected = {"energy", "climate", "lighting", "media", "security", "presence",
                "vacuum", "weather", "calendar", "notifications",
                "automation_helper", "frontend", "infrastructure",
                "voice_assistant", "other"}
    missing = expected - set(cats)
    assert not missing, (
        f"hacs-integration schema's category enum is missing: {missing}."
    )


# additionalProperties: false at the top level.

def test_external_component_schema_rejects_unknown_top_level_fields(external_schema):
    """Top-level additionalProperties must be false so unknown fields are
    flagged at validation time."""
    assert external_schema.get("additionalProperties") is False, (
        "external-component schema does not set additionalProperties: false at "
        "the top level. Contributors could silently add unrecognized fields."
    )


def test_hacs_integration_schema_rejects_unknown_top_level_fields(hacs_schema):
    assert hacs_schema.get("additionalProperties") is False


# Lifecycle status enum consistency.

def test_lifecycle_status_enum_matches_across_schemas(external_schema, hacs_schema):
    """The same lifecycle statuses (active/experimental/deprecated/abandoned/
    merged_to_core) must be valid for both catalogs."""
    ec_statuses = set(
        external_schema["properties"]["lifecycle"]["properties"]["status"]["enum"]
    )
    hacs_statuses = set(
        hacs_schema["properties"]["lifecycle"]["properties"]["status"]["enum"]
    )
    expected = {"active", "experimental", "deprecated", "abandoned", "merged_to_core"}
    assert expected.issubset(ec_statuses), f"external schema missing: {expected - ec_statuses}"
    assert expected.issubset(hacs_statuses), f"hacs schema missing: {expected - hacs_statuses}"


# Catalog directories exist with CONTRIBUTING.md.

def test_external_components_directory_has_contributing_doc():
    assert (EXTERNAL_DIR / "CONTRIBUTING.md").is_file(), (
        f"{EXTERNAL_DIR}/CONTRIBUTING.md missing. Contributors need a clear "
        "contract for adding catalog entries."
    )


def test_hacs_integrations_directory_has_contributing_doc():
    assert (HACS_DIR / "CONTRIBUTING.md").is_file(), (
        f"{HACS_DIR}/CONTRIBUTING.md missing."
    )


# Catalogs ship empty by design.

def test_external_components_catalog_ships_empty():
    """Plan 6 ships only the infrastructure. Adding entries requires manual
    verification per CONTRIBUTING.md and arrives via PR, not in this commit."""
    entries = list(EXTERNAL_DIR.glob("*.json"))
    assert len(entries) == 0, (
        f"external_components catalog contains entries: {[p.name for p in entries]}. "
        "Plan 6 ships zero seed entries by design — adding even one risks "
        "readers treating it as a curated 'recommended' list. Move entries "
        "to a follow-up PR with the verification floor met."
    )


def test_hacs_integrations_catalog_ships_empty():
    entries = list(HACS_DIR.glob("*.json"))
    assert len(entries) == 0, (
        f"hacs_integrations catalog contains entries: {[p.name for p in entries]}. "
        "Plan 6 ships zero seed entries by design."
    )


# Protocol document.

@pytest.fixture(scope="module")
def protocol_text():
    assert PROTOCOL_PATH.is_file(), f"{PROTOCOL_PATH} missing"
    return PROTOCOL_PATH.read_text(encoding="utf-8")


def test_protocol_doc_names_three_questions(protocol_text):
    """The three questions (source URL, version requirements, docs link)
    are the contract's load-bearing piece. They must be enumerated."""
    text_lower = protocol_text.lower()
    assert "source url" in text_lower, "Protocol must enumerate 'Source URL' question"
    assert re.search(r"(version|chips?)", text_lower), "Protocol must require version/chip info"
    assert re.search(r"(documentation|docs|datasheet)", text_lower), (
        "Protocol must require a documentation link"
    )


def test_protocol_doc_blocks_when_user_cannot_answer(protocol_text):
    """If the user cannot supply a required answer, the agent must refuse
    rather than fabricate. This is the entire point of the protocol."""
    text_lower = protocol_text.lower()
    assert re.search(r"(refuse|block|do not generate|must\s+not\s+generate)", text_lower), (
        "Protocol does not explicitly say agents refuse when answers are "
        "missing. Without that, agents will fabricate plausible-but-wrong "
        "configuration."
    )


def test_protocol_doc_records_in_snapshot(protocol_text):
    """The snapshot's notes[] entry preserves the audit trail. Without it,
    future agents won't know the component was user-supplied rather than
    verified."""
    text_lower = protocol_text.lower()
    assert "notes" in text_lower, (
        "Protocol does not mention the snapshot notes[] recording step."
    )
    assert re.search(r"snapshot|aurora-project", text_lower), (
        "Protocol does not mention the snapshot file."
    )


def test_protocol_doc_specifies_caution_block(protocol_text):
    """Output must carry a visible warning that the component lacks an
    Aurora profile. A silent answer is the failure mode."""
    text_lower = protocol_text.lower()
    assert re.search(r"caution|warning|⚠️", text_lower), (
        "Protocol does not require a visible caution block in agent output."
    )


def test_protocol_doc_references_tiered_format(protocol_text):
    """Consistent with other validators in the suite."""
    assert "_tiered-errors.md" in protocol_text, (
        "unknown-component-validator.md does not reference _tiered-errors.md."
    )
