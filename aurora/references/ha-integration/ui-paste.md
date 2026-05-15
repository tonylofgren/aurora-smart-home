# HA Integration Pattern: UI Paste

Copy generated YAML directly into the Home Assistant editor, without touching
the file system. The simplest path — no SSH, no Samba, no restart for
automations.

## When to use

- Single automation, script, blueprint, or dashboard
- User has no server access (HA Cloud, Nabu Casa, managed host)
- Quick test before committing to a file-based install
- One-time delivery with no expected updates

## When NOT to use

- More than 3–4 files (tedious to paste individually)
- User needs version history
- Config must survive HA reinstallation
- Files need to be kept in sync with an Aurora-generated project folder

## Step-by-step: automation / script

1. Open Home Assistant in a browser.
2. Go to **Settings > Automations & Scenes** (for automations) or
   **Settings > Scripts** (for scripts).
3. Click **+ Create automation** or **+ Create script**.
4. In the top-right corner, click the three-dot menu and select
   **Edit in YAML**.
5. Select all existing content and replace it with the generated YAML.
   Do not include the `alias:` line if HA pre-filled it — the YAML already
   contains it.
6. Click **Save**.
7. The automation or script is immediately active. No restart needed.

**Verification:** Go back to the list view. The new automation / script should
appear. Open it, click the three-dot menu, and select **Trigger** to test it.

## Step-by-step: dashboard

1. Open Home Assistant in a browser.
2. Go to the dashboard you want to edit (or create a new one under
   **Settings > Dashboards**).
3. Click the pencil icon (Edit) in the top-right.
4. Click the three-dot menu in the top-right and select
   **Raw Configuration Editor**.
5. Select all existing content and replace it with the generated dashboard YAML.
6. Click **Save**.

**Verification:** Close the editor. The dashboard should reflect the new layout
immediately. If tiles are missing, check that all entity IDs in the YAML exist
in your HA instance.

## Step-by-step: package (YAML mode)

Packages require file system access. If the user has no server access, the
package must be broken into individual automations / helpers and pasted one
by one via the UI. See [file-sync.md](./file-sync.md) for the file-based
approach.

## Common issues

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Save button greyed out | YAML syntax error | Check indentation; YAML uses 2-space indent |
| "Unknown entity" warning | Entity ID does not exist yet | Create the helper / sensor first, then paste the automation |
| Automation not triggering | Platform / state mismatch | Open the automation trace (three-dot > Traces) to see why |
| Dashboard tiles blank | Entity ID wrong or unavailable | Verify entity IDs in Developer Tools > States |

## Limitations

- UI-pasted automations do not survive a HA configuration restore from a
  backup that predates the paste (they live in `.storage/`, not
  `configuration.yaml`).
- Packages and multi-file deliveries cannot be pasted in one step — use
  [file sync](./file-sync.md) instead.
- No version history. If the automation breaks, the previous version is gone
  unless the user saved a copy.
