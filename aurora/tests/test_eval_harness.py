"""Tests for the runtime eval harness (run_evals.py) and the golden baseline.

The harness grades a saved iteration and gates with-skill scores against
the golden baseline. Live subagent runs are not reproducible in CI, so
these tests cover the deterministic parts: golden/evals.json agreement
and the pure compare/update logic on synthetic summaries.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALS_DIR = REPO_ROOT / "aurora" / "evals"
GOLDEN = json.loads((EVALS_DIR / "golden-baseline.json").read_text(encoding="utf-8"))
EVALS = json.loads((EVALS_DIR / "evals.json").read_text(encoding="utf-8"))

sys.path.insert(0, str(EVALS_DIR))
import run_evals  # noqa: E402


def eval_dir_name(ev: dict) -> str:
    return f"eval-{ev['id']}-{ev['name'].replace('_', '-')}"


class TestGoldenIntegrity:
    def test_golden_covers_exactly_the_evals(self):
        expected = {eval_dir_name(ev) for ev in EVALS["evals"]}
        actual = set(GOLDEN["evals"].keys())
        assert actual == expected, (
            f"golden baseline drifted from evals.json. "
            f"only in golden: {actual - expected}; only in evals: {expected - actual}"
        )

    def test_golden_total_matches_assertion_count(self):
        by_name = {eval_dir_name(ev): len(ev["assertions"]) for ev in EVALS["evals"]}
        for name, entry in GOLDEN["evals"].items():
            assert entry["total"] == by_name[name], (
                f"{name}: golden total {entry['total']} != {by_name[name]} assertions"
            )

    def test_golden_min_within_bounds(self):
        for name, entry in GOLDEN["evals"].items():
            assert 0 <= entry["with_skill_min"] <= entry["total"], (
                f"{name}: with_skill_min out of range"
            )


def _summary(scores: dict) -> dict:
    """scores: {eval_name: with_skill_pass_count}. total taken from golden."""
    evals = {}
    for name, got in scores.items():
        total = GOLDEN["evals"][name]["total"]
        evals[name] = {"with_skill": {"pass_count": got, "total": total}}
    return {"iteration": "test", "evals": evals}


class TestCompareToGolden:
    def test_all_at_baseline_is_clean(self):
        scores = {n: e["with_skill_min"] for n, e in GOLDEN["evals"].items()}
        report = run_evals.compare_to_golden(_summary(scores), GOLDEN)
        assert not report["regressions"] and not report["missing"]
        assert len(report["ok"]) == len(GOLDEN["evals"])

    def test_detects_regression(self):
        scores = {n: e["with_skill_min"] for n, e in GOLDEN["evals"].items()}
        victim = "eval-7-safety-gate-vera-before-volt"
        scores[victim] = GOLDEN["evals"][victim]["with_skill_min"] - 1
        report = run_evals.compare_to_golden(_summary(scores), GOLDEN)
        assert any(r["eval"] == victim for r in report["regressions"])

    def test_detects_improvement(self):
        # eval-1 baseline 3/3 cannot improve; use eval with headroom by
        # temporarily lowering the floor in a copy of the golden.
        golden = json.loads(json.dumps(GOLDEN))
        golden["evals"]["eval-1-vague-board-triggers-question"]["with_skill_min"] = 2
        scores = {n: e["with_skill_min"] for n, e in golden["evals"].items()}
        scores["eval-1-vague-board-triggers-question"] = 3
        report = run_evals.compare_to_golden(_summary(scores), golden)
        assert any(i["eval"] == "eval-1-vague-board-triggers-question"
                   for i in report["improvements"])

    def test_detects_missing(self):
        scores = {n: e["with_skill_min"] for n, e in GOLDEN["evals"].items()}
        scores.pop("eval-5-routing-iris-dashboard")
        report = run_evals.compare_to_golden(_summary(scores), GOLDEN)
        assert "eval-5-routing-iris-dashboard" in report["missing"]


class TestUpdateGolden:
    def test_update_sets_mins_from_summary(self):
        golden = json.loads(json.dumps(GOLDEN))
        scores = {n: 0 for n in golden["evals"]}  # pretend everything scored 0
        run_evals.update_golden(_summary(scores), golden)
        assert all(e["with_skill_min"] == 0 for e in golden["evals"].values())
        assert golden["baseline_iteration"] == "test"
