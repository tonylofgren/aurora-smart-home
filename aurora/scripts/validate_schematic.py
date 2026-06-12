#!/usr/bin/env python3
"""
aurora/scripts/validate_schematic.py

Validates a project's hardware/schematic.json: first against the JSON
Schema at aurora/references/schemas/schematic.schema.json, then with
netlist-level checks the schema cannot express. Companion to the
pin/i2c/voltage validator procedures, which use schematic.json as their
machine-readable input when it exists (see fab-export-format.md).

Netlist checks beyond the schema:
    1. refdes uniqueness across components
    2. every net pin references a declared component
    3. no component pin appears in more than one net (electrical short)
    4. no duplicate net names
    5. a ground net exists (GND/GNDA/AGND/DGND), warning otherwise
    6. components not connected to any net, warning
    7. TBD LCSC count reported (informational; production-tier BOM.csv
       needs real part numbers before ordering assembly)

Usage:
    python aurora/scripts/validate_schematic.py <project>/hardware/schematic.json
    python aurora/scripts/validate_schematic.py --quiet <path>

Exit codes:
    0  valid (warnings allowed)
    1  one or more errors
    2  file or schema could not be loaded
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover
    print("jsonschema is required: pip install -r requirements-dev.txt")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "aurora" / "references" / "schemas" / "schematic.schema.json"

GROUND_NAMES = {"GND", "GNDA", "AGND", "DGND"}


def check_netlist(doc: dict) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for netlist-level rules."""
    errors: list[str] = []
    warnings: list[str] = []

    refdes_counts = Counter(c["refdes"] for c in doc["components"])
    for refdes, n in refdes_counts.items():
        if n > 1:
            errors.append(f"refdes {refdes} declared {n} times; reference designators must be unique")
    declared = set(refdes_counts)

    net_names = Counter(net["name"] for net in doc["nets"])
    for name, n in net_names.items():
        if n > 1:
            errors.append(f"net name {name} declared {n} times; merge the pin lists into one net")

    pin_owner: dict[str, str] = {}
    connected: set[str] = set()
    for net in doc["nets"]:
        for pin in net["pins"]:
            ref = pin.split(".")[0]
            connected.add(ref)
            if ref not in declared:
                errors.append(f"net {net['name']} references {pin} but component {ref} is not declared")
            if pin in pin_owner and pin_owner[pin] != net["name"]:
                errors.append(
                    f"pin {pin} appears in both net {pin_owner[pin]} and net {net['name']}; "
                    "one physical pin cannot belong to two nets"
                )
            pin_owner.setdefault(pin, net["name"])

    if not GROUND_NAMES & {net["name"] for net in doc["nets"]}:
        warnings.append("no ground net found (expected one of GND/GNDA/AGND/DGND)")

    for ref in sorted(declared - connected):
        warnings.append(f"component {ref} is not connected to any net")

    tbd = sum(1 for c in doc["components"] if c.get("lcsc") == "TBD")
    if tbd:
        warnings.append(
            f"{tbd} component(s) have lcsc: TBD; replace with real LCSC numbers "
            "before ordering JLCPCB assembly (see fab-export-format.md)"
        )

    return errors, warnings


def validate(path: Path, quiet: bool = False) -> int:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL  cannot read {path}: {exc}")
        return 2

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    schema_errors = [
        f"schema: {'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
        for e in validator.iter_errors(doc)
    ]
    if schema_errors:
        for e in schema_errors:
            print(f"FAIL  {e}")
        return 1

    errors, warnings = check_netlist(doc)
    for e in errors:
        print(f"FAIL  {e}")
    if not quiet:
        for w in warnings:
            print(f"WARN  {w}")
        if not errors:
            n_c, n_n = len(doc["components"]), len(doc["nets"])
            print(f"OK    {path.name}: {n_c} components, {n_n} nets, {len(warnings)} warning(s)")
    return 1 if errors else 0


def main(argv: list[str]) -> int:
    quiet = "--quiet" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2
    worst = 0
    for p in paths:
        worst = max(worst, validate(Path(p), quiet=quiet))
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
