# PCB Format

PCB artifact format for hardware projects that move past breadboard or perfboard. Used by Volt under Iron Law 8 (Complete Delivery) when the manufacturing tier is `custom-PCB` or `production`. The artifacts are textual specifications, not KiCad files (an LLM agent cannot reliably produce `.kicad_sch` or `.kicad_pcb` binaries).

## Manufacturing tiers

Volt asks the user which tier applies at the start of every hardware project. The answer determines which artifacts are required.

| Tier              | Wiring | BOM      | Schematic | PCB notes  | Manufacturing | Cost analysis | Certification | Test jig |
|-------------------|--------|----------|-----------|------------|---------------|---------------|---------------|----------|
| **Breadboard**    | yes    | yes      | -         | -          | -             | -             | -             | -        |
| **Perfboard**     | yes    | yes      | -         | -          | -             | -             | -             | -        |
| **Custom PCB (small batch, 1–50)** | yes | yes + LCSC + package | yes (text + ASCII) | yes (basic) | -             | yes (basic)   | -             | -        |
| **Production (100+)** | yes | yes (production BOM) | yes | yes (full)  | yes           | yes (detailed) | yes (CE/FCC path) | yes |

The user can override the recommended tier. If they pick `breadboard` for a project that obviously wants production (e.g. "I want to sell this to 200 people"), Volt asks once whether they want production artifacts, accepts the answer, and proceeds.

## Files per tier

### Custom PCB (small batch)

```
<project>/
├── README.md           (manual, links to the PCB files below)
├── BOM.md              (table with LCSC part numbers and packages)
├── SCHEMATIC.md
└── PCB-NOTES.md
```

### Production

```
<project>/
├── README.md
├── BOM.md
├── SCHEMATIC.md
├── PCB-NOTES.md
├── MANUFACTURING.md    (assembly service, stencil, finish, file expectations)
├── COST-ANALYSIS.md    (prototype vs volume pricing, break-even)
├── CERTIFICATION.md    (CE / FCC / RoHS path, pre-certified module strategy)
└── TEST-JIG.md         (production test rig: bed of nails, fixtures, pass/fail)
```

## SCHEMATIC.md format

Required sections:

1. **Component list with reference designators.** `U1` is the MCU, `U2` the sensor, `D1` the protection diode, etc. Cross-reference the BOM by row number.
2. **Net list.** For each net (named or numbered), list the pins it connects in the form `U1.GPIO8 -- U2.SDA -- R1.A`.
3. **ASCII block diagram** showing the major sub-circuits (power, MCU, sensor block, antenna section) and their connections at a high level.
4. **Per-net design notes** for anything non-trivial: pull-up values, decoupling caps, ferrite beads, ground-plane crossings.

The reader is expected to redraw this in KiCad (or hand it to a PCB designer). The schematic does not have to be visually beautiful — it has to be unambiguous.

## PCB-NOTES.md format

Required sections:

1. **Board outline and size estimate.** Width × height in mm. Justify against the BOM and the enclosure plan.
2. **Layer count.** 2-layer for most hobby projects; 4-layer when the antenna section needs a solid ground plane.
3. **Antenna clearance.** For ESP32-family boards with onboard PCB antennas: keep the keep-out zone clear of copper, ground pour, and components. Cite the exact zone shape from the chip's hardware design guide.
4. **Decoupling and bulk caps.** Position relative to the chip's power pins. 100nF within 5 mm of each VDD, plus a 10–22 µF bulk near the regulator output.
5. **Power section.** Regulator choice, input and output cap values, thermal vias if dropping more than ~500 mW.
6. **Connector placement.** USB-C / programming header / I/O headers — orientation and accessibility through the enclosure.
7. **Critical traces.** I2C / SPI / UART length, USB differential pair impedance, RF traces. Name them and state the constraint.
8. **Fanout strategy** for any QFN / BGA part. Most ESP32 dev modules avoid this, but raw ESP32-PICO requires it.

## MANUFACTURING.md format (production tier only)

Required sections:

1. **Assembly service recommendation.** JLCPCB, PCBWay, NextPCB, or local. Justify by board complexity, lead time, and component sourcing.
2. **Stencil type.** Framed vs frameless. Aperture reductions if any.
3. **Surface finish.** HASL, ENIG, OSP. Recommend ENIG for fine-pitch parts and for boards that sit in storage.
4. **File expectations.** Gerber (RS-274X), drill (.drl or Excellon), pick-and-place CSV (per the service's column expectations), BOM CSV.
5. **Panelization.** If the service requires it, what V-cut or tab-routing pattern. Otherwise note "single board".
6. **Test points.** Pads exposed for assembly verification. Position relative to the test jig.

## COST-ANALYSIS.md format (production tier only)

A small table:

| Volume       | PCB unit cost | Assembly unit cost | Components unit cost | Total unit cost | Total batch cost |
|--------------|---------------|--------------------|----------------------|-----------------|------------------|
| 5 (prototype) | ~5 USD        | ~15 USD            | ~20 USD              | ~40 USD         | ~200 USD         |
| 50 (small batch) | ~2 USD     | ~6 USD             | ~18 USD              | ~26 USD         | ~1,300 USD       |
| 500 (production) | ~0.8 USD   | ~3 USD             | ~15 USD              | ~18.8 USD       | ~9,400 USD       |

Date the table. Note assumptions: which service, which region, components from LCSC's standard library vs extended.

## CERTIFICATION.md format (production tier only)

Sections:

1. **Target markets.** EU (CE), US (FCC), Canada (ISED), UK (UKCA), and any others the user names.
2. **Pre-certified module strategy.** Using ESP32-WROOM / ESP32-S3-WROOM and similar modules avoids most of the radio certification cost because the module ships pre-certified. Document which module is used and which certifications it inherits.
3. **Additional testing required.** Even with a pre-certified module: EMC pre-scan, RoHS declaration, REACH declaration, packaging marking.
4. **Test labs.** Name two or three reputable labs by region with approximate cost ranges.
5. **Self-declaration vs notified body.** Class 1 vs Class 2 radio under RED, and what each path costs.

The user is responsible for their own certification. Volt names the path, the user follows it.

## TEST-JIG.md format (production tier only)

Sections:

1. **Test point list.** Reference each test point from PCB-NOTES.md.
2. **Pass/fail criteria.** What each test point should read under what condition.
3. **Fixture mechanical layout.** Bed-of-nails footprint, spring-pin diameter, alignment dowels.
4. **Programming interface.** UART pins exposed on the jig for firmware flashing.
5. **Functional test sequence.** Power on → flash → run self-test → verify outputs → pass.

## What NOT to do

- No promises that the schematic compiles in KiCad. It will not. A human or a PCB designer will redraw it.
- No invented LCSC part numbers. If the agent does not know the number, leave it blank and say so in BOM Notes.
- No "approximately correct" antenna keep-out zones. Cite the chip's hardware design guide directly or omit the section.
- No certification claims. The agent names the path, the user pays the lab, the lab certifies.
