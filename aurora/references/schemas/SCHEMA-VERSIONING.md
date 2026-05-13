# Schema Versioning

Operational rules for bumping `schema_version` on Aurora's JSON Schema files and on the profile JSON files that conform to them. Short list, not a philosophy essay.

## What Has a Schema Version

Two surfaces:

1. **The schema definitions** themselves (`aurora/references/schemas/*.schema.json`). Each declares a `$schema` (the JSON Schema meta-schema version — Draft 2020-12 across the repo) and a `$id` (the canonical URL). The schema's own version is implicit in the file's git history; we do not bump it as a field today.

2. **Profile files** that conform to a schema (`aurora/references/boards/<id>.json`, `components/<id>.json`, `expanders/<id>.json`, `voltage-shifters/<id>.json`, `external_components/<id>.json`, `hacs_integrations/<id>.json`, plus the project snapshot at `<project>/aurora-project.json`). Every profile carries a `schema_version` field. That field is what these rules govern.

## When to Bump `schema_version` on a Profile

| Change | Bump |
|--------|------|
| Patch description, fix typo, refine example | **Patch** (1.0.0 → 1.0.1) |
| Add a new **optional** field | **Minor** (1.0.0 → 1.1.0) |
| Add a new **required** field | **Major** (1.0.0 → 2.0.0) |
| Change the meaning of an existing field | **Major** |
| Rename a field | **Major** (the old name is no longer valid; consumers see breakage) |
| Tighten validation (e.g. narrow an `enum`, raise `minLength`) | **Major** if previously-valid data now fails; **Minor** if the tightening only catches data that was always meant to be invalid |
| Loosen validation (e.g. add an `enum` member, lower `minLength`) | **Minor** |
| Reorder fields in the JSON | **No bump** (JSON is unordered) |

Profile authors do not need to track schema versions. The catalog maintainer (currently the repo owner) bumps `schema_version` in lockstep with the matching schema file's changes; existing profiles either continue to validate (no change for them) or get a coordinated update PR.

## Backwards Compatibility

Today the catalog ships with `schema_version: "1.0"` across every profile and every schema. No versioned `$id` URLs exist for older schema revisions; bumping to `2.0` would mean older profiles no longer validate against the current schema. That is acceptable now because the catalog is small. When the catalog grows to dozens of community profiles, we will need:

- Per-version `$id` URLs (e.g. `https://aurora-smart-home.dev/schemas/board-profile-v2.schema.json`).
- A registry of historical schema URLs so old profiles can still be validated by anyone curious.
- A migration tool that rewrites profiles from `schema_version: "1.0"` to `"2.0"`.

That work is **explicitly future**; this document calls it out so a future contributor does not silently bump a schema to `2.0` and break every existing profile in the catalog without the supporting infrastructure.

## How to Land a Schema Change

1. **Decide the bump size** using the table above. When in doubt, ask: would an existing profile fail to validate against the new schema? If yes, major bump.
2. **Edit the schema file** at `aurora/references/schemas/<name>.schema.json`. Run the test suite (`python -m pytest aurora/tests/`) to confirm every existing profile still validates against the modified schema. If any profile fails, either fix the profile in the same PR or roll the schema change back.
3. **Update profiles in the same PR** when the bump is major. Mixed `schema_version` values across the catalog cause silent confusion.
4. **Add a CHANGELOG entry** under the next release describing the bump, the reason, and any profile updates that accompanied it.
5. **Re-run pytest** before commit. The schema tests (`test_board_schemas.py`, `test_component_schemas.py`, etc.) validate every profile against every schema; they catch ninety percent of accidental breakage.

## What Schema Versioning Does NOT Do

- It does not prevent a contributor from submitting a profile with the wrong `schema_version` value. Catch that in PR review.
- It does not version the meta-schema (Draft 2020-12). When a new JSON Schema draft is widely supported by tools we use (jsonschema Python lib, etc.), upgrading is a coordinated cross-schema change tracked under a project plan, not via this document.
- It does not version the *protocol* between aurora and its agents. Agent souls and validator markdown specs are versioned via git, not via `schema_version`.

## Tooling

The pytest suite under `aurora/tests/` runs in CI on every push and pull request to main. Schema changes that break any profile fail CI before merge. There is no separate migration tool today; if one becomes necessary it will be added under the "future" backwards-compatibility section above.
