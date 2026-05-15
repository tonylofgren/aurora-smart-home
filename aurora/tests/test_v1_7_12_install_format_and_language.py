"""Tests for v1.7.12 features.

Locks the Install-Format-Disclosure Rule, multi-agent README ownership,
root-level files exception, user override clause, and the Language Rule's
explicit per-file enforcement for INSTALL/TROUBLESHOOTING/BOM/WIRING/README.
These were added in v1.7.12 in response to two user reports:

1. Multi-agent projects produced ambiguous README ownership; the rule
   was not explicit about whether the first or last specialist owns
   the root README.
2. INSTALL.md was generated in English even when the conversation was
   in another language, because the install templates in
   `aurora/references/templates/install-*.md` were not flagged for
   translation at runtime.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "aurora" / "SKILL.md"
SOULS = REPO / "aurora" / "souls"
MANUAL_FORMAT = REPO / "aurora" / "references" / "deliverables" / "manual-format.md"
ESPHOME_SKILL = REPO / "esphome" / "SKILL.md"


def test_skill_has_install_format_disclosure_rule():
    content = SKILL.read_text(encoding="utf-8")
    assert "Install-Format-Disclosure Rule" in content, (
        "aurora/SKILL.md missing 'Install-Format-Disclosure Rule' section. "
        "Without it, Sage and Iris ship a single format and users have no "
        "documented path for the alternative install method."
    )
    text_lower = content.lower()
    assert "file-header comment" in text_lower, (
        "Install-Format-Disclosure Rule must require a file-header comment "
        "naming the install method, so the user knows what the file is "
        "without opening the README."
    )


def test_skill_install_format_disclosure_has_per_agent_table():
    content = SKILL.read_text(encoding="utf-8")
    # The per-agent table inside the rule must name Sage's "packages/"
    # as the bundled-format target.
    section = content.split("Install-Format-Disclosure Rule", 1)[1]
    assert "<project>/packages/" in section, (
        "Install-Format-Disclosure Rule must include Sage's packages/ "
        "directory as the bundled-format target."
    )
    assert "Raw Configuration Editor" in section, (
        "Install-Format-Disclosure Rule must include Iris's Raw "
        "Configuration Editor as the UI-paste install path."
    )


def test_skill_has_multi_agent_readme_ownership():
    content = SKILL.read_text(encoding="utf-8")
    assert "Multi-agent README ownership" in content, (
        "Project Structure Rule must define Multi-agent README ownership "
        "so multi-specialist projects produce ONE shared README, not many."
    )
    assert "FIRST specialist" in content, (
        "Multi-agent README ownership must name who writes the root "
        "README first (the FIRST specialist invoked)."
    )
    assert "APPENDS" in content or "appends" in content.lower(), (
        "Multi-agent README ownership must specify that subsequent "
        "specialists APPEND, not overwrite."
    )


def test_skill_has_root_level_files_exception():
    content = SKILL.read_text(encoding="utf-8")
    assert "Root-level files exception" in content, (
        "Project Structure Rule must include a Root-level files exception "
        "listing which root-level files are allowed. Without it the "
        "'ONLY to its own subdirectory' rule contradicts Ada's "
        "HACS-ready output (hacs.json, LICENSE, .github/workflows)."
    )
    for marker in ["hacs.json", "LICENSE", ".github/workflows"]:
        assert marker in content, (
            f"Root-level files exception must explicitly list '{marker}' "
            f"as an allowed root-level file (HACS-ready integrations need it)."
        )


def test_skill_has_user_override_clause():
    content = SKILL.read_text(encoding="utf-8")
    assert "User override" in content, (
        "Project Structure Rule must include a 'User override' clause so "
        "users can explicitly request a different layout (flat, no "
        "subdirectories). Without it the rule reads as an absolute ban."
    )


def test_skill_language_rule_explicit_per_file_enforcement():
    content = SKILL.read_text(encoding="utf-8")
    assert "Explicit per-file enforcement" in content or "Big Five" in content, (
        "Language Rule must include explicit per-file enforcement for "
        "INSTALL.md, TROUBLESHOOTING.md, BOM.md, WIRING.md, and README.md. "
        "The runtime kept defaulting them to English; the rule needs a "
        "named, testable enforcement clause."
    )
    for filename in ["INSTALL.md", "TROUBLESHOOTING.md", "BOM.md", "WIRING.md"]:
        assert filename in content, (
            f"Language Rule must explicitly name '{filename}' as a "
            f"human-readable doc that follows the user's language."
        )


def test_sage_soul_has_format_selection_rule():
    content = (SOULS / "sage.md").read_text(encoding="utf-8")
    assert "Format-selection rule" in content, (
        "Sage Iron Law 3 must include a Format-selection rule that picks "
        "between automation-only and automation+package based on whether "
        "helpers/scripts/template sensors are part of the feature."
    )
    assert "packages/" in content, (
        "Sage Format-selection rule must reference packages/ as the "
        "bundled output path."
    )


def test_sage_soul_has_file_header_comments():
    content = (SOULS / "sage.md").read_text(encoding="utf-8")
    assert "File-header comment" in content, (
        "Sage Iron Law 3 must require a file-header comment block at the "
        "top of every generated YAML file, naming the install method."
    )
    assert "Edit in YAML" in content, (
        "Sage automations/<name>.yaml file-header must reference HA's "
        "'Edit in YAML' UI-paste path."
    )


def test_iris_soul_has_file_header_comment():
    content = (SOULS / "iris.md").read_text(encoding="utf-8")
    assert "File-header comment" in content, (
        "Iris Iron Law 3 must require a file-header comment at the top of "
        "the dashboard YAML naming both install paths."
    )
    assert "Raw Configuration Editor" in content, (
        "Iris file-header must reference Raw Configuration Editor as one "
        "of the install paths."
    )


def test_volt_soul_iron_law_8_mentions_language_for_install_md():
    content = (SOULS / "volt.md").read_text(encoding="utf-8")
    assert "Language Rule" in content, (
        "Volt Iron Law 8 must reference the Language Rule explicitly so "
        "INSTALL.md / TROUBLESHOOTING.md / BOM.md / WIRING.md / README.md "
        "are translated when the user writes in a non-English language."
    )
    text_lower = content.lower()
    assert "translated" in text_lower or "translation" in text_lower, (
        "Volt Iron Law 8 must explicitly call out translation (this was "
        "the v1.7.12 runtime bug: install templates stayed English even "
        "for Swedish users)."
    )


def test_esphome_skill_delivery_contract_mentions_language():
    content = ESPHOME_SKILL.read_text(encoding="utf-8")
    assert "Language Rule" in content, (
        "esphome/SKILL.md Delivery Contract must reference the Language "
        "Rule so the specialist translates install templates instead of "
        "shipping English INSTALL.md to non-English users."
    )


def test_manual_format_describes_hierarchy():
    content = MANUAL_FORMAT.read_text(encoding="utf-8")
    assert "Project structure context" in content, (
        "manual-format.md must describe the hierarchical project "
        "structure so the agent knows whether it is writing the root "
        "README or a sub-README."
    )
    for subdir in [
        "esphome/",
        "automations/",
        "custom_components/",
        "dashboards/",
        "node-red-flows/",
    ]:
        assert subdir in content, (
            f"manual-format.md must reference '{subdir}' as a canonical "
            f"subdirectory."
        )


def test_manual_format_describes_multi_agent_ownership():
    content = MANUAL_FORMAT.read_text(encoding="utf-8")
    assert "Multi-agent README ownership" in content, (
        "manual-format.md must document Multi-agent README ownership so "
        "specialists know whether to write the root README or append a "
        "section."
    )
    text_lower = content.lower()
    assert "first specialist" in text_lower, (
        "manual-format.md Multi-agent README ownership must name who "
        "writes the root README first."
    )


def test_manual_format_describes_install_format_disclosure():
    content = MANUAL_FORMAT.read_text(encoding="utf-8")
    assert "Install-Format-Disclosure" in content, (
        "manual-format.md must document Install-Format-Disclosure so the "
        "README Installation section presents Option A / Option B for "
        "Sage and Iris."
    )


def test_manual_format_sage_install_has_option_a_b():
    content = MANUAL_FORMAT.read_text(encoding="utf-8")
    sage_idx = content.find("### Sage (HA YAML)")
    assert sage_idx >= 0, "manual-format.md missing Sage Installation variant."
    sage_block = content[sage_idx:sage_idx + 4000]
    assert "Option A" in sage_block and "Option B" in sage_block, (
        "Sage Installation variant in manual-format.md must list "
        "Option A (UI paste) and Option B (package)."
    )


def test_manual_format_iris_install_has_option_a_b():
    content = MANUAL_FORMAT.read_text(encoding="utf-8")
    iris_idx = content.find("### Iris (dashboard)")
    assert iris_idx >= 0, "manual-format.md missing Iris Installation variant."
    iris_block = content[iris_idx:iris_idx + 4000]
    assert "Option A" in iris_block and "Option B" in iris_block, (
        "Iris Installation variant in manual-format.md must list "
        "Option A (Raw Configuration Editor) and Option B (YAML-mode dashboard)."
    )
