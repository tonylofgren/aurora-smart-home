# HA Integration Pattern: File Sync

Copy Aurora-generated files directly into the Home Assistant `config/` folder
using Samba, SCP, or the File Editor add-on. The most straightforward
file-based approach: files on disk, HA loads them on restart or reload.

## When to use

- Multiple files delivered as part of one project (automation + package + dashboard)
- User wants files on disk (survives HA reinstall if backup includes `config/`)
- Updates are infrequent — manual copy per update is acceptable
- User has Samba or SSH access to the HA server

## When NOT to use

- User has no server access — use [UI paste](./ui-paste.md)
- User wants version control and rollback — use [Git pull](./git-pull.md)
- Files update frequently (daily generation) — git pull is more ergonomic

## Access methods

### Samba share (Windows / Mac / Linux)

The Samba add-on exposes the HA config folder as a network share.

1. Install the **Samba share** add-on (Settings > Add-ons > Add-on store).
2. Configure a username and password in the add-on configuration.
3. Access the share:
   - Windows: `\\<ha-ip>\config` in File Explorer
   - Mac: `Cmd+K` in Finder → `smb://<ha-ip>/config`
   - Linux: `smb://<ha-ip>/config` in Nautilus or `mount -t cifs`
4. Copy files directly into the share.

### SCP / SFTP (SSH)

If SSH is enabled (Settings > System > Terminal & SSH, or SSH add-on):

```bash
scp automations/co2-alert.yaml homeassistant@<ha-ip>:/config/automations/
scp dashboards/co2-dashboard.yaml homeassistant@<ha-ip>:/config/dashboards/
```

Replace `<ha-ip>` with your HA instance's IP address.

For multiple files at once:

```bash
scp -r co2-air-quality/automations/* homeassistant@<ha-ip>:/config/automations/
```

### File Editor add-on

1. Install the **File Editor** add-on (Settings > Add-ons).
2. Open File Editor from the sidebar.
3. Navigate to the target folder.
4. Create a new file, paste the generated YAML, save.

## Installing Aurora-generated files

After copying files to the server, trigger HA to load them:

| File type | Reload method |
|-----------|--------------|
| Automations (`automations/*.yaml`) | Developer Tools > YAML > Reload Automations |
| Scripts (`scripts/*.yaml`) | Developer Tools > YAML > Reload Scripts |
| Packages (`packages/*.yaml`) | Full restart (Settings > System > Restart) |
| Dashboards (`dashboards/*.yaml`) | No reload needed — HA reads dashboards dynamically |
| Custom components (`custom_components/`) | Full restart |

**Quick restart from CLI** (if SSH is available):

```bash
ssh homeassistant@<ha-ip> ha core restart
```

## Verification

After reload: check **Settings > Automations & Scenes** for automations, or
**Developer Tools > States** to confirm entities from packages exist.

## Common issues

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| File copied but not loaded | Reload not triggered | Reload or restart HA |
| "Permission denied" on SCP | Wrong SSH user or key | Use the `root` user for SSH add-on, or configure key auth |
| Samba share not visible | Add-on not running | Start the Samba add-on in Settings > Add-ons |
| Automation appears but does not trigger | Entity IDs in YAML do not match HA | Check entity IDs in Developer Tools > States |

## Folder layout in config/

```
config/
├── automations/          ← drop automation .yaml files here
├── scripts/              ← drop script .yaml files here
├── packages/             ← drop package .yaml files here
├── dashboards/           ← drop dashboard .yaml files here
└── custom_components/    ← drop custom component folders here
    └── <integration_id>/
```

If any of these folders do not exist, create them before copying files, and
configure `configuration.yaml` to load them per
[include-dir-named.md](./include-dir-named.md).
