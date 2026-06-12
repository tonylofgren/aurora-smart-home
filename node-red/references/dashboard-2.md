# Node-RED Dashboard 2.0

Build web UIs from Node-RED flows with @flowfuse/node-red-dashboard.

**Source:** https://dashboard.flowfuse.com/

## Why Dashboard 2.0 Exists

The original `node-red-dashboard` package was built on AngularJS, which Google
stopped supporting at the end of 2021. With its framework dead, the old
dashboard entered maintenance-only mode and was formally deprecated. FlowFuse
built Dashboard 2.0 as the successor, rewritten on Vue 3 and Vuetify, and it
is the actively maintained option today.

Key differences from Dashboard 1:

- Vue 3 component model instead of AngularJS
- Different node set (`ui-button` etc. instead of `ui_button`)
- Layout is driven by config nodes: `ui-base`, `ui-page`, `ui-group`, `ui-theme`
- Custom widgets are written as Vue templates, not Angular directives
- Both packages can be installed side by side during migration; they serve
  separate UIs on different paths

## When to Use It with Home Assistant

For day-to-day household dashboards, the HA frontend (Lovelace) is usually the
better choice: it is entity-aware, mobile-app friendly, and lives where the
rest of your HA UI lives. Dashboard 2.0 earns its place for:

- Kiosk and wall-panel displays driven directly by flows
- Operations panels for the Node-RED instance itself (flow status, queues,
  manual override buttons)
- UIs that mix HA data with non-HA sources already flowing through Node-RED
- Quick internal tools where you do not want to touch HA configuration

Rule of thumb: primary home UI in Lovelace, flow-centric or kiosk panels in
Dashboard 2.0.

## Installation

Via the editor palette:

1. Menu > Manage palette > Install tab
2. Search for `@flowfuse/node-red-dashboard`
3. Install, then the `dashboard 2` category appears in the palette

Via npm in the Node-RED user directory (`~/.node-red`):

```bash
npm install @flowfuse/node-red-dashboard
```

The UI is served at `http://<node-red-host>:1880/dashboard` by default.

## Core UI Nodes

| Node | Purpose |
|------|---------|
| `ui-button` | Clickable button, emits a msg on press |
| `ui-text` | Display a read-only value with a label |
| `ui-text-input` | Free text entry from the user |
| `ui-dropdown` | Select from a list of options |
| `ui-switch` | On/off toggle, in and out |
| `ui-slider` | Numeric input on a range |
| `ui-chart` | Line, bar, or scatter plots of incoming values |
| `ui-gauge` | Radial or linear gauge for a single value |
| `ui-notification` | Popup toast messages |
| `ui-template` | Custom widget written as a Vue template |
| `ui-markdown` | Render markdown content |
| `ui-event` | Emits events about client connections and page views |
| `ui-control` | Programmatic navigation and show/hide of UI parts |

`ui-template` is the escape hatch: you write Vue 3 template markup (with
access to incoming `msg` data) for anything the stock widgets cannot do.

## Layout Concepts

Dashboard 2.0 uses a hierarchy of config nodes:

- **Base** (`ui-base`): one per dashboard, sets the URL path
- **Page** (`ui-page`): a browser page within the base; each page picks a
  layout style (grid, fixed, notebook)
- **Group** (`ui-group`): a card on a page that holds widgets; widgets are
  ordered and sized in units of grid columns
- **Theme** (`ui-theme`): colors and sizing shared by pages

Every widget node points at a group, the group points at a page, and the page
points at the base. Create these once in the edit dialog of your first widget
and reuse them for the rest.

## Example: HA Sensor Panel

Goal: show a live temperature from Home Assistant as a gauge plus a history
chart. Node-by-node configuration (wire them in this order):

1. **`server-state-changed` (events: state)**
   - Entity: `sensor.living_room_temperature`
   - Output only on state change, state type `number`
   - This node comes from node-red-contrib-home-assistant-websocket, see
     `node-reference.md`
2. **`ui-gauge`**
   - Group: `Climate` (create page `Home` and base `/dashboard` when prompted)
   - Type: gauge, range 10 to 35, label `Living room`, units `C`
   - Input: the msg payload from the state node is the gauge value
3. **`ui-chart`** (wired in parallel from the same state node)
   - Group: `Climate`
   - Type: line, x-axis: timestamp, series: single
   - Set a point limit or time window so the in-memory dataset stays bounded

Optional: add a `ui-button` labeled `Refresh` wired to an
`api-current-state` node for the same entity, with its output wired into the
gauge and chart, so a manual press repaints the panel immediately.

This pattern (HA event node feeding `ui-*` widgets) generalizes to any sensor:
energy meters, presence counts, queue depths.

## Migrating from Dashboard 1

There is no automatic converter; plan a manual migration:

- Install Dashboard 2.0 alongside the old package; the two UIs do not clash
- Rebuild each tab as a `ui-page`, each old group as a `ui-group`
- Most widgets have a direct counterpart (`ui_gauge` to `ui-gauge`, etc.);
  rewire your existing msg sources to the new nodes
- `ui_template` widgets need a rewrite from Angular syntax to Vue templates;
  budget most of your migration time here
- `ui_control` behavior moved to the `ui-control` and `ui-event` nodes
- When a page is fully rebuilt, delete the Dashboard 1 tab, and remove
  `node-red-dashboard` entirely once nothing references it

## Quick Checklist

- [ ] Installed `@flowfuse/node-red-dashboard`, not the deprecated package?
- [ ] Base, page, group, and theme config nodes created and linked?
- [ ] Charts bounded by point count or time window?
- [ ] Considered whether the panel belongs in Lovelace instead?
