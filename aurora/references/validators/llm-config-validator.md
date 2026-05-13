# LLM Config Validator

Flags common configuration mistakes in Home Assistant conversation agents and LLM-backed integrations: unknown providers, malformed local endpoint URLs, prompt templates that will exceed token limits, exposed-entity blocks that do not match what HA actually has. Catches the everyday mistakes; does not attempt to evaluate prompt quality or judge model choice.

## When to Run

Mira MUST run this validator before delivering any of:

- `conversation:` blocks in `configuration.yaml`
- intent scripts in `intent_scripts.yaml`
- conversation-agent Python code (custom `llm_api` integrations)
- YAML `expose:` filters listing which entities the agent can read or control
- assistant pipeline configurations (`assist_pipeline:` overrides)

The validator runs on YAML for HA-side config and on Python source for custom integrations. For Python it shares the import / comment / docstring / string-literal exemptions documented in `async-correctness-validator.md`.

## Inputs

- `config_text`: the YAML or Python being delivered, as a UTF-8 string.
- `language`: `"yaml"` or `"python"`.
- `target_version`: the user's HA version (e.g. `"2026.5.0"`). Optional; if absent, version-dependent checks emit warnings rather than failures.
- `snapshot`: the parsed project snapshot, when present. Used to cross-check `expose:` lists against `entity_ids_generated`.
- `file_path`: optional path for error messages.

## Known Providers

The validator enumerates the LLM providers Home Assistant ships as core or first-party integrations. Other providers (community HACS integrations) are NOT flagged as unknown, but the validator emits an informational note when the provider is not in this list.

| Provider key | HA integration name | Endpoint convention |
|--------------|---------------------|---------------------|
| `openai_conversation` | OpenAI Conversation | api.openai.com |
| `anthropic` | Anthropic Conversation | api.anthropic.com |
| `google_generative_ai_conversation` | Google Generative AI | generativelanguage.googleapis.com |
| `ollama` | Ollama | `http://<host>:11434` (local) |
| `local_llm_conversation` | Local LLM | varies (Ollama, LocalAI, etc.) |
| `conversation` (HA default) | Built-in HA assistant | no external endpoint |

Casing is significant: `OpenAI` in a YAML key is wrong; `openai_conversation` is correct.

## Checks

For each LLM-related block:

1. **Provider key casing** — provider keys in YAML must be lowercase snake_case. Failure if a known provider is referenced with mixed case (`OpenAI`, `Anthropic`, etc.): `Provider key '<bad>' must be lowercase snake_case. Use '<corrected>'.`

2. **Unknown provider warning** — if the provider key does not appear in the Known Providers table, emit a warning (not failure): `Provider '<key>' is not in the validator's known list. Confirm the integration is installed (HACS or core) and that the configuration matches its documentation.`

3. **Local endpoint URL** — when the provider is `ollama` or `local_llm_conversation` and a URL is configured, the URL must match `^https?://[a-zA-Z0-9.-]+(:\d+)?(/.*)?$`. Failure otherwise: `Local LLM endpoint '<url>' is malformed. Expected pattern: http(s)://host[:port][/path]. Common example for Ollama: 'http://homeassistant.local:11434'.`

4. **Cloud provider without secret reference** — when the provider is one of `openai_conversation`, `anthropic`, `google_generative_ai_conversation`, the YAML must include an `api_key` field set to a `!secret <name>` reference. The secrets-validator catches literal credentials; this rule catches the more common "forgot the api_key field entirely" case: `Cloud LLM provider '<key>' is configured without an api_key. Add: 'api_key: !secret <suggested_name>'.`

5. **Prompt template token-budget warning** — when a `prompt:` field is present, count the characters in the rendered template. If the total exceeds 12,000 characters (rough proxy for 3,000 tokens), emit a warning: `Prompt template at <file>:<line> is approximately <chars> characters (~<tokens> tokens). This leaves little room for conversation history. Most providers cap the combined prompt + history at <provider_limit> tokens; trim the template or move static guidance to a system prompt.`

6. **Streaming flag mismatch** — when `streaming: true` is set, the provider must be one of `ollama`, `local_llm_conversation`, `openai_conversation`, `anthropic`. Failure otherwise: `Provider '<key>' does not support 'streaming: true'. Either remove the flag or switch to a streaming-capable provider.`

7. **`expose:` cross-check (when snapshot is provided)** — every entity ID listed in `expose:` must exist in `snapshot.entity_ids_generated` or in a documented HA core domain (sensor, light, switch, climate, cover, fan, etc.). Failure on a missing snapshot entity: `expose lists '<id>' which is not in the project snapshot's entity_ids_generated. Either Volt/Ada/Sage must create it, or remove the reference.`

8. **Intent script consistency** — when an intent script references entity IDs in its `action:` block, those IDs must also be `expose`d to the conversation agent. Failure: `Intent script '<name>' acts on '<id>' but '<id>' is not exposed in conversation.<entity>.expose. Add the entity to the expose list or pick an exposed alternative.`

9. **Conversation agent without language** — when a `conversation:` block exists without a `language:` field, emit a warning: `conversation agent '<entity_id>' does not specify a language. HA defaults to 'en', which may surprise users in non-English locales. Add 'language: <code>' explicitly.`

10. **Privacy warning for cloud providers** — when the provider is a cloud LLM (`openai_conversation`, `anthropic`, `google_generative_ai_conversation`) and `expose:` lists entities like `camera.*`, `media_player.*` with sensitive metadata, emit a warning: `Conversation agent exposes '<id>' to cloud provider '<key>'. State data leaves your home network. Confirm this is intentional or move to a local provider (ollama, local_llm_conversation).`

## Output

- Pass: empty failures list.
- Warnings: list of warning strings. Mira surfaces these but does not block delivery.
- Failures: list of failure strings. Mira MUST NOT deliver the file if non-empty.

Failure and warning entries follow the four-tier output defined in [`_tiered-errors.md`](_tiered-errors.md): `❌ Problem` (short) / `📚 Explanation` (medium) / `🔧 Fix` (concrete) / `💡 Deeper` (optional). Tiers 1 and 3 are mandatory for every failure; tier 2 is added during the next round of edits where it is still missing.

## Examples

### Example 1: Cloud provider missing api_key

Input (`configuration.yaml`):
```yaml
conversation:
  agent: anthropic
  prompt: "You help with smart home tasks."
```

Output:
```
Failures:
- Cloud LLM provider 'anthropic' is configured without an api_key. Add: 'api_key: !secret anthropic_api_key'.
```

Mira's fix:
```yaml
conversation:
  agent: anthropic
  api_key: !secret anthropic_api_key
  prompt: "You help with smart home tasks."
```

### Example 2: Malformed Ollama endpoint

Input:
```yaml
ollama:
  url: "homeassistant.local:11434"
```

Output:
```
Failures:
- Local LLM endpoint 'homeassistant.local:11434' is malformed. Expected pattern: http(s)://host[:port][/path]. Common example for Ollama: 'http://homeassistant.local:11434'.
```

### Example 3: Mismatched provider casing

Input:
```yaml
conversation:
  agent: OpenAI
```

Output:
```
Failures:
- Provider key 'OpenAI' must be lowercase snake_case. Use 'openai_conversation'.
```

### Example 4: expose list references unknown entity

Input (snapshot `entity_ids_generated: ["sensor.living_room_temperature"]`):
```yaml
conversation:
  agent: ollama
  expose:
    - light.kitchen
```

Output:
```
Failures:
- expose lists 'light.kitchen' which is not in the project snapshot's entity_ids_generated. Either Volt/Ada/Sage must create it, or remove the reference.
```

### Example 5: Healthy config

Input:
```yaml
conversation:
  agent: ollama
  url: "http://homeassistant.local:11434"
  model: "llama3.1:8b"
  language: "sv"
  prompt: |
    You are a Swedish-speaking smart home assistant.
```

Output:
```
Failures: []
Warnings: []
```
