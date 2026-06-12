# Home Assistant Conditions Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [State Condition](#state-condition)
- [Numeric State Condition](#numeric-state-condition)
- [Time Condition](#time-condition)
- [Sun Condition](#sun-condition)
- [Zone Condition](#zone-condition)
- [Template Condition](#template-condition)
- [Device Condition](#device-condition)
- [Device-Specific Conditions](#device-specific-conditions)
- [Trigger Condition](#trigger-condition)
- [Logical Conditions](#logical-conditions)
- [Shorthand Conditions](#shorthand-conditions)
- [Common Patterns](#common-patterns)
- [Selection Guide](#selection-guide)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Conditions determine whether an automation's actions should run. If any condition evaluates to false, the actions are skipped.

### Key Terms

| Term | Description |
|------|-------------|
| **Condition** | Check that must pass for actions to run |
| **And** | All conditions must be true |
| **Or** | At least one condition must be true |
| **Not** | Inverts the condition result |
| **Shorthand** | Simplified condition syntax |

### Condition Evaluation

```yaml
# Conditions are evaluated in order
# All must pass for actions to run (implicit AND)
conditions:
  - condition: state
    entity_id: input_boolean.enabled
    state: "on"
  - condition: time
    after: "08:00:00"
    before: "22:00:00"
  # Both must be true
```

### Condition Location

```yaml
automation:
  - id: example
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
    conditions:
      # Conditions go here
      - condition: state
        entity_id: input_boolean.enabled
        state: "on"
    actions:
      # Actions only run if conditions pass
      - action: light.turn_on
```

---

## State Condition

Check if an entity is in a specific state.

### Basic State Condition

```yaml
conditions:
  - condition: state
    entity_id: light.living_room
    state: "on"
```

### Multiple States (OR)

```yaml
# Entity can be in any of these states
conditions:
  - condition: state
    entity_id: vacuum.robot
    state:
      - cleaning
      - returning
```

### Multiple Entities (AND)

```yaml
# All entities must be in specified state
conditions:
  - condition: state
    entity_id:
      - light.living_room
      - light.kitchen
    state: "off"
```

### State with Duration (for)

```yaml
# Entity must have been in state for duration
conditions:
  - condition: state
    entity_id: binary_sensor.motion
    state: "off"
    for: "00:10:00"

# With dynamic duration
conditions:
  - condition: state
    entity_id: binary_sensor.motion
    state: "off"
    for:
      minutes: "{{ states('input_number.timeout') | int }}"
```

### Attribute Check

```yaml
# Check entity attribute instead of state
conditions:
  - condition: state
    entity_id: light.living_room
    attribute: brightness
    state: 255

# Multiple attribute values
conditions:
  - condition: state
    entity_id: climate.thermostat
    attribute: hvac_action
    state:
      - heating
      - cooling
```

### Not Equal

```yaml
# Wrap a state condition in 'not' to express "must not be in this state"
conditions:
  - condition: not
    conditions:
      - condition: state
        entity_id: alarm_control_panel.home
        state: disarmed
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `entity_id` | string/list | Entity or list of entities |
| `state` | string/list | Expected state(s) |
| `attribute` | string | Attribute to check (optional) |
| `for` | time | Minimum duration in state |
| `match` | string | `all` (default) requires all entities to match; `any` requires at least one |

---

## Numeric State Condition

Check if a numeric value is above or below thresholds.

### Basic Numeric Condition

```yaml
# Value above threshold
conditions:
  - condition: numeric_state
    entity_id: sensor.temperature
    above: 25

# Value below threshold
conditions:
  - condition: numeric_state
    entity_id: sensor.temperature
    below: 18

# Value in range
conditions:
  - condition: numeric_state
    entity_id: sensor.humidity
    above: 30
    below: 70
```

### With Attribute

```yaml
# Check attribute value
conditions:
  - condition: numeric_state
    entity_id: light.living_room
    attribute: brightness
    above: 100
```

### Template Threshold

```yaml
# Dynamic threshold from helper
conditions:
  - condition: numeric_state
    entity_id: sensor.battery
    below: "{{ states('input_number.low_battery_threshold') | int }}"
```

### Value Template

```yaml
# Apply template to entity value before comparison
conditions:
  - condition: numeric_state
    entity_id: sensor.data
    value_template: "{{ state.state | float * 1.8 + 32 }}"
    above: 77  # Compare converted value
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `entity_id` | string/list | Entity to check |
| `above` | number/template | Minimum value (exclusive) |
| `below` | number/template | Maximum value (exclusive) |
| `attribute` | string | Attribute to check |
| `value_template` | template | Transform value before comparison |

---

## Time Condition

Check if current time is within a range.

### Basic Time Range

```yaml
# Between 8 AM and 10 PM
conditions:
  - condition: time
    after: "08:00:00"
    before: "22:00:00"
```

### Weekday Filter

```yaml
# Only on weekdays
conditions:
  - condition: time
    weekday:
      - mon
      - tue
      - wed
      - thu
      - fri

# Only on weekends
conditions:
  - condition: time
    weekday:
      - sat
      - sun
```

### Combined Time and Weekday

```yaml
# Weekdays between 7 AM and 9 AM
conditions:
  - condition: time
    after: "07:00:00"
    before: "09:00:00"
    weekday:
      - mon
      - tue
      - wed
      - thu
      - fri
```

### Input Datetime as Time

```yaml
# Use input_datetime helper
conditions:
  - condition: time
    after: input_datetime.quiet_hours_start
    before: input_datetime.quiet_hours_end
```

### Crossing Midnight

```yaml
# For times crossing midnight, use template
conditions:
  - condition: template
    value_template: >
      {% set now_time = now().strftime('%H:%M:%S') %}
      {{ now_time >= '22:00:00' or now_time < '06:00:00' }}

# Or use two conditions with OR
conditions:
  - condition: or
    conditions:
      - condition: time
        after: "22:00:00"
      - condition: time
        before: "06:00:00"
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `after` | time/input_datetime | Start time (inclusive) |
| `before` | time/input_datetime | End time (exclusive) |
| `weekday` | list | Days of week (mon, tue, wed, thu, fri, sat, sun) |

---

## Sun Condition

Check position relative to sunrise/sunset.

### Basic Sun Condition

```yaml
# After sunset
conditions:
  - condition: sun
    after: sunset

# Before sunrise
conditions:
  - condition: sun
    before: sunrise

# Between sunset and sunrise (nighttime)
conditions:
  - condition: sun
    after: sunset
    before: sunrise
```

### With Offset

```yaml
# 30 minutes after sunset
conditions:
  - condition: sun
    after: sunset
    after_offset: "00:30:00"

# 1 hour before sunset
conditions:
  - condition: sun
    before: sunset
    before_offset: "-01:00:00"

# Golden hour (1 hour before sunset)
conditions:
  - condition: sun
    after: sunset
    after_offset: "-01:00:00"
    before: sunset
```

### Combined Example

```yaml
# Evening: after sunset but before midnight
conditions:
  - condition: and
    conditions:
      - condition: sun
        after: sunset
      - condition: time
        before: "23:59:59"
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `after` | string | `sunrise` or `sunset` |
| `after_offset` | time | Offset from after time |
| `before` | string | `sunrise` or `sunset` |
| `before_offset` | time | Offset from before time |

---

## Zone Condition

Check if a person/device tracker is in a zone.

### Basic Zone Condition

```yaml
# Person is home
conditions:
  - condition: zone
    entity_id: person.john
    zone: zone.home

# Device tracker in zone
conditions:
  - condition: zone
    entity_id: device_tracker.phone
    zone: zone.work
```

### Multiple Entities

```yaml
# All family members home
conditions:
  - condition: zone
    entity_id:
      - person.john
      - person.jane
    zone: zone.home
```

### Any Person in Zone

```yaml
# At least one person in zone
conditions:
  - condition: or
    conditions:
      - condition: zone
        entity_id: person.john
        zone: zone.home
      - condition: zone
        entity_id: person.jane
        zone: zone.home
```

### Not in Zone

```yaml
# Person is not home
conditions:
  - condition: not
    conditions:
      - condition: zone
        entity_id: person.john
        zone: zone.home
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `entity_id` | string/list | Person or device_tracker entity |
| `zone` | string | Zone entity (zone.home, zone.work, etc.) |

---

## Template Condition

Use Jinja2 templates for complex conditions.

### Basic Template

```yaml
# Simple comparison
conditions:
  - condition: template
    value_template: "{{ states('sensor.temperature') | float > 25 }}"
```

### Complex Logic

```yaml
# Multiple conditions in template
conditions:
  - condition: template
    value_template: >
      {{ is_state('binary_sensor.motion', 'on') and
         is_state('input_boolean.enabled', 'on') and
         states('sensor.illuminance') | float < 50 }}
```

### Using Trigger Variables

```yaml
# Access trigger data in condition
conditions:
  - condition: template
    value_template: >
      {{ trigger.to_state.state != trigger.from_state.state }}
```

### Attribute Comparisons

```yaml
# Compare attributes
conditions:
  - condition: template
    value_template: >
      {{ state_attr('climate.thermostat', 'current_temperature') | float >
         state_attr('climate.thermostat', 'temperature') | float }}
```

### Time-Based Logic

```yaml
# Complex time conditions
conditions:
  - condition: template
    value_template: >
      {% set hour = now().hour %}
      {% set is_weekday = now().weekday() < 5 %}
      {{ (is_weekday and 7 <= hour < 22) or
         (not is_weekday and 9 <= hour < 23) }}
```

### Entity Availability

```yaml
# Check entity is available
conditions:
  - condition: template
    value_template: >
      {{ states('sensor.temperature') not in ['unknown', 'unavailable'] }}
```

### Last Changed

```yaml
# Entity changed recently
conditions:
  - condition: template
    value_template: >
      {{ (now() - states.binary_sensor.motion.last_changed).total_seconds() < 300 }}
```

### Count Matching Entities

```yaml
# At least 2 lights on
conditions:
  - condition: template
    value_template: >
      {{ states.light | selectattr('state', 'eq', 'on') | list | count >= 2 }}
```

---

## Device Condition

Check device-specific conditions.

### Basic Device Condition

```yaml
# Device is on
conditions:
  - condition: device
    device_id: abc123def456
    domain: light
    type: is_on
```

### Battery Level

```yaml
# Battery above threshold
conditions:
  - condition: device
    device_id: abc123def456
    domain: sensor
    type: is_battery_level
    above: 20
```

### Common Device Types

```yaml
# Light is on
conditions:
  - condition: device
    device_id: abc123def456
    domain: light
    type: is_on

# Switch is off
conditions:
  - condition: device
    device_id: abc123def456
    domain: switch
    type: is_off

# Binary sensor is on
conditions:
  - condition: device
    device_id: abc123def456
    domain: binary_sensor
    type: is_on
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `device_id` | string | Device ID |
| `domain` | string | Entity domain |
| `type` | string | Condition type |
| `entity_id` | string | Entity (if device has multiple) |
| `above` / `below` | number | For numeric conditions |

---

## Device-Specific Conditions

**Source:** https://www.home-assistant.io/docs/scripts/conditions/

Home Assistant exposes domain-specific condition types through the same `condition: device` framework. Each installed integration registers its own `type` values. The full list visible in the UI depends on which integrations are loaded; the groups below cover the most common ones.

All device-specific conditions follow this structure:

```yaml
conditions:
  - condition: device
    device_id: abc123def456
    domain: light
    type: is_on
```

### Binary State Conditions

These check a simple on/off, open/closed, or locked/unlocked state.

| Domain | Types |
|--------|-------|
| `light` | `is_on`, `is_off` |
| `switch` | `is_on`, `is_off` |
| `fan` | `is_on`, `is_off` |
| `siren` | `is_on`, `is_off` |
| `door` | `is_open`, `is_closed` |
| `window` | `is_open`, `is_closed` |
| `garage_door` | `is_open`, `is_closed` |
| `gate` | `is_open`, `is_closed` |
| `lock` | `is_locked`, `is_unlocked`, `is_open`, `is_jammed` |
| `motion` | `is_detected`, `is_not_detected` |
| `binary_sensor` | `is_on`, `is_off` |

Example - check that a door is closed before locking:

```yaml
conditions:
  - condition: device
    device_id: abc123def456
    domain: door
    type: is_closed
```

Example - lock is not jammed:

```yaml
conditions:
  - condition: device
    device_id: abc123def456
    domain: lock
    type: is_locked
```

### Alarm Control Panel Conditions

```yaml
conditions:
  - condition: device
    device_id: abc123def456
    domain: alarm_control_panel
    type: is_disarmed
```

Available types: `is_armed`, `is_armed_away`, `is_armed_home`, `is_armed_night`, `is_armed_vacation`, `is_disarmed`, `is_triggered`.

### Climate and Humidifier Conditions

```yaml
conditions:
  - condition: device
    device_id: abc123def456
    domain: climate
    type: is_heating
```

Climate types: `is_on`, `is_off`, `is_heating`, `is_cooling`, `is_drying`, `is_hvac_mode`, `target_temperature`, `target_humidity`.

Humidifier types: `is_on`, `is_off`, `is_humidifying`, `is_drying`, `is_mode`, `is_target_humidity`.

### Numeric and Threshold Conditions

These require `above` and/or `below` fields in addition to `type`.

```yaml
# Battery level above 20 percent
conditions:
  - condition: device
    device_id: abc123def456
    domain: sensor
    type: is_battery_level
    above: 20

# Temperature sensor below threshold
conditions:
  - condition: device
    device_id: abc123def456
    domain: temperature
    type: is_value
    below: 25
```

Domains with numeric types include: `temperature` (`is_value`), `humidity` (`is_value`), `counter` (`is_value`), `light` (`is_brightness`), `air_quality` (various `is_*_value` types for CO2, PM2.5, VOC, etc.).

### Mobile Robot Conditions

```yaml
# Vacuum is docked (ready to start)
conditions:
  - condition: device
    device_id: abc123def456
    domain: vacuum
    type: is_docked

# Lawn mower is mowing
conditions:
  - condition: device
    device_id: abc123def456
    domain: lawn_mower
    type: is_mowing
```

Vacuum types: `is_cleaning`, `is_docked`, `is_paused`, `is_returning`, `is_encountering_an_error`.

Lawn mower types: `is_mowing`, `is_docked`, `is_paused`, `is_returning`, `is_encountering_an_error`.

### Timer Conditions

Check whether a timer helper is running, idle, or paused.

```yaml
# Cooldown timer has expired (idle means not running)
conditions:
  - condition: device
    device_id: abc123def456
    domain: timer
    type: is_idle
```

Timer types: `is_active`, `is_idle`, `is_paused`.

### Calendar Condition

The `calendar.is_event_active` type checks whether a calendar event is currently active (the calendar entity reads `"on"` while an event is in progress).

```yaml
conditions:
  - condition: device
    device_id: abc123def456
    domain: calendar
    type: is_event_active
```

Alternatively, a calendar entity can be tested with a plain state condition since it exposes `"on"` during an active event and `"off"` otherwise:

```yaml
conditions:
  - condition: state
    entity_id: calendar.my_calendar
    state: "on"
```

### Update and To-do Conditions

```yaml
# A software update is available for a device
conditions:
  - condition: device
    device_id: abc123def456
    domain: update
    type: is_available

# All to-do items are completed
conditions:
  - condition: device
    device_id: abc123def456
    domain: todo
    type: all_completed
```

Update types: `is_available`, `is_not_available`.
To-do types: `all_completed`, `incomplete`.

---

## Trigger Condition

Check which trigger fired the automation.

### Basic Trigger Condition

```yaml
automation:
  - id: multi_trigger
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion_living
        to: "on"
        id: living_room
      - trigger: state
        entity_id: binary_sensor.motion_kitchen
        to: "on"
        id: kitchen
    conditions:
      - condition: trigger
        id: living_room
    actions:
      # Only runs for living room trigger
```

### Multiple Trigger IDs

```yaml
conditions:
  - condition: trigger
    id:
      - morning_trigger
      - evening_trigger
```

### In Choose Block

```yaml
actions:
  - choose:
      - conditions:
          - condition: trigger
            id: motion_detected
        sequence:
          - action: light.turn_on
      - conditions:
          - condition: trigger
            id: motion_cleared
        sequence:
          - action: light.turn_off
```

---

## Logical Conditions

Combine conditions with AND, OR, NOT logic.

### AND Condition

```yaml
# All conditions must be true (explicit)
conditions:
  - condition: and
    conditions:
      - condition: state
        entity_id: input_boolean.enabled
        state: "on"
      - condition: time
        after: "08:00:00"
        before: "22:00:00"
      - condition: numeric_state
        entity_id: sensor.temperature
        below: 25
```

### OR Condition

```yaml
# At least one condition must be true
conditions:
  - condition: or
    conditions:
      - condition: state
        entity_id: binary_sensor.motion_living
        state: "on"
      - condition: state
        entity_id: binary_sensor.motion_kitchen
        state: "on"
```

### NOT Condition

```yaml
# Inverts the condition result
conditions:
  - condition: not
    conditions:
      - condition: state
        entity_id: alarm_control_panel.home
        state: armed_away
```

### Nested Logic

```yaml
# Complex nested conditions
conditions:
  - condition: and
    conditions:
      # Must be enabled
      - condition: state
        entity_id: input_boolean.enabled
        state: "on"
      # AND either daytime OR motion detected
      - condition: or
        conditions:
          - condition: sun
            after: sunrise
            before: sunset
          - condition: state
            entity_id: binary_sensor.motion
            state: "on"
```

### Implicit AND

```yaml
# Multiple conditions at root level are implicitly ANDed
conditions:
  - condition: state
    entity_id: input_boolean.enabled
    state: "on"
  - condition: time
    after: "08:00:00"
# Both must be true
```

---

## Shorthand Conditions

Simplified syntax for common conditions.

### Shorthand State

```yaml
# Full syntax
conditions:
  - condition: state
    entity_id: light.living_room
    state: "on"

# Shorthand
conditions:
  - "{{ is_state('light.living_room', 'on') }}"
```

### Shorthand Numeric

```yaml
# Full syntax
conditions:
  - condition: numeric_state
    entity_id: sensor.temperature
    above: 25

# Shorthand
conditions:
  - "{{ states('sensor.temperature') | float > 25 }}"
```

### Shorthand OR

```yaml
# Full syntax
conditions:
  - condition: or
    conditions:
      - condition: state
        entity_id: light.a
        state: "on"
      - condition: state
        entity_id: light.b
        state: "on"

# Shorthand
conditions:
  - "{{ is_state('light.a', 'on') or is_state('light.b', 'on') }}"
```

### Mixed Syntax

```yaml
# Can mix full and shorthand
conditions:
  - condition: state
    entity_id: input_boolean.enabled
    state: "on"
  - "{{ now().hour >= 8 }}"
```

---

## Common Patterns

### Someone Home

```yaml
# At least one person home
conditions:
  - condition: not
    conditions:
      - condition: state
        entity_id: group.family
        state: not_home

# Or using zone
conditions:
  - condition: or
    conditions:
      - condition: zone
        entity_id: person.john
        zone: zone.home
      - condition: zone
        entity_id: person.jane
        zone: zone.home
```

### Nobody Home

```yaml
conditions:
  - condition: state
    entity_id: group.family
    state: not_home
```

### Dark Outside

```yaml
# After sunset
conditions:
  - condition: sun
    after: sunset
    before: sunrise

# Or low illuminance
conditions:
  - condition: numeric_state
    entity_id: sensor.outdoor_illuminance
    below: 50
```

### Quiet Hours

```yaml
# Using time condition
conditions:
  - condition: time
    after: "22:00:00"
    before: "07:00:00"

# Using input_datetime
conditions:
  - condition: time
    after: input_datetime.quiet_start
    before: input_datetime.quiet_end

# Using schedule helper
conditions:
  - condition: state
    entity_id: schedule.quiet_hours
    state: "on"
```

### Automation Not Recently Run

```yaml
conditions:
  - condition: template
    value_template: >
      {{ (now() - state_attr('automation.door_notification', 'last_triggered')).total_seconds() > 1800 }}
```

### Entity Available

```yaml
conditions:
  - condition: template
    value_template: >
      {{ states('sensor.temperature') not in ['unknown', 'unavailable', 'none'] }}
```

### Workday Check

```yaml
# Using workday integration
conditions:
  - condition: state
    entity_id: binary_sensor.workday
    state: "on"
```

### Rate Limiting

```yaml
# With counter
conditions:
  - condition: numeric_state
    entity_id: counter.daily_notifications
    below: 10

# With timer cooldown
conditions:
  - condition: state
    entity_id: timer.notification_cooldown
    state: "idle"
```

### Mode-Based Conditions

```yaml
# Check input_select mode
conditions:
  - condition: state
    entity_id: input_select.home_mode
    state:
      - Home
      - Guest

# Not in certain modes
conditions:
  - condition: not
    conditions:
      - condition: state
        entity_id: input_select.home_mode
        state:
          - Away
          - Vacation
```

---

## Selection Guide

**Source:** https://www.home-assistant.io/docs/scripts/conditions/

Use this table to pick the right condition type for the job.

| What you want to check | Condition to use |
|------------------------|-----------------|
| Entity is in a specific state | `state` |
| Numeric value is above, below, or in a range | `numeric_state` |
| After sunset or before sunrise (coarse) | `sun` |
| Precise outdoor darkness (elevation degrees) | `numeric_state` on `sun.sun` attribute `elevation` |
| Time of day or specific weekdays | `time` |
| Only when a particular trigger fired | `trigger` |
| Person or device tracker is inside a zone | `zone` |
| Domain-specific device capability (is_heating, is_docked, etc.) | `device` with domain + type |
| Calendar event is currently active | `device` with `calendar.is_event_active`, or `state` on the calendar entity |
| Complex expression or cross-entity logic | `template` |
| All conditions must pass | Implicit AND (sequential list) or `condition: and` |
| At least one condition must pass | `condition: or` |
| Condition must fail to proceed | `condition: not` |

**Quick rules:**
- Reach for `state` or `numeric_state` first; they are faster and produce cleaner automation traces than template conditions.
- Use `template` only when no built-in type can express the logic.
- Use `device` conditions when the UI automation editor generates them; they are tied to the device registry and survive entity renames.
- Wrap `condition: not` around any condition to invert it rather than trying to enumerate all "other" states.

---

## Best Practices

### Order Conditions Efficiently

```yaml
# Put fast/cheap conditions first
conditions:
  # Boolean check is fast
  - condition: state
    entity_id: input_boolean.enabled
    state: "on"
  # Then time check
  - condition: time
    after: "08:00:00"
  # Template checks last (more expensive)
  - condition: template
    value_template: "{{ complex_calculation }}"
```

### Use Appropriate Condition Type

```yaml
# Use state for simple state checks
conditions:
  - condition: state
    entity_id: light.lamp
    state: "on"  # Good

# Don't use template for simple checks
conditions:
  - condition: template
    value_template: "{{ is_state('light.lamp', 'on') }}"  # Unnecessary
```

### Handle Edge Cases

```yaml
# Always handle unavailable states
conditions:
  - condition: template
    value_template: >
      {{ states('sensor.temperature') not in ['unknown', 'unavailable'] and
         states('sensor.temperature') | float > 25 }}
```

### Document Complex Conditions

```yaml
conditions:
  # Only proceed if:
  # - Automation is enabled by user
  # - It's during active hours
  # - Not in vacation mode
  - condition: and
    conditions:
      - condition: state
        entity_id: input_boolean.automation_enabled
        state: "on"
      - condition: time
        after: "07:00:00"
        before: "23:00:00"
      - condition: state
        entity_id: input_boolean.vacation_mode
        state: "off"
```

### Test Conditions

```jinja2
# Test in Developer Tools > Template
{{ is_state('input_boolean.test', 'on') and
   is_state('binary_sensor.motion', 'on') }}
```

---

## Troubleshooting

### Condition Never Passes

| Problem | Cause | Solution |
|---------|-------|----------|
| State mismatch | State is string | Quote values: `state: "on"` not `state: on` |
| Entity unavailable | Entity not ready | Add availability check |
| Time zone issue | Wrong time zone | Check HA time zone config |
| Attribute check fails | Wrong attribute name | Check entity attributes |

### Debug Conditions

```yaml
# Add logging to trace condition evaluation
automation:
  - id: debug_condition
    triggers:
      - trigger: state
        entity_id: binary_sensor.test
    actions:
      - action: system_log.write
        data:
          message: >
            Conditions met! States:
            - enabled: {{ states('input_boolean.enabled') }}
            - motion: {{ states('binary_sensor.motion') }}
          level: info
```

### Check Condition in Template

```jinja2
# Developer Tools > Template
# Test your condition logic

{% set enabled = is_state('input_boolean.enabled', 'on') %}
{% set motion = is_state('binary_sensor.motion', 'on') %}
{% set dark = states('sensor.illuminance') | float < 50 %}

enabled: {{ enabled }}
motion: {{ motion }}
dark: {{ dark }}
all conditions: {{ enabled and motion and dark }}
```

### Common Mistakes

```yaml
# Wrong: state without quotes for "on"/"off"
conditions:
  - condition: state
    entity_id: switch.test
    state: on  # YAML interprets as boolean True

# Correct: quoted string
conditions:
  - condition: state
    entity_id: switch.test
    state: "on"

# Wrong: above/below are exclusive
conditions:
  - condition: numeric_state
    entity_id: sensor.temp
    above: 25  # Means > 25, not >= 25

# Wrong: time crossing midnight
conditions:
  - condition: time
    after: "22:00:00"
    before: "06:00:00"  # This NEVER matches!

# Correct: use OR for midnight crossing
conditions:
  - condition: or
    conditions:
      - condition: time
        after: "22:00:00"
      - condition: time
        before: "06:00:00"
```

### Trace Analysis

```yaml
# Check automation trace in UI
# Settings > Automations > (automation) > Traces

# Trace shows:
# - Trigger that fired
# - Each condition and result
# - Actions executed

# Failed condition shows:
# Result: false
# Reason: State is 'off', expected 'on'
```
