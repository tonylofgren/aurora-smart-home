# Hand-Off Protocol (Project Snapshot)

When two or more Aurora specialist agents collaborate on the same project (DEEP mode), they exchange a single structured artifact called a **project snapshot**. The snapshot is a JSON file on disk that travels between agents.

This document defines:

1. Where the snapshot lives.
2. Which agent creates it.
3. What each agent reads, writes, and must not touch.
4. How conflicts are reported and resolved.

The schema is `aurora/references/schemas/project-snapshot.schema.json`. A passing example lives under `examples/`.

## When Is a Snapshot Used

A snapshot is used whenever a project involves **2 or more specialist agents**. Examples:

- `Volt` (ESPHome firmware) → `Sage` (HA automations) → `Iris` (dashboard)
- `Ada` (custom integration) → `Sage` (config) → `Iris` (dashboard)
- `Mira` (voice assistant) → `Sage` (automations) → `Volt` (voice satellite firmware)

Single-agent tasks do **not** need a snapshot. A user asking Volt for one ESPHome config is a single-agent task and should stay lightweight.

## Storage Location

The snapshot is written to **`aurora-project.json` at the project root** by default. The orchestrator (aurora SKILL.md) may override this path for users who keep multiple projects in one repo, in which case the override goes in the snapshot's own `snapshot_file_path` field.

Why a file on disk, not an in-conversation artifact:

- Survives session boundaries. A user can come back tomorrow and continue.
- Survives context window compaction. The snapshot is the source of truth, the conversation transcript is not.
- Can be version-controlled by the user if they want.
- Can be read by humans without parsing chat history.

If the user does not want a file on disk (e.g. they are exploring in a sandbox), the orchestrator MAY hold the snapshot in conversation context only, but every agent must still read and update the same structured object. The schema does not change.

## Lifecycle

```
1. User describes project to aurora orchestrator.
2. Orchestrator decides DEEP mode is needed.
3. Orchestrator creates the snapshot:
   - Generates project_id (UUID v4).
   - Fills user_requirements, current_agent, agents_pending.
   - Writes to disk.
4. Orchestrator invokes the first agent.
5. Agent reads the snapshot.
6. Agent performs its work, including validation against
   aurora/references/ data where applicable (Iron Law 6).
7. Agent updates the snapshot:
   - Appends itself to agents_completed.
   - Removes itself from agents_pending.
   - Records validation_results[<soul>].
   - Adds any new fields it owns (e.g. Volt writes
     selected_board, gpio_allocation, esphome_filename).
   - Updates updated_at.
8. Orchestrator picks the next agent from agents_pending,
   sets current_agent, repeats from step 4.
9. When agents_pending is empty and conflict_log has no
   unresolved entries, DEEP mode is complete.
```

## Per-Agent Ownership

Each field has exactly **one owner agent** that writes it. Other agents read but never overwrite. This prevents the "two agents disagreeing about the same field" bug.

| Field | Owner | Who reads it |
|-------|-------|--------------|
| `schema_version` | orchestrator | all |
| `project_id` | orchestrator | all |
| `project_name` | orchestrator | all |
| `created_at` | orchestrator | all |
| `updated_at` | every agent (on its turn) | all |
| `snapshot_file_path` | orchestrator | all |
| `current_agent` | orchestrator | all |
| `agents_completed` | every agent (appends itself) | orchestrator |
| `agents_pending` | orchestrator | orchestrator |
| `user_requirements` | orchestrator | all |
| `selected_board` | Volt | Sage, Iris, Atlas, Vera |
| `selected_components` | Volt | Sage, Iris, Atlas, Vera |
| `gpio_allocation` | Volt | Vera (conflict checks) |
| `esphome_filename` | Volt | Sage, Atlas |
| `entity_ids_generated` | Volt (sensors), Ada (custom), Sage (helpers) | Iris, Mira |
| `ha_yaml_files` | Sage | Atlas |
| `validation_results[<soul>]` | the named agent | orchestrator, Vera |
| `conflict_log[]` | any agent | orchestrator (resolves) |
| `notes[]` | any agent | all |

Vera is the cross-agent reviewer. Vera **only reads**, never writes outside `validation_results.vera` and `conflict_log`.

## Reading the Snapshot

When an agent receives control:

1. Read the snapshot file at the path the orchestrator provides.
2. Verify `current_agent` matches its own soul name. If not, refuse to write.
3. Verify the snapshot validates against the schema. If not, refuse to write and add a `conflict_log` entry naming the schema violation.
4. Use `selected_board`, `selected_components`, `gpio_allocation`, `entity_ids_generated`, and any other relevant fields as the **authoritative project state**.

The snapshot is more trustworthy than the conversation transcript. If the snapshot says `selected_board: esp32-c3-mini` and the conversation mentions C6, the snapshot wins until the orchestrator updates it.

## Writing the Snapshot

When an agent completes its work:

1. Update only the fields it owns (see table above).
2. Set `updated_at` to the current ISO 8601 timestamp.
3. Append its own soul name to `agents_completed`.
4. Record its `validation_results[<own_soul>]` entry with at minimum:
   - `status`: passed | failed | warning | skipped
   - `validators_run`: list of validator module names
   - `failures`: list of failure messages (must be empty if status is passed)
5. Write the file atomically (write to `<snapshot>.tmp` then rename) to avoid corruption if the run is interrupted.
6. Validate the written file against the schema before reporting completion. If validation fails, restore the previous version and raise a conflict.

## Conflict Handling

Any agent that detects a problem it cannot resolve unilaterally must add an entry to `conflict_log` instead of guessing:

```json
{
  "raised_by": "vera",
  "blocks_agent": "volt",
  "message": "Volt selected GPIO 0 for BME280 SDA, but GPIO 0 is a strapping pin on ESP32-C3-MINI. See aurora/references/boards/esp32/esp32-c3-mini.json.",
  "raised_at": "2026-05-13T22:40:00Z",
  "resolution": null,
  "resolved_at": null
}
```

The orchestrator surfaces unresolved conflicts to the user and stops the pipeline. The user picks a resolution, the orchestrator (or an agent re-invoked by the orchestrator) updates the relevant fields, marks `resolution` and `resolved_at`, then resumes.

DEEP mode does NOT complete while any `conflict_log` entry has `resolution: null`.

## Failure Modes the Protocol Is Designed to Prevent

- **Lost context between agents.** Without the snapshot, Sage would have to re-derive what Volt did from chat history. The snapshot is structured, schema-validated, and survives compaction.
- **Stale assumptions.** If Volt later changes a pin assignment after Sage already wrote automations, the diff in `gpio_allocation` (and `updated_at`) is visible. Sage can be re-invoked.
- **Silent conflicts.** Without `conflict_log`, an agent might "work around" something that should have blocked the project (e.g. Vera disagreeing with Volt). With the log, conflicts are surfaced to the user.
- **Ambiguous ownership.** With explicit per-field ownership, two agents cannot fight over the same value.

## Out of Scope for Phase 1

This protocol document and its schema/example/tests are the foundation. The following are **explicitly not** part of Phase 1 and will come in later phases:

- Per-agent Iron Law 6 propagation (Ada, Sage, River, Mira, Atlas, Iris each need their own version).
- Per-agent validator modules (each agent has different things to validate against — Sage has YAML syntax, Ada has Python async correctness, etc.). Validators require reference data, which most agents do not yet ship.
- Orchestrator wiring to actually create/route/clean up snapshots inside aurora SKILL.md.
- Migration helpers for users with in-flight DEEP projects.

Phase 1 lands the contract. Later phases will implement the agents against that contract.
