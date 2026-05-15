# Manual Format

Format for the project `README.md` that ships in every project folder. The manual is the master document for the project. It is written by Volt for hardware projects, by Sage / Ada / River / Iris for software-only projects, each with its agent-specific Installation section.

## Project structure context

This spec describes the **root** `README.md` at `<project>/README.md`. The root README is the master document. Agent-specific deliverables live in canonical subdirectories per the **Project Structure Rule** in `aurora/SKILL.md`:

- `<project>/esphome/` (Volt — firmware YAML, INSTALL.md, TROUBLESHOOTING.md)
- `<project>/hardware/` (Volt — BOM.md, WIRING.md when split out, HAZARD-ANALYSIS.md, SCHEMATIC.md, PCB-NOTES.md, MANUFACTURING.md, COST-ANALYSIS.md, CERTIFICATION.md, TEST-JIG.md)
- `<project>/automations/`, `<project>/scripts/`, `<project>/blueprints/`, `<project>/packages/` (Sage)
- `<project>/custom_components/<integration_id>/` (Ada)
- `<project>/node-red-flows/` (River)
- `<project>/dashboards/` (Iris)

The root README links to each subdirectory's contribution. Per-subdirectory READMEs (e.g. `<project>/automations/README.md`) are optional and only added when a subdirectory's content has non-obvious context that does not belong in the master. The required sections below apply to the **root** README; sub-READMEs may use any structure.

## Language

The root README and any sub-README MUST be written in the user's detected language per the **Language Rule for Deliverables** in `aurora/SKILL.md`. The same rule applies to every other human-readable file in the project (`INSTALL.md`, `TROUBLESHOOTING.md`, `BOM.md`, `WIRING.md`). The default-to-English fallback only fires when the user explicitly wrote their request in English. A Swedish user gets a Swedish `INSTALL.md` with translated headings, prerequisites, step descriptions, and verification text; only quoted commands, paths, and identifiers stay English.

## Multi-agent README ownership

When multiple specialists contribute to one project, the FIRST specialist invoked writes the root `README.md` with H2 sections for its own contribution. Each subsequent specialist APPENDS a new H2 section to the same root `README.md`:

| First-in agent | First sections written         | Later agent appends            |
|----------------|---------------------------------|--------------------------------|
| Volt           | Bill of materials, Wiring, Installation (Volt), Calibration, Troubleshooting (Volt), Recovery (Volt) | Sage adds "Automations", Iris adds "Dashboard", Ada adds "Custom integration" |
| Sage           | Installation (Sage), Troubleshooting, Recovery | Iris adds "Dashboard", Volt rare in this order |
| Ada            | Installation (Ada), Configuration, Troubleshooting, Recovery | Sage adds "Automations using this integration" |

The Attribution banner under the H1 is owned by the first specialist; subsequent specialists do not duplicate it. Specialists never overwrite each other's sections, never create competing root READMEs, and never split themselves into a sub-README unless the appended section grows past ~150 lines.

## Install-Format-Disclosure (Sage, Iris)

When the agent ships both a UI-paste-ready file AND a packaged / dashboard-mode-ready file, the README "Installation" section MUST present them as two clearly labelled options (Option A, Option B) with a one-line recommendation for which to pick. Per the **Install-Format-Disclosure Rule** in `aurora/SKILL.md`, the user picks the install path at install-time, not at generation-time. Both files are generated when both apply.

## Required sections (every project)

Every project README has these sections, in this order, as H2 headings:

1. **What this does** — one or two paragraphs naming what the project measures, controls, or automates, and where the result shows up (entity IDs, dashboard tile, notification, etc.).
2. **Bill of materials** — hardware projects only. Inline BOM table per [bom-format.md](./bom-format.md), or a one-line link to `BOM.md` if the table was split out.
3. **Wiring** — hardware projects only. Inline wiring per [wiring-format.md](./wiring-format.md), or a one-line link to `WIRING.md` if it was split out.
4. **Installation** — agent-specific stepwise instructions (see below).
5. **Calibration** — hardware projects with sensors that require it (per Volt Iron Law 3). Omit if no sensor in the BOM needs calibration.
6. **Troubleshooting** — three most likely failure points (per Volt Iron Law 5 for hardware). For software projects: the three most likely deployment or runtime issues.
7. **Recovery** — what to do if the device is unreachable (hardware) or the change broke an existing entity (software).

The manual starts with an attribution banner directly under the H1 title (see Attribution banner below) per the relevant skill's Code Attribution section.

## Attribution banner

Every project README MUST start with an attribution banner that links back to Aurora's GitHub repo. The banner sits directly under the project's H1 title, before any other content. It is a Markdown blockquote with a clickable Markdown link inside, never plain text. The repo URL is always `https://github.com/tonylofgren/aurora-smart-home`.

Format depends on which skill produced the README:

| Skill                         | Banner (paste verbatim under the `#` H1 title)                                                                                       |
|-------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `esphome` (Volt)              | `> *Generated by [aurora@aurora-smart-home (esphome skill)](https://github.com/tonylofgren/aurora-smart-home)*`                       |
| `home-assistant` (Sage, Iris) | `> *Generated by [aurora@aurora-smart-home (home-assistant skill)](https://github.com/tonylofgren/aurora-smart-home)*`                |
| `ha-integration-dev` (Ada)    | `> *Generated by [aurora@aurora-smart-home (ha-integration-dev skill)](https://github.com/tonylofgren/aurora-smart-home)*`            |
| `node-red` (River)            | `> *Generated by [aurora@aurora-smart-home (node-red skill)](https://github.com/tonylofgren/aurora-smart-home)*`                      |

Example top-of-README structure:

    # Bedroom CO2 Monitor

    > *Generated by [aurora@aurora-smart-home (esphome skill)](https://github.com/tonylofgren/aurora-smart-home)*

    ## What this does

    [content]

The blockquote (`>`) separates the banner visually from the H1 title above and from the content below. The Markdown link makes the GitHub URL clickable when the README is rendered on GitHub or in a Markdown viewer.

If the agent does not know which skill it represents, attribution falls back to `> *Generated by [aurora@aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*` without the sub-skill marker.

**Without this banner at the top of the project README, the README does not satisfy Iron Law 8 (Volt) or Iron Law 3 (Sage, Ada, River, Iris).** A README that does not link back to its source from the very top is not deliverable.

## GitHub topics for published projects

When the user publishes an Aurora-generated project to GitHub, the repo should carry topics that make it discoverable. Two layers:

1. **Discovery topic (Aurora-specific, always included):** `made-with-aurora-skill` lets anyone find every Aurora-generated repo via the GitHub topic page (`https://github.com/topics/made-with-aurora-skill`) or `gh search repos --topic made-with-aurora-skill`. This is the universal discovery hook for the Aurora community across all agent types.
2. **Domain topics (ecosystem-specific):** topics that match the project's stack so HACS, ESPHome Dashboard, and search engines can find it.

The agent does NOT run any `gh` commands itself. It hands the user a paste-ready block in the project README so the user can execute them when ready to publish. If the user does not intend to publish, the block is informational and ignored.

### Topics for HACS integrations (Ada)

Standard topic set:

- `made-with-aurora-skill` (discovery: Aurora-generated)
- `home-assistant`
- `hacs`
- `home-assistant-integration`
- `custom-component`
- `python`

Plus one or two domain-specific topics:

- The integration's primary entity domain (`sensor`, `light`, `media-player`, `switch`, etc.).
- The cloud, device, or protocol it integrates with (`tibber`, `philips-hue`, `unifi`, `mqtt`, etc.).

In Ada's `README.md` Installation section, include a `Publish to HACS` step that gives the user a paste-ready command set:

```
gh repo create <user>/<integration-id>-integration --public --source=. --remote=origin --push
gh repo edit --add-topic made-with-aurora-skill
gh repo edit --add-topic home-assistant
gh repo edit --add-topic hacs
gh repo edit --add-topic home-assistant-integration
gh repo edit --add-topic custom-component
gh repo edit --add-topic python
gh repo edit --add-topic <integration-specific-1>
gh repo edit --add-topic <integration-specific-2>
```

Topics are not part of the integration's own `manifest.json`. They are GitHub-side metadata set on the repo. Without them, the HACS catalog discovery flow may not find the repo and prospective users have a harder time searching.

### Topics for published ESPHome projects (Volt)

For Volt-generated ESPHome projects the user wants to share (less common than HACS, but for community hardware builds):

- `made-with-aurora-skill` (discovery: Aurora-generated)
- `esphome`
- `esp32` (or the specific MCU: `esp32-s3`, `esp32-c3`, `rp2040`)
- `home-assistant`
- `iot`

Volt only includes a `Publish` step when the user mentions sharing the build. Personal one-off ESPHome projects skip it.

### Topics for published automations, flows, and dashboards (Sage, River, Iris)

When the user shares a Sage automation, River flow, or Iris dashboard via GitHub, the standard topic set is:

- `made-with-aurora-skill` (discovery: Aurora-generated)
- `home-assistant`
- Plus agent-specific:
  - Sage: `blueprint`, `automation`
  - River: `node-red`, `node-red-flow`
  - Iris: `lovelace`, `dashboard`

Like Volt, these agents only include a publish step when the user signals they want to share. Personal automations stay local.

## Installation, per agent

The Installation section is agent-specific. Every variant must be stepwise and reproducible without inferring missing context.

### Volt (hardware)

```
## Installation

1. Prerequisites
   - ESPHome installed (CLI 2026.4.5 or later) or ESPHome Dashboard.
   - Home Assistant 2026.4 or later with the ESPHome integration.
   - USB cable that supports data (not all USB-C cables do).
   - The components from the Bill of Materials, assembled per the Wiring section.

2. Configure secrets
   - Copy `secrets.yaml.example` to `secrets.yaml`.
   - Fill in `wifi_ssid`, `wifi_password`, and `api_encryption_key`
     (generate a new key, do not reuse one from another device).

3. Flash the device
   - Connect the device via USB.
   - `esphome run <device-name>.yaml` and pick the USB port.
   - First boot logs appear in the terminal. Wait for "API: Connected".

4. Add to Home Assistant
   - Settings → Devices & Services. The device should auto-discover.
   - If not, click "Add Integration" → ESPHome → enter the device IP.
   - Paste the `api_encryption_key` from `secrets.yaml`.

5. Verify entities
   - Open the new device entry. The entities listed in "What this does"
     must all be present and reporting.
```

### Sage (HA YAML)

When Sage shipped both an `automations/<name>.yaml` (UI-paste form) AND a `packages/<name>.yaml` (bundled form), the Installation section lists both options. When only the single automation was shipped, omit Option B and the recommendation line.

```
## Installation

Two ways to install. Pick one.

### Option A: Paste into the HA UI (recommended for first-time HA users)

1. Prerequisites
   - Home Assistant 2026.4 or later.
   - The entities the automation references must exist (see "What this does").

2. Open Settings → Automations & Scenes → Create automation.

3. Click the "⋮" menu (top right of the editor) → "Edit in YAML".

4. Paste the contents of `automations/<name>.yaml`.

5. Save. Trigger manually to verify.

### Option B: Drop in as a package (advanced)

Use this when the project ships helpers, scripts, or template sensors
alongside the automation, and you want everything in one file.

1. Prerequisites
   - Your `configuration.yaml` has, under `homeassistant:`:
     `packages: !include_dir_named packages/`
   - If not, add it now and restart HA once before continuing.

2. Copy `packages/<name>.yaml` to your HA `config/packages/` folder.

3. Settings → System → Restart, OR Developer Tools → YAML → "Restart"
   (a full restart is needed because packages register helpers and
   template sensors at boot, not on reload).

4. Verify: the helpers, scripts, and template sensors listed in
   "What this does" all appear under Settings → Devices & Services →
   Helpers. Trigger the automation manually.

**Not sure?** Use Option A. It works on any HA install with zero
extra configuration.
```

### Ada (Python custom integration)

```
## Installation

1. Prerequisites
   - Home Assistant 2026.4 or later.
   - Access to `config/custom_components/` (file editor add-on, SSH, or Samba).

2. Copy the integration
   - Place the `custom_components/<integration_id>/` folder into your
     HA `config/custom_components/`.
   - Or install via HACS (Custom repositories → add this repo's URL,
     category Integration) if HACS is set up.

3. Restart Home Assistant
   - Settings → System → Restart.

4. Add the integration
   - Settings → Devices & Services → "Add Integration".
   - Search for the integration name → follow the config flow.

5. Verify
   - The integration entry appears under Devices & Services.
   - The entities listed in "What this does" are present.
```

### River (Node-RED flow)

```
## Installation

1. Prerequisites
   - Node-RED 4.x with node-red-contrib-home-assistant-websocket 0.80+.
   - The HA server node already configured in Node-RED.

2. Import the flow
   - Hamburger menu → Import → paste the JSON from this project.
   - Pick the workspace tab to import into.

3. Deploy
   - Top-right "Deploy" button → "Full".
   - Verify the HA nodes show "connected" status (blue dot).

4. Verify
   - Trigger the flow's entry point (state change, event, manual inject).
   - Watch the flow's debug nodes confirm the path completed.
```

### Iris (dashboard)

```
## Installation

Two ways to install. Pick one.

### Option A: Paste into Raw Configuration Editor (recommended)

1. Prerequisites
   - The entities the dashboard references must exist.

2. Open the target dashboard.

3. Top-right "⋮" menu → "Edit dashboard" → "⋮" → "Raw configuration editor".

4. For a full dashboard: replace the contents with `dashboards/<name>.yaml`.
   For a single card or view: copy the relevant block into the existing
   structure at the right indentation level.

5. Save. Exit edit mode. Verify every card renders and every entity
   shows live state.

### Option B: Add as a YAML-mode dashboard (advanced)

Use this when you want the dashboard tracked as a file on disk instead
of in HA's `.storage/` database, e.g. for git versioning.

1. Copy `dashboards/<name>.yaml` to your HA `config/dashboards/` folder.

2. In `configuration.yaml`, under `lovelace:`, add:
   ```
   dashboards:
     <name>:
       mode: yaml
       title: <Dashboard Title>
       icon: mdi:view-dashboard
       show_in_sidebar: true
       filename: dashboards/<name>.yaml
   ```

3. Restart Home Assistant. The new dashboard appears in the sidebar.

**Not sure?** Use Option A. It is faster and does not require restarting HA.
```

## Recovery section, per agent

The Recovery section names what to do when the worst-case happens. Common cases:

- **Volt**: OTA failed and the device is unreachable → USB recovery (which pin is BOOT, which is RESET, how to enter download mode). Mention `usb_cdc` if the board supports it.
- **Sage**: an automation fires when it should not / does not fire when it should → check the Logbook, then the Trace timeline, then the entity history for the trigger.
- **Ada**: integration fails to load after restart → check `home-assistant.log` for the integration's domain, look for `ImportError` or config schema errors.
- **River**: deploy broke something → Node-RED has built-in version history; undo with the Deploy menu's "Restore previous deployment".
- **Iris**: dashboard YAML invalid → Raw editor refuses to save invalid YAML; if a saved dashboard is broken, use HA's `core.config` storage backup or the file editor on `.storage/lovelace*`.

## What NOT to put in the manual

- No "follow the official docs" without a link to the specific page and step.
- No generic "verify it works" without naming what success looks like.
- No "depends on your setup". Pick the most common setup and document it; mention alternatives only when they are necessary.
- No screenshots Aurora cannot generate. Describe the UI path in words: "Settings → Devices & Services → Add Integration".
- No promises Aurora cannot keep ("this will work on any board"). Constrain to the BOM and the wiring.
