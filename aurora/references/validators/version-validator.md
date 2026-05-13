# Version Validator

Verifies that every feature, component, and integration referenced in a generated configuration is supported by the platform version the user is actually running. A Sage automation using a 2026.4-only trigger syntax on a 2024.x install fails silently at load time; a Volt config using ESPHome `serial_proxy` on 2025.x errors at compile. Both are preventable.

## When to Run

This validator runs at two points:

- **Volt**, before generating ESPHome YAML — checks that the project's `esphome.min_version` against the board profile and each component profile is satisfied by the user's ESPHome install.
- **Sage**, before generating Home Assistant YAML — checks that automation triggers, blueprints, helper types, and integrations referenced in the YAML are supported by the user's Home Assistant version.

Both agents read `aurora/references/platform-versions.md` as the source of truth for current and historical feature availability.

## Inputs

- `platform`: `"esphome"` or `"homeassistant"`.
- `target_version`: the user's running version (e.g. `"2026.4.5"` for ESPHome or `"2026.5.0"` for HA). Volt and Sage read this from the user's project context or ask if unknown.
- `referenced_features`: list of feature/component/integration identifiers that the generated YAML uses. Examples:
  - Volt: `["bme280", "esp32-s3-devkitc-1", "serial_proxy", "matter_device"]`
  - Sage: `["automation_v2_trigger_syntax", "input_text.helper", "blueprint_input_selector", "tts.cloud"]`
- `component_profiles` (optional): when Volt invokes, the parsed component profiles being used. The validator reads each profile's `esphome.min_version`.
- `board_profile` (optional): when Volt invokes, the parsed board profile. The validator reads `esphome.min_version`.

## Checks

For each entry in `referenced_features`:

1. **Minimum version known** — look up the feature in `platform-versions.md`. If the feature does not appear in the file, emit a warning (not a failure): `<platform>: feature '<id>' has no minimum-version entry in aurora/references/platform-versions.md. Add it to the reference data or proceed with caution.`

2. **Target meets minimum** — when both `target_version` and the feature's `min_version` are known, compare them as semver. Failure if target is older: `<platform> <target_version> is older than the minimum '<id>' requires (<min_version>). The user must upgrade <platform> to <min_version> or higher, or remove the feature from the configuration.`

3. **Profile minimum check (Volt only)** — for each component profile in `component_profiles`, check `esphome.min_version` against `target_version`. Failure if target is older: `<component_id> requires ESPHome >= <min_version>, but the project targets <target_version>. Upgrade ESPHome or pick a different sensor.`

4. **Board minimum check (Volt only)** — same as #3 for `board_profile.esphome.min_version`. Failure if target is older: `<board_id> requires ESPHome >= <min_version>, but the project targets <target_version>. Upgrade ESPHome or pick a different board.`

5. **Deprecated feature warning** — if `platform-versions.md` marks the feature as `deprecated_since: <V>` and `target_version` is at or above `<V>`, emit a warning: `<platform> '<id>' is deprecated since <V>. <successor> is the recommended replacement. The validator does not block, but new projects should use the successor.`

6. **Pre-release / experimental** — if the feature is marked `experimental: true` in `platform-versions.md`, emit a warning: `<id> is marked experimental in <platform> <min_version>. The API may change in future releases; do not rely on it for production.`

## Output

- Pass: empty failures list.
- Warnings: list of warning strings.
- Failures: list of failure strings. Agents MUST NOT generate output if non-empty. The remediation is always one of: upgrade the platform, remove the feature, or pick a different component.

## Version Comparison

Semver-ish comparison, since both HA and ESPHome use date-style versions (e.g. `2026.4.5`):

- Split on `.` → integer tuple
- Compare lexicographically
- Missing patch component defaults to `0` (e.g. `2026.4` becomes `2026.4.0`)

Example: `2026.5.0` > `2026.4.5` (because `(2026,5,0) > (2026,4,5)`).

## Examples

### Example 1: Volt using HA 2026.5 features on ESPHome 2026.3

Input:
```
platform: "esphome"
target_version: "2026.3.0"
referenced_features: ["serial_proxy"]
```

`platform-versions.md` says ESPHome `serial_proxy` requires `2026.4.0`.

Output:
```
Failures:
- esphome 2026.3.0 is older than the minimum 'serial_proxy' requires (2026.4.0). The user must upgrade esphome to 2026.4.0 or higher, or remove the feature from the configuration.
```

### Example 2: Sage using a deprecated automation syntax

Input:
```
platform: "homeassistant"
target_version: "2026.5.0"
referenced_features: ["automation_v1_trigger_syntax"]
```

`platform-versions.md` says `automation_v1_trigger_syntax` is `deprecated_since: 2025.10.0`, successor `automation_v2_trigger_syntax`.

Output:
```
Warnings:
- homeassistant 'automation_v1_trigger_syntax' is deprecated since 2025.10.0. automation_v2_trigger_syntax is the recommended replacement. The validator does not block, but new projects should use the successor.
Failures: []
```

Sage delivers the automation but surfaces the warning, and Lore can update the doc with the modern syntax later.

### Example 3: Component minimum-version check

Input:
```
platform: "esphome"
target_version: "2025.6.0"
component_profiles:
  ld2410: {esphome: {min_version: "2024.10.0"}}
  ld2412: {esphome: {min_version: "2026.2.0"}}
```

Output:
```
Failures:
- ld2412 requires ESPHome >= 2026.2.0, but the project targets 2025.6.0. Upgrade ESPHome or pick a different sensor.
```

### Example 4: Healthy match

Input:
```
platform: "esphome"
target_version: "2026.4.5"
referenced_features: ["bme280", "esp32-s3-devkitc-1"]
component_profiles:
  bme280: {esphome: {min_version: "2024.1.0"}}
board_profile:
  esphome: {min_version: "2024.6.0"}
```

Output:
```
Failures: []
Warnings: []
```
