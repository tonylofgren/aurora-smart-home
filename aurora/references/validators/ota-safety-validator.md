# OTA Safety Validator

Verifies that the generated ESPHome configuration leaves the user a way to recover the device if an OTA update bricks it. The most common cause of "I uploaded a broken config and now the ESP is offline" is a YAML that disables WiFi or removes the `ota` block while no physical recovery path exists.

## When to Run

Volt MUST run this validator before generating any ESPHome YAML that goes through OTA. Run after pin allocation (Step 7 of the validation workflow) and after the conflict-validator. If failures are reported, do NOT generate the YAML — describe the recovery risk and ask the user to choose a safer configuration.

## Inputs

- `board_profile`: parsed JSON from `aurora/references/boards/<chip>/<board>.json`. The validator reads `board_profile.ota_safety` for board-specific recovery information.
- `planned_features`: object describing which features the new YAML will enable, e.g. `{"wifi": true, "ota": true, "usb_cdc": true, "ap_fallback": false, "factory_reset_button": true}`.

## Checks

For every planned configuration:

1. **WiFi disabled with no fallback** — if `planned_features.wifi` is `false` and `board_profile.ota_safety.external_programmer_needed` is `false`, the device can still be recovered via USB CDC if `usb_cdc_recovery` is `true`. Otherwise fail: `Disabling WiFi removes the only OTA path on <display_name>. Either keep wifi enabled, add an AP fallback, or accept that future updates will require a USB cable / external programmer.`

2. **OTA block removed** — if `planned_features.ota` is `false`, emit a failure: `'ota:' block removed. The device cannot be reflashed wirelessly. Future updates will require <recovery>.` `<recovery>` is `'usb_cdc'` if `board_profile.ota_safety.usb_cdc_recovery` is `true`, otherwise `'an external programmer or factory reset (pin <factory_reset_pin>)'`.

3. **AP fallback recommendation** — if `planned_features.wifi` is `true` and `planned_features.ap_fallback` is `false`, emit a warning (not a failure): `Consider adding an 'ap:' fallback. If the configured WiFi credentials are wrong or the network changes, the device will boot into an access point and stay reachable for re-flashing. No fallback means a wrong SSID requires physical access.`

4. **Factory reset button on strapping pin** — if `planned_features.factory_reset_button` is `true` and the factory-reset GPIO equals a known strapping pin from `board_profile.gpio.strapping_pins`, emit a warning: `Factory reset button on GPIO <N> shares the strapping line. Add a strong pull resistor to the boot-required level so the device still boots cleanly when the button is not pressed.` (The `factory_reset_pin` value in the profile is the validator's default suggestion; if the user overrides, the validator checks the override.)

5. **External programmer requirement** — if `board_profile.ota_safety.external_programmer_needed` is `true` and the user has not acknowledged it in the project state, emit a failure: `<display_name> cannot be unbricked over USB or WiFi. It requires an external programmer (FTDI, J-Link, or similar) to recover from a bad firmware. Confirm the user has a programmer available before generating OTA-capable YAML.`

6. **min_required_features_for_unbricking** — the validator must verify that every feature listed in `board_profile.ota_safety.min_required_features_for_unbricking` is present in `planned_features`. Failure if any are missing: `<display_name> requires <list> to remain recoverable. The planned YAML disables: <missing>.` The 'OR' syntax in the list (e.g. `'ota OR usb_cdc'`) means *at least one* of the alternatives must be present.

## Output

- Pass: empty failures list.
- Warnings: list of warning strings. Volt surfaces these to the user but does not block.
- Failures: list of failure strings. Volt MUST NOT generate YAML if non-empty. The user picks: enable the missing feature, acknowledge the recovery risk explicitly (which Volt logs in the snapshot's `notes[]`), or pick a different board.

## Examples

### Example 1: WiFi disabled on a board without USB CDC

Input:
- `board_profile`: ESP32 DevKit V1 (`ota_safety.usb_cdc_recovery = false`)
- `planned_features`: `{"wifi": false, "ota": true, "usb_cdc": false}`

Output:
```
Failures:
- Disabling WiFi removes the only OTA path on ESP32 DevKit V1. Either keep wifi enabled, add an AP fallback, or accept that future updates will require a USB cable / external programmer.
- ESP32 DevKit V1 requires ['wifi', 'ota'] to remain recoverable. The planned YAML disables: ['wifi'].
```

Volt must not deliver this YAML.

### Example 2: OTA block removed on a board with USB CDC recovery

Input:
- `board_profile`: ESP32-S3 DevKit C-1 (`ota_safety.usb_cdc_recovery = true`)
- `planned_features`: `{"wifi": true, "ota": false, "usb_cdc": true}`

Output:
```
Failures:
- 'ota:' block removed. The device cannot be reflashed wirelessly. Future updates will require usb_cdc.
```

Volt explains the implication. If the user confirms they always use USB, Volt records the choice in `notes[]` and proceeds. Otherwise Volt restores the `ota:` block.

### Example 3: AP fallback missing (warning only)

Input:
- `board_profile`: ESP32-C3 Super Mini
- `planned_features`: `{"wifi": true, "ota": true, "ap_fallback": false}`

Output:
```
Warnings:
- Consider adding an 'ap:' fallback. If the configured WiFi credentials are wrong or the network changes, the device will boot into an access point and stay reachable for re-flashing. No fallback means a wrong SSID requires physical access.
Failures: []
```

Volt delivers the YAML but surfaces the warning so the user can opt in to safer recovery.

### Example 4: Healthy config

Input:
- `board_profile`: ESP32-S3 DevKit C-1
- `planned_features`: `{"wifi": true, "ota": true, "usb_cdc": true, "ap_fallback": true}`

Output:
```
Failures: []
Warnings: []
```

All recovery paths are intact.
