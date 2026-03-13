---
description: Create Home Assistant YAML automations, blueprints, scripts, scenes, template sensors, and dashboards
---

**Why ask first:** Home Assistant automations are highly specific to each user's setup — entity IDs,
naming conventions, automation vs blueprint choice, and UI vs YAML format all vary. Generating code
without this context wastes time and produces wrong results. Always clarify before generating.

## First Response

Ask these questions BEFORE generating any code:

1. **Type:** Automation, Blueprint, Script, or Scene?
2. **Format:** UI editor or YAML files?
3. **Entities:** Which specific entity IDs? (e.g., light.living_room)
4. **Options:** Brightness? Conditions? Timing?

**Example correct response:**
> I'll help you create a sunset light automation. Let me clarify:
> 1. Automation or Blueprint?
> 2. UI editor or YAML file?
> 3. Which lights? (entity IDs)
> 4. Any brightness or conditions?

THEN STOP. Wait for answers.

---

**What this does:**
- Creates automations, scripts, scenes, blueprints
- Uses modern HA 2024.8+ syntax: `action:` (not `service:`), plural keys (`triggers:`, `conditions:`, `actions:`)
- Avoids deprecated patterns: `service_template`, `data_template`, `platform: template` sensors
