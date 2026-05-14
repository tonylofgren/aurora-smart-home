# BOM Format

Bill of Materials format for hardware projects. Used by Volt under Iron Law 8 (Complete Delivery). Sage and other software-only agents do not produce a BOM.

## Required structure

Every BOM is a Markdown table with these columns, in this order:

| # | Component | Qty | Source | Unit price (USD) | Notes |

- **#** — sequential row number starting at 1.
- **Component** — exact part name a buyer can search for. Include the package or variant when ambiguous (`BME280 (I2C breakout)`, not just `BME280`).
- **Qty** — integer count.
- **Source** — common source (AliExpress, Adafruit, Mouser, DigiKey, LCSC, local maker store). Use the most realistic source for hobby-scale projects.
- **Unit price (USD)** — rough estimate prefixed with `~`. Always USD. Always rough.
- **Notes** — package (0805, SOIC-8), I2C address, voltage range, any quirk a buyer needs to know.

## Required footer

Below the table, every BOM ends with:

```
**Estimated total:** ~XX USD (<month YYYY>, <source assumption>).

Prices are rough estimates. Actual cost varies by region, supplier,
shipping, and current stock. Verify before ordering, especially for
production volumes.
```

The date stamp is mandatory. Prices drift. A reader landing on the BOM six months later needs to know how old the numbers are.

## Production tier addition

When the manufacturing tier (per Iron Law 8) is `custom-PCB` or `production`, the BOM gets two extra columns inserted before Notes:

| # | Component | Qty | Source | Unit price (USD) | LCSC part # | Package | Notes |

- **LCSC part #** — the JLCPCB / LCSC catalog number when the component is available there. Empty for components that are not.
- **Package** — SMT package (0805, SOIC-8, QFN-32, etc.) for placement files.

## Example (breadboard tier)

```
| # | Component                       | Qty | Source       | Unit price (USD) | Notes                                                |
|---|---------------------------------|-----|--------------|------------------|------------------------------------------------------|
| 1 | ESP32-S3 DevKit C-1             | 1   | AliExpress   | ~5               | USB-C, 8MB PSRAM, full pinout.                       |
| 2 | SCD40 CO2 sensor breakout       | 1   | AliExpress   | ~25              | I2C 0x62, factory calibrated, 2.4V–5.5V tolerant.    |
| 3 | Jumper wires (M-F, 20 cm, set)  | 1   | AliExpress   | ~2               | At least 4 of red/black/blue/yellow.                 |
| 4 | Breadboard 400-tie              | 1   | AliExpress   | ~2               | Half-size is enough for this project.                |

**Estimated total:** ~34 USD (May 2026, AliExpress with regular shipping not included).

Prices are rough estimates. Actual cost varies by region, supplier,
shipping, and current stock. Verify before ordering, especially for
production volumes.
```

## What goes in `Notes`

Always at least one note per row, even if it is short. Useful note categories:

- **Variant disambiguation** when the part is easily confused with a similar one (BME280 vs BMP280, SCD40 vs SCD41, AM312 vs HC-SR501).
- **Pinout / addressing** (I2C address, fixed or strapped) so wiring decisions are reproducible.
- **Voltage range** when the component is not a default-safe 3.3V-only device.
- **Calibration requirement** so buyers know if a sensor needs prep before use.
- **Lifecycle warning** when the part is end-of-lifed or has a recommended successor.

## What NOT to put in the BOM

- No prices without a date stamp in the footer.
- No invented sources. If you do not know a reliable source, say so in Notes, do not guess.
- No "see Notes" placeholders in the Source column. Always name a real source.
- No "TBD" rows. If a part is undecided, the BOM is not ready to ship.
