"""Contract tests for the orchestrator working-method rules added 2026-06.

Guards the routing-precedence rules, the Vera safety gate, the audited
model-tier mapping, and the Question/Language rule requirements in
aurora/SKILL.md against silent removal or weakening, in the same spirit
as the Iron Law presence tests.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL = (REPO_ROOT / "aurora" / "SKILL.md").read_text(encoding="utf-8")


class TestRoutingPrecedence:
    def test_precedence_section_exists(self):
        assert "### Routing Precedence" in SKILL

    def test_safety_gate_wins_first(self):
        section = SKILL.split("### Routing Precedence")[1].split("## Step")[0]
        assert "Safety gate wins" in section
        assert section.index("Safety gate wins") < section.index("Deliverable beats transport")

    def test_volt_nano_tiebreaker(self):
        assert "route to Nano only when the protocol itself is the deliverable" in SKILL

    def test_watt_never_primary_builder(self):
        assert "Watt is a pre-check, not a builder" in SKILL

    def test_glitch_requires_existing_breakage(self):
        assert "Glitch needs something broken" in SKILL


class TestSafetyGate:
    def test_step_2_6_exists(self):
        assert "## Step 2.6: Safety Gate" in SKILL

    def test_vera_runs_before_build_agent(self):
        gate = SKILL.split("## Step 2.6: Safety Gate")[1].split("## ")[0]
        assert "MUST start with Vera" in gate

    def test_quick_promotes_to_deep_on_trigger(self):
        gate = SKILL.split("## Step 2.6: Safety Gate")[1].split("## ")[0]
        assert "becomes DEEP mode" in gate

    def test_triggers_cover_known_hazards(self):
        gate = SKILL.split("## Step 2.6: Safety Gate")[1].split("## ")[0]
        for hazard in ("Battery", "mains", "5V", "relays", "Water", "Outdoor"):
            assert hazard.lower() in gate.lower(), f"safety trigger missing: {hazard}"


class TestModelTierMapping:
    def test_audited_mapping_exists(self):
        assert re.search(r"### Model Names \(audited \d{4}-\d{2}-\d{2}\)", SKILL)

    def test_mapping_names_concrete_models(self):
        block = SKILL.split("### Model Names")[1].split("### ")[0]
        for model in ("Fable", "Opus", "Sonnet", "Haiku"):
            assert model in block, f"model tier missing from mapping: {model}"

    def test_fallback_chain_includes_fable(self):
        chain = SKILL.split("### Fallback Chain")[1].split("### ")[0]
        assert "fable" in chain and "haiku" in chain
        assert chain.index("fable") < chain.index("opus")


class TestCommunicationRuleContracts:
    def test_question_rule_requires_options_plus_recommendation(self):
        rule = SKILL.split("### Question Rule")[1].split("### ")[0]
        assert "every available option listed" in rule
        assert "Recommended:" in rule

    def test_language_rule_deep_mode_consistency(self):
        rule = SKILL.split("### Language Rule for Deliverables")[1].split("### ")[0]
        assert "DEEP mode language consistency" in rule
        assert "detects the language ONCE" in rule
