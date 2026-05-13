# Contributing a HACS Integration Profile

Aurora's catalog of HACS-distributed Home Assistant integrations is intentionally narrow. Adding an entry is a manual verification step. The catalog only carries integrations that have been confirmed to install and run against a known HA version, with a maintainer who responds, and a clear lifecycle status.

If you want Atlas or Ada to handle a community HACS integration you use, add a profile here.

## Before You Open a PR

1. **Verify the source URL is live.** The repository must exist and be public.
2. **Verify the maintainer is active.** Last commit or issue reply within 6 months. Otherwise the entry's `lifecycle.status` is `abandoned`.
3. **Install the integration via HACS yourself** on the HA version you list in `homeassistant.min_version`. Verify the integration's entities appear, the config flow works (if applicable), and any documented features behave.
4. **Read the integration's documentation** for warnings the user must know: cloud calls, required credentials, polling intervals, breaking-change history.

## Profile Shape

Profiles live at `aurora/references/hacs_integrations/<hacs_integration_id>.json` and validate against `aurora/references/schemas/hacs-integration.schema.json`.

### Required fields

- `schema_version`
- `hacs_integration_id` — snake_case identifier matching the integration's `custom_components/<id>/` directory.
- `display_name`
- `source` — `{type, url, hacs_default?}`. `hacs_default: true` if the integration is in the HACS default repository (no custom repository needed).
- `homeassistant` — `{min_version, domains, config_flow?, yaml_example?}`. `domains` lists every entity domain the integration provides; `config_flow` is false only when the integration is YAML-only.
- `category` — one of: `energy`, `climate`, `lighting`, `media`, `security`, `presence`, `vacuum`, `weather`, `calendar`, `notifications`, `automation_helper`, `frontend`, `infrastructure`, `voice_assistant`, `other`.
- `lifecycle` — `{status, released}`.
- `last_verified`

### Optional but strongly recommended

- `summary` — one-sentence description.
- `documentation_url`
- `tags` — free-form labels for grouping.
- `maintainer` — `{github_handle, last_active_check_date, responsive}`.
- `requires_credentials` — true when the integration needs API keys, OAuth, or username/password. When true, the secrets-validator path applies to the user's `configuration.yaml` if YAML setup is needed.
- `cloud_calls` — true when the integration makes calls to a cloud service. Surfaces a privacy warning when paired with a conversation agent (see `llm-config-validator`).
- `warnings` — known caveats: rate limits, breaking changes between HA versions, login flow quirks. Atlas and Ada surface these verbatim.
- `verified_by` — at least one entry required for non-experimental status. Format: `{who, date, ha_version, notes}`.

## Lifecycle Rules

Same as for external_components (see `aurora/references/external_components/CONTRIBUTING.md`):

- `active`, `experimental`, `deprecated`, `abandoned`, `merged_to_core`.

The verification floor is the same: profile must come from someone who has installed and run the integration on the listed HA version within the last 30 days.

## What Aurora Will Reject

- Profiles for integrations the contributor has not personally installed.
- Profiles missing `verified_by` for `active` lifecycle status.
- Profiles whose `last_verified` is more than 6 months old.
- Integrations that exist in the HA core. Aurora does not duplicate core integrations as community profiles.
- Profiles claiming `requires_credentials: false` for an integration that actually needs credentials. Atlas's `secrets-validator` path depends on this flag being accurate.

## Pull Request Checklist

- [ ] `aurora/references/hacs_integrations/<id>.json` validates against the schema.
- [ ] At least one entry in `verified_by` for non-experimental status.
- [ ] `last_verified` within the last 30 days.
- [ ] `requires_credentials` is set correctly (relevant for secrets-validator).
- [ ] `cloud_calls` is set correctly (relevant for conversation-agent privacy warnings).
- [ ] `warnings` lists every known issue from your verification install.
- [ ] PR description includes a screenshot of the integration's entities loaded successfully in HA.
