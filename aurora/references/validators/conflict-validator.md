# Conflict Validator

Detects pin and bus conflicts when two or more components share a board. Pin validation alone is not enough: two correctly assigned pins can still collide.

## When to Run

Volt runs this validator after pin allocation (Step 7) and after pin-validator passes. It runs once per project, not once per component.

## Inputs

- `board_profile`: parsed board JSON
- `component_assignments`: list of objects, each `{"component_id": "bme280", "component_profile": <loaded JSON>, "pins": [8, 9], "i2c_address": "0x76"}`
- `config_flags`: same as for pin-validator

## Checks

1. **Pin collision (non-bus)**: For each pin, count how many components claim it. If a pin is claimed by more than one component AND none of the colliding components use a shared bus protocol (i2c, onewire), fail with: `GPIO <N> is claimed by both <component_a> and <component_b>. Choose distinct pins for non-bus protocols.`

2. **I2C bus sharing**: Components with `protocol: i2c` may share SDA/SCL. Group them by the SDA/SCL pair. For each group, verify the `i2c_address` values are unique. If not, fail with: `<component_a> and <component_b> both use I2C address <addr>. Reassign one address via the strap pin or add a TCA9548A multiplexer.`

3. **OneWire bus sharing**: Multiple DS18B20 sensors may share a single GPIO. Permit collision when ALL colliding components use `protocol: onewire`.

4. **Voltage compatibility**: For each component, if `component_profile.power.tolerates_5v` is false and `board_profile.power.gpio_5v_tolerant` is false, no issue. If the component is on a 5V board and the component is not tolerant, fail with: `<component_id> max voltage is <voltage_max>V but the board operates at 5V. Add a level shifter (e.g. TXS0108E or BSS138 for I2C).`

5. **Strapping pin conflict**: For each component pin in `board_profile.gpio.strapping_pins`, check `component_profile.pin_requirements.strapping_pin_ok`. If false, fail with: `<component_id> cannot use strapping pin GPIO <N>. The boot requirement conflicts with the component's idle level.`

6. **ADC requirement**: For each component where `component_profile.pin_requirements.adc_required` is true, verify the assigned pin is in `board_profile.gpio.adc1_pins` or `board_profile.gpio.adc2_pins`. If not, fail with: `<component_id> needs an ADC-capable pin, but GPIO <N> on <display_name> is digital-only.`

7. **Interrupt capability**: For each component where `interrupt_capable_required` is true, verify the pin supports edge interrupts on the chip. On ESP32 family all GPIO support interrupts except `input_only` listed without `interrupt_capable`. If incompatible, fail with: `<component_id> needs interrupt support on GPIO <N>, but the board profile does not list it as interrupt-capable.`

## Output

Same structure as pin-validator: `{failures: [...], warnings: [...]}`.

Volt MUST NOT generate YAML if `failures` is non-empty.

## Example

Input:
- `board_profile`: ESP32-S3 DevKit C-1
- Components:
  - `bme280` at I2C addresses 0x76, pins 8/9
  - A second BME280 at I2C address 0x76, pins 8/9

Output:
```
Failures:
- bme280 and bme280 both use I2C address 0x76. Reassign one address via the strap pin or add a TCA9548A multiplexer.
```
