"""Tests that every aurora soul appears as a uniquely-presented entry in the
top-level README.md agent roster.

If a future edit silently drops an agent from the roster (or removes the
voice tagline format that makes the roster distinctive), this suite fails.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"
SOULS_DIR = Path(__file__).resolve().parents[1] / "souls"

# Soul filename (without .md) → display name in README.
ALL_AGENTS = {
    "aurora": "Aurora",
    "volt": "Volt",
    "nano": "Nano",
    "echo": "Echo",
    "watt": "Watt",
    "sage": "Sage",
    "ada": "Ada",
    "mira": "Mira",
    "river": "River",
    "iris": "Iris",
    "atlas": "Atlas",
    "glitch": "Glitch",
    "probe": "Probe",
    "vera": "Vera",
    "lens": "Lens",
    "manual": "Manual",
    "scout": "Scout",
    "lore": "Lore",
    "forge": "Forge",
    "grid": "Grid",
    "canvas": "Canvas",
}


@pytest.fixture(scope="module")
def readme_text():
    return README_PATH.read_text(encoding="utf-8")


def test_one_soul_per_listed_agent():
    """Every roster entry must back onto an actual soul file. No orphan agents."""
    for soul_name in ALL_AGENTS:
        soul_path = SOULS_DIR / f"{soul_name}.md"
        assert soul_path.is_file(), (
            f"Roster lists agent '{soul_name}' but souls/{soul_name}.md is missing."
        )


def test_all_agents_listed_in_roster(readme_text):
    """Every aurora soul must appear in the README roster with bold name formatting."""
    missing = []
    for soul_name, display_name in ALL_AGENTS.items():
        # Roster format: **Name** or 🏠 **Name** — ...
        pattern = rf"\*\*{re.escape(display_name)}\*\*"
        if not re.search(pattern, readme_text):
            missing.append(display_name)
    assert not missing, (
        f"Agents missing from the README roster: {missing}. "
        f"Every soul in aurora/souls/ must have a presentation entry."
    )


def test_every_agent_entry_has_a_voice_tagline(readme_text):
    """Each agent's roster entry must include an italic 'voice' quote, that
    is what makes the roster distinctive instead of a bland name list.

    The separator between **Name** and the domain text accepts em-dash or
    pipe so the format respects the no-em-dash docs preference."""
    missing = []
    for soul_name, display_name in ALL_AGENTS.items():
        pattern = rf"\*\*{re.escape(display_name)}\*\*\s*[—|]\s*[^\n]*?\*\"[^\"]+\"\*"
        if not re.search(pattern, readme_text):
            missing.append(display_name)
    assert not missing, (
        f"Agents in the roster without a voice tagline: {missing}. "
        f"The roster format is: emoji **Name** [—|] domain. *\"voice line.\"*"
    )


def test_roster_does_not_duplicate_an_agent(readme_text):
    """Within the roster section, each agent should appear exactly once.
    Other parts of README may mention an agent name multiple times — this
    test only checks the roster block to catch copy-paste errors there."""
    roster_match = re.search(
        r"^##\s+Meet the Aurora team\b(.+?)(?=\n##\s|\n---\s*\n)",
        readme_text,
        re.DOTALL | re.MULTILINE,
    )
    assert roster_match, (
        "Could not locate the roster section (anchor: '## Meet the Aurora team' H2). "
        "If the heading changed, update this test together with the README."
    )
    roster_block = roster_match.group(1)
    duplicates = []
    for display_name in ALL_AGENTS.values():
        pattern = rf"\*\*{re.escape(display_name)}\*\*"
        count = len(re.findall(pattern, roster_block))
        if count > 1:
            duplicates.append((display_name, count))
    assert not duplicates, (
        f"Agents bolded multiple times inside the roster section: {duplicates}. "
        f"Each agent should have exactly one roster entry."
    )


def test_roster_count_matches_advertised_total(readme_text):
    """README must consistently advertise the team size. The roster intro
    says '1 orchestrator + 20 named specialists'; ALL_AGENTS must match."""
    assert "1 orchestrator + 20 named specialists" in readme_text, (
        "README roster intro no longer states '1 orchestrator + 20 named specialists'. "
        "If the team size changed, update both the intro and ALL_AGENTS together."
    )
    assert len(ALL_AGENTS) == 21, (
        f"This test file lists {len(ALL_AGENTS)} agents, expected 21 "
        f"(1 orchestrator + 20 specialists). If a new agent has been added, "
        f"both the README roster and ALL_AGENTS here must be updated together."
    )
