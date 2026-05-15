# HA Integration Pattern: !include_dir_named

Use Home Assistant's `!include_dir_named` directive to have HA automatically
load all YAML files in a folder. Every file dropped into the folder is picked
up on the next restart — no editing of `configuration.yaml` needed per file.

## When to use

- Many automations or helpers that grow over time
- User wants to drop Aurora-generated files into a folder and restart
- Packages folder already configured with `!include_dir_named`
- User prefers file-based config over UI-created automations

## When NOT to use

- User has no SSH / Samba / File Editor access to the HA server
- Single file: plain [UI paste](./ui-paste.md) is simpler
- Dashboard YAML: dashboards use a different loading mechanism
  (see [ui-paste.md](./ui-paste.md) for dashboards)

## Prerequisites

- SSH, Samba share, or HA File Editor add-on access to the HA `config/` folder
- A folder created under `config/` for the file type (e.g. `config/automations/`)
- `configuration.yaml` edited once to point at the folder

## Setup (one-time)

### For automations

Edit `config/configuration.yaml`:

```yaml
automation: !include_dir_merge_list automations/
```

Create the folder:

```
config/
└── automations/
    └── (drop .yaml files here)
```

Restart HA after editing `configuration.yaml`.

### For packages

Edit `config/configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages/
```

Create the folder:

```
config/
└── packages/
    └── (drop .yaml files here)
```

Restart HA after editing `configuration.yaml`.

### For scripts

```yaml
script: !include_dir_named scripts/
```

## Installing Aurora-generated files

1. Connect to your HA server via Samba, SSH, or the File Editor add-on.
2. Copy the generated `.yaml` file(s) into the correct subfolder:
   - Automations → `config/automations/`
   - Packages → `config/packages/`
   - Scripts → `config/scripts/`
3. In HA: **Developer Tools > YAML > Reload Automations** (for automations)
   or do a full restart for packages and scripts.

**No changes to `configuration.yaml` are needed for subsequent files** — any
`.yaml` file dropped in the folder is picked up automatically.

## Verification

After reload: **Settings > Automations & Scenes** — the new automation should
appear. For packages: **Developer Tools > Template** — test that entities
defined in the package exist.

## Common issues

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Automation not appearing | Wrong folder path in `configuration.yaml` | Check the path matches exactly; trailing slash matters |
| "Failed to load" error in logs | YAML syntax error in the file | Open the file, fix indentation, reload |
| Entity from package not found | Package not loaded | Check `configuration.yaml` has `!include_dir_named` under `homeassistant: packages:` |
| Duplicate automation IDs | Two files define the same `id:` | Remove the `id:` line from one, or rename it |

## Notes on !include_dir_merge_list vs !include_dir_named

| Directive | Returns | Use for |
|-----------|---------|---------|
| `!include_dir_merge_list` | Flat list (merged) | `automation:` key (list of automation objects) |
| `!include_dir_named` | Dict keyed by filename | `homeassistant: packages:`, `script:`, `scene:` |

Mixing these up causes HA to fail loading the config. Automations use
`!include_dir_merge_list`; packages and scripts use `!include_dir_named`.
