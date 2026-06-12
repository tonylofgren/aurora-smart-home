# Advanced Triggers in Home Assistant

> Comprehensive guide to advanced trigger types and optimization patterns

## Overview

Home Assistant 2024/2025 introduces powerful new trigger capabilities. This guide covers advanced trigger patterns, the new Wait for State trigger (2024.4+), enhanced Conversation triggers (2024.11+), and performance optimization strategies.

---

## Wait for State Trigger (2024.4+)

### Introduction

The `wait_for_trigger` action with state triggers was enhanced in 2024.4 to support comparison operators, making it easier to wait for specific state conditions without complex template logic.

### Basic Syntax

```yaml
automation:
  - id: wait_for_state_basic
    alias: "Wait for Door to Close"
    triggers:
      - trigger: state
        entity_id: binary_sensor.front_door
        to: "on"
    actions:
      - action: notify.mobile_app
        data:
          message: "Front door opened, waiting for it to close..."
      - wait_for_trigger:
          - trigger: state
            entity_id: binary_sensor.front_door
            to: "off"
        timeout:
          minutes: 5
      - choose:
          - conditions: "{{ wait.trigger == none }}"
            sequence:
              - action: notify.mobile_app
                data:
                  message: "Warning: Front door still open after 5 minutes!"
          - conditions: "{{ wait.trigger != none }}"
            sequence:
              - action: notify.mobile_app
                data:
                  message: "Front door closed"
```

### Comparison Operators (2024.4+)

Wait for numeric state changes with operators:

```yaml
automation:
  - id: wait_for_temperature
    alias: "Wait for Temperature to Drop"
    triggers:
      - trigger: numeric_state
        entity_id: sensor.outdoor_temperature
        above: 30
    actions:
      - action: climate.turn_on
        target:
          entity_id: climate.living_room
      - wait_for_trigger:
          - trigger: numeric_state
            entity_id: sensor.outdoor_temperature
            below: 25
        timeout:
          hours: 4
      - action: climate.turn_off
        target:
          entity_id: climate.living_room
```

### Available Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `above` | Value greater than | `above: 25` |
| `below` | Value less than | `below: 20` |
| `to` | Exact state match | `to: "on"` |
| `from` | Previous state match | `from: "off"` |
| `for` | Duration held | `for: "00:05:00"` |

### Advanced Wait Patterns

#### Multiple Conditions Wait

```yaml
actions:
  - wait_for_trigger:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "off"
        for:
          minutes: 10
      - trigger: state
        entity_id: input_boolean.override
        to: "on"
    timeout:
      minutes: 30
  # wait.trigger contains whichever triggered first
  - choose:
      - conditions: "{{ wait.trigger.platform == 'state' and wait.trigger.entity_id == 'input_boolean.override' }}"
        sequence:
          - action: notify.mobile_app
            data:
              message: "Override activated"
```

#### Wait with Template Condition

```yaml
actions:
  - wait_for_trigger:
      - trigger: template
        value_template: >
          {{ states('sensor.power_usage') | float(0) < 100
             and is_state('binary_sensor.grid_available', 'on') }}
    timeout:
      hours: 2
    continue_on_timeout: true
```

#### Timeout Handling

```yaml
actions:
  - wait_for_trigger:
      - trigger: state
        entity_id: lock.front_door
        to: "locked"
    timeout:
      minutes: 2
    continue_on_timeout: true  # Don't stop if timeout
  - if:
      - condition: template
        value_template: "{{ wait.trigger == none }}"
    then:
      - action: lock.lock
        target:
          entity_id: lock.front_door
      - action: notify.mobile_app
        data:
          message: "Auto-locked front door after timeout"
```

---

## Conversation Trigger (2024.11+)

### Introduction

Conversation triggers allow automations to respond to natural language commands through Assist. The 2024.11+ update brings enhanced slot handling and response variables.

### Basic Syntax

```yaml
automation:
  - id: voice_lights
    alias: "Voice: Control Lights"
    triggers:
      - trigger: conversation
        command:
          - "turn on the {area} lights"
          - "turn off the {area} lights"
          - "lights on in {area}"
          - "lights off in {area}"
    actions:
      - variables:
          action: >
            {% if 'on' in trigger.sentence | lower %}
              turn_on
            {% else %}
              turn_off
            {% endif %}
          target_area: "{{ trigger.slots.area }}"
      - action: "light.{{ action }}"
        target:
          area_id: "{{ target_area }}"
```

### Slot Types

```yaml
automation:
  - id: voice_temperature
    alias: "Voice: Set Temperature"
    triggers:
      - trigger: conversation
        command:
          - "set temperature to {temperature}"
          - "set thermostat to {temperature} degrees"
          - "make it {temperature} degrees"
    actions:
      - action: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: "{{ trigger.slots.temperature | float }}"
```

### Response Variables (2024.11+)

```yaml
automation:
  - id: voice_status
    alias: "Voice: Get Status"
    triggers:
      - trigger: conversation
        command:
          - "what is the {entity_type} in the {area}"
          - "how is the {entity_type} in {area}"
    actions:
      - variables:
          entity_type: "{{ trigger.slots.entity_type }}"
          area: "{{ trigger.slots.area }}"
          response_text: >
            {% set domain_map = {
              'temperature': 'sensor',
              'humidity': 'sensor',
              'light': 'light',
              'lights': 'light'
            } %}
            {% set domain = domain_map.get(entity_type, 'sensor') %}
            {% set entities = area_entities(area) | select('match', domain ~ '.*') | list %}
            {% if entities %}
              {% set entity = entities[0] %}
              The {{ entity_type }} in {{ area }} is {{ states(entity) }}
            {% else %}
              I couldn't find {{ entity_type }} in {{ area }}
            {% endif %}
      - stop: ""
        response_variable: response_text
```

### Advanced Conversation Patterns

#### Wildcards and Alternatives

```yaml
triggers:
  - trigger: conversation
    command:
      - "[please|] turn {state} [the|] {area} [light|lights]"
      - "[please|] {state} [the|] {area} [light|lights]"
```

Syntax:
- `[option1|option2]` - alternatives (either/or)
- `[optional|]` - optional word
- `{slot}` - capture variable

#### Context-Aware Commands

```yaml
automation:
  - id: voice_contextual
    alias: "Voice: Contextual Commands"
    triggers:
      - trigger: conversation
        command:
          - "I'm going to bed"
          - "goodnight"
          - "time for bed"
    conditions:
      - condition: time
        after: "20:00:00"
        before: "06:00:00"
    actions:
      - action: script.bedtime_routine
      - stop: ""
        response_variable: "Good night! Running bedtime routine."
```

#### Multi-Intent Handling

```yaml
automation:
  - id: voice_multi_intent
    alias: "Voice: Complex Commands"
    triggers:
      - trigger: conversation
        command:
          - "turn on {device1} and {device2}"
          - "{device1} and {device2} on"
    actions:
      - action: homeassistant.turn_on
        target:
          entity_id: "{{ trigger.slots.device1 }}"
      - action: homeassistant.turn_on
        target:
          entity_id: "{{ trigger.slots.device2 }}"
```

---

## Template Triggers - Advanced

### Multi-Entity Monitoring

```yaml
automation:
  - id: template_multi_entity
    alias: "Monitor Multiple Sensors"
    triggers:
      - trigger: template
        value_template: >
          {% set sensors = [
            'sensor.temp_living_room',
            'sensor.temp_bedroom',
            'sensor.temp_kitchen'
          ] %}
          {% set temps = sensors | map('states') | map('float', 0) | list %}
          {% set avg = temps | average %}
          {{ avg > 25 }}
    actions:
      - action: climate.set_hvac_mode
        target:
          entity_id: climate.main
        data:
          hvac_mode: cool
```

### Rate-Limited Template Trigger

```yaml
automation:
  - id: template_rate_limited
    alias: "Rate Limited Trigger"
    triggers:
      - trigger: template
        value_template: >
          {{ states('sensor.power_usage') | float(0) > 5000 }}
        for:
          seconds: 30  # Debounce: must be true for 30s
    mode: single
    max_exceeded: silent
    actions:
      - action: notify.mobile_app
        data:
          message: "High power usage detected"
      - delay:
          minutes: 15  # Rate limit: don't trigger again for 15min
```

### State Change Rate Detection

```yaml
automation:
  - id: template_rate_of_change
    alias: "Detect Rapid Temperature Change"
    triggers:
      - trigger: template
        value_template: >
          {% set current = states('sensor.temperature') | float(0) %}
          {% set previous = state_attr('sensor.temperature', 'last_value') | float(current) %}
          {% set change_rate = (current - previous) | abs %}
          {{ change_rate > 2 }}  # More than 2 degrees change
    actions:
      - action: notify.mobile_app
        data:
          message: "Rapid temperature change detected!"
```

### Combined Condition Template

```yaml
automation:
  - id: template_complex_condition
    alias: "Complex State Monitoring"
    triggers:
      - trigger: template
        value_template: >
          {% set occupancy = is_state('binary_sensor.occupancy', 'on') %}
          {% set time_ok = now().hour >= 8 and now().hour < 22 %}
          {% set not_vacation = is_state('input_boolean.vacation', 'off') %}
          {% set lights_off = expand('group.all_lights')
             | selectattr('state', 'eq', 'on') | list | count == 0 %}
          {{ occupancy and time_ok and not_vacation and lights_off }}
    actions:
      - action: light.turn_on
        target:
          area_id: living_room
```

---

## Device Triggers - Edge Cases

### Button Events

```yaml
automation:
  - id: device_button_multi
    alias: "Multi-Click Button Handler"
    triggers:
      - trigger: device
        domain: mqtt
        device_id: abc123
        type: action
        subtype: single
        id: single_click
      - trigger: device
        domain: mqtt
        device_id: abc123
        type: action
        subtype: double
        id: double_click
      - trigger: device
        domain: mqtt
        device_id: abc123
        type: action
        subtype: hold
        id: hold
    actions:
      - choose:
          - conditions: "{{ trigger.id == 'single_click' }}"
            sequence:
              - action: light.toggle
                target:
                  entity_id: light.ceiling
          - conditions: "{{ trigger.id == 'double_click' }}"
            sequence:
              - action: scene.turn_on
                target:
                  entity_id: scene.bright
          - conditions: "{{ trigger.id == 'hold' }}"
            sequence:
              - action: light.turn_off
                target:
                  area_id: living_room
```

### Remote Control Events

```yaml
automation:
  - id: device_remote
    alias: "Handle Remote Control"
    triggers:
      - trigger: event
        event_type: zha_event
        event_data:
          device_ieee: "00:11:22:33:44:55:66:77"
    actions:
      - variables:
          command: "{{ trigger.event.data.command }}"
          args: "{{ trigger.event.data.args }}"
      - choose:
          - conditions: "{{ command == 'on' }}"
            sequence:
              - action: light.turn_on
                target:
                  entity_id: light.main
          - conditions: "{{ command == 'off' }}"
            sequence:
              - action: light.turn_off
                target:
                  entity_id: light.main
          - conditions: "{{ command == 'move_with_on_off' }}"
            sequence:
              - action: light.turn_on
                target:
                  entity_id: light.main
                data:
                  brightness_step_pct: >
                    {% if args.move_mode == 0 %}
                      10
                    {% else %}
                      -10
                    {% endif %}
```

### State vs Event Triggers

| Use Case | Trigger Type | Why |
|----------|-------------|-----|
| Light turned on | State | Persistent state |
| Button pressed | Event | Momentary action |
| Temperature crossed threshold | Numeric State | Value comparison |
| Motion detected | State | Binary sensor state |
| Zigbee command received | Event | No persistent state |
| Webhook received | Webhook | External event |

```yaml
# State trigger - for persistent states
triggers:
  - trigger: state
    entity_id: light.living_room
    to: "on"

# Event trigger - for momentary events
triggers:
  - trigger: event
    event_type: zha_event
    event_data:
      command: "toggle"
```

---

## Time-Based Trigger Patterns

### Dynamic Time Triggers

```yaml
automation:
  - id: time_dynamic
    alias: "Dynamic Wake Up Time"
    triggers:
      - trigger: time
        at: input_datetime.wake_up_time
    actions:
      - action: light.turn_on
        target:
          entity_id: light.bedroom
```

### Workday-Aware Triggers

```yaml
automation:
  - id: time_workday
    alias: "Workday Morning Routine"
    triggers:
      - trigger: time
        at: "06:30:00"
    conditions:
      - condition: state
        entity_id: binary_sensor.workday_sensor
        state: "on"
      - condition: state
        entity_id: person.john
        state: "home"
    actions:
      - action: script.morning_routine
```

### Sunrise/Sunset with Offset

```yaml
automation:
  - id: time_sun_offset
    alias: "Lights Before Sunset"
    triggers:
      - trigger: sun
        event: sunset
        offset: "-00:30:00"  # 30 minutes before
    conditions:
      - condition: state
        entity_id: group.family
        state: "home"
    actions:
      - action: light.turn_on
        target:
          area_id: living_room
        data:
          brightness_pct: 30
```

### Time Pattern Triggers

```yaml
automation:
  - id: time_pattern
    alias: "Every 15 Minutes Check"
    triggers:
      - trigger: time_pattern
        minutes: "/15"  # Every 15 minutes
    actions:
      - action: script.periodic_check
```

---

## MQTT Trigger Patterns

### JSON Payload Parsing

```yaml
automation:
  - id: mqtt_json
    alias: "MQTT JSON Trigger"
    triggers:
      - trigger: mqtt
        topic: "sensors/outdoor/weather"
    conditions:
      - condition: template
        value_template: >
          {{ trigger.payload_json.temperature | float(0) > 30 }}
    actions:
      - action: notify.mobile_app
        data:
          message: "Outdoor temperature is {{ trigger.payload_json.temperature }}°C"
```

### MQTT with Wildcards

```yaml
automation:
  - id: mqtt_wildcard
    alias: "All Room Sensors"
    triggers:
      - trigger: mqtt
        topic: "home/+/temperature"  # + = single level wildcard
    actions:
      - variables:
          room: "{{ trigger.topic.split('/')[1] }}"
          temp: "{{ trigger.payload | float }}"
      - action: input_number.set_value
        target:
          entity_id: "input_number.temp_{{ room }}"
        data:
          value: "{{ temp }}"
```

---

## Performance Optimization

### High-Frequency Trigger Management

```yaml
# BAD: Triggers on every state change
automation:
  - id: bad_high_frequency
    alias: "Bad: Every Power Update"
    triggers:
      - trigger: state
        entity_id: sensor.power_usage
    actions:
      # Fires hundreds of times per hour

# GOOD: Debounced with threshold
automation:
  - id: good_debounced
    alias: "Good: Power Threshold"
    triggers:
      - trigger: numeric_state
        entity_id: sensor.power_usage
        above: 3000
        for:
          seconds: 30
    actions:
      # Fires only when sustained above threshold
```

### Template Caching

```yaml
# BAD: Complex template evaluated constantly
triggers:
  - trigger: template
    value_template: >
      {% set entities = states.light | list %}
      {% set on_count = entities | selectattr('state', 'eq', 'on') | list | count %}
      {{ on_count > 5 }}

# GOOD: Use dedicated sensor
template:
  - sensor:
      - name: "Lights On Count"
        state: >
          {{ states.light | selectattr('state', 'eq', 'on') | list | count }}

automation:
  triggers:
    - trigger: numeric_state
      entity_id: sensor.lights_on_count
      above: 5
```

### State Change Batching

```yaml
automation:
  - id: batched_triggers
    alias: "Batched State Changes"
    triggers:
      - trigger: state
        entity_id:
          - binary_sensor.door_1
          - binary_sensor.door_2
          - binary_sensor.door_3
          - binary_sensor.door_4
        to: "on"
    mode: queued
    max: 10
    actions:
      - action: notify.mobile_app
        data:
          message: "{{ trigger.to_state.name }} opened"
```

### Trigger ID for Efficiency

```yaml
automation:
  - id: efficient_multi_trigger
    alias: "Efficient Multi-Trigger"
    triggers:
      - trigger: state
        entity_id: binary_sensor.front_door
        to: "on"
        id: front
      - trigger: state
        entity_id: binary_sensor.back_door
        to: "on"
        id: back
      - trigger: state
        entity_id: binary_sensor.garage_door
        to: "on"
        id: garage
    actions:
      - action: notify.mobile_app
        data:
          message: >
            {% set door_names = {
              'front': 'Front door',
              'back': 'Back door',
              'garage': 'Garage door'
            } %}
            {{ door_names[trigger.id] }} opened
```

---

## Debouncing Strategies

### For Clause Debouncing

```yaml
automation:
  - id: debounce_for
    alias: "Debounced Motion"
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
        for:
          seconds: 5  # Must stay "on" for 5 seconds
    actions:
      - action: light.turn_on
        target:
          entity_id: light.room
```

### Mode-Based Debouncing

```yaml
automation:
  - id: debounce_mode
    alias: "Single Mode Debounce"
    mode: single  # Ignore new triggers while running
    triggers:
      - trigger: state
        entity_id: binary_sensor.button
        to: "on"
    actions:
      - action: light.toggle
        target:
          entity_id: light.room
      - delay:
          milliseconds: 500  # Minimum delay between executions
```

### Counter-Based Rate Limiting

```yaml
automation:
  - id: rate_limit_counter
    alias: "Rate Limited Notifications"
    triggers:
      - trigger: state
        entity_id: binary_sensor.doorbell
        to: "on"
    conditions:
      - condition: template
        value_template: >
          {{ (as_timestamp(now()) - as_timestamp(state_attr('automation.rate_limit_counter', 'last_triggered') | default(0))) > 30 }}
    actions:
      - action: notify.mobile_app
        data:
          message: "Doorbell pressed"
```

---

## Best Practices

### Trigger Selection Guide

| Scenario | Recommended Trigger | Why |
|----------|-------------------|-----|
| Light state change | `state` | Simple, efficient |
| Temperature threshold | `numeric_state` with `for` | Avoids rapid firing |
| Button press | `device` or `event` | Momentary action |
| Complex condition | `template` with sensor | Pre-calculate |
| Time-based | `time` or `time_pattern` | Built-in scheduling |
| Voice command | `conversation` | Natural language |
| External webhook | `webhook` | API integration |

### Performance Checklist

1. **Avoid** template triggers that evaluate complex expressions
2. **Use** `for` clause to debounce rapid state changes
3. **Prefer** `numeric_state` over template for value comparisons
4. **Create** template sensors for frequently-used calculations
5. **Use** trigger IDs instead of complex condition logic
6. **Set** appropriate `mode` (single, queued, restart)
7. **Batch** related triggers in single automation
8. **Monitor** automation traces for performance issues

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Trigger never fires | Check entity exists, conditions met |
| Triggers too often | Add `for` clause, debounce |
| Template trigger slow | Move calculation to sensor |
| Missing events | Use event trigger instead of state |
| Timeout not working | Check `continue_on_timeout` setting |

---

## Calendar Trigger

**Source:** https://www.home-assistant.io/docs/automation/trigger/

Use the calendar trigger to react to calendar event start and end times. This is more reliable than watching the calendar entity state directly, because it fires at the precise moment an event begins or ends rather than polling.

### Fields

| Field | Notes |
|-------|-------|
| `entity_id` | Required. The `calendar.*` entity to watch. |
| `event` | Required. `start` or `end`. |
| `offset` | Optional. Fire this duration before or after the boundary, e.g. `"-00:15:00"` for 15 minutes early. |

### Examples

Fire 10 minutes before a family calendar event starts:

```yaml
triggers:
  - trigger: calendar
    entity_id: calendar.family
    event: start
    offset: "-00:10:00"
    id: family_event_starting_soon
```

Fire when a work calendar event ends:

```yaml
triggers:
  - trigger: calendar
    entity_id: calendar.work
    event: end
    id: work_event_ended
```

The trigger exposes event metadata through `trigger.calendar_event`:

| Field | Content |
|-------|---------|
| `trigger.calendar_event.summary` | Event title |
| `trigger.calendar_event.start` | Start datetime string |
| `trigger.calendar_event.end` | End datetime string |
| `trigger.calendar_event.description` | Event description (if set) |

Example action using event data:

```yaml
actions:
  - action: notify.notify
    data:
      message: >
        {{ trigger.calendar_event.summary }} starts in 10 minutes
        ({{ trigger.calendar_event.start }}).
```

Full automation example -- announce upcoming meeting:

```yaml
automation:
  - alias: "Announce upcoming calendar event"
    id: announce_upcoming_calendar_event
    mode: queued
    triggers:
      - trigger: calendar
        entity_id: calendar.work
        event: start
        offset: "-00:05:00"
        id: work_event_soon
    actions:
      - action: tts.speak
        target:
          entity_id: media_player.office_speaker
        data:
          message: >
            Reminder: {{ trigger.calendar_event.summary }} starts in 5 minutes.
```

---

## Device Trigger Inventory

**Source:** https://www.home-assistant.io/docs/automation/trigger/

Device triggers are exposed by integrations and represent device-specific events that may not map to a simple entity state. The trigger pattern is:

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: DOMAIN
    type: EVENT_TYPE
    subtype: EVENT_SUBTYPE   # optional, integration-dependent
    id: my_trigger_id
```

Use the UI automation editor to discover the correct `device_id`, `domain`, `type`, and `subtype` for a specific device, then copy the generated YAML. The values below are sourced from the official trigger index snapshot (2026-05-30) and represent the semantic trigger types each domain publishes.

### Binary and State Device Triggers

These domains expose open/close or on/off state transitions as device triggers.

**Door, garage door, gate, valve, window:**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: door
    type: door.opened
    id: door_opened
```

Types available: `door.opened`, `door.closed`, `garage_door.opened`, `garage_door.closed`, `gate.opened`, `gate.closed`, `window.opened`, `window.closed`, `valve.opened`, `valve.closed`.

**Lock:**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: lock
    type: lock.unlocked
    id: door_unlocked
```

Types available: `lock.locked`, `lock.unlocked`, `lock.opened`, `lock.jammed`.

**Motion:**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: motion
    type: motion.detected
    id: motion_detected
```

Types available: `motion.detected`, `motion.cleared`.

**Alarm control panel:**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: alarm_control_panel
    type: alarm_control_panel.armed_away
    id: alarm_armed_away
```

Types available: `alarm_control_panel.armed`, `alarm_control_panel.armed_away`, `alarm_control_panel.armed_home`, `alarm_control_panel.armed_night`, `alarm_control_panel.armed_vacation`, `alarm_control_panel.disarmed`, `alarm_control_panel.triggered`.

### Environment and Climate Device Triggers

**Climate (HVAC):**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: climate
    type: climate.started_heating
    id: heating_started
```

Types available: `climate.turned_on`, `climate.turned_off`, `climate.started_heating`, `climate.started_cooling`, `climate.started_drying`, `climate.hvac_mode_changed`, `climate.target_temperature_changed`, `climate.target_temperature_crossed_threshold`, `climate.target_humidity_changed`, `climate.target_humidity_crossed_threshold`.

**Humidifier:**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: humidifier
    type: humidifier.started_humidifying
    id: humidifier_on
```

Types available: `humidifier.turned_on`, `humidifier.turned_off`, `humidifier.started_humidifying`, `humidifier.started_drying`, `humidifier.mode_changed`.

**Temperature and humidity sensors:**

Types available: `temperature.changed`, `temperature.crossed_threshold`, `humidity.changed`, `humidity.crossed_threshold`.

**Air quality:**

Air quality device triggers cover individual pollutant levels. Common types include `air_quality.co2_crossed_threshold`, `air_quality.pm25_crossed_threshold`, `air_quality.voc_crossed_threshold`, `air_quality.smoke_detected`, `air_quality.smoke_cleared`, `air_quality.co_detected`, `air_quality.co_cleared`, and equivalent `_changed` variants for each measured quantity (CO2, CO, NO, NO2, N2O, O3, PM1, PM2.5, PM4, PM10, SO2, VOC).

### Button and Remote Triggers

**Button (momentary press):**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: button
    type: button.pressed
    id: button_pressed
```

Types available: `button.pressed`.

**Multi-action remotes via MQTT or ZHA:**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: mqtt
    type: action
    subtype: single
    id: remote_single_press
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: mqtt
    type: action
    subtype: double
    id: remote_double_press
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: mqtt
    type: action
    subtype: hold
    id: remote_hold
```

The `subtype` values (`single`, `double`, `hold`, `rotate_left`, etc.) depend on the specific device and integration. Use the UI editor to find valid subtypes for a given device.

**Counter:**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: counter
    type: counter.incremented
    id: counter_incremented
```

Types available: `counter.incremented`, `counter.decremented`, `counter.reset`, `counter.minimum_reached`, `counter.maximum_reached`.

**Timer:**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: timer
    type: timer.finished
    id: timer_done
```

Types available: `timer.started`, `timer.paused`, `timer.cancelled`, `timer.finished`, `timer.restarted`, `timer.time_remaining`.

### Appliance and Robot Device Triggers

**Vacuum:**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: vacuum
    type: vacuum.started_cleaning
    id: vacuum_cleaning
```

Types available: `vacuum.started_cleaning`, `vacuum.paused_cleaning`, `vacuum.started_returning`, `vacuum.docked`, `vacuum.errored`.

**Lawn mower:**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: lawn_mower
    type: lawn_mower.started_mowing
    id: mowing_started
```

Types available: `lawn_mower.started_mowing`, `lawn_mower.paused_mowing`, `lawn_mower.started_returning`, `lawn_mower.docked`, `lawn_mower.errored`.

### Light, Fan, and Siren Triggers

**Light:**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: light
    type: light.turned_on
    id: light_on
```

Types available: `light.turned_on`, `light.turned_off`, `light.brightness_changed`, `light.brightness_crossed_threshold`.

**Fan:**

Types available: `fan.turned_on`, `fan.turned_off`.

**Siren:**

Types available: `siren.turned_on`, `siren.turned_off`.

### Update and Battery Triggers

**Update (pending software updates):**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: update
    type: update.update_became_available
    id: update_available
```

Types available: `update.update_became_available`.

**Battery level:**

```yaml
triggers:
  - trigger: device
    device_id: YOUR_DEVICE_ID
    domain: battery
    type: battery.level_crossed
    id: battery_critical
```

Types available: `battery.level_changed`, `battery.level_crossed`.

### Task and Notification Triggers

**To-do list:**

Types available: `todo.item_added`, `todo.item_completed`, `todo.item_removed`.

### Domain Reference Table

| Domain | Key trigger types |
|--------|------------------|
| `door` / `garage_door` / `gate` | `.opened`, `.closed` |
| `window` / `valve` | `.opened`, `.closed` |
| `lock` | `.locked`, `.unlocked`, `.opened`, `.jammed` |
| `motion` | `.detected`, `.cleared` |
| `alarm_control_panel` | `.armed_*`, `.disarmed`, `.triggered` |
| `climate` | `.turned_on/off`, `.started_heating/cooling/drying`, `.*_changed` |
| `humidifier` | `.turned_on/off`, `.started_humidifying/drying`, `.mode_changed` |
| `temperature` / `humidity` | `.changed`, `.crossed_threshold` |
| `air_quality` | `.*_detected`, `.*_cleared`, `.*_changed`, `.*_crossed_threshold` |
| `button` | `.pressed` |
| `counter` | `.incremented`, `.decremented`, `.reset`, `.*_reached` |
| `timer` | `.started`, `.paused`, `.cancelled`, `.finished`, `.restarted` |
| `light` | `.turned_on/off`, `.brightness_changed/crossed_threshold` |
| `fan` / `siren` | `.turned_on`, `.turned_off` |
| `vacuum` / `lawn_mower` | `.started_*`, `.paused_*`, `.docked`, `.errored` |
| `update` | `.update_became_available` |
| `battery` | `.level_changed`, `.level_crossed` |
| `todo` | `.item_added`, `.item_completed`, `.item_removed` |

---

## Resources

- [Home Assistant Trigger Documentation](https://www.home-assistant.io/docs/automation/trigger/)
- [Wait for Trigger](https://www.home-assistant.io/docs/scripts/#wait-for-trigger)
- [Conversation Integration](https://www.home-assistant.io/integrations/conversation/)
- [Template Triggers](https://www.home-assistant.io/docs/automation/trigger/#template-trigger)
