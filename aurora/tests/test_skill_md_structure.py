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


def test_skill_version_matches_marketplace():
    """Version string in aurora/SKILL.md must match marketplace.json — bumping
    one without the other was the root of multiple drifts (v1.6.x, v1.7.x).
    Reading both from disk keeps this test correct across future bumps."""
    import json

    content = SKILL_PATH.read_text(encoding="utf-8")
    marketplace = json.loads(
        (SKILL_PATH.parents[1] / ".claude-plugin" / "marketplace.json").read_text(
            encoding="utf-8"
        )
    )
    version = marketplace["version"]
    assert f"v{version}" in content, (
        f"aurora/SKILL.md does not mention v{version} from marketplace.json. "
        "When bumping the version, update SKILL.md output line + banner "
        "release date together with marketplace.json."
    )


def test_skill_has_reactivation_check_before_version_check():
    """Aurora must skip the banner and gh call when /aurora:aurora is invoked
    twice in the same conversation. Without a guard, every reactivation
    re-runs the version check, reprints the banner, and re-asks the opening
    question — pure noise mid-session."""
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "Reactivation Check" in content, (
        "aurora/SKILL.md is missing the Reactivation Check section. Without "
        "it, /aurora:aurora typed a second time re-runs version-check + "
        "banner + opening question, which wastes tokens and confuses the user."
    )
    reactivation_pos = content.index("Reactivation Check")
    version_check_pos = content.index("Version Check")
    assert reactivation_pos < version_check_pos, (
        "Reactivation Check must come BEFORE Version Check so the gh call is "
        "skipped on reactivation."
    )


def test_skill_has_project_structure_rule():
    """aurora/SKILL.md must define the Project Structure Rule that maps each
    agent to its canonical subdirectory. Without it, agents drop files at
    the project root and the build becomes a flat pile instead of an
    HA-conventional hierarchy."""
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "Project Structure Rule" in content, (
        "aurora/SKILL.md is missing the Project Structure Rule. Without it, "
        "each agent invents its own subdirectory and the canonical hierarchy "
        "(esphome/, automations/, dashboards/, node-red-flows/, "
        "custom_components/) is not enforced."
    )
    required_subdirs = [
        "<project>/esphome/",
        "<project>/automations/",
        "<project>/dashboards/",
        "<project>/node-red-flows/",
        "<project>/custom_components/",
    ]
    missing = [s for s in required_subdirs if s not in content]
    assert not missing, (
        f"Project Structure Rule does not enumerate every canonical "
        f"subdirectory: missing {missing}."
    )


def test_souls_enforce_project_subdirectory():
    """Every soul that writes files must point at its canonical subdirectory
    (Iron Law-enforced). A soul that says 'create <project-slug>/' without
    naming the subdirectory falls back to root-level files, which is the
    flat-pile regression Project Structure Rule fixes."""
    souls_dir = SKILL_PATH.parent / "souls"
    expected = {
        "volt.md": "<project>/esphome/",
        "sage.md": "<project>/automations/",
        "ada.md": "<project>/custom_components/",
        "river.md": "<project>/node-red-flows/",
        "iris.md": "<project>/dashboards/",
    }
    missing = []
    for soul_filename, subdir in expected.items():
        content = (souls_dir / soul_filename).read_text(encoding="utf-8")
        if subdir not in content:
            missing.append((soul_filename, subdir))
    assert not missing, (
        f"Souls missing their canonical subdirectory reference: {missing}. "
        f"Each soul's Iron Law must name the agent's <project>/<subdir>/ path."
    )


def test_clustered_questions_offer_run_with_defaults():
    """When Aurora or a specialist clusters multiple related questions in a
    single prompt, the prompt must close with a plain-language 'run with
    recommendations?' question (Yes / No / own choices) instead of asking
    the user to type 'default' or remember a string of numbers. v1.7.10
    UX fix after a user found '1, 1, 1' clumsy."""
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "Clustered questions" in content, (
        "aurora/SKILL.md is missing the 'Clustered questions' sub-section "
        "of the Question Rule. Without it, specialists default to asking "
        "the user to remember and type three numbers for board + tier + "
        "deployment, which is high cognitive load."
    )
    text_lower = content.lower()
    assert "run with all the recommendations" in text_lower or "run with the recommendations" in text_lower or "do you want to run with" in text_lower, (
        "aurora/SKILL.md Clustered Questions block does not include the "
        "'run with recommendations?' closing question. The closing question "
        "is what replaces the typed 'default' shortcut with plain language."
    )


def test_aurora_skill_loads_specialist_soul_before_delegating():
    """Aurora orchestrator must instruct the agent to load the specialist's
    soul file from aurora/souls/ before delegating. Without this, Iron Laws
    (Iron Law 8 for Volt, Iron Law 3 for Sage/Ada/River/Iris) never reach
    the runtime context and the delivery contract is bypassed."""
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "Load Specialist Soul" in content or "load the specialist's soul" in content.lower(), (
        "aurora/SKILL.md does not instruct the orchestrator to load the "
        "specialist's soul before delegating. Without this step, Iron Laws "
        "are invisible at runtime and the delivery contract is silently "
        "bypassed (the v1.7.3 runtime regression)."
    )
    assert "aurora/souls/" in content, (
        "aurora/SKILL.md does not reference aurora/souls/ where soul files live."
    )


def test_skill_has_version_check_section():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "## Version Check" in content, (
        "aurora/SKILL.md is missing the 'Version Check' section. Without "
        "it Aurora cannot warn users when a newer plugin version exists."
    )


def test_skill_version_check_uses_gh_cli():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "gh release view" in content, (
        "aurora/SKILL.md does not invoke 'gh release view' for the version "
        "check. gh CLI is the single source of truth for the latest tag."
    )


def test_skill_version_check_does_not_use_webfetch():
    content = SKILL_PATH.read_text(encoding="utf-8")
    skill_body = content.split("---", 2)[2]
    assert "WebFetch" not in skill_body or "Do not" in skill_body, (
        "aurora/SKILL.md body references WebFetch as an active fetching path. "
        "WebFetch fallback leaks tool errors to the user when blocked by "
        "context-mode-style wrappers. Only gh CLI should be used."
    )


def test_skill_allowed_tools_excludes_webfetch():
    content = SKILL_PATH.read_text(encoding="utf-8")
    frontmatter = content.split("---", 2)[1]
    assert "WebFetch" not in frontmatter, (
        "aurora/SKILL.md frontmatter still lists WebFetch in allowed-tools. "
        "v1.7.3 removed WebFetch entirely from the version-check chain."
    )
