# Home Assistant Automations Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Automation Structure](#automation-structure)
- [Automation Modes](#automation-modes)
- [Triggers](#triggers)
- [Conditions](#conditions)
- [Actions](#actions)
- [Variables](#variables)
- [Automation Traces](#automation-traces)
- [YAML vs UI](#yaml-vs-ui)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Home Assistant automations follow a **Trigger -> Condition -> Action** pattern:

```yaml
automation:
  - id: "unique_id"
    alias: "Human Readable Name"
    description: "What this automation does"
    triggers:
      # WHEN should this run?
    conditions:
      # Should it run NOW? (optional)
    actions:
      # WHAT should happen?
```

> **Syntax history:** HA 2024.8 renamed `service:` (step key) to `action:`. HA 2024.10 pluralized the top-level automation block keys: `trigger:` -> `triggers:`, `condition:` -> `conditions:`, `action:` -> `actions:`. Legacy singular keys still work but new automations should use the plural forms. Inside each trigger list item, `platform: state` etc. also changed to `trigger: state`.

### Key Terms

| Term | Description |
|------|-------------|
| **Trigger** | Event that starts the automation |
| **Condition** | Optional check that must pass for actions to run |
| **Action** | What happens when triggered and conditions pass |
| **Mode** | How concurrent triggers are handled |
| **Trace** | Debug log of automation execution |

---

## Automation Structure

### Complete Automation Example

```yaml
automation:
  - id: "motion_light_living_room"
    alias: "Motion Light - Living Room"
    description: "Turn on living room light when motion detected"
    mode: restart
    max_exceeded: silent

    triggers:
      - trigger: state
        entity_id: binary_sensor.living_room_motion
        to: "on"
        id: motion_detected
      - trigger: state
        entity_id: binary_sensor.living_room_motion
        to: "off"
        for: "00:05:00"
        id: motion_cleared

    conditions:
      - condition: state
        entity_id: input_boolean.automation_enabled
        state: "on"

    actions:
      - choose:
          - conditions:
              - condition: trigger
                id: motion_detected
            sequence:
              - action: light.turn_on
                target:
                  entity_id: light.living_room
          - conditions:
              - condition: trigger
                id: motion_cleared
            sequence:
              - action: light.turn_off
                target:
                  entity_id: light.living_room
```

### Required Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes* | Unique identifier (auto-generated in UI) |
| `alias` | Yes | Human-readable name |
| `triggers` | Yes | At least one trigger |
| `actions` | Yes | At least one action |

*Required for UI-managed automations

### Optional Fields

| Field | Default | Description |
|-------|---------|-------------|
| `description` | None | Longer description |
| `mode` | `single` | How concurrent triggers are handled |
| `max` | 10 | Max parallel runs (for `queued`/`parallel`) |
| `max_exceeded` | `warning` | Log level when max exceeded |
| `conditions` | None | Conditions to check |
| `variables` | None | Local variables |
| `trace` | Enabled | Store trace data |

---

## Automation Modes

### Available Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| `single` | Ignore new triggers while running | Default, most automations |
| `restart` | Stop current run, start new | Motion lights, timeout resets |
| `queued` | Queue triggers, run one at a time | Sequential notifications |
| `parallel` | Run all triggers simultaneously | Independent actions |

### Mode Examples

```yaml
# Single - Default behavior
automation:
  - alias: "Daily Backup"
    mode: single
    triggers:
      - trigger: time
        at: "03:00:00"
    actions:
      - action: backup.create

# Restart - Reset timeout on new trigger
automation:
  - alias: "Motion Light with Restart"
    mode: restart
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
    actions:
      - action: light.turn_on
        target:
          entity_id: light.hallway
      - delay: "00:05:00"
      - action: light.turn_off
        target:
          entity_id: light.hallway

# Queued - Process one at a time
automation:
  - alias: "Doorbell Notification Queue"
    mode: queued
    max: 5
    triggers:
      - trigger: state
        entity_id: binary_sensor.doorbell
        to: "on"
    actions:
      - action: notify.mobile_app
        data:
          message: "Someone at the door!"
      - delay: "00:00:30"

# Parallel - Run all simultaneously
automation:
  - alias: "Log All Motion Events"
    mode: parallel
    max: 20
    triggers:
      - trigger: state
        entity_id:
          - binary_sensor.motion_1
          - binary_sensor.motion_2
          - binary_sensor.motion_3
        to: "on"
    actions:
      - action: logbook.log
        data:
          name: "Motion"
          message: "{{ trigger.entity_id }} detected motion"
```

### max_exceeded Options

| Value | Behavior |
|-------|----------|
| `silent` | Silently ignore |
| `warning` | Log a warning (default) |
| `error` | Log an error |
| `critical` | Log critical error |

---

## Triggers

### State Trigger

```yaml
triggers:
  # Basic state change
  - trigger: state
    entity_id: binary_sensor.door
    to: "on"

  # From specific state
  - trigger: state
    entity_id: light.bedroom
    from: "on"
    to: "off"

  # Any state change (not attribute)
  - trigger: state
    entity_id: sensor.temperature

  # With duration requirement
  - trigger: state
    entity_id: binary_sensor.door
    to: "on"
    for: "00:10:00"

  # Dynamic duration
  - trigger: state
    entity_id: binary_sensor.motion
    to: "off"
    for:
      minutes: "{{ states('input_number.motion_timeout') | int }}"

  # Multiple entities
  - trigger: state
    entity_id:
      - binary_sensor.window_1
      - binary_sensor.window_2
      - binary_sensor.window_3
    to: "on"

  # Exclude attribute changes
  - trigger: state
    entity_id: light.bedroom
    attribute: brightness
    # Only triggers on brightness attribute changes

  # Not from unavailable
  - trigger: state
    entity_id: sensor.temperature
    not_from:
      - "unknown"
      - "unavailable"
    not_to:
      - "unknown"
      - "unavailable"
```

### Numeric State Trigger

```yaml
triggers:
  # Above threshold
  - trigger: numeric_state
    entity_id: sensor.temperature
    above: 25

  # Below threshold
  - trigger: numeric_state
    entity_id: sensor.humidity
    below: 30

  # Within range
  - trigger: numeric_state
    entity_id: sensor.battery
    below: 20
    above: 0

  # With duration
  - trigger: numeric_state
    entity_id: sensor.power
    above: 3000
    for: "00:05:00"

  # Attribute value
  - trigger: numeric_state
    entity_id: light.bedroom
    attribute: brightness
    above: 200

  # Using template for threshold
  - trigger: numeric_state
    entity_id: sensor.temperature
    above: "{{ states('input_number.temp_threshold') | float }}"
```

### Time Trigger

```yaml
triggers:
  # Specific time
  - trigger: time
    at: "08:00:00"

  # Multiple times
  - trigger: time
    at:
      - "08:00:00"
      - "12:00:00"
      - "18:00:00"

  # Using input_datetime
  - trigger: time
    at: input_datetime.wake_up_time

  # Using sensor
  - trigger: time
    at: sensor.next_alarm
```

### Time Pattern Trigger

```yaml
triggers:
  # Every hour
  - trigger: time_pattern
    hours: "/1"

  # Every 5 minutes
  - trigger: time_pattern
    minutes: "/5"

  # Every 30 seconds
  - trigger: time_pattern
    seconds: "/30"

  # At minute 0 of every hour
  - trigger: time_pattern
    minutes: 0

  # Every 15 minutes during work hours
  - trigger: time_pattern
    hours: "8-17"
    minutes: "/15"
```

### Sun Trigger

```yaml
triggers:
  # At sunset
  - trigger: sun
    event: sunset

  # At sunrise
  - trigger: sun
    event: sunrise

  # 30 minutes before sunset
  - trigger: sun
    event: sunset
    offset: "-00:30:00"

  # 1 hour after sunrise
  - trigger: sun
    event: sunrise
    offset: "01:00:00"
```

### Zone Trigger

```yaml
triggers:
  # Person enters zone
  - trigger: zone
    entity_id: person.john
    zone: zone.home
    event: enter

  # Person leaves zone
  - trigger: zone
    entity_id: person.john
    zone: zone.work
    event: leave

  # Multiple people
  - trigger: zone
    entity_id:
      - person.john
      - person.jane
    zone: zone.home
    event: enter
```

### Event Trigger

```yaml
triggers:
  # Home Assistant events
  - trigger: event
    event_type: homeassistant_start

  # Call service events
  - trigger: event
    event_type: call_service
    event_data:
      domain: light
      service: turn_on

  # Custom events
  - trigger: event
    event_type: my_custom_event
    event_data:
      action: button_pressed

  # ESPHome events
  - trigger: event
    event_type: esphome.button_pressed
    event_data:
      device: kitchen_switch
```

### MQTT Trigger

```yaml
triggers:
  # Simple topic
  - trigger: mqtt
    topic: "home/doorbell"

  # With payload filter
  - trigger: mqtt
    topic: "home/motion/+"
    payload: "ON"

  # JSON payload with template
  - trigger: mqtt
    topic: "zigbee2mqtt/motion_sensor"
    value_template: "{{ value_json.occupancy }}"
    payload: "true"
```

### Webhook Trigger

```yaml
triggers:
  - trigger: webhook
    webhook_id: "my_unique_webhook_id"
    allowed_methods:
      - POST
    local_only: false
```

### Device Trigger

```yaml
triggers:
  # Device-specific trigger (from UI)
  - trigger: device
    device_id: "abc123..."
    domain: zwave_js
    type: "event.value_notification.entry_control"
    property: "eventType"
    value: 6  # Keypad unlock
```

### Calendar Trigger

```yaml
triggers:
  # Calendar event starts
  - trigger: calendar
    entity_id: calendar.work
    event: start

  # Calendar event ends
  - trigger: calendar
    entity_id: calendar.vacation
    event: end
    offset: "-01:00:00"  # 1 hour before end
```

### Template Trigger

```yaml
triggers:
  # Template becomes true
  - trigger: template
    value_template: >
      {{ states('sensor.temperature') | float > 25 and
         is_state('climate.living_room', 'off') }}

  # With for duration
  - trigger: template
    value_template: "{{ states('sensor.power') | float > 3000 }}"
    for: "00:05:00"
```

### Tag Trigger

```yaml
triggers:
  # NFC tag scanned
  - trigger: tag
    tag_id: "abc123-def456"

  # Multiple tags
  - trigger: tag
    tag_id:
      - "tag1"
      - "tag2"
```

### Sentence Trigger (Voice)

```yaml
triggers:
  # Voice command matching
  - trigger: conversation
    command:
      - "turn on the {area} lights"
      - "lights on in the {area}"
```

### Trigger ID

Assign IDs to triggers for use in conditions/actions:

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.motion_living
    to: "on"
    id: living_motion
  - trigger: state
    entity_id: binary_sensor.motion_kitchen
    to: "on"
    id: kitchen_motion

conditions:
  - condition: trigger
    id: living_motion

actions:
  - choose:
      - conditions:
          - condition: trigger
            id: living_motion
        sequence:
          - action: light.turn_on
            target:
              entity_id: light.living_room
```

---

## Conditions

### State Condition

```yaml
conditions:
  # Entity is in state
  - condition: state
    entity_id: light.bedroom
    state: "on"

  # Multiple allowed states
  - condition: state
    entity_id: alarm_control_panel.home
    state:
      - "armed_home"
      - "armed_away"

  # With duration (entity has been in state for)
  - condition: state
    entity_id: binary_sensor.motion
    state: "off"
    for: "00:10:00"

  # Attribute check
  - condition: state
    entity_id: climate.living_room
    attribute: hvac_action
    state: "heating"
```

### Numeric State Condition

```yaml
conditions:
  # Above threshold
  - condition: numeric_state
    entity_id: sensor.temperature
    above: 20

  # Below threshold
  - condition: numeric_state
    entity_id: sensor.battery
    below: 20

  # Within range
  - condition: numeric_state
    entity_id: sensor.humidity
    above: 30
    below: 70

  # Attribute value
  - condition: numeric_state
    entity_id: light.bedroom
    attribute: brightness
    above: 100
```

### Time Condition

```yaml
conditions:
  # Within time range
  - condition: time
    after: "08:00:00"
    before: "22:00:00"

  # Using input_datetime
  - condition: time
    after: input_datetime.day_start
    before: input_datetime.day_end

  # Specific weekdays
  - condition: time
    weekday:
      - mon
      - tue
      - wed
      - thu
      - fri
```

### Sun Condition

```yaml
conditions:
  # After sunset
  - condition: sun
    after: sunset

  # Before sunrise
  - condition: sun
    before: sunrise

  # With offset (30 min after sunset)
  - condition: sun
    after: sunset
    after_offset: "00:30:00"
```

### Zone Condition

```yaml
conditions:
  # Person is in zone
  - condition: zone
    entity_id: person.john
    zone: zone.home

  # Person is NOT in zone (use not condition)
  - condition: not
    conditions:
      - condition: zone
        entity_id: person.john
        zone: zone.home
```

### Template Condition

```yaml
conditions:
  # Template evaluates to true
  - condition: template
    value_template: >
      {{ states('sensor.temperature') | float > 25 }}

  # Complex template
  - condition: template
    value_template: >
      {% set temp = states('sensor.temperature') | float %}
      {% set humidity = states('sensor.humidity') | float %}
      {{ temp > 20 and humidity < 60 }}
```

### Device Condition

```yaml
conditions:
  # Device-specific condition (from UI)
  - condition: device
    device_id: "abc123..."
    domain: zwave_js
    type: "is_locked"
```

### Trigger Condition

```yaml
conditions:
  # Check which trigger fired
  - condition: trigger
    id: motion_detected

  # Multiple triggers
  - condition: trigger
    id:
      - motion_living
      - motion_kitchen
```

### Logical Conditions

```yaml
conditions:
  # AND - All must be true (default when multiple conditions)
  - condition: and
    conditions:
      - condition: state
        entity_id: input_boolean.guests
        state: "off"
      - condition: sun
        after: sunset

  # OR - Any must be true
  - condition: or
    conditions:
      - condition: state
        entity_id: person.john
        state: "home"
      - condition: state
        entity_id: person.jane
        state: "home"

  # NOT - Invert condition
  - condition: not
    conditions:
      - condition: state
        entity_id: alarm_control_panel.home
        state: "disarmed"
```

### Shorthand Conditions

```yaml
conditions:
  # Shorthand for state condition
  - "{{ is_state('light.bedroom', 'on') }}"

  # Shorthand for multiple
  - "{{ is_state('binary_sensor.motion', 'off') }}"
  - "{{ now().hour >= 8 and now().hour < 22 }}"
```

---

## Actions

### Action Call

```yaml
actions:
  # Basic action call
  - action: light.turn_on
    target:
      entity_id: light.living_room

  # With data
  - action: light.turn_on
    target:
      entity_id: light.living_room
    data:
      brightness_pct: 80
      color_temp: 350

  # Target area
  - action: light.turn_off
    target:
      area_id: living_room

  # Target device
  - action: light.turn_on
    target:
      device_id: "abc123..."

  # Target all
  - action: light.turn_off
    target:
      entity_id: all

  # Using templates
  - action: "light.turn_{{ states('input_select.action') }}"
    target:
      entity_id: "{{ states('input_text.target_light') }}"
    data:
      brightness: "{{ states('input_number.brightness') | int }}"
```

### Delay

```yaml
actions:
  # Fixed delay
  - delay: "00:05:00"

  # Dynamic delay
  - delay:
      seconds: "{{ states('input_number.delay_seconds') | int }}"

  # Template delay
  - delay: "{{ states('input_text.delay_time') }}"
```

### Wait Template

```yaml
actions:
  # Wait for condition
  - wait_template: "{{ is_state('binary_sensor.motion', 'off') }}"

  # With timeout
  - wait_template: "{{ is_state('lock.front_door', 'locked') }}"
    timeout: "00:01:00"
    continue_on_timeout: true
```

### Wait for Trigger

```yaml
actions:
  # Wait for trigger
  - wait_for_trigger:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "off"
        for: "00:05:00"
    timeout: "01:00:00"
    continue_on_timeout: true
```

### Choose (Conditional Branches)

```yaml
actions:
  - choose:
      # First matching condition wins
      - conditions:
          - condition: state
            entity_id: input_select.mode
            state: "movie"
        sequence:
          - action: scene.turn_on
            target:
              entity_id: scene.movie_mode

      - conditions:
          - condition: state
            entity_id: input_select.mode
            state: "dinner"
        sequence:
          - action: scene.turn_on
            target:
              entity_id: scene.dinner_mode

    # Default if no conditions match
    default:
      - action: scene.turn_on
        target:
          entity_id: scene.normal
```

### If/Then/Else

```yaml
actions:
  - if:
      - condition: sun
        after: sunset
    then:
      - action: light.turn_on
        target:
          entity_id: light.porch
        data:
          brightness_pct: 100
    else:
      - action: light.turn_on
        target:
          entity_id: light.porch
        data:
          brightness_pct: 30
```

### Repeat

```yaml
actions:
  # Repeat count
  - repeat:
      count: 3
      sequence:
        - action: light.toggle
          target:
            entity_id: light.indicator
        - delay: "00:00:01"

  # Repeat while condition
  - repeat:
      while:
        - condition: state
          entity_id: input_boolean.alarm
          state: "on"
      sequence:
        - action: notify.mobile_app
          data:
            message: "Alarm still active!"
        - delay: "00:01:00"

  # Repeat until condition
  - repeat:
      until:
        - condition: state
          entity_id: lock.front_door
          state: "locked"
      sequence:
        - action: lock.lock
          target:
            entity_id: lock.front_door
        - delay: "00:00:05"

  # Repeat for each item
  - repeat:
      for_each:
        - light.bedroom
        - light.bathroom
        - light.kitchen
      sequence:
        - action: light.turn_off
          target:
            entity_id: "{{ repeat.item }}"
        - delay: "00:00:01"
```

### Parallel

```yaml
actions:
  # Run actions in parallel
  - parallel:
      - action: light.turn_on
        target:
          entity_id: light.living_room
      - action: media_player.play_media
        target:
          entity_id: media_player.speaker
        data:
          media_content_id: "welcome_home.mp3"
          media_content_type: "music"
      - action: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: 22
```

### Stop

```yaml
actions:
  - if:
      - condition: state
        entity_id: input_boolean.vacation
        state: "on"
    then:
      - stop: "Vacation mode active, stopping automation"

  # Continue with rest of actions...
  - action: light.turn_on
    target:
      entity_id: light.welcome
```

### Variables

```yaml
actions:
  # Set variables
  - variables:
      brightness: "{{ states('input_number.brightness') | int }}"
      color: >
        {% if now().hour < 12 %}
          warm_white
        {% else %}
          cool_white
        {% endif %}

  # Use variables
  - action: light.turn_on
    target:
      entity_id: light.bedroom
    data:
      brightness: "{{ brightness }}"
      color_name: "{{ color }}"
```

### Fire Event

```yaml
actions:
  - event: custom_event
    event_data:
      action: "automation_completed"
      source: "motion_light"
```

### Set Input Helpers

```yaml
actions:
  # Set input_boolean
  - action: input_boolean.turn_on
    target:
      entity_id: input_boolean.automation_ran

  # Set input_number
  - action: input_number.set_value
    target:
      entity_id: input_number.counter
    data:
      value: "{{ states('input_number.counter') | int + 1 }}"

  # Set input_select
  - action: input_select.select_option
    target:
      entity_id: input_select.mode
    data:
      option: "home"

  # Set input_text
  - action: input_text.set_value
    target:
      entity_id: input_text.last_motion
    data:
      value: "{{ trigger.entity_id }} at {{ now() }}"
```

---

## Variables

### Automation-Level Variables

```yaml
automation:
  - id: example_with_variables
    alias: "Example with Variables"
    variables:
      light_entity: light.living_room
      timeout_minutes: 5
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
    actions:
      - action: light.turn_on
        target:
          entity_id: "{{ light_entity }}"
      - delay:
          minutes: "{{ timeout_minutes }}"
      - action: light.turn_off
        target:
          entity_id: "{{ light_entity }}"
```

### Trigger Variables

```text
# Available in all triggers
trigger.platform        # "state", "time", etc.
trigger.id              # Trigger ID if set

# State trigger
trigger.entity_id       # Entity that triggered
trigger.from_state      # Previous state object
trigger.to_state        # New state object
trigger.for             # Duration (if specified)

# Time trigger
trigger.now             # Time that triggered

# Event trigger
trigger.event           # Event object
trigger.event.data      # Event data

# Webhook trigger
trigger.json            # JSON payload
trigger.data            # Form data
trigger.query           # Query parameters

# Zone trigger
trigger.zone            # Zone entity
trigger.event           # "enter" or "leave"

# MQTT trigger
trigger.payload         # Message payload
trigger.topic           # Message topic
trigger.payload_json    # Parsed JSON (if valid)
```

### Using Variables in Templates

```yaml
actions:
  - variables:
      room: >
        {% if trigger.entity_id == 'binary_sensor.motion_living' %}
          living_room
        {% elif trigger.entity_id == 'binary_sensor.motion_kitchen' %}
          kitchen
        {% else %}
          unknown
        {% endif %}

  - action: light.turn_on
    target:
      area_id: "{{ room }}"
```

---

## Automation Traces

### Viewing Traces

1. Go to **Settings → Automations & Scenes**
2. Click on an automation
3. Click **Traces** in the top right
4. Select a trace from the list

### Trace Information

- **Triggered at:** When automation started
- **Trigger:** Which trigger fired
- **Condition:** Condition evaluation results
- **Action:** Each action with inputs and results
- **Variables:** Variable values at each step

### Trace Configuration

```yaml
automation:
  - id: example
    alias: "Example"
    trace:
      stored_traces: 10  # Number of traces to keep (default: 5)
```

### Disabling Traces

```yaml
automation:
  - id: frequent_automation
    alias: "Frequent Automation"
    trace:
      stored_traces: 0  # Disable trace storage
```

---

## YAML vs UI

### YAML Advantages
- Version control (git)
- Copy/paste between systems
- Complex templates easier to write
- Bulk editing
- Comments for documentation

### UI Advantages
- Visual editor
- Built-in validation
- Device/entity pickers
- Easier for beginners
- Trace integration

### When to Use Which

| Scenario | Recommendation |
|----------|----------------|
| Simple automations | UI |
| Complex templates | YAML |
| Team environment | YAML (git) |
| Single user | UI |
| Learning HA | UI |
| Power users | YAML |

### Converting Between Formats

**UI to YAML:**
1. Edit automation in UI
2. Click three dots menu → Edit in YAML
3. Copy YAML content

**YAML to UI:**
1. Paste YAML in `automations.yaml`
2. Reload automations
3. Edit in UI (with limitations)

---

## Common Patterns

### Motion Light with Timeout Reset

```yaml
automation:
  - id: motion_light_with_reset
    alias: "Motion Light with Timeout Reset"
    mode: restart
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
    actions:
      - action: light.turn_on
        target:
          entity_id: light.hallway
      - wait_for_trigger:
          - trigger: state
            entity_id: binary_sensor.motion
            to: "off"
            for: "00:03:00"
      - action: light.turn_off
        target:
          entity_id: light.hallway
```

### Presence-Based Climate

```yaml
automation:
  - id: climate_away_mode
    alias: "Climate - Away Mode"
    triggers:
      - trigger: state
        entity_id: group.family
        to: "not_home"
        for: "00:15:00"
    actions:
      - action: climate.set_preset_mode
        target:
          entity_id: climate.living_room
        data:
          preset_mode: "away"

  - id: climate_home_mode
    alias: "Climate - Home Mode"
    triggers:
      - trigger: state
        entity_id: group.family
        to: "home"
    actions:
      - action: climate.set_preset_mode
        target:
          entity_id: climate.living_room
        data:
          preset_mode: "home"
```

### Notification on Low Battery

```yaml
automation:
  - id: low_battery_notification
    alias: "Low Battery Notification"
    triggers:
      - trigger: numeric_state
        entity_id:
          - sensor.phone_battery
          - sensor.tablet_battery
          - sensor.sensor_battery
        below: 20
    conditions:
      - condition: template
        value_template: >
          {{ trigger.from_state.state | int >= 20 }}
    actions:
      - action: notify.mobile_app
        data:
          title: "Low Battery Alert"
          message: >
            {{ trigger.to_state.attributes.friendly_name }}
            is at {{ trigger.to_state.state }}%
```

### Time-Based Brightness

```yaml
automation:
  - id: adaptive_brightness
    alias: "Adaptive Brightness Light"
    triggers:
      - trigger: state
        entity_id: light.bedroom
        to: "on"
    actions:
      - action: light.turn_on
        target:
          entity_id: light.bedroom
        data:
          brightness_pct: >
            {% set hour = now().hour %}
            {% if hour < 7 %}
              10
            {% elif hour < 9 %}
              50
            {% elif hour < 20 %}
              100
            {% elif hour < 22 %}
              50
            {% else %}
              10
            {% endif %}
```

### Doorbell with Camera Snapshot

```yaml
automation:
  - id: doorbell_snapshot
    alias: "Doorbell with Snapshot"
    triggers:
      - trigger: state
        entity_id: binary_sensor.doorbell
        to: "on"
    actions:
      - action: camera.snapshot
        target:
          entity_id: camera.front_door
        data:
          filename: "/config/www/snapshots/doorbell_{{ now().strftime('%Y%m%d_%H%M%S') }}.jpg"
      - delay: "00:00:02"
      - action: notify.mobile_app
        data:
          title: "Doorbell"
          message: "Someone is at the door"
          data:
            image: "/local/snapshots/doorbell_{{ now().strftime('%Y%m%d_%H%M%S') }}.jpg"
```

---

## Best Practices

### Naming Conventions

```yaml
# Use snake_case for IDs
id: motion_light_living_room   # Good
id: MotionLightLivingRoom      # Avoid

# Use descriptive aliases
alias: "Motion Light - Living Room"  # Good
alias: "Automation 1"                 # Avoid

# Group related automations
id: climate_morning_schedule
id: climate_evening_schedule
id: climate_away_mode
```

### Organization

1. **Split by domain** - Group automations by function
2. **Use packages** - Organize related entities together
3. **Document complex logic** - Use `description` field

### Performance

```yaml
# Debounce rapid triggers
triggers:
  - trigger: state
    entity_id: sensor.power
    for: "00:00:05"  # Wait 5 seconds before triggering

# Avoid unnecessary polling
# Use event-based triggers instead of time_pattern when possible

# Limit parallel executions
mode: queued
max: 5
```

### Security

```yaml
# Validate webhook data
triggers:
  - trigger: webhook
    webhook_id: !secret webhook_id
    local_only: true  # Only accept local requests

# Use secrets for sensitive data
# Don't expose automation IDs publicly
```

---

## Troubleshooting

### Automation Not Triggering

| Check | Solution |
|-------|----------|
| Entity exists | Verify entity_id in Developer Tools |
| State matches | Check exact state string (case-sensitive) |
| Conditions pass | Test each condition separately |
| Automation enabled | Check toggle in UI |

### Template Errors

```jinja2
# Common mistakes:

# Missing quotes
state: on           # Wrong
state: "on"         # Correct

# Float conversion without default
{{ states('sensor.temp') | float }}      # May error
{{ states('sensor.temp') | float(0) }}   # Safe

# Missing namespace
{{ state_attr('light.x', 'brightness') }}  # Correct
{{ light.x.attributes.brightness }}        # Wrong
```

### Action Not Executing

| Check | Solution |
|-------|----------|
| Action exists | Verify in Developer Tools -> Actions |
| Target valid | Ensure entity_id/area_id is correct |
| Data format | Check data types match action requirements |
| Previous action | Look for errors in earlier actions |

### Debug Actions

```yaml
actions:
  # Log for debugging
  - action: system_log.write
    data:
      message: "Debug: {{ trigger.entity_id }} = {{ trigger.to_state.state }}"
      level: warning

  # Persistent notification
  - action: persistent_notification.create
    data:
      title: "Automation Debug"
      message: "Triggered at {{ now() }}"
```

### Using Traces

1. Run the automation
2. Open Traces in UI
3. Check each step for:
   - Input values
   - Output/result
   - Error messages
4. Identify where failure occurs
