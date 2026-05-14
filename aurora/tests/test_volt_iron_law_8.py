"""Contract tests for Volt's Iron Law 8 (Complete Delivery).

A hardware project is not delivered until every required artifact exists
on disk in the project folder. The law enforces:
- A project folder per project (slug-based).
- The minimum file set per manufacturing tier.
- Required README sections (manual format).
- An estimated price column in the BOM, with a date stamp.
- A pre-delivery disk check.
- Attribution in every generated file.

These tests do not run Volt. They lock the law's contract in the soul
file so silent edits cannot weaken it.
"""
from pathlib import Path

import pytest

VOLT_PATH = Path(__file__).resolve().parents[1] / "souls" / "volt.md"
DELIVERABLES_DIR = (
    Path(__file__).resolve().parents[1] / "references" / "deliverables"
)


@pytest.fixture(scope="module")
def law_8_text():
    content = VOLT_PATH.read_text(encoding="utf-8")
    start = content.index("**Iron Law 8")
    end = content.index("## Voice", start)
    return content[start:end]


def test_volt_iron_law_8_exists():
    """Iron Law 8 'Complete Delivery' must be present in Volt's soul."""
    content = VOLT_PATH.read_text(encoding="utf-8")
    assert "**Iron Law 8" in content, (
        "Volt's soul is missing Iron Law 8 (Complete Delivery). Without it, "
        "hardware projects ship without BOM, manual, or even a project folder."
    )
    assert "Complete Delivery" in content, (
        "Iron Law 8 is present but does not carry the 'Complete Delivery' "
        "label. The label is what makes the law searchable in soul-pattern tests."
    )


def test_law_8_requires_project_folder(law_8_text):
    """Project folder per project, slug-based, not bare files in CWD."""
    text_lower = law_8_text.lower()
    assert "project folder" in text_lower or "project-slug" in text_lower, (
        "Iron Law 8 does not mention the project folder. Without it, Volt "
        "may scatter files into the working directory next to unrelated files."
    )


def test_law_8_requires_manufacturing_tier_question(law_8_text):
    """Volt must ask manufacturing tier at the start of a hardware project."""
    text_lower = law_8_text.lower()
    assert "manufacturing tier" in text_lower, (
        "Iron Law 8 does not mention the manufacturing-tier question. "
        "Without it, Volt cannot pick the right artifact set for the project."
    )
    for tier in ("breadboard", "perfboard", "custom-pcb", "production"):
        assert tier in text_lower, (
            f"Iron Law 8 does not enumerate tier '{tier}'. All four tiers "
            f"must be named so the user picks from a finite list."
        )


def test_law_8_lists_required_files_for_every_tier(law_8_text):
    """The minimum file set is: device YAML, secrets template, README."""
    required_markers = [
        "<device-name>.yaml",
        "secrets.yaml.example",
        "README.md",
    ]
    missing = [m for m in required_markers if m not in law_8_text]
    assert not missing, (
        f"Iron Law 8 does not list every base-tier file: missing {missing}. "
        f"Skipping any of these means a project that cannot be installed."
    )


def test_law_8_lists_required_readme_sections(law_8_text):
    """README must always carry these H2 sections."""
    required_sections = [
        "What this does",
        "Bill of materials",
        "Wiring",
        "Installation",
        "Calibration",
        "Troubleshooting",
        "Recovery",
    ]
    text = law_8_text
    missing = [s for s in required_sections if s not in text]
    assert not missing, (
        f"Iron Law 8 does not name every required README section: "
        f"missing {missing}. The manual format spec depends on this list."
    )


def test_law_8_requires_price_in_bom(law_8_text):
    """BOM must include estimated price + date stamp."""
    text_lower = law_8_text.lower()
    assert "estimated unit price" in text_lower or "estimated price" in text_lower, (
        "Iron Law 8 does not require an estimated price in the BOM. "
        "A price-free BOM is not deliverable."
    )
    assert "date stamp" in text_lower or "month-year" in text_lower, (
        "Iron Law 8 does not require a date stamp on BOM prices. "
        "Without it, stale prices accumulate silently."
    )


def test_law_8_requires_disk_check(law_8_text):
    """Pre-delivery verification: files must exist on disk."""
    text_lower = law_8_text.lower()
    assert "disk check" in text_lower or "actually exists" in text_lower, (
        "Iron Law 8 does not require a pre-delivery disk check. Without "
        "this, Volt can declare delivery on a project that exists only "
        "in chat output."
    )


def test_law_8_requires_attribution(law_8_text):
    """Every generated file must carry attribution per esphome SKILL.md."""
    text_lower = law_8_text.lower()
    assert "attribution" in text_lower, (
        "Iron Law 8 does not mention attribution. Bug 1 from the user "
        "session (banner missing from generated YAML) was the reason this "
        "law exists."
    )


def test_law_8_references_deliverable_specs(law_8_text):
    """The law must point at the format specs, not redefine them."""
    expected_refs = [
        "aurora/references/deliverables/bom-format.md",
        "aurora/references/deliverables/manual-format.md",
        "aurora/references/deliverables/wiring-format.md",
        "aurora/references/deliverables/pcb-format.md",
    ]
    missing = [r for r in expected_refs if r not in law_8_text]
    assert not missing, (
        f"Iron Law 8 does not reference every deliverable spec: "
        f"missing {missing}. The law without spec references becomes "
        f"a generic instruction agents will paraphrase away."
    )


def test_law_8_lists_pcb_tier_additional_files(law_8_text):
    """custom-PCB tier adds SCHEMATIC.md + PCB-NOTES.md on top of base."""
    for fname in ("SCHEMATIC.md", "PCB-NOTES.md"):
        assert fname in law_8_text, (
            f"Iron Law 8 does not list '{fname}' for the custom-PCB tier."
        )


def test_law_8_lists_production_tier_additional_files(law_8_text):
    """production tier adds manufacturing, cost, certification, test jig."""
    for fname in (
        "MANUFACTURING.md",
        "COST-ANALYSIS.md",
        "CERTIFICATION.md",
        "TEST-JIG.md",
    ):
        assert fname in law_8_text, (
            f"Iron Law 8 does not list '{fname}' for the production tier."
        )
