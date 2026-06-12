#!/usr/bin/env python3
"""
aurora/scripts/lint_ha_syntax.py

Guards the repo against reintroduction of legacy Home Assistant syntax
after the 2026-06 repo-wide modernization, and verifies that every
yaml-labelled markdown fence actually parses as YAML.

Legacy patterns flagged (context-aware, indentation-based):
    - service: domain.name        in action steps (use action:)
    - platform: x                 inside trigger lists (use trigger:)
    - bare trigger:/condition:/action: block keys (use plural forms)
    - action: call-service        in dashboard actions (use perform-action)

Intentional exceptions that are NOT flagged:
    - blueprint selector keys (selector: action: / trigger: / condition:)
    - field names under fields: in integration services.yaml
    - service: inside browser_mod fire-dom-event blocks
    - platform: keys for sensor/binary_sensor/device_tracker integrations
      and bayesian observations (only trigger-list platform: is legacy)
    - the esphome/ tree and ESPHome device configs in examples/, which
      follow the ESPHome schema (homeassistant.service:, api: services:,
      singular condition: in if: blocks)
    - migration-guide.md and *-2026-official.md, which document legacy
      syntax on purpose
    - fence sections under an "Old"/"deprecated"/"legacy" comment marker,
      until a "New"/"Current"/"Correct" marker ends the legacy section

Usage:
    python aurora/scripts/lint_ha_syntax.py            # lint whole repo
    python aurora/scripts/lint_ha_syntax.py PATH ...   # lint given files

Exit codes:
    0  clean
    1  one or more findings
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("pyyaml is required: pip install -r requirements-dev.txt")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]

# Files where legacy syntax is the documented subject matter.
SKIP_LEGACY_FILE = re.compile(r"(migration-guide\.md|-2026-official\.md)$")

# Trees that follow the ESPHome schema rather than HA automation syntax.
SKIP_LEGACY_TREE = re.compile(r"^esphome[/\\]")

# ESPHome device configs in examples/ (anything that is not the HA-side
# automations.yaml or dashboard.yaml is firmware YAML).
EXAMPLES_HA_FILE = re.compile(r"^examples[/\\][^/\\]+[/\\](automations|dashboard)\.yaml$")

TRIGGER_PARENTS = {"trigger", "triggers", "wait_for_trigger"}
SERVICE_EXCLUDE_PARENTS = {
    "browser_mod", "data", "service_data", "payload", "variables",
    "fields", "event_data", "json_attributes", "services",
    "homeassistant.service",
}
BARE_KEY_EXCLUDE_PARENTS = {"selector", "fields"}

KEY_RE = re.compile(r"^(\s*)((?:- )*)([A-Za-z_][\w.\-]*):(\s*)(.*)$")
FENCE_OPEN_RE = re.compile(r"^\s*```(\w*)")
LEGACY_MARKER_RE = re.compile(r"#.*\b(old|deprecated|legacy)\b", re.I)
MODERN_MARKER_RE = re.compile(r"#.*\b(new|current|correct|modern)\b", re.I)


class _LooseLoader(yaml.SafeLoader):
    """SafeLoader that tolerates HA tags such as !secret and !input."""


_LooseLoader.add_multi_constructor("!", lambda loader, suffix, node: None)


def lint_yaml_lines(lines, path, offset=0):
    """Return findings for one YAML block. offset is 0-based line of block start."""
    findings = []
    stack = []  # (column, key)
    in_legacy_section = False

    for i, line in enumerate(lines):
        if LEGACY_MARKER_RE.search(line):
            in_legacy_section = True
        elif MODERN_MARKER_RE.search(line):
            in_legacy_section = False

        m = KEY_RE.match(line)
        if not m:
            continue
        indent, dashes, key, _sep, value = m.groups()
        col = len(indent) + len(dashes)
        while stack and stack[-1][0] >= col:
            stack.pop()
        parent = stack[-1][1] if stack else None
        stack.append((col, key))

        if in_legacy_section:
            continue
        value_nc = value.split("#", 1)[0].strip() if value else ""
        where = f"{path}:{offset + i + 1}"

        if key == "action" and value_nc == "call-service":
            findings.append(f"{where}: use 'perform-action' instead of 'call-service'")
        elif (key == "service" and parent not in SERVICE_EXCLUDE_PARENTS
              and re.match(r"^[a-z_]+\.[a-z_0-9]+", value_nc)):
            findings.append(f"{where}: use 'action:' instead of 'service:' ({value_nc})")
        elif key in ("service_template", "data_template"):
            findings.append(f"{where}: '{key}:' is deprecated, template inside action:/data:")
        elif key == "platform" and parent in TRIGGER_PARENTS:
            findings.append(f"{where}: use 'trigger:' instead of 'platform:' in trigger lists")
        elif (key in ("trigger", "condition", "action") and not value_nc
              and parent not in BARE_KEY_EXCLUDE_PARENTS):
            findings.append(f"{where}: use plural '{key}s:' for automation block keys")

    return findings


def iter_yaml_fences(text):
    """Yield (start_line_0based, fence_lines, info_string) for each fenced block."""
    lines = text.split("\n")
    in_fence, info, block, start = False, "", [], 0
    for idx, line in enumerate(lines):
        m = FENCE_OPEN_RE.match(line)
        if not in_fence and m:
            in_fence, info, block, start = True, m.group(1).lower(), [], idx + 1
        elif in_fence and m and m.group(1) == "":
            yield start, block, info
            in_fence = False
        elif in_fence:
            block.append(line)


def check_fence_parses(block_lines, path, start):
    try:
        list(yaml.load_all("\n".join(block_lines), Loader=_LooseLoader))
        return []
    except yaml.YAMLError as exc:
        msg = str(exc).split("\n")[0][:100]
        return [f"{path}:{start + 1}: yaml fence does not parse ({msg}) "
                "- fix it or relabel the fence as jinja2/text"]


def lint_file(path: Path, rel: str):
    findings = []
    text = path.read_text(encoding="utf-8")
    skip_legacy = bool(SKIP_LEGACY_FILE.search(rel) or SKIP_LEGACY_TREE.match(rel))

    if rel.endswith((".yaml", ".yml")):
        if rel.startswith("examples") and not EXAMPLES_HA_FILE.match(rel):
            skip_legacy = True
        if not skip_legacy:
            findings += lint_yaml_lines(text.split("\n"), rel)
        return findings

    for start, block, info in iter_yaml_fences(text):
        if info not in ("yaml", "yml"):
            continue
        findings += check_fence_parses(block, rel, start)
        if not skip_legacy:
            findings += lint_yaml_lines(block, rel, offset=start)
    return findings


def tracked_files():
    out = subprocess.run(
        ["git", "ls-files", "*.md", "*.yaml", "*.yml"],
        capture_output=True, text=True, cwd=REPO_ROOT, check=True,
    ).stdout.split("\n")
    return [f for f in out if f and not f.startswith("graphify-out")]


def main(argv):
    targets = argv or tracked_files()
    findings = []
    for rel in targets:
        rel = rel.replace("\\", "/")
        path = REPO_ROOT / rel
        if not path.is_file() or not rel.endswith((".md", ".yaml", ".yml")):
            continue
        findings += lint_file(path, rel)

    for f in findings:
        print(f)
    print(f"lint_ha_syntax: {len(findings)} finding(s) in {len(targets)} file(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
