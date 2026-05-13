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


def test_skill_version_bumped_to_1_6_3():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "v1.6.3" in content
