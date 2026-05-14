"""Contract tests for the Delivery Contract that every output-producing skill
must enforce.

Background: In v1.7.3 a runtime regression surfaced where Aurora generated a
YAML file in the working directory without a project folder, without a
README, without BOM/wiring/installation, and without the attribution banner.
The root cause was that esphome/SKILL.md (and home-assistant + ha-integration-dev)
told the agent to "save file to current directory" and offered a "Copy from chat"
output option. Iron Law 8 (in volt.md) said the opposite but the soul was never
loaded into context, so the SKILL.md text won.

v1.7.4 fixes the SKILL.md files: no chat-only output option, every artifact
written to a project folder. These tests lock the new contract so a future
edit cannot silently restore the regression.
"""
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Skills that produce on-disk output for the user
OUTPUT_PRODUCING_SKILLS = [
    REPO_ROOT / "esphome" / "SKILL.md",
    REPO_ROOT / "home-assistant" / "SKILL.md",
    REPO_ROOT / "ha-integration-dev" / "SKILL.md",
]


@pytest.mark.parametrize("skill_path", OUTPUT_PRODUCING_SKILLS, ids=lambda p: p.parent.name)
def test_skill_does_not_offer_chat_only_output(skill_path):
    """No SKILL.md may offer 'Copy from chat' as an output option. That
    pattern is what caused the v1.7.3 runtime regression (BOM, wiring,
    installation written to chat instead of to disk)."""
    text = skill_path.read_text(encoding="utf-8")
    assert "Copy from chat" not in text, (
        f"{skill_path.parent.name}/SKILL.md offers 'Copy from chat' as an "
        f"output option. This bypasses the delivery contract — wiring, BOM, "
        f"and README end up in chat instead of as files in the project folder. "
        f"Remove the option entirely; every artifact must be written to disk."
    )


@pytest.mark.parametrize("skill_path", OUTPUT_PRODUCING_SKILLS, ids=lambda p: p.parent.name)
def test_skill_requires_project_folder(skill_path):
    """Each output-producing SKILL.md must instruct the agent to create a
    project folder. Bare files in the current working directory are not
    deliverable per Iron Law 8 / Iron Law 3."""
    text = skill_path.read_text(encoding="utf-8")
    assert "project folder" in text.lower(), (
        f"{skill_path.parent.name}/SKILL.md does not mention a 'project folder'. "
        f"Iron Law 8 (Volt) and Iron Law 3 (Sage/Ada/River/Iris) require a "
        f"folder per project, not bare files in the CWD."
    )


@pytest.mark.parametrize("skill_path", OUTPUT_PRODUCING_SKILLS, ids=lambda p: p.parent.name)
def test_skill_states_chat_is_not_delivery(skill_path):
    """Each output-producing SKILL.md must explicitly state that chat output
    is not delivery. The explicit statement is what stops the agent from
    pasting wiring or BOM in chat as a shortcut."""
    text = skill_path.read_text(encoding="utf-8")
    text_lower = text.lower()
    valid_phrases = [
        "chat output is not delivery",
        "no chat-only output",
        "no chat-only path",
        "every artifact is written to disk",
        "every artifact written to disk",
    ]
    assert any(phrase in text_lower for phrase in valid_phrases), (
        f"{skill_path.parent.name}/SKILL.md does not state that chat output "
        f"is not delivery. Without this explicit phrase, the agent may treat "
        f"described artifacts as delivered. The v1.7.3 regression happened "
        f"exactly here."
    )


def test_esphome_skill_has_delivery_contract_block():
    """esphome/SKILL.md must carry a top-of-file 'Delivery Contract' block
    before the 'First Step: Determine Scope' section. Putting the contract
    earlier than the scope question is what makes Volt read it first."""
    text = (REPO_ROOT / "esphome" / "SKILL.md").read_text(encoding="utf-8")
    delivery_contract_idx = text.find("## Delivery Contract")
    first_step_idx = text.find("## First Step")
    assert delivery_contract_idx != -1, (
        "esphome/SKILL.md is missing the '## Delivery Contract' block."
    )
    assert first_step_idx != -1, (
        "esphome/SKILL.md is missing the '## First Step' section."
    )
    assert delivery_contract_idx < first_step_idx, (
        "esphome/SKILL.md has the Delivery Contract block AFTER First Step. "
        "It must come BEFORE so the agent reads delivery rules before scope."
    )


def test_esphome_delivery_contract_references_soul_and_specs():
    """The Delivery Contract block must point at Volt's soul (where Iron Law
    8 lives) and at the deliverable format specs."""
    text = (REPO_ROOT / "esphome" / "SKILL.md").read_text(encoding="utf-8")
    contract_start = text.find("## Delivery Contract")
    contract_end = text.find("## First Step", contract_start)
    contract = text[contract_start:contract_end]
    assert "aurora/souls/volt.md" in contract, (
        "esphome/SKILL.md Delivery Contract does not reference volt.md. "
        "The soul is where Iron Law 8 lives."
    )
    assert "aurora/references/deliverables" in contract, (
        "esphome/SKILL.md Delivery Contract does not reference the format "
        "specs in aurora/references/deliverables/."
    )
