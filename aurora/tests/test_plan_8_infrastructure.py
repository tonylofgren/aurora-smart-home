"""Contract tests for Plan 8: CI / schema versioning / contribution flow.

Verifies the operational infrastructure exists and that key contracts
(pytest runs in CI, schema-versioning rules are documented, contribution
docs point at the right places) are intact.
"""
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AURORA_ROOT = Path(__file__).resolve().parents[1]

CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "validate.yaml"
SCHEMA_VERSIONING_DOC = AURORA_ROOT / "references" / "schemas" / "SCHEMA-VERSIONING.md"
TOP_CONTRIBUTING = REPO_ROOT / "CONTRIBUTING.md"
PR_TEMPLATE = REPO_ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md"
BUG_TEMPLATE = REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.md"
FEATURE_TEMPLATE = REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.md"
REQUIREMENTS_DEV = REPO_ROOT / "requirements-dev.txt"


# CI workflow.

@pytest.fixture(scope="module")
def workflow_text():
    assert CI_WORKFLOW.is_file(), f"{CI_WORKFLOW} missing"
    return CI_WORKFLOW.read_text(encoding="utf-8")


def test_ci_workflow_runs_pytest(workflow_text):
    """The CI workflow must include a job that runs the aurora pytest
    suite. Without it the 500+ contract tests are not enforced in CI."""
    text_lower = workflow_text.lower()
    assert "pytest" in text_lower, (
        "validate.yaml does not invoke pytest. The aurora test suite that "
        "protects schemas, validators, and souls would not run in CI."
    )
    assert "aurora/tests" in workflow_text, (
        "validate.yaml does not reference aurora/tests/. Even if pytest "
        "is mentioned, it has no target to run."
    )


def test_ci_workflow_triggers_on_aurora_changes(workflow_text):
    """The pytest job's path triggers must include `aurora/**` so changes
    to schemas, profiles, or souls actually trigger CI."""
    assert "aurora/**" in workflow_text, (
        "validate.yaml does not list 'aurora/**' as a path trigger. "
        "Changes under aurora/ would not run the CI suite."
    )


def test_ci_workflow_pins_python_version(workflow_text):
    """Python version must be pinned. Drifting Python versions break
    tests in ways orthogonal to the code under test."""
    import re
    assert re.search(r"python-version:\s*['\"]?3\.\d+", workflow_text), (
        "validate.yaml does not pin a specific Python version. CI will "
        "drift as GitHub Actions updates its default."
    )


def test_ci_workflow_caches_pip(workflow_text):
    """Cached pip installs keep CI fast. Without caching the setup step
    takes longer than the test run itself."""
    text_lower = workflow_text.lower()
    assert "cache: pip" in text_lower or "actions/cache" in text_lower, (
        "validate.yaml does not cache pip installs. CI setup will be "
        "slower than the test run on every push."
    )


def test_ci_workflow_installs_from_requirements_dev(workflow_text):
    """Dependencies must come from requirements-dev.txt, not be hardcoded
    in the workflow. Otherwise the local-dev environment drifts from CI."""
    assert "requirements-dev.txt" in workflow_text, (
        "validate.yaml does not install from requirements-dev.txt. The "
        "pinned test-dependency set is not enforced in CI."
    )


# Schema versioning doc.

@pytest.fixture(scope="module")
def versioning_text():
    assert SCHEMA_VERSIONING_DOC.is_file(), f"{SCHEMA_VERSIONING_DOC} missing"
    return SCHEMA_VERSIONING_DOC.read_text(encoding="utf-8")


def test_schema_versioning_doc_exists():
    assert SCHEMA_VERSIONING_DOC.is_file()


def test_schema_versioning_doc_enumerates_bump_rules(versioning_text):
    """The doc must list when each level of bump applies. A doc that says
    'use semver' without spelling out which changes are major/minor/patch
    forces every contributor to guess."""
    text_lower = versioning_text.lower()
    for term in ("major", "minor", "patch"):
        assert term in text_lower, (
            f"SCHEMA-VERSIONING.md does not mention '{term}' bumps."
        )


def test_schema_versioning_doc_addresses_backwards_compatibility(versioning_text):
    """The doc must address what happens to existing profiles when a
    schema bumps major. Otherwise contributors will silently break the
    catalog."""
    text_lower = versioning_text.lower()
    assert "backward" in text_lower or "compat" in text_lower, (
        "SCHEMA-VERSIONING.md does not address backwards-compatibility. "
        "A future contributor may silently bump a schema to v2 and break "
        "every existing profile."
    )


def test_schema_versioning_doc_lists_how_to_land_a_change(versioning_text):
    """The 'how to land' steps protect against in-place schema edits that
    silently invalidate the catalog."""
    text_lower = versioning_text.lower()
    assert "pytest" in text_lower, (
        "SCHEMA-VERSIONING.md does not name the pytest suite as the "
        "validation gate. Contributors may skip running tests before "
        "submitting schema changes."
    )


# Contribution flow.

@pytest.mark.parametrize("path", [
    TOP_CONTRIBUTING,
    PR_TEMPLATE,
    BUG_TEMPLATE,
    FEATURE_TEMPLATE,
], ids=lambda p: p.name)
def test_contribution_doc_exists(path):
    """Every contribution-flow doc must exist. New contributors land on
    these first; missing docs read as 'this project is closed'."""
    assert path.is_file(), f"{path} missing"


def test_requirements_dev_pins_required_packages():
    """The pytest suite needs at minimum pytest, jsonschema. Without
    pinned versions in requirements-dev.txt, local dev and CI drift."""
    assert REQUIREMENTS_DEV.is_file(), f"{REQUIREMENTS_DEV} missing"
    text = REQUIREMENTS_DEV.read_text(encoding="utf-8")
    assert "pytest" in text, "requirements-dev.txt does not pin pytest"
    assert "jsonschema" in text, "requirements-dev.txt does not pin jsonschema"
