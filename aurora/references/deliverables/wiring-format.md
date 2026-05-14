# Wiring Format

Wiring documentation format for hardware projects. Used by Volt under Iron Law 8 (Complete Delivery). Lives in the project's `README.md` under `## Wiring`, or in a dedicated `WIRING.md` file for multi-board projects.

## Required parts

Every wiring section contains, in this order:

1. **Connection table** (machine-readable, copy-pasteable into electronics tools).
2. **ASCII diagram** (visual, scannable at a glance).
3. **Power budget** (one short paragraph).
4. **Safety notes** (mains, batteries, inductive loads).

## 1. Connection table

| Signal | MCU pin (board name) | Component | Component pin | Wire color (suggested) | Notes |

- **Signal** — what the wire carries (3.3V, GND, I2C SDA, UART TX, PWM, ADC, INT).
- **MCU pin** — the GPIO number plus the silkscreen label as it appears on the board the BOM names. `GPIO 8 (board label: G8)` is fine; ambiguity is not.
- **Component** — the component name from the BOM, matched exactly so a reader can cross-reference.
- **Component pin** — the pin label on the component (VDD, SDA, IRQ, etc.).
- **Wire color** — a suggestion only, but pick consistent conventions (red for VCC, black for GND, blue for I2C SDA, yellow for I2C SCL) so beginners can build the recommendation into a habit.
- **Notes** — pull-up resistor value, decoupling capacitor, inductive-load diode, common-ground requirement, anything a builder must do for the connection to work.

## 2. ASCII diagram

Required even when the connection table is complete. Beginners read pictures faster than tables. Format:

```
ESP32-S3 DevKit C-1            SCD40 breakout
┌───────────────┐              ┌───────────┐
│ 3V3  ●────────────────────── ● VDD       │
│ GND  ●────────────────────── ● GND       │
│ G8   ●──── pull-up 4.7kΩ ─── ● SDA       │
│ G9   ●──── pull-up 4.7kΩ ─── ● SCL       │
└───────────────┘              └───────────┘
```

Multi-component projects get a master diagram plus one per sub-circuit (e.g. sensor block, display block, button block). Master diagram shows components as boxes with a single wire between them; sub-circuits show the per-pin detail.

## 3. Power budget

One paragraph naming:

- **Peak current draw** for every component (best estimate from datasheet).
- **Voltage rail** the component sits on (3.3V regulated, 5V from USB, battery raw).
- **Total estimated current** for the whole circuit, especially when the project runs on a battery or solar.
- **Whether the MCU's onboard regulator is sufficient**, or whether a separate supply is needed.

For battery or solar projects: Iron Law 4 says flag Watt before delivering the BOM. The power budget here is the input to that calculation.

## 4. Safety notes

Required, even for low-voltage projects. Categories that always get a note when relevant:

- **Mains-powered boards** (Shelly, Sonoff): live wiring requires a qualified electrician. The wiring section must say this explicitly.
- **LiPo / Li-ion batteries**: protection circuit required. Never charge without one. Cite the protection IC by name (TP4056 or similar) in the BOM.
- **Inductive loads** (motors, relays, solenoids, valves): flyback diode required across the load. Position and polarity must be in the diagram.
- **ADC inputs**: voltage above the ADC reference fries the pin. Note the divider or clamp Zener if used.
- **Voltage level mismatch**: 5V sensor on a 3.3V MCU needs a level shifter (BSS138 for I2C, TXS0108E otherwise). The shifter goes in the BOM.

## What goes in a separate `WIRING.md`

When the project has more than ~12 rows in the connection table, or more than 3 separate sub-circuits, split it out:

- Keep a one-line summary in `README.md` under `## Wiring`: "See [WIRING.md](./WIRING.md)."
- Move the full content to `WIRING.md`.

For breadboard and perfboard tier projects with a single sub-circuit, keep wiring inline in `README.md`.

## What NOT to do

- No "see schematic" placeholder in the connection table. The table must stand on its own.
- No GPIO without a wire color suggestion. Beginners benefit, advanced users ignore.
- No diagram without a connection table, and no table without a diagram. They serve different readers.
- No PCB pin numbers (J1.3, U2.7) in place of board-silkscreen labels. The reader does not have the board file open.
