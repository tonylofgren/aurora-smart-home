#!/usr/bin/env python3
"""
aurora/evals/run_evals.py

Runtime eval harness: grade a saved iteration of subagent runs and compare
the with-skill scores against the committed golden baseline, failing on any
regression. This turns the eval suite from a manual spot-check into a
regression gate.

What it does NOT do: spawn the subagents. Running real Aurora flows needs a
live model and is non-deterministic, so it cannot run in CI. The subagent
runs are produced manually (see README.md "How to run") and saved under
aurora-workspace/iteration-N/; this harness grades and gates them.

Usage:
    # Grade an iteration and gate against the golden baseline:
    python aurora/evals/run_evals.py aurora-workspace/iteration-2

    # Re-baseline after assertions legitimately changed:
    python aurora/evals/run_evals.py aurora-workspace/iteration-3 --update

Exit codes:
    0  every eval meets or beats its golden with_skill_min
    1  at least one eval regressed
    2  iteration could not be graded
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLDEN_PATH = HERE / "golden-baseline.json"

sys.path.insert(0, str(HERE))
import grade  # noqa: E402  (sibling module, hyphen-free)


def compare_to_golden(summary: dict, golden: dict) -> dict:
    """Pure comparison. Returns {regressions, improvements, missing, ok}.

    A regression is a graded eval whose with_skill pass_count is below the
    golden with_skill_min. An improvement beats it. Missing means the golden
    lists an eval the iteration did not grade (with_skill absent)."""
    graded = summary.get("evals", {})
    regressions, improvements, missing, ok = [], [], [], []
    for name, exp in golden.get("evals", {}).items():
        run = graded.get(name, {}).get("with_skill")
        if run is None:
            missing.append(name)
            continue
        got, floor = run["pass_count"], exp["with_skill_min"]
        if got < floor:
            regressions.append({"eval": name, "got": got, "expected_min": floor})
        elif got > floor:
            improvements.append({"eval": name, "got": got, "expected_min": floor})
        else:
            ok.append(name)
    return {"regressions": regressions, "improvements": improvements,
            "missing": missing, "ok": ok}


def update_golden(summary: dict, golden: dict) -> dict:
    """Set each golden with_skill_min to the iteration's with_skill pass_count."""
    graded = summary.get("evals", {})
    for name, entry in golden.get("evals", {}).items():
        run = graded.get(name, {}).get("with_skill")
        if run is not None:
            entry["with_skill_min"] = run["pass_count"]
            entry["total"] = run["total"]
    golden["baseline_iteration"] = summary.get("iteration", golden.get("baseline_iteration"))
    return golden


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("iteration", help="path to aurora-workspace/iteration-N")
    ap.add_argument("--update", action="store_true",
                    help="re-baseline the golden file from this iteration")
    args = ap.parse_args(argv)

    iteration = Path(args.iteration)
    if not iteration.is_dir():
        print(f"FAIL iteration not found: {iteration}")
        return 2

    grade.main(str(iteration))  # writes grading-summary.json
    summary = json.loads((iteration / "grading-summary.json").read_text(encoding="utf-8"))
    golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))

    if args.update:
        GOLDEN_PATH.write_text(
            json.dumps(update_golden(summary, golden), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Golden baseline updated from {iteration.name}.")
        return 0

    report = compare_to_golden(summary, golden)
    print("\n--- eval regression gate ---")
    for r in report["regressions"]:
        print(f"  REGRESSION {r['eval']}: {r['got']} < golden {r['expected_min']}")
    for i in report["improvements"]:
        print(f"  IMPROVED    {i['eval']}: {i['got']} > golden {i['expected_min']} (run --update to lock in)")
    for m in report["missing"]:
        print(f"  MISSING     {m}: golden expects it but the iteration did not grade with_skill")
    print(f"  {len(report['ok'])} eval(s) at baseline, {len(report['regressions'])} regressed, "
          f"{len(report['missing'])} missing")

    failed = bool(report["regressions"] or report["missing"])
    print("GATE FAILED" if failed else "GATE PASSED")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
