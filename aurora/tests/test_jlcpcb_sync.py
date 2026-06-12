"""Tests for the JLCPCB sourcing field and sync_jlcpcb_status.py.

Verifies the component-profile schema accepts the sourcing block, every
shipped component profile carries one (TBD until verified), and the
sync script updates library type, MOQ, and check date correctly from a
CDFER-format CSV, including the not_listed and TBD-skip paths.
"""
import json
import sys
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "aurora" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import sync_jlcpcb_status as sync  # noqa: E402

SCHEMA = json.loads(
    (REPO_ROOT / "aurora" / "references" / "schemas" / "component-profile.schema.json")
    .read_text(encoding="utf-8")
)

CSV_FIXTURE = (
    "lcsc,Assembly Type,Assembly Type Batch,Assembly Process,Min Order Qty,"
    "Attrition Qty,Special Component Fee,Component Library Type\n"
    "1002,smtWeld,smtWeld,SMT,20,6,0.0,base\n"
    "99999,smtWeld,smtWeld,SMT,5,2,0.0,expand\n"
)


def make_profile(tmp_path, sourcing):
    doc = {"schema_version": "1.1", "component_id": "t", "sourcing": sourcing}
    p = tmp_path / "t.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


class TestSchema:
    def test_sourcing_block_validates(self):
        jsonschema.Draft202012Validator.check_schema(SCHEMA)
        props = SCHEMA["properties"]["sourcing"]["properties"]
        assert {"lcsc", "jlcpcb_library_type", "jlcpcb_moq", "jlcpcb_checked"} <= set(props)

    def test_every_component_profile_has_sourcing(self):
        for p in (REPO_ROOT / "aurora" / "references" / "components").rglob("*.json"):
            doc = json.loads(p.read_text(encoding="utf-8"))
            assert "sourcing" in doc, f"{p.name} lacks the sourcing block"
            jsonschema.validate(doc["sourcing"], SCHEMA["properties"]["sourcing"])

    def test_no_invented_lcsc_numbers_without_check_date(self):
        """A real C-number must come with a sync/verification date."""
        for p in (REPO_ROOT / "aurora" / "references" / "components").rglob("*.json"):
            s = json.loads(p.read_text(encoding="utf-8"))["sourcing"]
            if s["lcsc"] != "TBD":
                assert "jlcpcb_checked" in s, (
                    f"{p.name} has lcsc {s['lcsc']} but no jlcpcb_checked date; "
                    "run sync_jlcpcb_status.py after populating the number"
                )


class TestSyncScript:
    def test_listed_part_gets_type_and_moq(self, tmp_path):
        status = sync.load_status(CSV_FIXTURE)
        p = make_profile(tmp_path, {"lcsc": "C1002"})
        result = sync.sync_profile(p, status, "2026-06-12")
        assert "updated" in result
        s = json.loads(p.read_text(encoding="utf-8"))["sourcing"]
        assert s["jlcpcb_library_type"] == "base"
        assert s["jlcpcb_moq"] == 20
        assert s["jlcpcb_checked"] == "2026-06-12"

    def test_absent_part_marked_not_listed(self, tmp_path):
        status = sync.load_status(CSV_FIXTURE)
        p = make_profile(tmp_path, {"lcsc": "C123456", "jlcpcb_moq": 10})
        sync.sync_profile(p, status, "2026-06-12")
        s = json.loads(p.read_text(encoding="utf-8"))["sourcing"]
        assert s["jlcpcb_library_type"] == "not_listed"
        assert "jlcpcb_moq" not in s

    def test_tbd_profile_skipped(self, tmp_path):
        status = sync.load_status(CSV_FIXTURE)
        p = make_profile(tmp_path, {"lcsc": "TBD"})
        before = p.read_text(encoding="utf-8")
        result = sync.sync_profile(p, status, "2026-06-12")
        assert "skipped" in result
        assert p.read_text(encoding="utf-8") == before

    def test_idempotent(self, tmp_path):
        status = sync.load_status(CSV_FIXTURE)
        p = make_profile(tmp_path, {"lcsc": "C99999"})
        sync.sync_profile(p, status, "2026-06-12")
        assert sync.sync_profile(p, status, "2026-06-12") == "unchanged"
