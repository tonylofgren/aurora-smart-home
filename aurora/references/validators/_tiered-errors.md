# Tiered Error Output (shared format)

Every validator in `aurora/references/validators/` produces output that is consumed by an agent and ultimately shown to the user. Beginners struggle with terse failure lines like `GPIO 19 conflicts with USB`; experienced users want fix steps without prose. This document defines the four-tier format every validator uses so the experience is consistent across the suite.

## The Four Tiers

Each failure or warning is rendered as four labelled lines. Tiers 1–3 are mandatory. Tier 4 is optional but recommended for failures that have educational context worth surfacing.

```
❌ Problem (short):
<one short sentence stating what is wrong>

📚 Explanation (medium):
<one to three sentences explaining why it is wrong: which constraint
is violated, which datasheet / spec / reference data it comes from>

🔧 Fix (concrete):
<specific action the user takes: which pin, which value, which !secret
reference, which alternative component. Include file and line numbers
when the validator can point at them.>

💡 Deeper (optional):
<background a curious user might want: how the underlying mechanism
works, what the trade-off is, which other failure modes share the same
root cause. Omit when the fix is self-contained.>
```

Warnings use the same four-tier shape but lead with `⚠️ Warning (short):` instead of `❌ Problem (short):`. Pass output remains the empty lists `Failures: []` and `Warnings: []`.

## Why Four Tiers

- **Beginners** read tier 1 + 3 and act. They get a clear "what went wrong, what to do" pair without wading through theory.
- **Experienced users** skim tier 1 and jump straight to tier 3.
- **Curious users** read all four and learn the underlying constraint, which prevents the same mistake elsewhere.
- **LLM consumers** (downstream agents like Iris asking Volt to clarify) get structured fields rather than free prose.

## Format Rules

1. Every failure MUST have tiers 1, 2, and 3. Missing any of them is a bug in the validator's emitter, not a stylistic choice.
2. Tier 4 is optional. Omit when the fix is self-explanatory.
3. Use the exact emoji prefixes (`❌`, `⚠️`, `📚`, `🔧`, `💡`) so agents can parse the output without language detection.
4. Tier 1 fits on one line (no internal newlines). Tiers 2-4 may wrap.
5. When the validator can point at a file and line number, include them in tier 3 (`<file>:<line>`).

## Example: pin-validator failure on USB-reserved GPIO

```
❌ Problem (short):
GPIO 19 cannot be used on ESP32-S3 DevKit C-1 while USB CDC is enabled.

📚 Explanation (medium):
The ESP32-S3 routes USB D+ and D- to GPIO 19 and 20. With `usb_cdc:` enabled
(the default for boards that expose USB), these pins are reserved and any
assignment to them collides with the USB peripheral. See
`aurora/references/boards/esp32/esp32-s3-devkitc-1.json` field
`gpio.reserved_for_usb`.

🔧 Fix (concrete):
Move the sensor to GPIO 8 (SDA) and GPIO 9 (SCL), the board's default I2C
pins. In `living-room-sensor.yaml`, change line 12 from `sda: 19` to
`sda: 8` and line 13 from `scl: 20` to `scl: 9`.

💡 Deeper (optional):
USB-OTG protocol uses differential signalling on D+/D- mapped to these two
GPIOs. You can set `usb_cdc: false` to free GPIO 19/20 for general use,
but you lose USB serial console — only OTA-over-WiFi remains for log
inspection. For most projects keeping USB CDC is the right trade-off.
```

## Example: secrets-validator warning on a templated value

```
⚠️ Warning (short):
`webhook_secret` in `automations.yaml:23` uses a Jinja template.

📚 Explanation (medium):
The validator cannot prove what the template resolves to at render time.
If the template ever resolves to a literal string instead of a `!secret`
reference, the credential ends up in plaintext in the rendered config.

🔧 Fix (concrete):
Confirm `input_text.shared_secret` is populated from secrets.yaml at HA
startup (e.g. via `initial_value: !secret webhook_shared_secret`). If
the template is meant to dispatch between multiple secrets, ensure every
branch returns a `!secret` reference, never a string literal.
```

## Backward Compatibility

The pre-tiered format (single-line failure strings) is no longer the
contract. Validator docs SHOULD be updated to specify their tier 1-4
strings explicitly for at least one example per failure category. Older
examples in this repo that still emit single-line failures are
documentation debt; they will be updated incrementally.

Validators not yet covering all four tiers must at minimum produce
tiers 1 + 3 so the user gets a problem + fix pair. Tier 2 is filled in
during the next round of edits.

## Aggregation

When multiple failures fire on the same input, the validator emits each
failure as a separate four-tier block, separated by a single blank line.
Agents present them in order of severity (failures first, then warnings)
and never interleave the tiers.
