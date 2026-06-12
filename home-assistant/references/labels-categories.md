# Home Assistant Labels and Categories Reference

**Source:** https://www.home-assistant.io/docs/organizing/labels/ and https://www.home-assistant.io/docs/organizing/categories/

## Table of Contents
- [Core Concepts](#core-concepts)
- [Labels vs Areas, Floors, and Groups](#labels-vs-areas-floors-and-groups)
- [Creating and Assigning Labels](#creating-and-assigning-labels)
- [Targeting Labels in Actions](#targeting-labels-in-actions)
- [Label Template Functions](#label-template-functions)
- [Categories](#categories)
- [Practical Recipes](#practical-recipes)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Labels are free-form tags you attach to things in Home Assistant. One label can be attached to many objects, and one object can carry many labels. They cut across the physical layout of your home: a label like `holiday-lights` can cover a lamp in the living room, a plug in the hallway, and an automation, all at once.

Labels can be assigned to:

| Object | Example use |
|--------|-------------|
| Entities | `battery-check` on every battery sensor |
| Devices | `flaky-wifi` on devices that drop offline |
| Areas | `upstairs` across several rooms |
| Automations | `vacation` on everything that should run while away |
| Scripts | `maintenance` on cleanup scripts |
| Helpers | `dashboard` on helpers shown in the UI |

Categories are different: they only organize the settings tables for automations, scripts, scenes, and helpers. A category like "Lighting" or "Security" groups rows in Settings > Automations & Scenes so a long list stays manageable. Categories are per-table, UI-only, and cannot be targeted from YAML or templates.

### Quick decision guide

```text
Need to act on a set of things from an automation?      → Label
Need to group rows in the automations/scripts table?    → Category
Need a physical room for voice and area cards?          → Area
Need one entity that aggregates on/off state?           → Group helper
```

---

## Labels vs Areas, Floors, and Groups

| Feature | Label | Area | Floor | Group helper |
|---------|-------|------|-------|--------------|
| Object types | Entities, devices, areas, automations, scripts, helpers | Devices, entities | Areas | Entities of one domain |
| Multiple per object | Yes | No (one area per device/entity) | No (one floor per area) | Yes |
| Usable in `target:` | Yes (`label_id`) | Yes (`area_id`) | Yes (`floor_id`) | Yes (as entity) |
| Has its own state | No | No | No | Yes (on/off, etc.) |
| Voice assistant aware | No | Yes | Yes | Yes |
| Purpose | Cross-cutting tags | Physical location | Building level | Aggregated state |

Key consequences:

- A label has no state. You cannot write a state trigger on a label. To react to "any entity with label X", expand the label in a template.
- An entity lives in exactly one area, but can carry any number of labels. Use labels when a thing belongs to several logical sets at once.
- Group helpers give you a single entity with an aggregate state. Labels give you a targeting set without creating an entity.

---

## Creating and Assigning Labels

Labels are created and assigned in the UI; there is no YAML schema for defining them.

- Manage labels: Settings > Areas, labels & zones > Labels tab.
- Assign to an entity: open the entity > settings (gear) > Labels.
- Assign in bulk: Settings > Devices & Services > Entities, select multiple rows, then "Add label" from the selection toolbar.
- Assign to an automation: open the automation, top-right menu > Labels.

Each label has a name, an optional icon, an optional color, and an internal `label_id`. The id is the slugified name at creation time (`Holiday Lights` becomes `holiday_lights`) and does not change if you later rename the label. Check the real id under Settings > Areas, labels & zones, or with `label_id('Holiday Lights')` in the template editor.

---

## Targeting Labels in Actions

`target:` accepts `label_id` anywhere it accepts `entity_id`, `device_id`, `area_id`, or `floor_id`. The action runs on every matching entity that carries the label, plus all entities of labeled devices and areas.

```yaml
actions:
  - action: light.turn_off
    target:
      label_id: holiday_lights
```

Multiple labels and mixed targets work too:

```yaml
actions:
  - action: homeassistant.turn_off
    target:
      label_id:
        - holiday_lights
        - window_candles
      entity_id: switch.front_door_star
```

Note that the action still only affects entities its domain supports. `light.turn_off` with a label that also covers switches will skip the switches; use `homeassistant.turn_off` for mixed domains.

---

## Label Template Functions

| Function | Returns |
|----------|---------|
| `labels()` | All label ids in the system |
| `labels(entity_id)` | Label ids attached to that entity (also accepts a device id or area id) |
| `label_id(name)` | Label id for a label name |
| `label_name(id)` | Label name for a label id |
| `label_entities(label)` | Entity ids carrying the label |
| `label_devices(label)` | Device ids carrying the label |
| `label_areas(label)` | Area ids carrying the label |

All of these are also available as filters (`'holiday_lights' | label_entities`). The lookup functions accept either the label name or the label id.

```jinja2
# All entities labeled battery-check that are below 20 percent
{{ label_entities('battery_check')
   | select('is_state_attr', 'device_class', 'battery')
   | map('states') | map('int', 999)
   | select('lt', 20) | list }}

# Does this entity carry the maintenance label?
{{ 'maintenance' in labels('sensor.garage_door') }}

# How many lights are labeled holiday_lights?
{{ label_entities('holiday_lights') | select('match', 'light\.') | list | count }}
```

`label_entities()` only returns entities labeled directly. It does not expand devices or areas that carry the label; combine with `label_devices()` and `device_entities()` if you need full expansion in a template. Action targets with `label_id` do expand devices and areas for you.

---

## Categories

Categories keep long automation and script lists readable. They exist per table: a category created for automations does not appear for scripts.

- Create or assign: Settings > Automations & Scenes > select rows > "Move to category", or via the three-dot menu on a single row.
- Filter the table by category using the filter button at the top.
- Categories support a name and an icon, nothing else.

Limitations worth knowing:

- Not available in `target:`, templates, or any YAML.
- One category per automation per table (unlike labels).
- They do not affect execution, tracing, or the entity registry in any way.

Use categories for browsing ("show me my security automations") and labels for behavior ("disable everything labeled vacation").

---

## Practical Recipes

### Turn off everything labeled holiday-lights

One automation covers every decoration you will ever add. Adding a new plug to the set is one label assignment, no YAML edit.

```yaml
automation:
  - alias: "Holiday lights off at night"
    triggers:
      - trigger: time
        at: "23:30:00"
    actions:
      - action: homeassistant.turn_off
        target:
          label_id: holiday_lights
```

### Maintenance label that mutes notifications

Label a device `maintenance` while you work on it, and notification automations skip it. Remove the label when done.

```yaml
automation:
  - alias: "Notify when door sensor goes offline"
    triggers:
      - trigger: state
        entity_id: binary_sensor.front_door
        to: "unavailable"
        for: "00:05:00"
    conditions:
      - condition: template
        value_template: "{{ 'maintenance' not in labels(trigger.entity_id) }}"
    actions:
      - action: notify.mobile_app_phone
        data:
          message: "Front door sensor has been offline for 5 minutes."
```

### Weekly low-battery report from a label

Label every battery entity `battery_check` once, then iterate the label in a template.

```yaml
automation:
  - alias: "Sunday battery report"
    triggers:
      - trigger: time
        at: "09:00:00"
    conditions:
      - condition: time
        weekday:
          - sun
    actions:
      - action: notify.mobile_app_phone
        data:
          title: "Battery report"
          message: >
            {% set low = label_entities('battery_check')
               | select('has_value')
               | rejectattr('entity_id', 'in', label_entities('maintenance'))
               | map('states') | map('int', 100) | select('lt', 25) | list %}
            {% if low | count == 0 %}
              All batteries above 25 percent.
            {% else %}
              {{ low | count }} batteries need attention.
            {% endif %}
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `label_id` target does nothing | Label id does not match (renamed label keeps original id) | Verify with `label_id('Name')` in the template editor |
| Action skips some labeled entities | Domain-specific action used on mixed domains | Use `homeassistant.turn_on` / `turn_off`, or split per domain |
| `label_entities()` misses entities | Label sits on the device or area, not the entity | Label the entities directly, or expand devices in the template |
| Template errors on `labels(trigger.entity_id)` | Trigger has no entity (time trigger, event trigger) | Guard with `{% if trigger.entity_id is defined %}` |
| Cannot find categories for scripts | Categories are per table | Create the category again in the scripts table |
| Label missing from voice commands | Labels are not exposed to assistants | Use areas or expose entities individually |

If a label-targeted action behaves unexpectedly, open the automation trace: the resolved entity list for the action step shows exactly which entities the label expanded to at run time.
