# Manual Format

Format for the project `README.md` that ships in every project folder. The manual is the master document for the project. It is written by Volt for hardware projects, by Sage / Ada / River / Iris for software-only projects, each with its agent-specific Installation section.

## Required sections (every project)

Every project README has these sections, in this order, as H2 headings:

1. **What this does** — one or two paragraphs naming what the project measures, controls, or automates, and where the result shows up (entity IDs, dashboard tile, notification, etc.).
2. **Bill of materials** — hardware projects only. Inline BOM table per [bom-format.md](./bom-format.md), or a one-line link to `BOM.md` if the table was split out.
3. **Wiring** — hardware projects only. Inline wiring per [wiring-format.md](./wiring-format.md), or a one-line link to `WIRING.md` if it was split out.
4. **Installation** — agent-specific stepwise instructions (see below).
5. **Calibration** — hardware projects with sensors that require it (per Volt Iron Law 3). Omit if no sensor in the BOM needs calibration.
6. **Troubleshooting** — three most likely failure points (per Volt Iron Law 5 for hardware). For software projects: the three most likely deployment or runtime issues.
7. **Recovery** — what to do if the device is unreachable (hardware) or the change broke an existing entity (software).

The manual ends with an attribution footer per the relevant skill's Code Attribution section.

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

```
## Installation

1. Prerequisites
   - Home Assistant 2026.4 or later.
   - The entities the automation references must exist (see "What this does").

2. Copy the automation
   - Open `automations.yaml` (or the dashboard's automation editor).
   - Append the YAML from this project, or import the blueprint.

3. Reload
   - Developer Tools → YAML → "Reload Automations".
   - Or restart Home Assistant if the automation references new
     helpers / template sensors.

4. Verify
   - Trigger the automation manually from the UI.
   - Confirm the expected action fires (light turns on, notification
     sent, etc.).
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

1. Prerequisites
   - The entities the dashboard references must exist.

2. Add the YAML
   - Open the target dashboard in edit mode.
   - For full dashboards: Raw configuration editor → paste.
   - For single cards or views: copy the relevant block into the
     existing dashboard structure.

3. Verify
   - Exit edit mode. The card / view renders without errors.
   - Every entity referenced shows live state.
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
