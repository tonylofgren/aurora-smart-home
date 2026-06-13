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
    python aurora/scripts/sync_jlcpcb_status.py --stock          # refresh stock from parts API
    python aurora/scripts/sync_jlcpcb_status.py --download --stock  # both

Library type and MOQ come from the CDFER CSV. Coarse stock status
(in_stock / low_stock / out_of_stock) comes from the live JLCPCB parts
API via --stock; it is coarse on purpose so the catalog does not churn
on every sync.

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
        # The CDFER CSV only carries the basic/preferred subset. A part
        # already known to be in the extended library stays "expand";
        # anything else absent becomes "not_listed".
        if sourcing.get("jlcpcb_library_type") != "expand":
            new["jlcpcb_library_type"] = "not_listed"
        new.pop("jlcpcb_moq", None)
    new["jlcpcb_checked"] = today

    if new == sourcing:
        return "unchanged"
    doc["sourcing"] = new
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")
    return f"updated ({new['jlcpcb_library_type']})"


PARTS_API = ("https://jlcpcb.com/api/overseas-pcb-order/v1/"
             "shoppingCart/smtGood/selectSmtComponentList")


def stock_status(count: int) -> str:
    """Coarse stock bucket. Coarse on purpose: exact counts change hourly and
    would churn the catalog on every sync. What is actionable is in/low/out."""
    if count <= 0:
        return "out_of_stock"
    if count < 100:
        return "low_stock"
    return "in_stock"


def fetch_stock(lcsc: str) -> int | None:
    """Live stock count for an LCSC code from the JLCPCB parts API, or None if
    the part is not returned. Network call; used only by --stock."""
    body = json.dumps({"keyword": lcsc, "currentPage": 1, "pageSize": 3}).encode()
    req = urllib.request.Request(
        PARTS_API, data=body, method="POST",
        headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    items = ((data.get("data") or {}).get("componentPageInfo") or {}).get("list") or []
    for it in items:
        if it.get("componentCode") == lcsc:
            return int(it.get("stockCount") or 0)
    return None


def sync_stock_profile(path: Path, today: str) -> str:
    """Refresh jlcpcb_stock_status for one profile from the live parts API."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    sourcing = doc.get("sourcing")
    if not sourcing or sourcing.get("lcsc", "TBD") == "TBD":
        return "skipped (no verified lcsc)"
    try:
        count = fetch_stock(sourcing["lcsc"])
    except Exception as exc:
        return f"error ({type(exc).__name__})"
    new = dict(sourcing)
    new["jlcpcb_stock_status"] = "out_of_stock" if count is None else stock_status(count)
    new["jlcpcb_checked"] = today
    if new == sourcing:
        return "unchanged"
    doc["sourcing"] = new
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")
    return f"updated ({new['jlcpcb_stock_status']}, stock={count})"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, help="local assembly-details.csv (library type + MOQ)")
    ap.add_argument("--download", action="store_true", help=f"fetch {CSV_URL} (library type + MOQ)")
    ap.add_argument("--stock", action="store_true",
                    help="refresh coarse stock status from the live JLCPCB parts API")
    args = ap.parse_args(argv)

    if not (args.csv or args.download or args.stock):
        ap.error("choose at least one of --csv, --download, --stock")

    today = datetime.date.today().isoformat()

    status = None
    if args.csv or args.download:
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

    updated = 0
    for d in PROFILE_DIRS:
        if not d.is_dir():
            continue
        for path in sorted(d.rglob("*.json")):
            if status is not None:
                r = sync_profile(path, status, today)
                print(f"{path.relative_to(REPO_ROOT)}: {r}")
                updated += r.startswith("updated")
            if args.stock:
                r = sync_stock_profile(path, today)
                print(f"{path.relative_to(REPO_ROOT)} [stock]: {r}")
                updated += r.startswith("updated")
    extra = f", {len(status)} parts in CSV" if status is not None else ""
    print(f"sync_jlcpcb_status: {updated} field-set(s) updated{extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
