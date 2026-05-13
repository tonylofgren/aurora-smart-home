"""Tests that Volt's soul defines all expected Iron Laws."""
from pathlib import Path

VOLT_PATH = Path(__file__).resolve().parents[1] / "souls" / "volt.md"


def test_volt_has_six_iron_laws():
    content = VOLT_PATH.read_text(encoding="utf-8")
    for n in range(1, 7):
        marker = f"**Iron Law {n}"
        assert marker in content, f"Volt is missing {marker}"


def test_iron_law_6_references_validators():
    content = VOLT_PATH.read_text(encoding="utf-8")
    law_6_start = content.index("**Iron Law 6")
    law_6_end = content.index("## Voice", law_6_start)
    law_6 = content[law_6_start:law_6_end]
    assert "pin-validator" in law_6
    assert "conflict-validator" in law_6
    assert "aurora/references/boards" in law_6
