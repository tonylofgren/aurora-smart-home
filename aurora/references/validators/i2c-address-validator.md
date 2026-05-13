# I2C Address Validator

Verifies that no two devices on the same I2C bus share an address. I2C is a shared two-wire bus; if two components default to address `0x76` and the YAML wires both to the same SDA/SCL pair, the bus will appear to work intermittently or report wrong values — a classic "it works once and then never again" bug that is hard to debug from logs alone.

## When to Run

Volt MUST run this validator after pin allocation (Step 7) whenever the planned YAML includes two or more I2C-protocol components on the same bus. If only one I2C device is in the project, the validator can be skipped — but Volt should still emit a one-line note so the snapshot records the check was considered.

The validator also runs on GPIO expanders (`aurora/references/expanders/`) and I2C multiplexers (TCA9548A). Components placed behind a multiplexer channel do not collide with components on other channels.

## Inputs

- `bus_assignments`: list of objects, one per planned I2C device, with shape `{"component_id": "<id>", "default_addresses": [<int>, ...], "strap_pin_state": "<low|high|unset>", "bus": "<bus_id>"}`. `bus` is `default` for projects with a single bus; for multi-bus or multiplexed setups it identifies which physical bus the component sits on.
- `component_profiles`: object mapping each `component_id` to its parsed component profile (loaded from `aurora/references/components/`). The validator reads `i2c.default_addresses` and `i2c.address_strap_pin`.
- `expander_profiles` (optional): parsed expander profiles for any chips on the bus.

## Checks

For each I2C bus in `bus_assignments`:

1. **Direct address collision** — group devices on the same `bus` value. If two devices' chosen addresses overlap, fail: `Bus '<bus_id>' has '<a>' and '<b>' on address 0x<addr>. Move one device to its alternate address (<list of alternates>) by setting the address-strap pin, or place one device behind an I2C multiplexer (TCA9548A).`

2. **Strap pin not specified** — if a component has more than one entry in `default_addresses` and the project does not set `strap_pin_state`, fail: `<component_id> can be at 0x<a> or 0x<b> depending on its address-strap pin (<profile.i2c.address_strap_pin>). The project does not specify which. Pick one and add the pull resistor explicitly to the wiring.`

3. **Multiplexer channels** — when a TCA9548A appears in `expander_profiles`, devices placed on channel N do not collide with devices on channel M. Apply check #1 within each channel only.

4. **GPIO expander address collision** — expanders themselves have I2C addresses (PCF8574 defaults to 0x20-0x27 depending on A0/A1/A2 strap pins, MCP23017 similarly). Apply check #1 to expander chips as well as sensors.

5. **Common 7-bit reserved range** — addresses 0x00-0x07 and 0x78-0x7F are reserved by the I2C specification. Fail if any component is wired to one: `0x<addr> is in the I2C reserved range (0x00-0x07 or 0x78-0x7F). Pick a different default for <component_id>.` This catches mis-keyed addresses, not intentional design choices.

6. **Maximum speed mismatch** — when components on the same bus have differing `i2c.max_speed_khz` values, the bus speed must be set to the lowest. Emit a warning: `Bus '<bus_id>' runs <a> @ <a_max>kHz and <b> @ <b_max>kHz on the same lines. Set the ESPHome i2c frequency to <min(a_max, b_max)>kHz; otherwise the slower device misbehaves.`

## Output

- Pass: empty failures list.
- Warnings: list of warning strings. Volt surfaces these but does not block.
- Failures: list of failure strings. Volt MUST NOT generate YAML if non-empty. Recommended remediations are stated in each failure message.


Failure and warning entries follow the four-tier output defined in [`_tiered-errors.md`](_tiered-errors.md): `❌ Problem` (short) / `📚 Explanation` (medium) / `🔧 Fix` (concrete) / `💡 Deeper` (optional). Tiers 1 and 3 are mandatory for every failure; tier 2 is added during the next round of edits where it is still missing.

## Examples

### Example 1: BME280 + BMP280 collision

Input:
```
bus_assignments:
  - component_id: bme280
    default_addresses: [0x76, 0x77]
    strap_pin_state: unset
    bus: default
  - component_id: bmp280
    default_addresses: [0x76, 0x77]
    strap_pin_state: unset
    bus: default
```

Output:
```
Failures:
- bme280 can be at 0x76 or 0x77 depending on its address-strap pin (SDO). The project does not specify which. Pick one and add the pull resistor explicitly to the wiring.
- bmp280 can be at 0x76 or 0x77 depending on its address-strap pin (SDO). The project does not specify which. Pick one and add the pull resistor explicitly to the wiring.
- Bus 'default' has 'bme280' and 'bmp280' on address 0x76. Move one device to its alternate address ([0x77]) by setting the address-strap pin, or place one device behind an I2C multiplexer (TCA9548A).
```

Volt rewrites the BOM with the SDO pin of one device tied high to move it to 0x77.

### Example 2: SCD40 + AHT20 (no conflict)

Input:
```
bus_assignments:
  - component_id: scd40
    default_addresses: [0x62]
    bus: default
  - component_id: aht20
    default_addresses: [0x38]
    bus: default
```

Output:
```
Failures: []
Warnings: []
```

### Example 3: PCF8574 with default straps + SCD40

Input:
```
bus_assignments:
  - component_id: pcf8574
    default_addresses: [0x20]
    bus: default
  - component_id: scd40
    default_addresses: [0x62]
    bus: default
```

Output:
```
Failures: []
Warnings: []
```

### Example 4: Reserved range

Input:
```
bus_assignments:
  - component_id: custom_breakout
    default_addresses: [0x03]
    bus: default
```

Output:
```
Failures:
- 0x03 is in the I2C reserved range (0x00-0x07 or 0x78-0x7F). Pick a different default for custom_breakout.
```
