# Contributing an ESPHome external_components Profile

Aurora's catalog of community ESPHome external_components is intentionally narrow. Adding an entry is a manual verification step, not a popularity contest. The catalog only carries components that have been confirmed to install and run against a known ESPHome version, with a maintainer who responds, and a clear lifecycle status.

If you want Volt to handle a community component you use, add a profile here.

## Before You Open a PR

1. **Verify the source URL is live.** Open it in a browser. The repository must exist and be public.
2. **Verify the maintainer is active.** Check recent commits or issue replies (last 6 months). If the project has been silent, the lifecycle status is `abandoned` and the catalog should NOT carry the entry as `active`.
3. **Install the component yourself.** Compile and flash it against the ESPHome version you list in `min_version`. A profile that has never been verified end-to-end is worse than no profile.
4. **Read the documentation linked in your profile** for warnings the user must know (platformio overrides, framework incompatibilities, GPIO requirements that conflict with the chip's strapping pins).

## Profile Shape

Profiles live at `aurora/references/external_components/<external_component_id>.json` and validate against `aurora/references/schemas/external-component.schema.json`.

### Required fields

- `schema_version` — the schema version your profile targets.
- `external_component_id` — snake_case identifier matching the ESPHome `components:` key when used.
- `display_name` — human-readable name.
- `source` — `{type, url, ref?, path?}`. `type` is one of `github`, `git`, `local`, `url`.
- `esphome` — `{min_version, supported_chips}`. `supported_chips` lists every chip you verified, not every chip you think it might support.
- `lifecycle` — `{status, released}`. `status` is one of `active`, `experimental`, `deprecated`, `abandoned`, `merged_to_core`.
- `last_verified` — ISO 8601 date you last verified the profile against the upstream source.

### Optional but strongly recommended

- `summary` — a one-sentence description.
- `documentation_url` — link to the maintainer's docs.
- `datasheet_url` — when the component drives specific hardware, link the datasheet so Volt's pin and voltage validators have something to cross-check.
- `maintainer` — `{github_handle, last_active_check_date, responsive}`.
- `warnings` — known caveats (platformio overrides, framework constraints, GPIO surprises). Surfaced verbatim to the user when Volt picks the component.
- `verified_by` — at least one entry is required when `lifecycle.status` is anything other than `experimental`. Format: `{who, date, esphome_version, notes}`.

## Lifecycle Rules

- **`active`** — verified working in the last 6 months on a currently-supported ESPHome version. At least one `verified_by` entry required.
- **`experimental`** — works on at least one ESPHome version but lacks the breadth of verification for `active`. No `verified_by` required; the status itself is the disclaimer.
- **`deprecated`** — still works but the maintainer has signalled it will be removed. `deprecated_since` and `successor` must be set.
- **`abandoned`** — the maintainer has not responded in 12+ months. The profile stays in the catalog (so the unknown-component protocol does not fire) but Volt's recommendation flow warns the user.
- **`merged_to_core`** — the component is now in upstream ESPHome. The profile redirects users to the core component name via `successor`.

## What Aurora Will Reject

- Profiles for components the contributor has not personally installed.
- Profiles where `source.url` points at a fork unless that fork is the actively-maintained one (in which case state why in the PR).
- Profiles missing `verified_by` for `active` lifecycle status.
- Profiles whose `last_verified` is more than 6 months old (re-verify before submitting).
- "Popular" components without verification.

The catalog's value is exactly the verification floor. Lowering it for breadth would be worse than no catalog at all — that's why Aurora ships the `unknown-component-validator` protocol for everything else.

## Pull Request Checklist

- [ ] `aurora/references/external_components/<id>.json` added and validates against the schema (run `python -m pytest aurora/tests/`).
- [ ] At least one entry in `verified_by` for non-experimental status.
- [ ] `last_verified` is within the last 30 days.
- [ ] `warnings` lists every known issue you hit during your verification install.
- [ ] If `lifecycle.status` is `deprecated`, `successor` points at a real replacement.
- [ ] PR description includes a screenshot or log excerpt from the successful install.
