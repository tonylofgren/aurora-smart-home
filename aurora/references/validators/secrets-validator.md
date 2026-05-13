# Secrets Validator

Flags hardcoded credentials in YAML output before the agent delivers the
file to the user. The validator targets a tight, well-defined set of
high-risk keys; it deliberately avoids generic entropy or base64 scanning
because those produce too many false positives (UUIDs, MAC addresses,
example values in comments) to be useful in practice.

## When to Run

Any agent that produces YAML for the user — Volt (ESPHome configs), Sage
(Home Assistant `automations.yaml`, `scripts.yaml`, `configuration.yaml`),
and Atlas (external API config snippets) — MUST run this validator on the
generated YAML before delivery. If failures are reported, do NOT deliver
the file. Report failures with the recommended `!secret` rewrite and ask
the user to confirm.

This validator does NOT scan Python (Ada) or Node-RED flow JSON (River)
at this time. Those formats have their own credential conventions and
will get dedicated validators in a later phase.

## Inputs

- `yaml_text`: the full YAML document about to be written, as a single
  UTF-8 string.
- `file_path`: optional path that the YAML will be written to. Used only
  for error messages.

## High-Risk Keys

The validator only inspects values assigned to these key names (matched
case-insensitively, with or without surrounding whitespace). Other keys
are intentionally NOT inspected — extending the list is a deliberate
decision, not a side effect.

- `password`
- `api_key`
- `apikey`
- `api_token`
- `token`
- `secret`
- `client_secret`
- `private_key`
- `bearer`
- `auth_token`
- `access_token`
- `refresh_token`
- `webhook_secret`
- `encryption_key`
- `ota_password`
- `wifi_password`
- `mqtt_password`

The list intentionally excludes things like `username` (often not
sensitive on its own) and `host`/`url` (sometimes sensitive, but flagging
every URL would block legitimate config).

## Checks

For each line in `yaml_text` that contains a key from the high-risk list:

1. **`!secret` reference** — the value MUST be of the form
   `!secret <secret_name>` where `<secret_name>` matches
   `^[a-z][a-z0-9_]*$`. Failures:
   - Value is a literal string, number, or interpolation:
     `'<file_path>' line <N>: '<key>' assigns a literal value. Move the
     credential to secrets.yaml and reference it with '!secret
     <suggested_name>'.`
   - Value is empty:
     `'<file_path>' line <N>: '<key>' is empty. If this is intentional,
     remove the key; otherwise add a '!secret <name>' reference.`
   - Value is `!secret` without a name:
     `'<file_path>' line <N>: '!secret' is missing the secret name. Use
     '!secret <name>' where <name> matches ^[a-z][a-z0-9_]*$.`
   - Value contains `!secret` followed by an invalid name:
     `'<file_path>' line <N>: secret name '<bad_name>' is invalid. Names
     must be lowercase snake_case (^[a-z][a-z0-9_]*$).`

2. **Inline comments** — values that LOOK like credentials inside a
   comment (e.g. `# password: hunter2`) are intentionally NOT flagged.
   The validator only inspects YAML key-value pairs, not free text.

3. **Multi-line strings (`|` or `>`)** — when the value is a folded or
   literal block scalar, the validator emits a warning but not a failure:
   `'<file_path>' line <N>: '<key>' uses a block scalar. Verify the
   embedded content does not contain a literal credential; the validator
   cannot inspect block contents.`

4. **Templated values (`{{ ... }}`, `${...}`)** — flagged as a warning:
   `'<file_path>' line <N>: '<key>' uses a template. Confirm the template
   resolves to a !secret reference and not a literal at render time.`

## Output

- Pass: empty list of failures.
- Warnings: list of warning strings. Agents present these to the user but
  do not block delivery.
- Failures: list of failure strings. Agents MUST NOT write the YAML if
  the list is non-empty.


Failure and warning entries follow the four-tier output defined in [`_tiered-errors.md`](_tiered-errors.md): `❌ Problem` (short) / `📚 Explanation` (medium) / `🔧 Fix` (concrete) / `💡 Deeper` (optional). Tiers 1 and 3 are mandatory for every failure; tier 2 is added during the next round of edits where it is still missing.

## Suggested Secret Names

When emitting the "Move the credential to secrets.yaml" failure, the
validator should suggest a snake_case name derived from the key plus the
device or integration context. Examples:

| Key | Context | Suggested secret name |
|-----|---------|----------------------|
| `password` | `wifi:` block in ESPHome | `wifi_password` |
| `api_key` | ESPHome `api:` block | `api_encryption_key` |
| `ota_password` | ESPHome `ota:` block | `ota_password` |
| `password` | Sage `notify.email:` | `notify_email_password` |
| `client_secret` | Atlas OAuth integration | `<service>_client_secret` |

## Examples

### Example 1: Literal password in ESPHome WiFi

Input (`living-room-sensor.yaml`):
```yaml
wifi:
  ssid: "MyNetwork"
  password: "hunter2"
```

Output:
```
Failures:
- 'living-room-sensor.yaml' line 3: 'password' assigns a literal value. Move the credential to secrets.yaml and reference it with '!secret wifi_password'.
```

Volt must NOT deliver this YAML. Volt rewrites:
```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
```

### Example 2: Empty token

Input (`config.yaml`):
```yaml
api:
  token:
```

Output:
```
Failures:
- 'config.yaml' line 2: 'token' is empty. If this is intentional, remove the key; otherwise add a '!secret <name>' reference.
```

### Example 3: Valid !secret reference

Input (`scripts.yaml`):
```yaml
notify:
  - platform: smtp
    password: !secret smtp_password
```

Output:
```
Failures: []
Warnings: []
```

### Example 4: Template value

Input (`automations.yaml`):
```yaml
trigger:
  - platform: webhook
    webhook_secret: "{{ states('input_text.shared_secret') }}"
```

Output:
```
Warnings:
- 'automations.yaml' line 3: 'webhook_secret' uses a template. Confirm the template resolves to a !secret reference and not a literal at render time.
Failures: []
```

Sage delivers the YAML but surfaces the warning so the user can verify.

### Example 5: Block scalar

Input (`config.yaml`):
```yaml
private_key: |
  -----BEGIN PRIVATE KEY-----
  MIIE...
  -----END PRIVATE KEY-----
```

Output:
```
Warnings:
- 'config.yaml' line 1: 'private_key' uses a block scalar. Verify the embedded content does not contain a literal credential; the validator cannot inspect block contents.
Failures: []
```

The validator cannot prove the block content is safe, so it warns rather
than block. Agents should rewrite this to `!secret` whenever possible.
