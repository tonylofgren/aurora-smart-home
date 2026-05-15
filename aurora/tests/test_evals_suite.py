"""Validate the regression eval suite (added v1.7.8).

The suite itself (`aurora/evals/evals.json` + `aurora/evals/grade.py`)
must stay parseable and structurally complete. We do NOT spawn subagents
in CI — that requires real API budget and is the iteration step done
manually before each release.

What this test pins:

1. evals.json parses and matches the documented schema.
2. Every eval has a non-empty prompt and at least one assertion.
3. Each assertion declares a check type the grader supports.
4. grade.py exists and is importable (its functions can be called by
   future tooling without surprise).
"""

import json
from pathlib import Path
import importlib.util

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALS_FILE = REPO_ROOT / "aurora" / "evals" / "evals.json"
GRADE_FILE = REPO_ROOT / "aurora" / "evals" / "grade.py"

SUPPORTED_CHECKS = {
    "regex_any",
    "regex_all",
    "negative_regex",
    "file_regex",
    "file_exists",
}


def test_evals_json_exists_and_parses():
    assert EVALS_FILE.is_file(), "aurora/evals/evals.json missing"
    data = json.loads(EVALS_FILE.read_text(encoding="utf-8"))
    assert data.get("skill_name") == "aurora"
    assert isinstance(data.get("evals"), list) and data["evals"], (
        "evals.json must contain a non-empty 'evals' array"
    )


def test_every_eval_has_prompt_and_assertions():
    data = json.loads(EVALS_FILE.read_text(encoding="utf-8"))
    for ev in data["evals"]:
        eid = ev.get("id", "?")
        assert ev.get("prompt"), f"eval {eid} missing prompt"
        assert ev.get("name"), f"eval {eid} missing name"
        assert isinstance(ev.get("assertions"), list) and ev["assertions"], (
            f"eval {eid} must have at least one assertion"
        )


def test_assertions_use_supported_check_types():
    data = json.loads(EVALS_FILE.read_text(encoding="utf-8"))
    bad = []
    for ev in data["evals"]:
        for a in ev["assertions"]:
            check = a.get("check", "regex_any")
            if check not in SUPPORTED_CHECKS:
                bad.append((ev["id"], a.get("id", "?"), check))
    assert not bad, f"unsupported check types found: {bad}"


def test_grade_module_importable():
    """grade.py must import without side effects. The grader is invoked
    by a human after subagent runs; CI should not run it (no outputs)."""
    assert GRADE_FILE.is_file(), "aurora/evals/grade.py missing"
    spec = importlib.util.spec_from_file_location("aurora_evals_grade", GRADE_FILE)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    # core helpers must exist for future tooling
    for fn in ("grade_assertion", "gather_text", "find_files"):
        assert hasattr(module, fn), f"grade.py missing {fn}()"
