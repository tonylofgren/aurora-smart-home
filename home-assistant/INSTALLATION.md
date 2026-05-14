# Installation Guide

## Prerequisites

- [Claude Code](https://claude.ai/code) installed and configured
- Active Claude account with API access

---

## Installation

```bash
# Add the marketplace repository
/plugin marketplace add tonylofgren/aurora-smart-home

# Install aurora (since v1.3, Home Assistant ships as part of the single aurora plugin — choose one scope)
/plugin install aurora@aurora-smart-home                    # Global (default)
/plugin install aurora@aurora-smart-home --scope project    # Team (shared via git)
/plugin install aurora@aurora-smart-home --scope local      # This project only
```

Restart Claude Code after installation.

---

## Verify Installation

Test by asking:
```
Create a simple automation that turns on a light when motion is detected
```

**Expected:** A complete Home Assistant YAML configuration with an offer to save.

---

## Update

Since v1.3, all aurora skills (including Home Assistant) ship as the single `aurora@aurora-smart-home` plugin.

```bash
# Inside Claude Code — refreshes every installed plugin
/reload-plugins

# From your terminal — targeted at aurora
claude plugin update aurora@aurora-smart-home
```

The slash command `/plugin` opens an interactive UI; it does not accept arguments like `/plugin update <name>`.

### Enable Auto-Update

1. Run `/plugin` to open the plugin manager
2. Go to **Marketplaces** tab
3. Select `aurora-smart-home`
4. Choose **Enable auto-update**

---

## Uninstall

Use the interactive UI for complete removal:

1. Run `/plugin`
2. Go to **Installed** tab
3. Select `aurora`
4. Choose **Uninstall**

**Note:** The CLI command `/plugin uninstall` only disables plugins.

---

## Change Scope

To move from one scope to another (e.g., user → local):

1. Uninstall via interactive UI (see above)
2. Reinstall with new scope:
   ```bash
   /plugin install aurora@aurora-smart-home --scope local
   ```

---

## Troubleshooting

### Skill Not Triggering

1. Verify installation: `/plugin`
2. Restart Claude Code
3. Try rephrasing with keywords: "Home Assistant", "automation", "smart home"

### Template Errors

1. Specify your HA version in requests
2. Report issues on [GitHub](https://github.com/tonylofgren/aurora-smart-home/issues)

---

## Getting Help

- **Usage examples:** See [USAGE-GUIDE.md](USAGE-GUIDE.md)
- **300+ prompts:** See [PROMPT-IDEAS.md](PROMPT-IDEAS.md)
- **Issues:** [GitHub Issues](https://github.com/tonylofgren/aurora-smart-home/issues)
