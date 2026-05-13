"""Contract tests for aurora/references/validators/secrets-validator.md.

The validator is a markdown spec that YAML-producing agents (Volt, Sage,
Atlas) read and apply. These tests assert that the spec is structurally
sound, names the high-risk keys explicitly, scopes the rule to the strict
`!secret` form, documents the false-positive guard (no generic entropy
scanning), and that Volt's Iron Law 6 invokes it before delivery.
"""
import re
from pathlib import Path

import pytest

AURORA_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = AURORA_ROOT / "references" / "validators" / "secrets-validator.md"
VOLT_SOUL_PATH = AURORA_ROOT / "souls" / "volt.md"

# Keys the validator must explicitly enumerate. If a future edit drops one,
# agents will silently stop flagging that pattern.
REQUIRED_HIGH_RISK_KEYS = [
    "password",
    "api_key",
    "token",
    "secret",
    "client_secret",
    "private_key",
    "ota_password",
    "wifi_password",
]


@pytest.fixture(scope="module")
def doc_text():
    assert VALIDATOR_PATH.is_file(), (
        f"secrets-validator.md missing at {VALIDATOR_PATH}"
    )
    return VALIDATOR_PATH.read_text(encoding="utf-8")


def test_doc_has_title(doc_text):
    assert re.search(r"^#\s+Secrets\s+Validator", doc_text, re.MULTILINE), (
        "secrets-validator.md does not start with '# Secrets Validator'."
    )


def test_doc_has_required_sections(doc_text):
    """Match the structure used by other validator docs."""
    required = ["When to Run", "Inputs", "Checks", "Output", "Examples"]
    missing = [
        s for s in required
        if not re.search(rf"^##\s+{re.escape(s)}", doc_text, re.MULTILINE)
    ]
    assert not missing, (
        f"secrets-validator.md is missing required sections: {missing}."
    )


def test_doc_enumerates_high_risk_keys(doc_text):
    """The validator's scope MUST be enumerated explicitly. A "look for
    things that look like credentials" instruction is a tarpit."""
    missing = [k for k in REQUIRED_HIGH_RISK_KEYS if k not in doc_text]
    assert not missing, (
        f"secrets-validator.md does not enumerate required high-risk keys: "
        f"{missing}. The validator's scope is intentionally narrow; the list "
        f"must be explicit, not implied."
    )


def test_doc_requires_secret_reference(doc_text):
    """The defining rule is: high-risk key value MUST be `!secret <name>`."""
    assert "!secret" in doc_text, (
        "secrets-validator.md does not mention the `!secret <name>` form. "
        "Without that rule the validator has no defensible failure criterion."
    )


def test_doc_excludes_generic_entropy_scanning(doc_text):
    """The doc must call out that generic high-entropy / base64 scanning is
    intentionally OUT of scope — otherwise a future edit may reintroduce
    the tarpit."""
    text_lower = doc_text.lower()
    assert "entropy" in text_lower or "base64" in text_lower, (
        "secrets-validator.md does not mention the generic-entropy or base64 "
        "false-positive issue. Future edits may quietly reintroduce the "
        "tarpit if the rationale is not stated."
    )


def test_doc_documents_comment_exemption(doc_text):
    """Values inside YAML comments must be intentionally NOT flagged.
    Without that exemption the validator would block legitimate example
    YAML in agent output."""
    text_lower = doc_text.lower()
    assert "comment" in text_lower, (
        "secrets-validator.md does not address comments. Inline YAML "
        "comments like '# password: example' would otherwise be flagged."
    )


def test_doc_documents_block_scalar_handling(doc_text):
    """Block scalars (`|`, `>`) cannot be inspected line-by-line and must
    have explicit guidance."""
    text_lower = doc_text.lower()
    assert "block scalar" in text_lower or "multi-line" in text_lower, (
        "secrets-validator.md does not address block scalars (`|`, `>`). "
        "Embedded credentials in literal blocks would not be handled."
    )


def test_doc_documents_template_value_handling(doc_text):
    """Templated values like `{{ states('...') }}` need a documented path."""
    text_lower = doc_text.lower()
    assert "template" in text_lower, (
        "secrets-validator.md does not address templated values. Agents "
        "would not know whether to flag or pass them."
    )


def test_doc_includes_failure_and_pass_examples(doc_text):
    """Concrete examples make the contract usable."""
    examples_match = re.search(r"##\s+Examples(.+)$", doc_text, re.DOTALL)
    assert examples_match, "Examples section missing"
    examples = examples_match.group(1)
    assert re.search(r"Failures:\s*\n\s*-", examples), (
        "Examples section has no failing example."
    )
    assert re.search(r"Failures:\s*\[\]", examples), (
        "Examples section has no passing example."
    )


def test_doc_suggests_secret_names(doc_text):
    """Failure output must suggest a concrete secret name, not just 'use
    secrets.yaml'. Without a suggested name agents produce vague advice."""
    text_lower = doc_text.lower()
    assert "suggested" in text_lower, (
        "secrets-validator.md does not include a suggested-secret-name "
        "table or guidance. Failure messages would be vague."
    )


def test_volt_iron_law_6_references_secrets_validator():
    """Volt produces ESPHome YAML containing wifi/OTA passwords and API
    keys, so its Iron Law 6 must invoke the secrets-validator before
    delivery."""
    volt_text = VOLT_SOUL_PATH.read_text(encoding="utf-8")
    assert "secrets-validator" in volt_text, (
        "volt.md does not reference secrets-validator. Volt's YAML routinely "
        "contains wifi_password, ota_password, and api encryption keys — "
        "without invoking the validator, literal credentials can ship."
    )
