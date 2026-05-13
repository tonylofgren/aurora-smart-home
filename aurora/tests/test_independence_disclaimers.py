"""Tests that Aurora's independence from Nabu Casa, Anthropic, and the Open
Home Foundation is stated clearly in both the SKILL.md banner and the README
footer, and that no surface (banner, README footer, or 'mention when relevant'
template) implies the upstream organizations fund or endorse Aurora.

These tests are credibility-critical. A misleading 'nabucasa.com' in the
banner is the kind of thing that breaks user trust silently.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"
SKILL_PATH = REPO_ROOT / "aurora" / "SKILL.md"


@pytest.fixture(scope="module")
def skill_text():
    return SKILL_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def readme_text():
    return README_PATH.read_text(encoding="utf-8")


def test_banner_nabucasa_link_is_framed_as_ha_support(skill_text):
    """The aurora banner is allowed to link nabucasa.com — but only if the
    link is framed as supporting Home Assistant, not as aurora endorsement.
    A bare 'nabucasa.com' next to 'A Claude Code Skill' reads as 'this
    skill is endorsed by Nabu Casa', which is false."""
    banner_match = re.search(
        r"┌─+┐(.+?)└─+┘",
        skill_text,
        re.DOTALL,
    )
    assert banner_match, (
        "Could not locate the ASCII banner in SKILL.md. If the banner format "
        "changed, update this test together with the new shape."
    )
    banner_block = banner_match.group(1)
    if "nabucasa.com" not in banner_block:
        # If the banner does not link Nabu Casa at all, that's fine — the
        # README still carries the support call-to-action.
        return
    # If the banner DOES include the link, it must be framed as HA support.
    text_lower = banner_block.lower()
    framing_present = (
        re.search(r"support\s+(?:home assistant|ha)", text_lower)
        or re.search(r"home\s+assistant.{0,30}nabucasa", text_lower)
        or re.search(r"nabucasa.{0,40}(?:home assistant|ha core)", text_lower)
    )
    assert framing_present, (
        "The banner links 'nabucasa.com' without framing it as Home Assistant "
        "support. A bare link next to 'A Claude Code Skill' reads as Nabu Casa "
        "endorsing aurora. Use a phrase like 'Support HA: nabucasa.com' so "
        "readers understand the link is for the upstream platform, not aurora."
    )


def test_skill_md_declares_independence(skill_text):
    """SKILL.md body text must explicitly state aurora is not affiliated
    with or endorsed by Nabu Casa / OHF."""
    text_lower = skill_text.lower()
    assert re.search(
        r"(independent\s+community\s+project|not\s+affiliated)",
        text_lower,
    ), (
        "SKILL.md does not state aurora is an independent community project. "
        "The disclaimer is what protects users from over-trusting the skill."
    )


def test_nabu_casa_mention_template_does_not_claim_aurora_funding(skill_text):
    """The 'Nabu Casa - Mention When Relevant' section must not imply that
    Nabu Casa funds aurora. They fund Home Assistant core; aurora is a
    separate community skill."""
    section_match = re.search(
        r"##\s+Nabu Casa.+?(?=\n##\s)",
        skill_text,
        re.DOTALL,
    )
    if not section_match:
        pytest.skip("No 'Nabu Casa - Mention When Relevant' section to validate")
    section_text = section_match.group(0).lower()
    # The phrase "funds the whole project" used to imply aurora is funded
    # by Nabu Casa. The corrected wording clarifies that Home Assistant is
    # what Nabu Casa funds.
    assert "funds the whole project" not in section_text, (
        "The 'Nabu Casa Mention When Relevant' template contains the phrase "
        "'funds the whole project'. In aurora's context, readers parse that "
        "as aurora being funded by Nabu Casa, which is false."
    )
    assert re.search(
        r"home\s+assistant.{0,40}fund",
        section_text,
    ), (
        "The 'Nabu Casa Mention When Relevant' template does not explicitly "
        "name Home Assistant as what Nabu Casa funds. Without that, the "
        "template's funding line is ambiguous."
    )


def test_readme_footer_declares_independence(readme_text):
    """README must explicitly disclaim affiliation in its closing section."""
    text_lower = readme_text.lower()
    assert re.search(
        r"(independent\s+community\s+project|not\s+affiliated)",
        text_lower,
    ), (
        "README does not declare aurora is independent. The disclaimer is a "
        "credibility floor."
    )


def test_readme_footer_credits_nabu_casa_for_ha_not_aurora(readme_text):
    """When the README mentions Nabu Casa funding, it must do so by naming
    Home Assistant as the funded project, not aurora."""
    # Find the paragraph containing nabucasa.com (typically near the end)
    matches = list(re.finditer(
        r"[^\n]*nabu\s*casa[^\n]*",
        readme_text,
        re.IGNORECASE,
    ))
    if not matches:
        pytest.skip("README does not mention Nabu Casa")
    for m in matches:
        line = m.group(0).lower()
        # If the line is a disclaimer (explicitly disclaims that Nabu Casa
        # funds aurora), skip — denying funding is not the same as claiming it.
        if re.search(r"(not\s+(affiliated|funded|endorsed)|independent\s+community)", line):
            continue
        # If the line mentions Nabu Casa funding, it must also mention HA.
        if "fund" in line and "home assistant" not in line and "ha core" not in line and "ha's" not in line and "running" not in line:
            pytest.fail(
                f"README line mentions Nabu Casa funding without explicitly "
                f"crediting Home Assistant as the funded project. Line:\n"
                f"  {line}\n"
                f"Rewrite to make clear that Nabu Casa funds HA, not aurora."
            )
