# Entity ID Validator

Validates that every Home Assistant entity ID referenced or produced in agent output is well-formed and, when the project is running under DEEP mode, is either present in the project snapshot's `entity_ids_generated` list or being added to it by the owning agent.

## When to Run

Two modes, depending on which agent is calling:

- **Producer mode** — when an agent that owns `entity_ids_generated` (Volt for sensors, Ada for custom integrations, Sage for helpers) generates a new entity ID, it must run the format check against the proposed ID before appending the ID to the snapshot.
- **Consumer mode** — when a downstream agent (Sage when wiring automations, Iris when laying out cards, Mira when exposing entities to a conversation agent, River when building Node-RED flows) references an entity ID in its output, it must run the existence check against the snapshot's `entity_ids_generated` list.

Both modes are tied to Iron Law 6 in the agent's soul ("validate before generating"). The validator MUST be run before the YAML/Python/JSON output reaches the user.

## Inputs

- `entity_id`: the candidate entity ID being created or referenced (e.g. `sensor.living_room_temperature`).
- `mode`: `"producer"` or `"consumer"`.
- `snapshot`: the parsed project snapshot loaded from `aurora-project.json`. Required in DEEP mode; may be `null` in QUICK mode (single-agent task).
- `producing_agent`: in producer mode, the soul name of the agent generating the ID (`"volt"`, `"ada"`, or `"sage"`). Required in producer mode; ignored in consumer mode.

## Checks

1. **Format check (both modes)** — `entity_id` must match the regex `^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`. Failures:
   - `Entity ID '<id>' is not lowercase snake_case. Home Assistant rejects uppercase, hyphens, and characters outside [a-z0-9_].`
   - `Entity ID '<id>' is missing a domain separator. Format must be 'domain.object_id'.`

2. **Domain plausibility (both modes)** — the part before `.` must be a known Home Assistant domain or a `*_sensor` variant (binary_sensor, image_processing). The validator's accepted domain set: `sensor`, `binary_sensor`, `switch`, `light`, `climate`, `cover`, `fan`, `media_player`, `lock`, `vacuum`, `camera`, `input_boolean`, `input_number`, `input_text`, `input_select`, `input_datetime`, `automation`, `script`, `scene`, `group`, `person`, `device_tracker`, `weather`, `sun`, `zone`, `timer`, `counter`, `number`, `text`, `select`, `update`, `button`, `event`, `image`, `siren`, `notify`, `tts`, `stt`, `conversation`. Warning (not failure) if the domain is outside this set: `Domain '<dom>' is not in the validator's known list. Continue only if this is a custom integration or new HA domain.`

3. **Producer mode: uniqueness check** — `entity_id` must not already appear in `snapshot.entity_ids_generated`. Failure if it does: `Producer agent '<producing_agent>' tried to add '<id>' but it is already owned by an earlier agent. Pick a unique object_id or raise a conflict_log entry to resolve ownership.`

4. **Producer mode: ownership check** — when `mode == "producer"` and `producing_agent` is set, the producer must be one of `volt`, `ada`, or `sage`. Failure otherwise: `Agent '<producing_agent>' is not authorised to produce entity IDs. Only volt (sensors), ada (custom integrations), and sage (helpers) own this field. See aurora/references/handoff/_protocol.md.`

5. **Consumer mode: existence check** — when `mode == "consumer"` and `snapshot` is provided, `entity_id` must appear in `snapshot.entity_ids_generated`. Failure if not: `Entity '<id>' is not in the project snapshot's entity_ids_generated list. Either Volt/Ada/Sage must produce it first, or this reference is a typo of an existing entity. Available entities: <list from snapshot>.`

6. **Consumer mode: QUICK fallback** — when `mode == "consumer"` and `snapshot` is `null`, skip the existence check. The agent is running standalone and the orchestrator has not staged a snapshot. Emit a warning: `QUICK mode: cannot verify '<id>' exists. Double-check the entity ID against the user's Home Assistant before delivery.`

7. **Snapshot integrity** — when a snapshot is provided in either mode, the `entity_ids_generated` array must itself pass the format check. Any malformed entry already in the snapshot is a failure: `Snapshot contains malformed entity ID '<id>'. This indicates a bug in the agent that added it; do not proceed.`

## Output

- Pass: empty list of failures.
- Warnings: list of warning strings. Agents present these to the user but do not block delivery.
- Failures: list of failure strings. Agents MUST NOT deliver output if non-empty. Producer agents that fail uniqueness or ownership must raise a `conflict_log` entry instead of overwriting.


Failure and warning entries follow the four-tier output defined in [`_tiered-errors.md`](_tiered-errors.md): `❌ Problem` (short) / `📚 Explanation` (medium) / `🔧 Fix` (concrete) / `💡 Deeper` (optional). Tiers 1 and 3 are mandatory for every failure; tier 2 is added during the next round of edits where it is still missing.

## Examples

### Example 1: Producer mode (Volt)

Input:
```
entity_id: "sensor.Living_Room_Temperature"
mode: "producer"
producing_agent: "volt"
snapshot: {entity_ids_generated: []}
```

Output:
```
Failures:
- Entity ID 'sensor.Living_Room_Temperature' is not lowercase snake_case. Home Assistant rejects uppercase, hyphens, and characters outside [a-z0-9_].
```

Volt must rename to `sensor.living_room_temperature` before adding to the snapshot.

### Example 2: Consumer mode (Sage)

Input:
```
entity_id: "sensor.living_room_humidity"
mode: "consumer"
snapshot:
  entity_ids_generated:
    - sensor.living_room_temperature
    - binary_sensor.living_room_presence
```

Output:
```
Failures:
- Entity 'sensor.living_room_humidity' is not in the project snapshot's entity_ids_generated list. Either Volt/Ada/Sage must produce it first, or this reference is a typo of an existing entity. Available entities: [sensor.living_room_temperature, binary_sensor.living_room_presence].
```

Sage must either reference an existing entity (likely `sensor.living_room_temperature`), or raise a `conflict_log` entry asking Volt to add a humidity sensor.

### Example 3: Producer mode (Volt) success

Input:
```
entity_id: "sensor.living_room_temperature"
mode: "producer"
producing_agent: "volt"
snapshot: {entity_ids_generated: ["binary_sensor.living_room_presence"]}
```

Output:
```
Failures: []
Warnings: []
```

Volt may now append `sensor.living_room_temperature` to `entity_ids_generated`.

### Example 4: QUICK mode consumer

Input:
```
entity_id: "sensor.kitchen_temperature"
mode: "consumer"
snapshot: null
```

Output:
```
Warnings:
- QUICK mode: cannot verify 'sensor.kitchen_temperature' exists. Double-check the entity ID against the user's Home Assistant before delivery.
Failures: []
```

Sage proceeds but flags the uncertainty to the user.
