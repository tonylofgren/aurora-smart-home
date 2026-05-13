# Pin Validator

Validates that every GPIO pin used in an ESPHome configuration exists on the selected board, is not reserved, and does not require special handling that the user has not provided.

## When to Run

Volt MUST run this validator after pin allocation (Step 7 of the validation workflow) and before generating YAML output. Other agents that touch GPIO (Echo, Nano, Watt) follow the same rule.

## Inputs

- `board_profile`: parsed JSON from `aurora/references/boards/<chip>/<board>.json`
- `pin_assignments`: object mapping component_id to a list of GPIO numbers, e.g. `{"bme280": [8, 9], "ld2410": [4, 5]}`
- `config_flags`: optional object describing project features that affect pin reservation, e.g. `{"usb_cdc_enabled": true, "psram_used": true, "wifi_enabled": true}`

## Checks

For every GPIO number in `pin_assignments`:

1. **Existence**: number must be in `board_profile.gpio.valid_pins`. If not, fail with: `GPIO <N> does not exist on <display_name>. Valid range: <list>.`

2. **USB reservation**: if `config_flags.usb_cdc_enabled` is true and number is in `board_profile.gpio.reserved_for_usb`, fail with: `GPIO <N> is used by USB CDC on <display_name>. Either move the pin or set usb_cdc: false (loses serial debug).`

3. **PSRAM reservation**: if `config_flags.psram_used` is true and number is in `board_profile.limitations.psram_blocks_gpio`, fail with: `GPIO <N> is reserved for PSRAM on <display_name>. Move the pin or build a board variant without PSRAM.`

4. **Flash reservation**: if number is in `board_profile.gpio.reserved_for_flash`, always fail with: `GPIO <N> is hardwired to the SPI flash chip. It cannot be used for anything else.`

5. **Strapping warning**: if number is in `board_profile.gpio.strapping_pins`, emit a warning (not a failure) with: `GPIO <N> is a strapping pin. Check the strapping_conflict_warnings entry: <text>. Add an external pull resistor matching the boot requirement.`

6. **Input-only check**: if `pin_assignments` requires output for this pin but number is in `board_profile.gpio.input_only`, fail with: `GPIO <N> is input only on <display_name>. Choose a different pin for outputs.`

7. **ADC2 with WiFi**: if number is in `board_profile.gpio.adc2_pins` and `config_flags.wifi_enabled` is true and `board_profile.limitations.adc2_blocked_when_wifi_active` is true, fail with: `GPIO <N> is on ADC2 which is unavailable while WiFi is active on <display_name>. Use an ADC1 pin instead: <adc1_pins>.`

## Output

- Pass: empty list
- Warnings: list of warning strings (Volt presents but does not block)
- Failures: list of failure strings (Volt MUST NOT generate YAML if non-empty)


Failure and warning entries follow the four-tier output defined in [`_tiered-errors.md`](_tiered-errors.md): `❌ Problem` (short) / `📚 Explanation` (medium) / `🔧 Fix` (concrete) / `💡 Deeper` (optional). Tiers 1 and 3 are mandatory for every failure; tier 2 is added during the next round of edits where it is still missing.

## Example

Input:
- `board_profile`: ESP32-S3 DevKit C-1
- `pin_assignments`: `{"hc_sr04": [19, 20]}`
- `config_flags`: `{"usb_cdc_enabled": true}`

Output:
```
Failures:
- GPIO 19 is used by USB CDC on ESP32-S3 DevKit C-1. Either move the pin or set usb_cdc: false (loses serial debug).
- GPIO 20 is used by USB CDC on ESP32-S3 DevKit C-1. Either move the pin or set usb_cdc: false (loses serial debug).
```
