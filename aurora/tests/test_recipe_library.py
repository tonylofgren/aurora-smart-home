"""Contract tests for the recipe library (v1.12.0).

A recipe is a curated starting point Aurora generates into a full
project. These tests pin the format so recipes cannot drift: every
recipe has the required header and sections, the index and the files
agree, hardware recipes never cite an invented LCSC number, and
SKILL.md keeps the recipe wiring (opening offer + recipe-to-project
flow). Same spirit as the Iron Law and deliverable-spec contract tests.
"""
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RECIPES_DIR = REPO_ROOT / "aurora" / "recipes"
INDEX = RECIPES_DIR / "_index.md"
FORMAT = RECIPES_DIR / "_recipe-format.md"
SKILL = REPO_ROOT / "aurora" / "SKILL.md"
COMPONENTS_DIR = REPO_ROOT / "aurora" / "references" / "components"

REQUIRED_HEADER_KEYS = ["name", "intent", "specialists", "hardware", "match_keywords"]
HW_SECTIONS = ["What you get", "Hardware", "Wiring", "Automation pattern",
               "Dashboard skeleton", "Customise", "Build it"]
HA_SECTIONS = ["What you get", "Automation pattern", "Dashboard skeleton",
               "Customise", "Build it"]

RECIPE_FILES = sorted(
    p for p in RECIPES_DIR.glob("*.md") if not p.name.startswith("_")
)


def parse_header(text: str) -> dict:
    """Parse the leading --- fenced metadata block into a dict (flat scalars
    and simple [list] values)."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "recipe is missing the leading --- header block"
    header = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            header[key] = [v.strip() for v in val[1:-1].split(",") if v.strip()]
        else:
            header[key] = val
    return header


def verified_lcsc() -> set[str]:
    out = set()
    for p in COMPONENTS_DIR.rglob("*.json"):
        doc = json.loads(p.read_text(encoding="utf-8"))
        lcsc = (doc.get("sourcing") or {}).get("lcsc")
        if lcsc and lcsc != "TBD":
            out.add(lcsc)
    return out


def test_recipe_library_is_populated():
    assert len(RECIPE_FILES) >= 10, "recipe library should hold at least 10 recipes"


def test_format_spec_lists_required_sections():
    text = FORMAT.read_text(encoding="utf-8")
    for section in ("What you get", "Hardware", "Automation pattern",
                    "Dashboard skeleton", "Customise", "Build it"):
        assert section in text, f"format spec omits the {section!r} section"


@pytest.mark.parametrize("path", RECIPE_FILES, ids=lambda p: p.stem)
class TestEachRecipe:
    def test_header_has_required_keys(self, path):
        header = parse_header(path.read_text(encoding="utf-8"))
        for key in REQUIRED_HEADER_KEYS:
            assert key in header, f"{path.name} header missing {key}"

    def test_name_matches_slug(self, path):
        header = parse_header(path.read_text(encoding="utf-8"))
        assert header["name"] == path.stem, (
            f"{path.name}: header name {header['name']!r} != filename slug"
        )

    def test_required_sections_present(self, path):
        text = path.read_text(encoding="utf-8")
        header = parse_header(text)
        is_hw = header["hardware"].lower() == "true"
        required = HW_SECTIONS if is_hw else HA_SECTIONS
        for section in required:
            assert re.search(rf"^##\s+{re.escape(section)}", text, re.MULTILINE), (
                f"{path.name} missing required section: {section}"
            )

    def test_no_em_or_en_dashes(self, path):
        text = path.read_text(encoding="utf-8")
        assert "—" not in text and "–" not in text, (
            f"{path.name} contains an em/en dash (repo style forbids them)"
        )

    def test_hardware_recipes_cite_only_verified_lcsc(self, path):
        text = path.read_text(encoding="utf-8")
        cited = set(re.findall(r"\bC\d{3,}\b", text))
        allowed = verified_lcsc()
        bad = cited - allowed
        assert not bad, (
            f"{path.name} cites LCSC number(s) {bad} not present in "
            "aurora/references/components/; use a verified number or TBD"
        )

    def test_related_example_exists_if_declared(self, path):
        header = parse_header(path.read_text(encoding="utf-8"))
        rel = header.get("related_example")
        if rel:
            assert (REPO_ROOT / rel).is_dir(), (
                f"{path.name} related_example {rel} does not exist"
            )


class TestIndexAgreesWithFiles:
    def test_every_recipe_is_indexed(self):
        index_text = INDEX.read_text(encoding="utf-8")
        for path in RECIPE_FILES:
            assert f"({path.name})" in index_text, (
                f"{path.name} is not linked in _index.md"
            )

    def test_index_has_no_orphan_links(self):
        index_text = INDEX.read_text(encoding="utf-8")
        linked = set(re.findall(r"\(([a-z0-9-]+\.md)\)", index_text))
        actual = {p.name for p in RECIPE_FILES}
        orphans = linked - actual
        assert not orphans, f"_index.md links non-existent recipes: {orphans}"


class TestSkillWiring:
    def test_opening_offer_step_present(self):
        text = SKILL.read_text(encoding="utf-8")
        assert "Step 1.5: Offer a Recipe" in text
        assert "aurora/recipes/_index.md" in text

    def test_recipe_to_project_flow_present(self):
        text = SKILL.read_text(encoding="utf-8")
        assert "Recipe-to-project flow" in text
        assert "never downgrade a verified part to a guess" in text
