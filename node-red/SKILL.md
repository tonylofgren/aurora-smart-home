---
name: node-red
description: Use when building Node-RED flows for Home Assistant automation. Triggers on "Node-RED", "flow", "visual automation", or node-red-contrib-home-assistant-websocket nodes.
---

# Node-RED for Home Assistant

Build Node-RED flows using node-red-contrib-home-assistant-websocket nodes.

## Critical: Node Names Have Changed

**STOP.** If you're about to use any of these node types, you're using outdated names:

| WRONG (Old) | CORRECT (Current) |
|-------------|-------------------|
| `server-state-changed` | `trigger-state` or `events:state` |
| `poll-state` | `poll-state` (unchanged but check config) |
| `call-service` | `api-call-service` |

## Trigger Node Configuration (Current API)

```json
{
  "type": "trigger-state",
  "entityId": "binary_sensor.motion",
  "entityIdType": "exact",
  "constraints": [
    {
      "targetType": "this_entity",
      "propertyType": "current_state",
      "comparatorType": "is",
      "comparatorValue": "on"
    }
  ],
  "outputs": 2
}
```

**entityIdType options:** `exact`, `substring`, `regex`

**There is NO `list` type.** To monitor multiple entities, use `regex`:
```json
"entityId": "binary_sensor\\.motion_(1|2|3)",
"entityIdType": "regex"
```

## Service Call Configuration (Current API)

```json
{
  "type": "api-call-service",
  "domain": "light",
  "service": "turn_on",
  "entityId": ["light.living_room"],
  "data": "",
  "dataType": "json"
}
```

Or dynamic via msg:
```json
{
  "type": "api-call-service",
  "domain": "",
  "service": "",
  "data": "",
  "dataType": "msg"
}
```

With function node before:
```javascript
msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.living_room"] },
  data: { brightness_pct: 80 }
};
return msg;
```

## Current State Node - Single Entity Only

`api-current-state` queries **ONE entity**, not patterns.

```json
{
  "type": "api-current-state",
  "entity_id": "person.john"
}
```

To check multiple entities, use function node:
```javascript
const ha = global.get("homeassistant").homeAssistant.states;
const people = Object.keys(ha)
  .filter(id => id.startsWith("person."))
  .filter(id => ha[id].state !== "home");
msg.awayPeople = people;
return msg;
```

## Entity Nodes Require Extra Integration

The following nodes require `hass-node-red` integration (separate from the websocket nodes):
- `ha-entity` (sensor, binary_sensor, switch, etc.)
- Entity config nodes

**Always mention this prerequisite when using entity nodes.**

## Timer Pattern (Motion Light)

Use single trigger node with `extend: true`:

```json
{
  "type": "trigger",
  "op1type": "nul",
  "op2": "timeout",
  "op2type": "str",
  "duration": "5",
  "extend": true,
  "units": "min"
}
```

**Do NOT create separate reset/start timer nodes.** The `extend` property handles this.

## Flow JSON Guidelines

1. **Never include server config node** - User configures separately
2. **Leave `server` field empty** - User selects their server
3. **Use placeholder entity IDs** - Document what to change
4. **Add comment node** - Explain required configuration

## Common Mistakes Table

| Mistake | Reality |
|---------|---------|
| Using `server-state-changed` | Node renamed to `trigger-state` |
| `entityIdType: "list"` | No such type. Use `regex` for multiple entities |
| `api-current-state` with pattern | Only accepts single entity_id |
| Using `ha-entity` without warning | Requires separate hass-node-red integration |
| Complex timer reset logic | Use `extend: true` on trigger node |
| `dataType: "jsonata"` for service data | Use `msg` when passing dynamic payload |

## Pre-Output Checklist

Before outputting flow JSON:

- [ ] Using current node type names?
- [ ] Entity filtering uses valid type (exact/substring/regex)?
- [ ] Service call has domain/service OR uses msg payload correctly?
- [ ] Single entity nodes don't assume pattern matching?
- [ ] Entity nodes mention hass-node-red requirement?
- [ ] Server field left empty for user configuration?
