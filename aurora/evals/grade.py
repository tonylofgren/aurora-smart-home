"""Grade eval outputs against assertions defined in evals.json.

Run:
    python aurora/evals/grade.py aurora-workspace/iteration-1

Reads evals.json + the iteration directory, runs each assertion against
the saved response.md / project/* files, writes grading.json per run.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALS_FILE = REPO_ROOT / "aurora" / "evals" / "evals.json"


def find_files(base: Path, pattern: str) -> list[Path]:
    """Return files matching pattern under base. Supports *.yaml glob and exact names."""
    if not base.exists():
        return []
    if "*" in pattern:
        return list(base.rglob(pattern))
    matches = list(base.rglob(pattern))
    return matches


def gather_text(outputs: Path) -> str:
    """Concatenate response.md + all project files for full-text checks."""
    parts: list[str] = []
    response = outputs / "response.md"
    if response.is_file():
        parts.append(response.read_text(encoding="utf-8", errors="replace"))
    project = outputs / "project"
    if project.exists():
        for p in project.rglob("*"):
            if p.is_file():
                try:
                    parts.append(p.read_text(encoding="utf-8", errors="replace"))
                except (OSError, UnicodeDecodeError):
                    pass
    return "\n".join(parts)


def check_regex_any(text: str, patterns: list[str]) -> tuple[bool, str]:
    for p in patterns:
        if re.search(p, text):
            return True, f"matched: {p}"
    return False, f"none of {len(patterns)} patterns matched"


def check_regex_all(text: str, patterns: list[str]) -> tuple[bool, str]:
    missed = [p for p in patterns if not re.search(p, text)]
    if not missed:
        return True, f"all {len(patterns)} patterns matched"
    return False, f"missed: {missed}"


def check_negative_regex(text: str, patterns: list[str]) -> tuple[bool, str]:
    hit = [p for p in patterns if re.search(p, text, re.IGNORECASE)]
    if not hit:
        return True, "no forbidden patterns matched"
    return False, f"forbidden pattern(s) found: {hit}"


def check_file_regex(outputs: Path, file_pat: str, patterns: list[str]) -> tuple[bool, str]:
    project = outputs / "project"
    files = find_files(project, file_pat)
    if not files:
        return False, f"no file matching '{file_pat}' under project/"
    text = "\n".join(
        f.read_text(encoding="utf-8", errors="replace") for f in files if f.is_file()
    )
    missed = [p for p in patterns if not re.search(p, text)]
    if not missed:
        return True, f"all {len(patterns)} patterns matched in {len(files)} file(s)"
    return False, f"in {[str(f.name) for f in files]}, missed: {missed}"


def check_file_exists(outputs: Path, file_pat: str) -> tuple[bool, str]:
    project = outputs / "project"
    files = find_files(project, file_pat)
    if files:
        return True, f"found: {[str(f.name) for f in files]}"
    return False, f"no file matching '{file_pat}' under project/"


def grade_assertion(outputs: Path, full_text: str, a: dict) -> dict:
    check = a.get("check", "regex_any")
    patterns = a.get("patterns", [])
    if check == "regex_any":
        passed, evidence = check_regex_any(full_text, patterns)
    elif check == "regex_all":
        passed, evidence = check_regex_all(full_text, patterns)
    elif check == "negative_regex":
        passed, evidence = check_negative_regex(full_text, patterns)
    elif check == "file_regex":
        passed, evidence = check_file_regex(outputs, a["file"], patterns)
    elif check == "file_exists":
        passed, evidence = check_file_exists(outputs, a["file"])
    else:
        passed, evidence = False, f"unknown check type: {check}"
    return {
        "id": a.get("id", "?"),
        "text": a.get("text", ""),
        "passed": passed,
        "evidence": evidence,
    }


def main(iteration_dir: str) -> int:
    iteration = Path(iteration_dir).resolve()
    evals = json.loads(EVALS_FILE.read_text(encoding="utf-8"))

    summary: dict = {"iteration": iteration.name, "evals": {}}

    for ev in evals["evals"]:
        eval_dir_name = f"eval-{ev['id']}-{ev['name'].replace('_', '-')}"
        eval_dir = iteration / eval_dir_name
        if not eval_dir.exists():
            print(f"SKIP {eval_dir_name}: directory not found")
            continue

        summary["evals"][eval_dir_name] = {}
        for mode in ("with_skill", "without_skill"):
            mode_dir = eval_dir / mode
            if not mode_dir.exists():
                # Iteration may verify only with_skill; skip absent modes.
                continue
            outputs = mode_dir / "outputs"
            full_text = gather_text(outputs)
            results = [grade_assertion(outputs, full_text, a) for a in ev["assertions"]]
            passed = sum(1 for r in results if r["passed"])
            total = len(results)
            grading = {
                "pass_count": passed,
                "total": total,
                "pass_rate": passed / total if total else 0,
                "assertions": results,
            }
            (outputs.parent / "grading.json").write_text(
                json.dumps(grading, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            summary["evals"][eval_dir_name][mode] = {
                "pass_count": passed,
                "total": total,
                "pass_rate": grading["pass_rate"],
            }
            print(f"{eval_dir_name} / {mode}: {passed}/{total}")

    summary_path = iteration / "grading-summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nSummary written to {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "aurora-workspace/iteration-1"))
