"""Contract tests for the deliverable format specs in
aurora/references/deliverables/.

These specs are what Volt's Iron Law 8 (Complete Delivery) points at.
Each spec must define a concrete format so two agent invocations cannot
drift into different shapes. The tests lock the structure, not the prose.
"""
from pathlib import Path

import pytest

DELIVERABLES_DIR = (
    Path(__file__).resolve().parents[1] / "references" / "deliverables"
)
BOM_PATH = DELIVERABLES_DIR / "bom-format.md"
MANUAL_PATH = DELIVERABLES_DIR / "manual-format.md"
WIRING_PATH = DELIVERABLES_DIR / "wiring-format.md"
PCB_PATH = DELIVERABLES_DIR / "pcb-format.md"


# Existence

@pytest.mark.parametrize(
    "path",
    [BOM_PATH, MANUAL_PATH, WIRING_PATH, PCB_PATH],
    ids=lambda p: p.name,
)
def test_spec_file_exists(path):
    assert path.is_file(), (
        f"{path.name} is missing. Volt's Iron Law 8 references this spec; "
        f"a dangling reference makes the law unenforceable."
    )


# BOM format spec

@pytest.fixture(scope="module")
def bom_text():
    return BOM_PATH.read_text(encoding="utf-8")


def test_bom_requires_price_column(bom_text):
    """BOM must include a unit price column. Price-free BOMs fail Iron Law 8."""
    assert "Unit price (USD)" in bom_text, (
        "bom-format.md does not require a 'Unit price (USD)' column. "
        "Iron Law 8 mandates an estimated price per row."
    )


def test_bom_requires_quantity_and_source(bom_text):
    """BOM must include qty and source so a reader can buy the parts."""
    for required in ("Qty", "Source"):
        assert required in bom_text, (
            f"bom-format.md does not require a '{required}' column."
        )


def test_bom_requires_date_stamp_in_footer(bom_text):
    """Prices drift. A BOM without a date stamp goes stale silently."""
    text_lower = bom_text.lower()
    assert "date stamp" in text_lower or "month-year" in text_lower or "month yyyy" in text_lower, (
        "bom-format.md does not require a date stamp on the price footer. "
        "Without it, a reader landing on the BOM six months later cannot "
        "tell how old the numbers are."
    )


def test_bom_requires_total_estimated_price(bom_text):
    """BOM footer must show a total, not just per-row prices."""
    text_lower = bom_text.lower()
    assert "estimated total" in text_lower, (
        "bom-format.md does not require an 'Estimated total' line. "
        "A row-only price list does not answer the 'how much does this "
        "project cost' question."
    )


def test_bom_production_tier_adds_lcsc_and_package(bom_text):
    """Production-tier BOMs need LCSC part numbers and package codes."""
    for required in ("LCSC", "Package"):
        assert required in bom_text, (
            f"bom-format.md does not document the '{required}' column for "
            f"production-tier BOMs. Without it, an assembly service cannot "
            f"source parts or place them."
        )


# Manual format spec

@pytest.fixture(scope="module")
def manual_text():
    return MANUAL_PATH.read_text(encoding="utf-8")


def test_manual_lists_required_h2_sections(manual_text):
    """The manual format must enumerate the seven required H2 sections."""
    required_sections = [
        "What this does",
        "Bill of materials",
        "Wiring",
        "Installation",
        "Calibration",
        "Troubleshooting",
        "Recovery",
    ]
    missing = [s for s in required_sections if s not in manual_text]
    assert not missing, (
        f"manual-format.md does not enumerate every required README "
        f"section: missing {missing}."
    )


def test_manual_documents_installation_per_agent(manual_text):
    """Installation steps differ per agent. The spec must show all five."""
    for agent in ("Volt", "Sage", "Ada", "River", "Iris"):
        assert agent in manual_text, (
            f"manual-format.md does not document the Installation variant "
            f"for {agent}. Without it, the agent will paraphrase steps "
            f"and drift between invocations."
        )


def test_manual_documents_recovery_per_agent(manual_text):
    """Recovery is the worst-case section. Must be agent-specific."""
    text_lower = manual_text.lower()
    assert "recovery" in text_lower, (
        "manual-format.md does not document the Recovery section."
    )


# Wiring format spec

@pytest.fixture(scope="module")
def wiring_text():
    return WIRING_PATH.read_text(encoding="utf-8")


def test_wiring_requires_connection_table(wiring_text):
    """Connection table is the machine-readable half of wiring."""
    text_lower = wiring_text.lower()
    assert "connection table" in text_lower, (
        "wiring-format.md does not require a connection table."
    )


def test_wiring_requires_ascii_diagram(wiring_text):
    """ASCII diagram is the visual half. Required even when the table exists."""
    text_lower = wiring_text.lower()
    assert "ascii diagram" in text_lower, (
        "wiring-format.md does not require an ASCII diagram. Tables alone "
        "do not help beginners build the circuit."
    )


def test_wiring_requires_power_budget(wiring_text):
    """Power budget is the input to Iron Law 4 (Power Budget / Watt)."""
    text_lower = wiring_text.lower()
    assert "power budget" in text_lower, (
        "wiring-format.md does not require a power budget paragraph. "
        "Without it, Iron Law 4's hand-off to Watt has no input."
    )


def test_wiring_requires_safety_notes(wiring_text):
    """Mains, batteries, inductive loads, ADC limits, voltage mismatch."""
    text_lower = wiring_text.lower()
    assert "safety notes" in text_lower, (
        "wiring-format.md does not require safety notes."
    )


# PCB format spec

@pytest.fixture(scope="module")
def pcb_text():
    return PCB_PATH.read_text(encoding="utf-8")


def test_pcb_enumerates_all_four_tiers(pcb_text):
    """Tiers must be a finite, named list. No 'and so on'."""
    text_lower = pcb_text.lower()
    for tier in ("breadboard", "perfboard", "custom pcb", "production"):
        assert tier in text_lower, (
            f"pcb-format.md does not enumerate tier '{tier}'."
        )


def test_pcb_documents_production_files(pcb_text):
    """Production tier must add four files on top of custom-PCB."""
    for fname in (
        "MANUFACTURING.md",
        "COST-ANALYSIS.md",
        "CERTIFICATION.md",
        "TEST-JIG.md",
    ):
        assert fname in pcb_text, (
            f"pcb-format.md does not document '{fname}' as a "
            f"production-tier file."
        )


def test_pcb_disclaims_kicad_file_generation(pcb_text):
    """The agent does not produce .kicad_sch / .kicad_pcb. Spec must say so."""
    text_lower = pcb_text.lower()
    assert "kicad" in text_lower, (
        "pcb-format.md does not mention KiCad. Without the disclaimer that "
        "the agent produces text specs (not KiCad binaries), users will "
        "expect files the agent cannot generate."
    )


def test_pcb_cost_analysis_table_dated(pcb_text):
    """Cost analysis must be dated like the BOM. Same reason."""
    text_lower = pcb_text.lower()
    assert "date the table" in text_lower or "date stamp" in text_lower, (
        "pcb-format.md does not require dating the cost-analysis table."
    )
