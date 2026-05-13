# Node-RED Syntax Validator

Flags common mistakes in Node-RED flow JSON that River produces for Home Assistant automation: legacy node names, missing server references, mis-spelled service calls, function nodes that import sync libraries. The validator targets the patterns that show up when an LLM-generated flow is imported into Node-RED and silently fails to deploy.

## When to Run

River MUST run this validator before delivering any Node-RED flow JSON. The validator runs on the full flow as a single JSON document.

## Inputs

- `flow_text`: the full flow JSON about to be delivered, as a UTF-8 string.
- `snapshot`: the parsed project snapshot, when present. Used for cross-checks against `entity_ids_generated`.
- `file_path`: optional path for error messages.

## Known Node Types

Node-RED Home Assistant nodes have been renamed across versions of `node-red-contrib-home-assistant-websocket`. The validator enumerates the current (4.x) node type names and the legacy aliases users sometimes paste in by mistake.

| Current node `type` | Legacy alias (FAIL) | Purpose |
|---------------------|---------------------|---------|
| `trigger-state` | `ha-state-changed`, `state_changed` | Trigger when an entity state changes |
| `api-call-service` | `ha-call-service`, `call-service` | Call any HA service |
| `api-current-state` | `ha-state`, `current_state` | Read current state of an entity |
| `events: state` | `events-state-changed` | Subscribe to all state events |
| `events: all` | `events-all` | Subscribe to all HA events |
| `get-entities` | `get-state` | Pull a list of entities by filter |
| `fire-event` | `ha-event` | Fire a custom HA event |
| `render-template` | `template` (only when alone) | Server-side template render |
| `wait-until` | (none) | Pause flow until condition met |
| `poll-state` | `state-trigger` | Periodic state poll |
| `time` | `inject-time` | Time-based trigger |
| `binary-state` | `ha-binary` | Boolean state evaluation |

When `flow_text` contains a node with a legacy `type` value, the validator emits a failure with the current replacement.

## Required Node Fields

These Home Assistant nodes must reference a configured HA server:

- `trigger-state`, `api-call-service`, `api-current-state`, `events: state`, `events: all`, `get-entities`, `fire-event`, `render-template`, `poll-state`, `binary-state`

The reference field name is `server` and must be a non-empty string. A missing or empty `server` field on any of these node types is a failure.

## Checks

The validator parses `flow_text` as JSON and iterates every node:

1. **Valid JSON** — `flow_text` must be parseable as JSON. Failure on parse error: `Flow JSON is malformed: <error>. Verify the export from Node-RED is complete (no truncated tail).`

2. **Top-level array** — Node-RED flows are arrays of node objects. Failure if the top-level value is not an array: `Flow JSON top level must be an array of node objects. Got <type>.`

3. **Legacy node type** — for each node, if `node.type` matches a legacy alias from the Known Node Types table, fail: `Node id='<node.id>' uses legacy type '<bad>'. Replace with the current type '<current>'. Legacy types were removed in node-red-contrib-home-assistant-websocket 4.x and the flow will fail to deploy.`

4. **Missing server reference** — for HA nodes (the types listed above), `server` must be a non-empty string. Failure: `Node id='<node.id>' (type='<type>') has no 'server' field. Add a reference to a configured Home Assistant server config node.`

5. **Entity ID format on trigger-state** — when a `trigger-state` node specifies an `entityid` or `entityidfilter` field, the value must match the entity_id regex `^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`. Failure on mismatch: `Node id='<node.id>' (trigger-state) entity '<id>' is not a valid entity_id. Lowercase snake_case domain.object_id required.`

6. **api-call-service domain/service split** — each `api-call-service` node must specify both `domain` and `service`. Failure if either is missing or empty: `Node id='<node.id>' (api-call-service) is missing '<domain|service>'. Specify both, e.g. domain='light' service='turn_on'.`

7. **Snapshot cross-check (when snapshot is provided)** — every entity referenced in any node (`entityid`, `entityidfilter` containing literal IDs, `target.entity_id` on api-call-service) must exist in `snapshot.entity_ids_generated`. Failure on missing reference: `Node id='<node.id>' references '<id>' which is not in the project snapshot's entity_ids_generated. Either the producing agent must create it, or this is a typo of an existing entity. Available: <list>.`

8. **Function node sync HTTP** — when a `function` node's `func` string contains `require('http')`, `require('https')`, `require('request')`, or `axios.get(`, emit a warning: `Function node id='<node.id>' uses a sync-style HTTP call. Prefer the dedicated 'http request' node so the call is non-blocking and uses Node-RED's connection pool.`

9. **Hardcoded credentials in function nodes** — function node `func` string scanned for the same high-risk key patterns documented in `secrets-validator.md` (`api_key:`, `password:`, `token:`, etc.) followed by a literal string. Failure on hits: `Function node id='<node.id>' contains a literal credential. Move to Node-RED credentials store or to HA secrets and reference via msg.payload.`

## Output

- Pass: empty failures list.
- Warnings: list of warning strings. River surfaces these but does not block delivery.
- Failures: list of failure strings. River MUST NOT deliver the flow if non-empty.

Failure and warning entries follow the four-tier output defined in [`_tiered-errors.md`](_tiered-errors.md): `❌ Problem` (short) / `📚 Explanation` (medium) / `🔧 Fix` (concrete) / `💡 Deeper` (optional). Tiers 1 and 3 are mandatory for every failure; tier 2 is added during the next round of edits where it is still missing.

## Examples

### Example 1: Legacy node type

Input:
```json
[
  {"id": "n1", "type": "ha-state-changed", "entityid": "light.kitchen", "server": "ha1"}
]
```

Output:
```
Failures:
- Node id='n1' uses legacy type 'ha-state-changed'. Replace with the current type 'trigger-state'. Legacy types were removed in node-red-contrib-home-assistant-websocket 4.x and the flow will fail to deploy.
```

### Example 2: Missing server reference

Input:
```json
[
  {"id": "n2", "type": "api-call-service", "domain": "light", "service": "turn_on"}
]
```

Output:
```
Failures:
- Node id='n2' (type='api-call-service') has no 'server' field. Add a reference to a configured Home Assistant server config node.
```

### Example 3: Snapshot cross-check failure

Input (snapshot `entity_ids_generated: ["sensor.living_room_temperature"]`):
```json
[
  {"id": "n3", "type": "trigger-state", "entityid": "sensor.kitchen_temperature", "server": "ha1"}
]
```

Output:
```
Failures:
- Node id='n3' references 'sensor.kitchen_temperature' which is not in the project snapshot's entity_ids_generated. Either the producing agent must create it, or this is a typo of an existing entity. Available: [sensor.living_room_temperature].
```

### Example 4: Function node sync HTTP warning

Input:
```json
[
  {"id": "n4", "type": "function", "func": "const axios = require('axios');\naxios.get('https://api.example.com');\nreturn msg;"}
]
```

Output:
```
Warnings:
- Function node id='n4' uses a sync-style HTTP call. Prefer the dedicated 'http request' node so the call is non-blocking and uses Node-RED's connection pool.
Failures: []
```

### Example 5: Healthy flow

Input:
```json
[
  {"id": "n5", "type": "trigger-state", "entityid": "binary_sensor.front_door", "server": "ha1"},
  {"id": "n6", "type": "api-call-service", "domain": "light", "service": "turn_on", "target": {"entity_id": "light.hallway"}, "server": "ha1"}
]
```

Output:
```
Failures: []
Warnings: []
```
