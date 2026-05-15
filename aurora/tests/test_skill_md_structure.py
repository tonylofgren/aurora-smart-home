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
