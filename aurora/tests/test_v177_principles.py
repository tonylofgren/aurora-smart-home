"""Pin the four principles introduced in v1.7.7:

A. Volt Iron Law 1 demands a specific board MODEL, not just chip family.
B. Volt Iron Law 8 includes a deployment-method question with 4 options
   and conditional deliverables, plus install-template files exist.
C. aurora/SKILL.md carries a global Question Rule that requires every
   question to ship with a recommendation and a reason.
D. aurora/SKILL.md carries a Language Rule that splits deliverable
   content into 'user language' vs 'always English'.

If any of these regress, the runtime issues from the 2026-05-15 test
session come back — Volt guesses a board, Volt suggests local-CLI as
default, questions ship as bare options, READMEs come out in English
when the user typed Swedish.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AURORA_SKILL = REPO_ROOT / "aurora" / "SKILL.md"
VOLT_SOUL = REPO_ROOT / "aurora" / "souls" / "volt.md"
TEMPLATES_DIR = REPO_ROOT / "aurora" / "references" / "templates"


def test_volt_iron_law_1_demands_specific_board_model():
    """Chip family is not enough — Volt must ask for the dev-board.
    The 2026-05-15 session revealed Volt defaulting to a generic
    breadboard config when the user said only 'ESP32-S3'."""
    text = VOLT_SOUL.read_text(encoding="utf-8")
    assert "board model" in text.lower(), (
        "Iron Law 1 must require the specific board model, not just chip "
        "family. Without this, Volt picks a generic breadboard layout."
    )
    assert "DevKitC" in text or "Lolin" in text or "XIAO" in text, (
        "Iron Law 1 must name specific board examples (DevKitC, Lolin, "
        "XIAO, etc.) so the agent knows what 'specific board' means."
    )


def test_volt_iron_law_8_has_deployment_method_question():
    """Volt must ask how the user will flash the device before
    generating YAML. Without this, Volt defaults to 'esphome run' even
    for users without Python installed."""
    text = VOLT_SOUL.read_text(encoding="utf-8")
    lower = text.lower()
    assert "deployment method" in lower, (
        "Iron Law 8 must include a deployment-method-question section."
    )
    for method in ["ha esphome add-on", "github actions", "esphome cli", "docker"]:
        assert method in lower, (
            f"Iron Law 8 deployment-method options must include '{method}'."
        )


def test_install_templates_exist_for_all_deployment_methods():
    """Each deployment method must have a template snippet so Volt has
    copy-paste-ready content per option."""
    expected = {
        "install-ha-addon.md",
        "install-github-actions.md",
        "install-cli.md",
        "install-docker.md",
        "build-firmware-workflow.yml",
    }
    have = {p.name for p in TEMPLATES_DIR.glob("*")}
    missing = expected - have
    assert not missing, f"Missing install templates: {missing}"


def test_aurora_skill_has_question_rule():
    """Every question Aurora or a specialist asks must include a
    recommendation and a reason. The rule lives in aurora/SKILL.md so
    all agents inherit it."""
    text = AURORA_SKILL.read_text(encoding="utf-8")
    assert "Question Rule" in text, (
        "aurora/SKILL.md must declare the Question Rule that bans bare-option questions."
    )
    assert "Recommended:" in text, (
        "Question Rule must show the 'Recommended: X — reason' format "
        "explicitly so the agent knows the exact shape to emit."
    )


def test_aurora_skill_has_language_rule_for_deliverables():
    """README/INSTALL/TROUBLESHOOTING in the user's project folder must
    be written in the user's language. Code stays English. The rule
    lives in aurora/SKILL.md so all specialists inherit it."""
    text = AURORA_SKILL.read_text(encoding="utf-8")
    assert "Language Rule for Deliverables" in text, (
        "aurora/SKILL.md must declare the Language Rule for deliverables."
    )
    lower = text.lower()
    for marker in ["user's detected language", "always english", "entity_id"]:
        assert marker.lower() in lower, (
            f"Language Rule must explicitly cover '{marker}' so the boundary "
            "between human text and code is unambiguous."
        )


def test_question_rule_and_language_rule_grouped_together():
    """Both rules apply globally, so they belong in one Communication
    Rules section. Grouping makes it harder to delete one without
    noticing the other."""
    text = AURORA_SKILL.read_text(encoding="utf-8")
    assert "Communication Rules" in text, (
        "aurora/SKILL.md must group Question Rule and Language Rule under a "
        "Communication Rules header."
    )
    comm_pos = text.index("Communication Rules")
    q_pos = text.index("Question Rule")
    l_pos = text.index("Language Rule for Deliverables")
    assert comm_pos < q_pos < l_pos, (
        "Communication Rules header must precede both Question Rule and "
        "Language Rule, in that order."
    )
