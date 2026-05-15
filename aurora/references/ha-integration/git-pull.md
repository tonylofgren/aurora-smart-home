# HA Integration Pattern: Git Pull

Store Aurora-generated project files in a git repository and pull updates
directly to the HA server. The most robust pattern for users who want version
history, rollback, and reproducible config.

## When to use

- User already uses git for HA config (common with advanced users)
- Multiple people contribute to the same HA config
- Updates happen regularly and the user wants a one-command update path
- Rollback ("undo the last Aurora change") is important
- User wants to track what changed and when

## When NOT to use

- User has no git experience and this is their first HA project — start with
  [UI paste](./ui-paste.md) or [file sync](./file-sync.md)
- The project is a one-off with no expected updates
- The HA server has no internet access and cannot reach the git remote

## Prerequisites

- A git repository (GitHub, GitLab, Gitea, or self-hosted)
- SSH or Samba access to the HA server
- Git installed on the HA server (available in the Terminal & SSH add-on)

## Setup (one-time)

### 1. Create a repository

Create a repository on GitHub (or your preferred host). For a private config
repo, use a private repository.

Recommended structure:

```
ha-config/                ← repository root (maps to config/)
├── automations/
├── packages/
├── dashboards/
├── custom_components/
└── README.md
```

### 2. Clone to the HA server

Via SSH add-on or Terminal add-on:

```bash
cd /config
git init
git remote add origin git@github.com:<user>/<repo>.git
git pull origin main
```

Or clone to a separate folder and symlink:

```bash
cd /
git clone git@github.com:<user>/<repo>.git ha-config
ln -s /ha-config/automations /config/automations
```

### 3. Configure SSH key for the HA server

Generate a key on the HA server and add the public key to the git remote:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/ha_git_key -N ""
cat ~/.ssh/ha_git_key.pub
# Add this to GitHub: Settings > SSH keys > New SSH key
```

## Workflow: adding Aurora-generated files

1. **On your local machine:** Run Aurora, generate the project files.
2. Copy generated files into your local clone of the config repository.
3. Commit and push:

```bash
git add automations/co2-alert.yaml packages/co2-package.yaml
git commit -m "feat: add CO2 alert automation from Aurora"
git push origin main
```

4. **On the HA server** (via SSH):

```bash
cd /config
git pull origin main
```

5. Reload HA:

```bash
ha core reload-automations   # for automations only
# or
ha core restart              # for packages, custom components
```

## Automating git pull (optional)

Use an HA automation to pull on a schedule or on demand:

```yaml
automation:
  - alias: "Git pull config on demand"
    trigger:
      - platform: event
        event_type: ha_config_pull_requested
    action:
      - service: shell_command.git_pull_config

shell_command:
  git_pull_config: "cd /config && git pull origin main"
```

Or use the **Git pull** add-on from HACS, which provides a dashboard button
for one-click pulls.

## Rollback

If a pulled change breaks HA:

```bash
cd /config
git log --oneline -10         # find the last good commit
git revert HEAD               # revert the last commit
# or
git reset --hard <commit-sha> # reset to a specific commit (destructive)
ha core restart
```

## Common issues

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `Permission denied (publickey)` | SSH key not added to git remote | Add the HA server's public key to the git host |
| `fatal: not a git repository` | Git not initialised | Run `git init` in `/config` |
| Conflict on pull | Local file differs from remote | Stash or discard local changes: `git checkout -- .` |
| HA does not pick up pulled files | Reload not triggered | Run `ha core reload-automations` or restart |

## Samba alternative

If SSH is unavailable, mount the Samba share locally and use a local git repo:

```bash
# Mount HA config over Samba (Linux/Mac)
mount -t cifs //<ha-ip>/config /mnt/ha-config -o user=<user>

# Pull and copy
cd ~/ha-project-repo
git pull
cp automations/*.yaml /mnt/ha-config/automations/
```

Then trigger reload via HA UI or REST API:

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  http://<ha-ip>:8123/api/services/automation/reload
```
