"""Tests that aurora/SKILL.md references the new reference data structure."""
from pathlib import Path

SKILL_PATH = Path(__file__).resolve().parents[1] / "SKILL.md"


def test_skill_references_boards_directory():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "aurora/references/boards/" in content


def test_skill_references_components_directory():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "aurora/references/components/" in content


def test_skill_references_validators_directory():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "aurora/references/validators/" in content


def test_skill_mentions_iron_law_6():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "Iron Law 6" in content


def test_skill_version_bumped_to_1_7_1():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "v1.7.1" in content


def test_skill_has_version_check_section():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "## Version Check" in content, (
        "aurora/SKILL.md is missing the 'Version Check' section. Without "
        "it Aurora cannot warn users when a newer plugin version exists."
    )


def test_skill_version_check_uses_webfetch():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "WebFetch" in content, (
        "aurora/SKILL.md does not mention WebFetch. The version check needs "
        "WebFetch to fetch the latest marketplace.json from GitHub."
    )


def test_skill_allowed_tools_includes_webfetch():
    content = SKILL_PATH.read_text(encoding="utf-8")
    frontmatter = content.split("---", 2)[1]
    assert "WebFetch" in frontmatter, (
        "aurora/SKILL.md frontmatter does not list WebFetch in allowed-tools. "
        "Without it the version-check WebFetch call cannot execute."
    )


def test_skill_version_check_fetches_raw_marketplace_json():
    content = SKILL_PATH.read_text(encoding="utf-8")
    expected_url_part = "raw.githubusercontent.com/tonylofgren/aurora-smart-home"
    assert expected_url_part in content, (
        "aurora/SKILL.md version check does not target the raw marketplace.json "
        "URL. Without the URL the check cannot resolve the latest version."
    )
