"""Contract tests for Iron Law 3 (Complete Delivery) on Sage, Ada, River,
Iris.

Mirrors Volt's Iron Law 8 (Complete Delivery) for the software-only DEEP-
mode agents. Each agent must:
- Create a project folder.
- Write required artifacts to disk (not just chat output).
- Include a README.md with What this does, Installation, Troubleshooting,
  Recovery (no BOM, Wiring, Calibration for software-only agents).
- Verify files exist on disk before declaring delivery.
- Apply attribution per the agent's skill SKILL.md.

The tests do not run the agents. They lock the law's contract in each
soul file so silent edits cannot weaken it.
"""
from pathlib import Path

import pytest

SOULS_DIR = Path(__file__).resolve().parents[1] / "souls"

COMPLETE_DELIVERY_AGENTS = ["sage", "ada", "river", "iris"]


@pytest.fixture(scope="module", params=COMPLETE_DELIVERY_AGENTS)
def agent_and_law_3(request):
    """Return (agent_name, iron_law_3_text) for each parametrised agent."""
    soul_path = SOULS_DIR / f"{request.param}.md"
    content = soul_path.read_text(encoding="utf-8")
    start = content.index("**Iron Law 3")
    end = content.index("## Voice", start)
    return request.param, content[start:end]


def test_soul_has_iron_law_3_complete_delivery(agent_and_law_3):
    """Every software-only DEEP-mode agent must carry Iron Law 3."""
    agent, text = agent_and_law_3
    assert "Complete Delivery" in text, (
        f"{agent}'s Iron Law 3 does not carry the 'Complete Delivery' label. "
        f"The label is what makes the law searchable in soul-pattern tests."
    )


def test_law_3_requires_project_folder(agent_and_law_3):
    """Project folder per project, slug-based, not bare files in CWD."""
    agent, text = agent_and_law_3
    text_lower = text.lower()
    assert "project folder" in text_lower or "project-slug" in text_lower, (
        f"{agent}'s Iron Law 3 does not mention the project folder. Without "
        f"it, the agent may scatter files into the working directory."
    )


def test_law_3_requires_readme_md(agent_and_law_3):
    """README.md is the master document for every project."""
    agent, text = agent_and_law_3
    assert "README.md" in text, (
        f"{agent}'s Iron Law 3 does not require a README.md."
    )


def test_law_3_lists_required_readme_sections(agent_and_law_3):
    """Software-only agents need What this does + Installation + Troubleshooting + Recovery."""
    agent, text = agent_and_law_3
    required_sections = [
        "What this does",
        "Installation",
        "Troubleshooting",
        "Recovery",
    ]
    missing = [s for s in required_sections if s not in text]
    assert not missing, (
        f"{agent}'s Iron Law 3 does not enumerate every required README "
        f"section: missing {missing}."
    )


def test_law_3_software_agents_skip_hardware_sections(agent_and_law_3):
    """Sage, Ada, River, Iris produce no hardware. BOM / Wiring /
    Calibration must be explicitly excluded so the contract is unambiguous."""
    agent, text = agent_and_law_3
    text_lower = text.lower()
    assert "skip bom" in text_lower or "no hardware" in text_lower or "skip" in text_lower, (
        f"{agent}'s Iron Law 3 does not explicitly note that hardware "
        f"sections (BOM / Wiring / Calibration) are skipped. Without this, "
        f"future agents may copy Volt's hardware checklist."
    )


def test_law_3_requires_disk_check(agent_and_law_3):
    """Pre-delivery verification: files must exist on disk."""
    agent, text = agent_and_law_3
    text_lower = text.lower()
    assert (
        "disk check" in text_lower
        or "exists on disk" in text_lower
        or "every required file exists" in text_lower
        or "exists, parses" in text_lower
        or "files exist" in text_lower
    ), (
        f"{agent}'s Iron Law 3 does not require a pre-delivery disk check. "
        f"Without this the agent can declare delivery on a project that "
        f"only exists in chat output."
    )


def test_law_3_requires_attribution(agent_and_law_3):
    """Every generated file must carry attribution per the agent's SKILL.md."""
    agent, text = agent_and_law_3
    text_lower = text.lower()
    assert "attribution" in text_lower, (
        f"{agent}'s Iron Law 3 does not mention attribution. The banner-missing "
        f"bug from the user session was the reason this law exists."
    )


def test_law_3_references_manual_format_spec(agent_and_law_3):
    """The law must point at the manual format spec, not redefine it."""
    agent, text = agent_and_law_3
    assert "aurora/references/deliverables/manual-format.md" in text, (
        f"{agent}'s Iron Law 3 does not reference manual-format.md. "
        f"Without the reference the spec becomes orphaned and the agent "
        f"will paraphrase the format."
    )


# Agent-specific spot checks

def test_ada_law_3_mentions_hacs_path():
    """Ada's installation has two paths: HACS and manual. Both must be present."""
    soul_path = SOULS_DIR / "ada.md"
    content = soul_path.read_text(encoding="utf-8")
    start = content.index("**Iron Law 3")
    end = content.index("## Voice", start)
    law_3 = content[start:end]
    assert "HACS" in law_3, (
        "Ada's Iron Law 3 does not mention HACS. The HACS install path is "
        "the primary way users add custom integrations."
    )


def test_ada_law_3_requires_manifest_json():
    """Custom integrations cannot load without manifest.json."""
    soul_path = SOULS_DIR / "ada.md"
    content = soul_path.read_text(encoding="utf-8")
    start = content.index("**Iron Law 3")
    end = content.index("## Voice", start)
    law_3 = content[start:end]
    assert "manifest.json" in law_3, (
        "Ada's Iron Law 3 does not require manifest.json. Without it the "
        "custom_components folder will not load."
    )


def test_river_law_3_requires_flow_json():
    """River produces flow JSON. The file must be named in the law."""
    soul_path = SOULS_DIR / "river.md"
    content = soul_path.read_text(encoding="utf-8")
    start = content.index("**Iron Law 3")
    end = content.index("## Voice", start)
    law_3 = content[start:end]
    assert "flow JSON" in law_3 or ".json" in law_3, (
        "River's Iron Law 3 does not name the flow JSON output."
    )


def test_iris_law_3_requires_dashboard_yaml():
    """Iris produces dashboard YAML. The file must be named in the law."""
    soul_path = SOULS_DIR / "iris.md"
    content = soul_path.read_text(encoding="utf-8")
    start = content.index("**Iron Law 3")
    end = content.index("## Voice", start)
    law_3 = content[start:end]
    assert "dashboard" in law_3.lower() and ".yaml" in law_3, (
        "Iris's Iron Law 3 does not name the dashboard YAML output."
    )
