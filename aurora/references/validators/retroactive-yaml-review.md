# Retroactive YAML Review

Defines the protocol when a user pastes an existing YAML configuration and asks "does this work?" or "is anything broken?". This is different from generating new YAML — the agent did not allocate the pins or pick the board, so it must first extract what the YAML claims, then run the validator suite against the extracted facts, and finally anchor every finding to the line in the user's input so they can locate it.

Without this protocol, agents either (a) skim the YAML and emit vague reassurance, or (b) treat every line in isolation and miss the cross-references that real failures depend on. Both fail the user.

## When to Run

Volt MUST run this protocol when the user pastes ESPHome YAML and asks for review.
Sage MUST run this protocol when the user pastes Home Assistant YAML (automations, scripts, configuration.yaml fragments) and asks for review.
Atlas runs it when the YAML wires an external API integration (`rest:`, `restful_command:`, OAuth2 config flow).

The protocol does NOT apply when the user is asking the agent to extend or modify their YAML — that case follows the normal generation Iron Law for the agent.

## Phase 1 — Extract Facts

Before running any validator, the agent parses the user's YAML and extracts the structured facts the validators need. The extraction step is documented so the agent does not guess.

For ESPHome YAML (Volt):

| Fact | YAML path |
|------|-----------|
| Board | `esphome.board` or `esp32.board` (case sensitive) |
| Chip variant | `esp32.variant`, `esp8266.platform`, `rp2040.board` |
| Framework | `esp32.framework.type` or `arduino`/`esp-idf` defaults |
| GPIO allocations | every `pin:` key under a component (sensor, switch, light, etc.); also `i2c.sda`/`scl`, `spi.miso`/`mosi`/`clk`, `uart.tx_pin`/`rx_pin` |
| Components used | every top-level platform key under `sensor:`, `binary_sensor:`, `switch:`, etc. |
| I2C addresses | `address:` keys inside i2c-protocol component blocks |
| Voltage assumptions | implicit; flagged when a 5V-only sensor appears on a 3.3V-only board (cross-checked from component profile) |
| Wireless features used | `wifi:`, `bluetooth_proxy:`, `esp32_ble_tracker:`, etc. |
| OTA / USB CDC settings | presence of `ota:` block, `wifi.ap:`, `logger.level: NONE` |
| Secrets references | every `!secret <name>` and every literal value under a high-risk key (delegated to secrets-validator) |
| Line numbers | every extracted fact records its line number from the original input |

For Home Assistant YAML (Sage):

| Fact | YAML path |
|------|-----------|
| File type | inferred from top-level keys (automation list, script dict, sensor list, etc.) |
| Entity references | every `entity_id`, `target.entity_id`, `state_attr('<id>', ...)`, `states('<id>')` |
| Service calls | every `service: <domain>.<action>` |
| Template usage | every `{{ ... }}` and `{% ... %}` block |
| Trigger types | `platform:` under each trigger |
| Secrets references | same rule as ESPHome |
| Line numbers | every extracted fact records its line number |

When the extraction step cannot determine a fact (the YAML is too fragmented, the board key is missing, etc.), the agent asks the user to supply it before proceeding. Do NOT guess.

## Phase 2 — Run the Validator Suite

With facts in hand, the agent invokes the same validators it would for generation. The set depends on agent and content:

**Volt (ESPHome YAML)** runs in this order:
1. `pin-validator` — every extracted GPIO assignment against the board profile.
2. `conflict-validator` — overlaps between components.
3. `i2c-address-validator` — addresses on shared buses.
4. `voltage-level-validator` — supply voltages against component profiles.
5. `ota-safety-validator` — recovery features against `min_required_features_for_unbricking`.
6. `version-validator` — `esphome.min_version` on every referenced component.
7. `entity-id-validator` (producer mode) — sensor `id:` fields and derived entity IDs.
8. `secrets-validator` — high-risk keys with literal values.

**Sage (HA YAML)** runs:
1. `entity-id-validator` (consumer mode) — every referenced ID against the snapshot's `entity_ids_generated` (when a snapshot exists).
2. `version-validator` — every feature, service, or trigger syntax against HA `target_version`.
3. `secrets-validator` — same high-risk-key contract.

**Atlas (API-wiring YAML)** runs:
1. `secrets-validator` first.
2. Then defers to Sage if the wiring is mostly HA automation, or to Volt if mostly ESPHome.

## Phase 3 — Anchor Every Finding

Every failure or warning from the validators MUST be re-emitted with the line number from the user's original YAML. Phase 1's extraction step recorded line numbers per fact; the agent threads them into the validator's output.

Example transformation. The pin-validator outputs:
```
GPIO 19 is used by USB CDC on ESP32-S3 DevKit C-1.
```
After anchoring it becomes:
```
Line 23 (`sda: 19`): GPIO 19 is used by USB CDC on ESP32-S3 DevKit C-1.
```

When a single failure relates to multiple lines (e.g. an I2C address collision involves two `address:` keys), anchor both:
```
Lines 18 + 47: bme280 (line 18) and bmp280 (line 47) both default to 0x76 on the same bus.
```

## Phase 4 — Tiered Output

Findings are then emitted in the standard four-tier format from `_tiered-errors.md`. The tier-3 (Fix) line MUST reference the specific lines from Phase 3 so the user can navigate directly:

```
❌ Problem (short):
Line 23 (`sda: 19`): GPIO 19 collides with USB CDC on ESP32-S3 DevKit C-1.

📚 Explanation (medium):
The ESP32-S3 routes USB D+/D- to GPIO 19/20. With `usb_cdc:` enabled
(line 8), the pin is reserved by the USB peripheral.

🔧 Fix (concrete):
On line 23, change `sda: 19` to `sda: 8` (the board's default I2C SDA pin).
On line 24, change `scl: 20` to `scl: 9`. Or set `usb_cdc: false` on line 8
(loses USB serial debug but frees GPIO 19/20).

💡 Deeper (optional):
USB-OTG protocol uses differential signalling on D+/D- mapped to GPIO 19/20.
Disabling usb_cdc frees them but you lose USB serial console.
```

## Output Aggregation

When the review reports zero failures and zero warnings, the agent emits a clean pass message that names the validators run:

```
✅ Looks correct.

Validators run: pin, conflict, i2c-address, voltage-level, ota-safety,
version, entity-id (producer), secrets.

Board identified: ESP32-S3 DevKit C-1
Components identified: bme280 (line 14), pir am312 (line 28)
GPIO allocations checked: SDA=8 (line 17), SCL=9 (line 18), PIR=4 (line 30)
```

The pass message lists what was checked so the user does not mistake "no findings" for "did not look".

When there are failures, the agent emits the tiered block per failure, then a summary footer:

```
─────────────────────────────────────────
Summary: 2 failures, 1 warning.
Do not flash this config until the failures are resolved.
```

## QUICK / DEEP Modes

The protocol applies identically in QUICK mode and DEEP mode. In DEEP mode, if a project snapshot exists, the agent also cross-references extracted facts against `selected_board`, `selected_components`, and `gpio_allocation` from the snapshot — a mismatch (the pasted YAML uses a different board than the snapshot records) is itself a warning the user should see.

## What This Protocol Does NOT Do

- It does not evaluate code quality, style, or readability. Validators check correctness, not aesthetics.
- It does not auto-fix the YAML. Fix suggestions are concrete enough for the user to apply manually; auto-rewriting is a separate generation flow that requires user confirmation per the agent's normal Iron Laws.
- It does not check upstream component documentation that aurora has no profile for. The unknown-component-validator protocol applies instead.

Failure and warning entries follow the four-tier output defined in [`_tiered-errors.md`](_tiered-errors.md): `❌ Problem` (short) / `📚 Explanation` (medium) / `🔧 Fix` (concrete) / `💡 Deeper` (optional).
