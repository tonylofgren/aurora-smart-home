# Voltage Level Validator

Verifies that every sensor or actuator on a project runs at a voltage the board can supply, and that no logic line crosses a voltage boundary without a level shifter. Connecting a 5V sensor's data line to a 3.3V ESP32 input is a common beginner mistake — the GPIO is rated for 3.6V max, but a 5V signal can exceed that and either crash the chip or kill the input over time.

## When to Run

Volt MUST run this validator after pin allocation (Step 7) and before generating ESPHome YAML. It runs on every project that includes one or more components — there is no QUICK-mode exemption because miswiring voltage levels can damage hardware permanently.

## Inputs

- `board_profile`: parsed JSON from `aurora/references/boards/<chip>/<board>.json`. Reads:
  - `power.operating_voltage` — the board's logic-level voltage (typically 3.3 for ESP32 family, 5.0 for some classic Arduinos)
  - `power.gpio_5v_tolerant` — boolean
  - `power.input_voltage_range` — supply range, e.g. `"3.3V-5V via USB"`
- `component_assignments`: list of `{"component_id": "<id>", "supply_voltage": <number>, "uses_logic_lines": true|false}`. `supply_voltage` is the voltage the sensor is being given (often 3.3 or 5).
- `component_profiles`: object mapping `component_id` to parsed profile. Reads:
  - `power.voltage_min` / `voltage_max` — supply tolerance
  - `power.tolerates_5v` — boolean (whether the sensor can run at 5V)
  - `power.level_shifter_required_on_5v_board` — boolean

## Checks

For each component in `component_assignments`:

1. **Supply outside profile range** — if `supply_voltage` is below `component_profiles[<id>].power.voltage_min` or above `voltage_max`, fail: `<component_id> is being supplied at <V>V but its profile says <min>V-<max>V. Re-check the wiring or pick a different sensor.`

2. **5V sensor on 3.3V-only logic** — if `component_assignments[<id>].supply_voltage` is 5 and `component_assignments[<id>].uses_logic_lines` is true and `board_profile.power.gpio_5v_tolerant` is false, fail: `<component_id> is supplied at 5V on a 3.3V-only board (<display_name>). The sensor's logic outputs will exceed the GPIO's max input voltage (3.6V) and can damage the chip. Add a BSS138 level shifter on the data lines, or supply the sensor at 3.3V if its profile allows.`

3. **Component flags level shifter as required** — if `component_profiles[<id>].power.level_shifter_required_on_5v_board` is true and `supply_voltage` is 5, fail: `<component_id>'s profile flags 'level_shifter_required_on_5v_board'. Add a BSS138 (recommended for I2C) or TXS0108E (general-purpose) shifter between the sensor and the ESP32. See aurora/references/voltage-shifters/.`

4. **Board cannot supply requested voltage** — if `supply_voltage` is 5 and `board_profile.power.input_voltage_range` does not include 5V routing (no `5V` mentioned in the field), fail: `<display_name> cannot supply 5V to the component without external power. Either run the sensor at 3.3V (if its profile allows) or add an external 5V rail and shifter.`

5. **3.3V sensor below board logic** — if `component_assignments[<id>].supply_voltage` is 3.3 and the component's profile minimum is above 3.3 (e.g. some 5V-only relays), fail: `<component_id> requires a minimum of <min>V but is being supplied at 3.3V. The sensor will either not power on or behave erratically.`

6. **Logic level mismatch warning** — if the component runs at 3.3V but reports logic-level outputs near 3.0V and the board logic-high threshold is higher (rare on ESP32 but possible), emit a warning: `<component_id> logic-high output is <V>V; the board may not register it reliably. Add a pull-up or use a different sensor.`

## Output

- Pass: empty failures list.
- Warnings: list of warning strings.
- Failures: list of failure strings. Volt MUST NOT generate YAML if non-empty. The user picks: change supply voltage, add a level shifter (Volt updates the BOM), or substitute a 3.3V-native component.


Failure and warning entries follow the four-tier output defined in [`_tiered-errors.md`](_tiered-errors.md): `❌ Problem` (short) / `📚 Explanation` (medium) / `🔧 Fix` (concrete) / `💡 Deeper` (optional). Tiers 1 and 3 are mandatory for every failure; tier 2 is added during the next round of edits where it is still missing.

## Suggested Level Shifters

When a failure recommends adding a shifter, Volt picks based on the bus type:

- I2C — BSS138 (open-drain, weak pull-ups) — see `aurora/references/voltage-shifters/bss138.json`
- General-purpose (push-pull SPI, UART) — TXS0108E — see `aurora/references/voltage-shifters/txs0108e.json`

## Examples

### Example 1: DHT22 at 5V on ESP32-S3 (not 5V tolerant)

Input:
```
board_profile.power: {operating_voltage: 3.3, gpio_5v_tolerant: false}
component_assignments:
  - component_id: dht22
    supply_voltage: 5
    uses_logic_lines: true
component_profiles.dht22.power: {voltage_min: 3.3, voltage_max: 6.0, tolerates_5v: true, level_shifter_required_on_5v_board: true}
```

Output:
```
Failures:
- dht22 is supplied at 5V on a 3.3V-only board (ESP32-S3 DevKit C-1). The sensor's logic outputs will exceed the GPIO's max input voltage (3.6V) and can damage the chip. Add a BSS138 level shifter on the data lines, or supply the sensor at 3.3V if its profile allows.
- dht22's profile flags 'level_shifter_required_on_5v_board'. Add a BSS138 (recommended for I2C) or TXS0108E (general-purpose) shifter between the sensor and the ESP32. See aurora/references/voltage-shifters/.
```

Volt's fix: drop supply to 3.3V (dht22 supports 3.3V-6.0V) — no shifter needed.

### Example 2: BME280 at 3.3V (healthy)

Input:
```
board_profile.power: {operating_voltage: 3.3, gpio_5v_tolerant: false}
component_assignments:
  - component_id: bme280
    supply_voltage: 3.3
    uses_logic_lines: true
component_profiles.bme280.power: {voltage_min: 1.7, voltage_max: 3.6, tolerates_5v: false, level_shifter_required_on_5v_board: true}
```

Output:
```
Failures: []
Warnings: []
```

### Example 3: 5V-only relay module on a 3.3V board with external 5V supply

Input:
```
board_profile.power: {operating_voltage: 3.3, gpio_5v_tolerant: false, input_voltage_range: "3.3V-12V via Vin"}
component_assignments:
  - component_id: relay_module_5v
    supply_voltage: 5
    uses_logic_lines: true
component_profiles.relay_module_5v.power: {voltage_min: 4.5, voltage_max: 5.5, tolerates_5v: true, level_shifter_required_on_5v_board: true}
```

Output:
```
Failures:
- relay_module_5v is supplied at 5V on a 3.3V-only board (ESP32 DevKit V1). The sensor's logic outputs will exceed the GPIO's max input voltage (3.6V) and can damage the chip. Add a BSS138 level shifter on the data lines, or supply the sensor at 3.3V if its profile allows.
- relay_module_5v's profile flags 'level_shifter_required_on_5v_board'. Add a BSS138 (recommended for I2C) or TXS0108E (general-purpose) shifter between the sensor and the ESP32. See aurora/references/voltage-shifters/.
```

Volt's fix: add a TXS0108E on the relay's control line. Update the BOM and wiring diagram.
