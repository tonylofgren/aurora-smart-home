---
description: Create Node-RED visual automation flows with trigger-state, function nodes, and HA websocket integration
---

**Why ask first:** Node-RED flows depend on which HA entities are involved, what triggers the flow,
and what conditions apply. Node type names have changed (e.g. trigger-state, api-call-service) and
entity nodes need extra integration. Always clarify before generating.

## First Response

Ask these questions BEFORE generating any code:

1. **Trigger:** What starts the flow? (state change, time, webhook, etc.)
2. **Entities:** Which Home Assistant entity IDs?
3. **Actions:** What should happen? (turn on lights, send notification, etc.)
4. **Conditions:** Any filtering? (only at night, only when home, etc.)

**Example correct response:**
> I'll help you create a Node-RED flow. Let me clarify:
> 1. What triggers the flow?
> 2. Which HA entities are involved?
> 3. What actions should occur?
> 4. Any conditions to check?

THEN STOP. Wait for answers.

---

**What this does:**
- Uses node-red-contrib-home-assistant-websocket v0.80+ nodes
- Generates importable JSON flows for Node-RED 4.x (Node.js 18+)
- Follows current API (trigger-state, api-call-service, number, select, text, time-entity)
- Avoids deprecated state type config (use entity state casting)
