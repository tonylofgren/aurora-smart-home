# Fab Export Format

Machine-readable manufacturing exports that take a project from "documented" to "orderable". They complement the human-readable artifacts in `pcb-format.md`; they never replace them.

| Artifact | Tier | Status |
|----------|------|--------|
| `hardware/schematic.json` | custom-PCB: recommended, production: required | Netlist companion to SCHEMATIC.md |
| `hardware/BOM.csv` | custom-PCB: recommended, production: required | JLCPCB/KiCad-compatible BOM export |
| `hardware/ENCLOSURE.scad` | any tier, on request | Parametric OpenSCAD enclosure |
| Fab order log in MANUFACTURING.md | production | Order status tracking table |

## schematic.json

Validates against `aurora/references/schemas/schematic.schema.json`. Same component list and net list as SCHEMATIC.md, structured for scripts:

```json
{
  "schema_version": "1.0",
  "project": {
    "name": "water-leak-sensor",
    "board": "esp32-c3-devkitm-1",
    "revision": "A",
    "generated": "2026-06-12",
    "generated_with": "aurora@aurora-smart-home (esphome skill)"
  },
  "components": [
    {"refdes": "U1", "value": "ESP32-C3-DevKitM-1", "description": "MCU dev module", "package": "module", "lcsc": "TBD", "bom_row": 1},
    {"refdes": "R1", "value": "1M", "description": "Probe pull-down", "package": "0603", "lcsc": "TBD", "bom_row": 2},
    {"refdes": "J1", "value": "2-pin screw terminal", "description": "Leak probe connector", "package": "5.0mm pitch", "lcsc": "TBD", "bom_row": 3}
  ],
  "nets": [
    {"name": "3V3", "pins": ["U1.3V3", "J1.1"]},
    {"name": "PROBE_SENSE", "pins": ["U1.GPIO4", "R1.A", "J1.2"], "note": "1M pull-down keeps the input low when dry"},
    {"name": "GND", "pins": ["U1.GND", "R1.B"]}
  ]
}
```

Rules:

1. **Every component in SCHEMATIC.md appears here with the same refdes.** The two files describe one design; a mismatch is a delivery failure.
2. **`lcsc` is the real LCSC part number when sourcing is decided, the literal string `TBD` when it is not.** Never invent part numbers. Sourcing happens at jlcpcb.com/parts, and the BOM footer carries the date stamp for when prices were checked.
3. **`bom_row` cross-references BOM.md** so a reader can move between the priced table and the netlist without guessing.
4. **Net notes carry constraints** (pull-up values, impedance, antenna keep-out), mirroring the per-net design notes in SCHEMATIC.md.
5. **Validate before delivery:** `python aurora/scripts/validate_schematic.py <project>/hardware/schematic.json` checks the schema plus netlist rules (refdes uniqueness, no pin in two nets, no undeclared components, ground net present). Zero errors required; warnings (TBD parts, unconnected components) are allowed but must be intentional.

## BOM.csv

CSV export of the BOM in the column order JLCPCB assembly expects, which KiCad BOM tools can also produce and consume:

```text
Comment,Designator,Footprint,LCSC Part #
ESP32-C3-DevKitM-1,U1,module,TBD
1M 0603,R1,R0603,TBD
Screw terminal 2P 5.0mm,J1,TerminalBlock_5.0mm,TBD
```

Rules:

1. **Column header is exactly** `Comment,Designator,Footprint,LCSC Part #`. JLCPCB's BOM parser matches on these names.
2. **One row per part value, designators comma-separated inside quotes** when a value is used by several refdes: `"R1,R2,R3"`.
3. **BOM.csv carries no prices.** Prices, quantities for hand-assembly, and the date-stamped total live in BOM.md per `bom-format.md`. The CSV is a fab input, not a shopping list.
4. **DNP parts are omitted** from the CSV (JLCPCB assembles everything listed) and marked `dnp: true` in schematic.json instead.

## KiCad workflow

The reader redraws the schematic in KiCad using schematic.json as the checklist:

1. Create the KiCad project; add each component from `components[]`, assigning the refdes and footprint listed.
2. Wire each net from `nets[]`; the `refdes.pin` strings map directly to KiCad pin connections. Tick off nets one by one; the file is the definition of done.
3. Annotate is already done (refdes are fixed); run ERC and compare any complaints against the net notes.
4. For assembly quoting, export gerbers plus position file from KiCad and pair them with `BOM.csv`. The kicad-jlcpcb-tools plugin automates gerber, BOM, and CPL generation in JLCPCB's expected formats and lets you assign real LCSC numbers to replace `TBD`.

## ENCLOSURE.scad

Parametric OpenSCAD box generated from the template at `aurora/references/templates/enclosure.scad`. The specialist copies the template into `<project>/hardware/ENCLOSURE.scad` and sets the parameter block at the top:

```text
board_l / board_w        PCB outline in mm (from PCB-NOTES.md)
board_clearance          air gap around the PCB
wall / floor_h / lid_h   shell thicknesses
standoff_h / standoff_d  PCB standoffs, M2.5 pilot holes by default
cable_d                  cable gland / wire opening diameter, 0 for none
vent_rows                ventilation slot rows, 0 for sealed
sensor_window_w/_l       rectangular opening in the lid, 0 for none
```

Rules: the enclosure references the board size justified in PCB-NOTES.md; sensors that sample air (temperature, humidity, VOC) get `vent_rows >= 2`; outdoor or wet placements get `vent_rows: 0` plus a note that sealing and glands are the user's verification responsibility (and Vera's hazard analysis applies). Print settings live in a comment block at the bottom of the file.

## JLCPCB ordering workflow and order log

Production-tier MANUFACTURING.md gains a **Fab order log** section. JLCPCB has no public order-status API, so the log is updated manually as the order advances:

```markdown
## Fab order log

| Date | Order # | Stage | Notes |
|------|---------|-------|-------|
| 2026-06-12 | TBD | Files uploaded | gerbers + BOM.csv + CPL, DFM passed |
| | | Payment confirmed | |
| | | In production | |
| | | SMT assembly | |
| | | Shipped | tracking # |
| | | Received and tested | link TEST-JIG.md results |
```

Ordering sequence the log tracks: upload gerber zip, confirm DFM review, upload BOM.csv and CPL for assembly quote, resolve part availability (replace every `TBD` with a real LCSC number or mark the part for hand-assembly), pay, then track production stages from the JLCPCB order page into the log.

## What NOT to do

- Do not invent LCSC part numbers, prices, or stock levels. `TBD` plus a sourcing instruction beats a fabricated number that wastes a fab round.
- Do not generate schematic.json without SCHEMATIC.md (or the reverse) at custom-PCB tier and above; they ship together.
- Do not put prices in BOM.csv; the priced table is BOM.md.
- Do not promise automated JLCPCB status sync; there is no public API, and the order log exists precisely to make manual sync cheap.
