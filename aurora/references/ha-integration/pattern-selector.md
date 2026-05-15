# HA Integration Pattern Selector

Decision guide for choosing how Aurora-generated YAML files land in Home
Assistant. Read this before writing any Installation section in README.md,
INSTALL.md, or a specialist soul. Point the user to the relevant pattern doc
for copy-paste-ready instructions.

## The four patterns

| Pattern | Best for | Requires |
|---------|----------|---------|
| [UI paste](./ui-paste.md) | One-off automation or single file | HA browser access |
| [!include_dir_named](./include-dir-named.md) | Many automations or helpers; want HA to auto-load a folder | SSH / Samba / File Editor; HA restart |
| [File sync](./file-sync.md) | Keeping generated files on disk; syncing updates | Samba share or SCP access; HA restart or reload |
| [Git pull](./git-pull.md) | Version control, team collaboration, reproducible config | Git repo; SSH or Samba to HA server |

## Decision flowchart

```
Is this a single automation, script, or dashboard?
    Yes → UI paste
    No  ↓

Do you want version control + git history?
    Yes → Git pull
    No  ↓

Do you have SSH or Samba access to the HA server?
    No  → UI paste (only safe option without server access)
    Yes ↓

Do you want HA to auto-load every file in a folder on restart?
    Yes → !include_dir_named
    No  → File sync
```

## Recommended default per agent

| Agent | Default pattern | Reason |
|-------|----------------|--------|
| Sage (automations) | File sync | Clean separation, easy to update |
| Sage (packages) | !include_dir_named | Packages are designed for folder-based loading |
| Iris (dashboards) | UI paste | Dashboard YAML has one standard path |
| Ada (custom components) | File sync | custom_components/ must be in config/ |

## How to reference this in an Installation section

In README.md or INSTALL.md, after listing the files delivered:

```markdown
## Installation

This project delivers [N] files. Choose the install method that matches your
setup — see the
[HA Integration Pattern Selector](https://github.com/tonylofgren/aurora-smart-home/blob/main/aurora/references/ha-integration/pattern-selector.md)
if you are unsure which to pick.

**Option A — UI paste** (recommended for single files, no server access needed)
[...]

**Option B — File sync via Samba** (recommended when you have server access)
[...]
```

The Install-Format-Disclosure Rule in `aurora/SKILL.md` requires both options
to appear when both apply. The pattern selector helps the user understand the
trade-offs so the recommendation has a reason behind it, not just a label.

## Pattern comparison

| | UI paste | !include_dir_named | File sync | Git pull |
|--|--|--|--|--|
| Survives HA update | No (UI config resets on some updates) | Yes | Yes | Yes |
| Version history | No | No | No | Yes |
| Multi-file updates | One by one | Drop folder + restart | rsync / scp | git pull + restart |
| Server access needed | No | Yes | Yes | Yes |
| Difficulty | Lowest | Medium | Medium | Highest |
| Recovery if broken | Delete + re-paste | Remove file + restart | Restore file + restart | git revert + restart |
