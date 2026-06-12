"""Tests for the fab-ready export formats (schematic.json, BOM.csv,
OpenSCAD enclosure, JLCPCB order log) introduced for v1.10.0.

Covers: the schematic JSON Schema is valid and strict, the shipped
example validates against it, BOM.csv follows the JLCPCB column
contract, the format spec documents every artifact, and the Volt soul
plus pcb/bom format specs are wired to the new spec file.
"""
import csv
import json
import re
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "aurora" / "references" / "schemas" / "schematic.schema.json"
SPEC_PATH = REPO_ROOT / "aurora" / "references" / "deliverables" / "fab-export-format.md"
SCAD_PATH = REPO_ROOT / "aurora" / "references" / "templates" / "enclosure.scad"
EXAMPLE_DIR = REPO_ROOT / "examples" / "water-leak-sensor" / "hardware"

JLCPCB_HEADER = ["Comment", "Designator", "Footprint", "LCSC Part #"]


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def spec_text():
    return SPEC_PATH.read_text(encoding="utf-8")


class TestSchematicSchema:
    def test_schema_is_draft_2020_12(self, schema):
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"

    def test_schema_is_itself_valid(self, schema):
        jsonschema.Draft202012Validator.check_schema(schema)

    def test_required_top_level_fields(self, schema):
        assert set(schema["required"]) == {"schema_version", "project", "components", "nets"}

    def test_lcsc_allows_real_numbers_and_tbd_only(self, schema):
        pattern = schema["properties"]["components"]["items"]["properties"]["lcsc"]["pattern"]
        assert re.match(pattern, "C2040")
        assert re.match(pattern, "TBD")
        assert not re.match(pattern, "guess-123")

    def test_example_in_repo_validates(self, schema):
        example = json.loads((EXAMPLE_DIR / "schematic.json").read_text(encoding="utf-8"))
        jsonschema.validate(example, schema)

    def test_example_nets_reference_declared_components(self, schema):
        example = json.loads((EXAMPLE_DIR / "schematic.json").read_text(encoding="utf-8"))
        refdes = {c["refdes"] for c in example["components"]}
        for net in example["nets"]:
            for pin in net["pins"]:
                assert pin.split(".")[0] in refdes, f"net {net['name']} references undeclared {pin}"


class TestBomCsv:
    def test_example_header_matches_jlcpcb_contract(self):
        with open(EXAMPLE_DIR / "BOM.csv", newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        assert rows[0] == JLCPCB_HEADER
        assert len(rows) > 1, "BOM.csv has no part rows"
        for row in rows[1:]:
            assert len(row) == 4, f"malformed row: {row}"

    def test_example_csv_carries_no_prices(self):
        text = (EXAMPLE_DIR / "BOM.csv").read_text(encoding="utf-8")
        assert not re.search(r"\$|USD|SEK|price", text, re.I)


class TestFabExportSpec:
    def test_spec_documents_every_artifact(self, spec_text):
        for section in ("## schematic.json", "## BOM.csv", "## KiCad workflow",
                        "## ENCLOSURE.scad", "## JLCPCB ordering workflow"):
            assert section in spec_text, f"fab-export-format.md missing section: {section}"

    def test_spec_pins_exact_csv_header(self, spec_text):
        assert "Comment,Designator,Footprint,LCSC Part #" in spec_text

    def test_spec_forbids_invented_part_numbers(self, spec_text):
        assert "Do not invent LCSC part numbers" in spec_text

    def test_spec_documents_fab_order_log(self, spec_text):
        assert "Fab order log" in spec_text
        assert "no public order-status API" in spec_text or "no public API" in spec_text


class TestEnclosureTemplate:
    def test_template_exists_with_parameter_block(self):
        text = SCAD_PATH.read_text(encoding="utf-8")
        for param in ("board_l", "board_w", "wall", "standoff_h",
                      "cable_d", "vent_rows", "lid_tolerance"):
            assert re.search(rf"^{param}\s*=", text, re.M), f"enclosure.scad missing parameter: {param}"

    def test_template_carries_attribution(self):
        assert "aurora@aurora-smart-home" in SCAD_PATH.read_text(encoding="utf-8")


class TestWiring:
    def test_volt_soul_requires_fab_exports_at_production(self):
        volt = (REPO_ROOT / "aurora" / "souls" / "volt.md").read_text(encoding="utf-8")
        assert "schematic.json" in volt and "BOM.csv" in volt
        assert "fab-export-format.md" in volt

    def test_pcb_and_bom_specs_point_at_fab_spec(self):
        for name in ("pcb-format.md", "bom-format.md"):
            text = (REPO_ROOT / "aurora" / "references" / "deliverables" / name).read_text(encoding="utf-8")
            assert "fab-export-format.md" in text, f"{name} does not reference fab-export-format.md"

    def test_esphome_skill_points_at_fab_spec(self):
        text = (REPO_ROOT / "esphome" / "SKILL.md").read_text(encoding="utf-8")
        assert "fab-export-format.md" in text
