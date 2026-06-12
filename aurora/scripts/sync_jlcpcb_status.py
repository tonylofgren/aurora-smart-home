#!/usr/bin/env python3
"""
aurora/scripts/sync_jlcpcb_status.py

Synchronizes the JLCPCB library status of component profiles against the
CDFER jlcpcb-parts-database (https://github.com/CDFER/jlcpcb-parts-database),
which publishes scraped/assembly-details.csv with the basic/preferred
assembly parts subset. No scraping happens here; this piggybacks on
CDFER's public CSV.

For every profile under aurora/references/components/ (and expanders/)
that declares sourcing.lcsc with a real C-number, the script updates:

    sourcing.jlcpcb_library_type   base | expand | not_listed
    sourcing.jlcpcb_moq            Min Order Qty (only when listed)
    sourcing.jlcpcb_checked        today's date

Profiles with sourcing.lcsc == "TBD" are skipped (populate the number
first, verified at jlcpcb.com/parts; never guess). not_listed means the
part is absent from the basic/preferred subset, i.e. extended-library
or out of stock; it is not an error.

Usage:
    python aurora/scripts/sync_jlcpcb_status.py --csv <path>     # local CSV
    python aurora/scripts/sync_jlcpcb_status.py --download       # fetch from CDFER

Exit codes:
    0  ran (whether or not anything changed); prints a summary
    2  CSV missing/unreadable
"""
from __future__ import annotations

import argparse
import csv
import datetime
import io
import json
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE_DIRS = [
    REPO_ROOT / "aurora" / "references" / "components",
    REPO_ROOT / "aurora" / "references" / "expanders",
]
CSV_URL = ("https://raw.githubusercontent.com/CDFER/jlcpcb-parts-database/"
           "main/scraped/assembly-details.csv")


def load_status(csv_text: str) -> dict[str, dict]:
    """Map numeric lcsc id -> {library_type, moq}."""
    table = {}
    for row in csv.DictReader(io.StringIO(csv_text)):
        table[row["lcsc"].strip()] = {
            "library_type": row["Component Library Type"].strip(),
            "moq": int(row["Min Order Qty"]) if row["Min Order Qty"].strip().isdigit() else None,
        }
    return table


def sync_profile(path: Path, status: dict[str, dict], today: str) -> str:
    doc = json.loads(path.read_text(encoding="utf-8"))
    sourcing = doc.get("sourcing")
    if not sourcing or sourcing.get("lcsc", "TBD") == "TBD":
        return "skipped (no verified lcsc)"

    numeric = sourcing["lcsc"].lstrip("C")
    entry = status.get(numeric)
    new = dict(sourcing)
    if entry:
        new["jlcpcb_library_type"] = entry["library_type"]
        if entry["moq"]:
            new["jlcpcb_moq"] = entry["moq"]
    else:
        new["jlcpcb_library_type"] = "not_listed"
        new.pop("jlcpcb_moq", None)
    new["jlcpcb_checked"] = today

    if new == sourcing:
        return "unchanged"
    doc["sourcing"] = new
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")
    return f"updated ({new['jlcpcb_library_type']})"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--csv", type=Path, help="local assembly-details.csv")
    group.add_argument("--download", action="store_true", help=f"fetch {CSV_URL}")
    args = ap.parse_args(argv)

    try:
        if args.download:
            with urllib.request.urlopen(CSV_URL, timeout=60) as resp:
                csv_text = resp.read().decode("utf-8")
        else:
            csv_text = args.csv.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"FAIL cannot load CSV: {exc}")
        return 2

    status = load_status(csv_text)
    today = datetime.date.today().isoformat()
    updated = 0
    for d in PROFILE_DIRS:
        if not d.is_dir():
            continue
        for path in sorted(d.rglob("*.json")):
            result = sync_profile(path, status, today)
            print(f"{path.relative_to(REPO_ROOT)}: {result}")
            updated += result.startswith("updated")
    print(f"sync_jlcpcb_status: {updated} profile(s) updated, {len(status)} parts in CSV")
    return 0


if __name__ == "__main__":
    sys.exit(main())
