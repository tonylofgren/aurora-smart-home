# Flow Organization in Node-RED

Structure flows for maintainability.

## Tabs (Flows)

### One Purpose Per Tab

```
[Motion Lights]     - All motion-triggered lighting
[Presence]          - Who's home detection
[Climate]           - Temperature automation
[Notifications]     - Alert routing
[Security]          - Door/window monitoring
```

### Tab Properties

```json
{
  "type": "tab",
  "label": "Motion Lights",
  "info": "Motion-triggered lighting automation.\n\nAreas:\n- Living Room\n- Kitchen\n- Hallway"
}
```

Use `info` for documentation that appears in sidebar.

---

## Naming Conventions

### Nodes

| Type | Convention | Example |
|------|------------|---------|
| Trigger | `[Area] [Event]` | `Living Room Motion` |
| Function | `[Verb] [Object]` | `Check Brightness` |
| Action | `[Action] [Target]` | `Turn On Lights` |
| Debug | `[What]` | `Motion State` |

### Entity References

```javascript
// Consistent naming in function nodes
const ENTITY_IDS = {
  motion: "binary_sensor.living_room_motion",
  light: "light.living_room",
  lux: "sensor.living_room_lux"
};
```

---

## Groups

Visual grouping for related nodes.

### Creating Groups

1. Select nodes
2. Ctrl+G (or menu)
3. Name the group

### Group Naming

```
[Area - Function]
Living Room - Motion Lights
Kitchen - Appliance Monitor
```

### Group Colors

| Color | Purpose |
|-------|---------|
| Default (light blue) | Normal automation |
| Green | Working, tested |
| Yellow | Needs configuration |
| Red | Error handling |
| Purple | External integrations |

---

## Link Nodes

Connect flows on same tab without wires.

### When to Use

- Avoid crossing wires
- Connect distant nodes
- Create reusable endpoints

### Link Node Pairs

```
[link out: "To Notification"]  →  [link in: "From Any"]
```

### Naming

```
Out: "To [Destination]"
In: "From [Source]" or "[Purpose]"
```

### Cross-Flow Links

Link nodes can connect across tabs:

```
[Tab: Motion] → [link out: "Alert"] → [Tab: Notifications] → [link in: "Alerts"]
```

---

## Comment Nodes

Document your flows.

### Header Comments

```
📋 MOTION LIGHTS
Automatically control lights based on motion.
Respects manual overrides and lux levels.
```

### Section Comments

```
--- TRIGGERS ---
[trigger nodes here]

--- LOGIC ---
[function nodes here]

--- ACTIONS ---
[action nodes here]
```

### Configuration Comments

```
⚙️ CONFIGURATION
Update these entity IDs:
- motion_sensor: binary_sensor.YOUR_MOTION
- light_entity: light.YOUR_LIGHT
- lux_sensor: sensor.YOUR_LUX (optional)
```

---

## Flow Layout

### Left to Right

```
[Input] → [Process] → [Output]

[Triggers]    [Logic]    [Actions]    [Debug]
     ↓           ↓          ↓           ↓
   x=100      x=300      x=500       x=700
```

### Vertical Alignment

Align related nodes vertically:

```
[Motion A] → [Logic] → [Light A]
                ↓
[Motion B] → [Logic] → [Light B]
                ↓
[Motion C] → [Logic] → [Light C]
```

### Spacing

| Direction | Spacing |
|-----------|---------|
| Horizontal | 200px between stages |
| Vertical | 60px between parallel nodes |

---

## Subflow Organization

### When to Create Subflow

- Same pattern used 3+ times
- Complex logic that should be abstracted
- Configurable automation component

### Subflow Naming

```
[Category] - [Function]
Lighting - Motion Timer
Notify - Smart Router
Climate - Hysteresis Controller
```

### Environment Variables

Define in subflow properties:

```json
{
  "env": [
    {
      "name": "TIMEOUT",
      "type": "num",
      "value": "300"
    },
    {
      "name": "ENTITY_ID",
      "type": "str",
      "value": ""
    }
  ]
}
```

---

## Configuration Patterns

### Config at Top

```
[comment: ⚙️ CONFIG] ← User updates here
         ↓
    [inject: Init]
         ↓
    [function: Set Config] → [context storage]
         ↓
    [... rest of flow ...]
```

### Function Node Config

```javascript
// === CONFIGURATION ===
const CONFIG = {
  // Update these values
  motionEntity: "binary_sensor.motion_CHANGE_ME",
  lightEntity: "light.living_room_CHANGE_ME",
  timeout: 300,          // seconds
  minBrightness: 20,     // percent
  maxBrightness: 100     // percent
};
// === END CONFIGURATION ===

// ... rest of code uses CONFIG object
```

### Input Number for Runtime Config

```javascript
const states = global.get("homeassistant").homeAssistant.states;
const timeout = parseFloat(states["input_number.motion_timeout"]?.state) || 300;
```

---

## Error Handling Layout

### Catch Node Placement

```
[Main Flow Nodes]
        ↓
[Catch] → [Error Handler] → [Notify/Log]
```

### Dedicated Error Tab

For complex flows:

```
[Tab: Error Handling]
├── [catch all: Flow 1] → [handler]
├── [catch all: Flow 2] → [handler]
└── [catch all: Flow 3] → [handler]
                              ↓
                         [unified logging]
                              ↓
                         [notification]
```

---

## Import/Export

### Selecting for Export

1. Select nodes (Ctrl+click or box select)
2. Ctrl+E to export
3. Copy JSON

### Tab Export

Right-click tab → Export → Selected Flow

### Clipboard vs Download

- Clipboard: Quick sharing
- Download: Backup/version control

---

## Version Control Integration

### Export Strategy

```
node-red-flows/
├── flows.json              # Full export (backup)
├── motion-lights.json      # Individual flow
├── presence.json
└── README.md
```

### Git Workflow

```bash
# Export flow
# Commit
git add flows/*.json
git commit -m "Update motion light timeout logic"
```

### Flow Diffs

JSON diffs are hard to read. Consider:
- Export with compact format
- Use node IDs that are meaningful
- Comment major changes

---

## Node-RED Projects (Git-Based Version Control)

Manual exports work, but Node-RED has a built-in alternative: Projects.
A project wraps your flows in a real git repository managed from the editor.

### Enabling Projects

Projects are off by default. Enable in `settings.js`, then restart Node-RED:

```javascript
editorTheme: {
    projects: {
        enabled: true
    }
}
```

On next start the editor walks you through creating or cloning a project.
Git must be installed on the host running Node-RED.

### What a Project Contains

Each project is its own directory under `~/.node-red/projects/<name>` with:

- `flow.json` - the flows for this project
- `flow_cred.json` - credentials, encrypted with a key you choose at setup
- `package.json` - project metadata and node dependencies
- `README.md` - shown on the project info panel

Switching projects switches the active flow file. The credentials encryption
key is stored outside the repo; without it the credentials file is useless to
anyone who clones the repo.

### Git Operations in the Editor

The history sidebar (Ctrl+Shift+H) exposes day-to-day git work:

- Stage and commit changed files with a message
- View local commit history and diffs between versions
- Create and switch branches
- Push/pull against a remote (GitHub, Gitea, GitLab) over HTTPS or SSH;
  SSH keys can be generated from the editor settings

Merge conflicts in flows are resolved through a visual diff tool rather than
raw JSON editing.

### Recommended Workflow for HA Users

1. One project per Node-RED instance (e.g. `ha-automations`); avoid juggling
   multiple projects on a production instance
2. Set a credentials encryption key at project creation and store it in your
   password manager; never disable encryption, since HA access tokens live in
   `flow_cred.json`
3. Commit after every working change: deploy, verify the flow behaves, then
   commit with a message like `Add hallway motion timeout`
4. Push to a private remote for off-host backup; the encrypted credentials
   file is safe to push, the key is not
5. Branch before risky rewires of core flows (presence, heating), merge after
   testing, delete the branch
6. Rolling back is then trivial: open history, check out the last good commit,
   deploy

### Projects vs Manual Export

| Aspect | Projects | Manual Export |
|--------|----------|---------------|
| Granularity | Commit per change | Snapshot when you remember |
| Credentials | Encrypted file in repo | Excluded entirely |
| Rollback | Editor history sidebar | Re-import old JSON |
| Setup cost | settings.js change + git | None |

---

## Documentation Standards

### Flow Documentation

Each tab should have:

1. **Info section** (in tab properties)
2. **Header comment** with overview
3. **Config section** with placeholders
4. **Section comments** for stages

### Example Documentation

```markdown
# Motion Lights Flow

## Purpose
Automatically control lights based on motion detection.

## Entities Required
- binary_sensor.motion_* - Motion sensors
- light.* - Lights to control
- sensor.*_lux - Optional lux sensors

## Configuration
1. Update entity IDs in Config function
2. Set timeout in input_number helper
3. Adjust brightness levels as needed

## Behavior
- Motion detected → Light on
- No motion for X seconds → Light off
- Respects manual override for 30 minutes
```

---

## Maintenance Tips

### Regular Cleanup

1. Remove disabled/unused nodes
2. Update outdated comments
3. Check for deprecated nodes
4. Review error logs

### Debugging Aids

```
[flow] → [debug: Always On] ← Keep for troubleshooting
           ↓
        [debug: Detailed] ← Enable when debugging
```

### Status Nodes

Show flow health:

```javascript
// In function node
node.status({
  fill: "green",
  shape: "dot",
  text: `Active: ${count} triggers today`
});
```

---

## Anti-Patterns

### ❌ Spaghetti Wires

Crossing, tangled wires → Use link nodes

### ❌ Giant Functions

500+ line function → Break into stages

### ❌ Magic Numbers

```javascript
if (lux < 50) // What does 50 mean?
```

→ Use named constants

### ❌ No Documentation

Returning to flow months later → Add comments

### ❌ Duplicate Logic

Same code in 5 functions → Create subflow

---

## Quick Reference

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Select All | Ctrl+A |
| Copy | Ctrl+C |
| Paste | Ctrl+V |
| Export | Ctrl+E |
| Import | Ctrl+I |
| Search | Ctrl+F |
| Deploy | Ctrl+D |
| Group | Ctrl+G |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |

### Node Arrangement

| Action | Shortcut |
|--------|----------|
| Align Left | A, L |
| Align Right | A, R |
| Align Top | A, T |
| Align Bottom | A, B |
| Distribute H | D, H |
| Distribute V | D, V |

