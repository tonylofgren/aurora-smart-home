# Home Assistant Triggers Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [State Trigger](#state-trigger)
- [Numeric State Trigger](#numeric-state-trigger)
- [Time Trigger](#time-trigger)
- [Time Pattern Trigger](#time-pattern-trigger)
- [Sun Trigger](#sun-trigger)
- [Zone Trigger](#zone-trigger)
- [Event Trigger](#event-trigger)
- [MQTT Trigger](#mqtt-trigger)
- [Webhook Trigger](#webhook-trigger)
- [Device Trigger](#device-trigger)
- [Calendar Trigger](#calendar-trigger)
- [Template Trigger](#template-trigger)
- [Tag Trigger](#tag-trigger)
- [Conversation Trigger](#conversation-trigger)
- [Persistent Notification Trigger](#persistent-notification-trigger)
- [Geo Location Trigger](#geo-location-trigger)
- [Multiple Triggers](#multiple-triggers)
- [Trigger Variables](#trigger-variables)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Triggers define WHEN an automation should run. When a trigger fires, conditions are checked, and if they pass, actions execute.

### Key Terms

| Term | Description |
|------|-------------|
| **Trigger** | Event that starts an automation |
| **Platform** | Type of trigger (state, time, etc.) |
| **Trigger ID** | Identifier for distinguishing triggers |
| **Trigger Variables** | Data available in conditions/actions |

### Trigger Structure

```yaml
automation:
  - id: example
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
    condition: []
    action: []
```

### Trigger ID

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "on"
    id: motion_detected  # Use in conditions/actions
```

---

## State Trigger

Fire when an entity's state changes.

### Basic State Change

```yaml
triggers:
  - trigger: state
    entity_id: light.living_room
```

### To Specific State

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "on"
```

### From Specific State

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    from: "off"
    to: "on"
```

### Multiple States (OR)

```yaml
triggers:
  - trigger: state
    entity_id: vacuum.robot
    to:
      - cleaning
      - returning
```

### Multiple Entities

```yaml
triggers:
  - trigger: state
    entity_id:
      - binary_sensor.motion_living
      - binary_sensor.motion_kitchen
    to: "on"
```

### With Duration (for)

```yaml
# Trigger only after entity has been in state for duration
triggers:
  - trigger: state
    entity_id: binary_sensor.door
    to: "on"
    for: "00:10:00"

# Dynamic duration
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "off"
    for:
      minutes: "{{ states('input_number.motion_timeout') | int }}"
```

### Attribute Change

```yaml
triggers:
  - trigger: state
    entity_id: light.living_room
    attribute: brightness

# Specific attribute value
triggers:
  - trigger: state
    entity_id: media_player.tv
    attribute: source
    to: "HDMI 1"
```

### Not From/To (any change)

```yaml
# Any state change except to/from unavailable
triggers:
  - trigger: state
    entity_id: sensor.temperature
    not_from:
      - unknown
      - unavailable
    not_to:
      - unknown
      - unavailable
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `entity_id` | string/list | Entity or entities to watch |
| `to` | string/list | Target state(s) |
| `from` | string/list | Source state(s) |
| `not_to` | string/list | States to exclude as target |
| `not_from` | string/list | States to exclude as source |
| `for` | time/template | Duration in state before firing |
| `attribute` | string | Watch specific attribute |
| `id` | string | Trigger identifier |

---

## Numeric State Trigger

Fire when a numeric value crosses a threshold.

### Above Threshold

```yaml
triggers:
  - trigger: numeric_state
    entity_id: sensor.temperature
    above: 25
```

### Below Threshold

```yaml
triggers:
  - trigger: numeric_state
    entity_id: sensor.battery
    below: 20
```

### Within Range

```yaml
# Fires when value enters the range
triggers:
  - trigger: numeric_state
    entity_id: sensor.humidity
    above: 30
    below: 70
```

### With Duration

```yaml
triggers:
  - trigger: numeric_state
    entity_id: sensor.power
    above: 1000
    for: "00:05:00"
```

### Attribute Value

```yaml
triggers:
  - trigger: numeric_state
    entity_id: light.living_room
    attribute: brightness
    above: 200
```

### Template Threshold

```yaml
triggers:
  - trigger: numeric_state
    entity_id: sensor.outdoor_temp
    above: "{{ states('input_number.temp_threshold') | float }}"
```

### Value Template

```yaml
# Transform value before comparison
triggers:
  - trigger: numeric_state
    entity_id: sensor.power
    value_template: "{{ state.state | float * 0.001 }}"  # Convert W to kW
    above: 5
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `entity_id` | string/list | Entity to monitor |
| `above` | number/template | Threshold to exceed |
| `below` | number/template | Threshold to go under |
| `for` | time/template | Duration above/below before firing |
| `attribute` | string | Monitor specific attribute |
| `value_template` | template | Transform value before comparison |
| `id` | string | Trigger identifier |

---

## Time Trigger

Fire at a specific time.

### Fixed Time

```yaml
triggers:
  - trigger: time
    at: "07:00:00"
```

### Multiple Times

```yaml
triggers:
  - trigger: time
    at:
      - "08:00:00"
      - "12:00:00"
      - "18:00:00"
```

### Using Input Datetime

```yaml
triggers:
  - trigger: time
    at: input_datetime.alarm_time
```

### Multiple Input Datetimes

```yaml
triggers:
  - trigger: time
    at:
      - input_datetime.morning_alarm
      - input_datetime.evening_alarm
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `at` | time/entity/list | Time(s) to trigger |
| `id` | string | Trigger identifier |

---

## Time Pattern Trigger

Fire on a recurring pattern.

### Every Minute

```yaml
triggers:
  - trigger: time_pattern
    minutes: "*"
```

### Every 5 Minutes

```yaml
triggers:
  - trigger: time_pattern
    minutes: "/5"
```

### Every Hour

```yaml
triggers:
  - trigger: time_pattern
    hours: "*"
    minutes: "0"
```

### Specific Minutes

```yaml
triggers:
  - trigger: time_pattern
    minutes: "15"  # At :15 every hour
```

### Every 30 Seconds

```yaml
triggers:
  - trigger: time_pattern
    seconds: "/30"
```

### Complex Pattern

```yaml
# At minute 0 and 30 of every hour
triggers:
  - trigger: time_pattern
    minutes: "0,30"
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `hours` | string | Hour pattern (`*`, `/N`, `N`, `N,N`) |
| `minutes` | string | Minute pattern |
| `seconds` | string | Second pattern |
| `id` | string | Trigger identifier |

---

## Sun Trigger

Fire at sunrise or sunset.

### At Sunset

```yaml
triggers:
  - trigger: sun
    event: sunset
```

### At Sunrise

```yaml
triggers:
  - trigger: sun
    event: sunrise
```

### With Offset

```yaml
# 30 minutes before sunset
triggers:
  - trigger: sun
    event: sunset
    offset: "-00:30:00"

# 1 hour after sunrise
triggers:
  - trigger: sun
    event: sunrise
    offset: "01:00:00"
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `event` | string | `sunrise` or `sunset` |
| `offset` | time | Time offset (positive or negative) |
| `id` | string | Trigger identifier |

---

## Zone Trigger

Fire when entity enters or leaves a zone.

### Enter Zone

```yaml
triggers:
  - trigger: zone
    entity_id: person.john
    zone: zone.home
    event: enter
```

### Leave Zone

```yaml
triggers:
  - trigger: zone
    entity_id: person.john
    zone: zone.home
    event: leave
```

### Multiple Entities

```yaml
triggers:
  - trigger: zone
    entity_id:
      - person.john
      - person.jane
    zone: zone.work
    event: enter
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `entity_id` | string/list | Person or device_tracker |
| `zone` | string | Zone entity |
| `event` | string | `enter` or `leave` |
| `id` | string | Trigger identifier |

---

## Event Trigger

Fire when a specific event occurs.

### Basic Event

```yaml
triggers:
  - trigger: event
    event_type: my_custom_event
```

### With Event Data

```yaml
triggers:
  - trigger: event
    event_type: call_service
    event_data:
      domain: light
      service: turn_on
```

### Mobile App Notification Action

```yaml
triggers:
  - trigger: event
    event_type: mobile_app_notification_action
    event_data:
      action: OPEN_DOOR
```

### Home Assistant Events

```yaml
# Home Assistant started
triggers:
  - trigger: event
    event_type: homeassistant_started

# Script started
triggers:
  - trigger: event
    event_type: script_started
    event_data:
      entity_id: script.morning_routine

# Automation triggered
triggers:
  - trigger: event
    event_type: automation_triggered
```

### Timer Events

```yaml
# Timer finished
triggers:
  - trigger: event
    event_type: timer.finished
    event_data:
      entity_id: timer.laundry

# Timer started
triggers:
  - trigger: event
    event_type: timer.started
    event_data:
      entity_id: timer.cooking
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `event_type` | string | Event type to listen for |
| `event_data` | dict | Filter by event data |
| `id` | string | Trigger identifier |

---

## MQTT Trigger

Fire when an MQTT message is received.

### Basic MQTT

```yaml
triggers:
  - trigger: mqtt
    topic: "home/doorbell"
```

### With Payload

```yaml
triggers:
  - trigger: mqtt
    topic: "home/doorbell"
    payload: "pressed"
```

### JSON Payload Template

```yaml
triggers:
  - trigger: mqtt
    topic: "sensors/temperature"
    value_template: "{{ value_json.temperature }}"
```

### Wildcard Topics

```yaml
triggers:
  - trigger: mqtt
    topic: "home/+/status"  # Single-level wildcard

triggers:
  - trigger: mqtt
    topic: "home/#"  # Multi-level wildcard
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `topic` | string | MQTT topic to subscribe |
| `payload` | string | Expected payload (optional) |
| `value_template` | template | Extract value from payload |
| `qos` | int | QoS level (0, 1, 2) |
| `encoding` | string | Payload encoding |
| `id` | string | Trigger identifier |

---

## Webhook Trigger

Fire when an HTTP request is received.

### Basic Webhook

```yaml
triggers:
  - trigger: webhook
    webhook_id: my_unique_webhook_id
```

### With Allowed Methods

```yaml
triggers:
  - trigger: webhook
    webhook_id: my_webhook
    allowed_methods:
      - POST
      - PUT
```

### Local Only

```yaml
triggers:
  - trigger: webhook
    webhook_id: my_webhook
    local_only: true
```

### Usage

```bash
# Call webhook
curl -X POST https://your-ha-instance/api/webhook/my_unique_webhook_id

# With data
curl -X POST https://your-ha-instance/api/webhook/my_webhook \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `webhook_id` | string | Unique webhook identifier |
| `allowed_methods` | list | HTTP methods (GET, POST, PUT, etc.) |
| `local_only` | bool | Only allow local requests |
| `id` | string | Trigger identifier |

---

## Device Trigger

Fire on device-specific events.

### Button Press

```yaml
triggers:
  - trigger: device
    device_id: abc123def456
    domain: zha
    type: remote_button_short_press
    subtype: button_1
```

### Motion Detected

```yaml
triggers:
  - trigger: device
    device_id: abc123def456
    domain: binary_sensor
    type: motion
```

### Battery Low

```yaml
triggers:
  - trigger: device
    device_id: abc123def456
    domain: sensor
    type: battery_level
    below: 20
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `device_id` | string | Device identifier |
| `domain` | string | Entity domain |
| `type` | string | Trigger type |
| `subtype` | string | Trigger subtype (e.g., button number) |
| `id` | string | Trigger identifier |

---

## Calendar Trigger

Fire on calendar events.

### Event Starts

```yaml
triggers:
  - trigger: calendar
    entity_id: calendar.family
    event: start
```

### Event Ends

```yaml
triggers:
  - trigger: calendar
    entity_id: calendar.family
    event: end
```

### With Offset

```yaml
# 15 minutes before event starts
triggers:
  - trigger: calendar
    entity_id: calendar.work
    event: start
    offset: "-00:15:00"
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `entity_id` | string | Calendar entity |
| `event` | string | `start` or `end` |
| `offset` | time | Time before/after event |
| `id` | string | Trigger identifier |

---

## Template Trigger

Fire when a template evaluates to true.

### Basic Template

```yaml
triggers:
  - trigger: template
    value_template: "{{ states('sensor.temperature') | float > 25 }}"
```

### Complex Condition

```yaml
triggers:
  - trigger: template
    value_template: >
      {{ is_state('binary_sensor.motion', 'on') and
         states('sensor.illuminance') | float < 50 and
         is_state('input_boolean.enabled', 'on') }}
```

### With Duration

```yaml
triggers:
  - trigger: template
    value_template: "{{ states('sensor.power') | float > 1000 }}"
    for: "00:05:00"
```

### Time-Based

```yaml
triggers:
  - trigger: template
    value_template: "{{ now().hour == 7 and now().minute == 0 }}"
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `value_template` | template | Template that returns true/false |
| `for` | time/template | Duration template must be true |
| `id` | string | Trigger identifier |

---

## Tag Trigger

Fire when an NFC tag is scanned.

### Basic Tag

```yaml
triggers:
  - trigger: tag
    tag_id: my_tag_id
```

### Specific Device

```yaml
triggers:
  - trigger: tag
    tag_id: my_tag_id
    device_id: abc123def456
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `tag_id` | string/list | Tag identifier(s) |
| `device_id` | string/list | Device(s) that scanned |
| `id` | string | Trigger identifier |

---

## Conversation Trigger

Fire on voice commands.

### Basic Sentence

```yaml
triggers:
  - trigger: conversation
    command: "turn on the lights"
```

### With Wildcards

```yaml
triggers:
  - trigger: conversation
    command:
      - "turn on [the] {area} lights"
      - "lights on [in] {area}"
```

### Multiple Commands

```yaml
triggers:
  - trigger: conversation
    command:
      - "goodnight"
      - "good night"
      - "time for bed"
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `command` | string/list | Sentence(s) to match |
| `id` | string | Trigger identifier |

---

## Persistent Notification Trigger

Fire on persistent notification events.

### Notification Created

```yaml
triggers:
  - trigger: persistent_notification
    update_type: added
```

### Specific Notification

```yaml
triggers:
  - trigger: persistent_notification
    notification_id: my_notification
    update_type: added
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `notification_id` | string | Specific notification ID |
| `update_type` | string | `added`, `removed`, `current` |
| `id` | string | Trigger identifier |

---

## Geo Location Trigger

Fire when geo location source enters/leaves zone.

### Enter Zone

```yaml
triggers:
  - trigger: geo_location
    source: usgs_earthquakes_feed
    zone: zone.home
    event: enter
```

### Leave Zone

```yaml
triggers:
  - trigger: geo_location
    source: usgs_earthquakes_feed
    zone: zone.home
    event: leave
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `source` | string | Geo location source |
| `zone` | string | Zone entity |
| `event` | string | `enter` or `leave` |
| `id` | string | Trigger identifier |

---

## Multiple Triggers

Combine multiple triggers in one automation.

### Multiple Triggers (OR)

```yaml
# Any trigger fires the automation
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "on"
  - trigger: state
    entity_id: binary_sensor.door
    to: "on"
```

### With Trigger IDs

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "on"
    id: motion
  - trigger: state
    entity_id: binary_sensor.door
    to: "on"
    id: door
conditions:
  - condition: trigger
    id: motion
actions:
  # Only runs for motion trigger
```

### Different Actions per Trigger

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "on"
    id: motion_on
  - trigger: state
    entity_id: binary_sensor.motion
    to: "off"
    for: "00:05:00"
    id: motion_off
actions:
  - choose:
      - conditions:
          - condition: trigger
            id: motion_on
        sequence:
          - action: light.turn_on
      - conditions:
          - condition: trigger
            id: motion_off
        sequence:
          - action: light.turn_off
```

---

## Trigger Variables

Access trigger data in conditions and actions.

### Common Trigger Variables

```jinja2
# Available for all triggers
{{ trigger.platform }}      # Trigger type
{{ trigger.id }}           # Trigger ID (if set)
{{ trigger.idx }}          # Trigger index (0-based)
{{ trigger.alias }}        # Trigger alias (if set)
```

### State Trigger Variables

```jinja2
{{ trigger.entity_id }}           # Entity that triggered
{{ trigger.from_state }}          # Previous state object
{{ trigger.from_state.state }}    # Previous state value
{{ trigger.to_state }}            # New state object
{{ trigger.to_state.state }}      # New state value
{{ trigger.for }}                 # Duration (if 'for' was used)

# Attributes
{{ trigger.to_state.attributes.brightness }}
{{ trigger.from_state.attributes.friendly_name }}
```

### Numeric State Variables

```jinja2
{{ trigger.entity_id }}
{{ trigger.from_state }}
{{ trigger.to_state }}
{{ trigger.for }}
{{ trigger.above }}               # Threshold value
{{ trigger.below }}               # Threshold value
```

### Event Trigger Variables

```jinja2
{{ trigger.event }}               # Event object
{{ trigger.event.event_type }}    # Event type
{{ trigger.event.data }}          # Event data
{{ trigger.event.data.key }}      # Specific data field
{{ trigger.event.origin }}        # Origin (local/remote)
{{ trigger.event.time_fired }}    # Timestamp
```

### MQTT Trigger Variables

```jinja2
{{ trigger.topic }}               # MQTT topic
{{ trigger.payload }}             # Raw payload
{{ trigger.payload_json }}        # Parsed JSON payload
{{ trigger.qos }}                 # QoS level
```

### Webhook Trigger Variables

```jinja2
{{ trigger.json }}                # JSON body
{{ trigger.data }}                # Form data
{{ trigger.query }}               # Query parameters
```

### Calendar Trigger Variables

```jinja2
{{ trigger.calendar_event }}      # Calendar event object
{{ trigger.calendar_event.summary }}
{{ trigger.calendar_event.start }}
{{ trigger.calendar_event.end }}
{{ trigger.calendar_event.description }}
{{ trigger.calendar_event.location }}
```

### Zone Trigger Variables

```jinja2
{{ trigger.entity_id }}           # Person/device tracker
{{ trigger.from_state }}
{{ trigger.to_state }}
{{ trigger.zone }}                # Zone entity
{{ trigger.event }}               # enter or leave
```

### Tag Trigger Variables

```jinja2
{{ trigger.tag_id }}              # Tag identifier
{{ trigger.device_id }}           # Scanning device
```

### Example Usage

```yaml
automation:
  - id: state_change_notification
    triggers:
      - trigger: state
        entity_id: binary_sensor.door
    actions:
      - action: notify.mobile_app
        data:
          title: "State Change"
          message: >
            {{ trigger.to_state.attributes.friendly_name }}
            changed from {{ trigger.from_state.state }}
            to {{ trigger.to_state.state }}
```

---

## Common Patterns

### Motion Light with Off Timer

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "on"
    id: motion_on
  - trigger: state
    entity_id: binary_sensor.motion
    to: "off"
    for: "00:05:00"
    id: motion_off
actions:
  - choose:
      - conditions:
          - condition: trigger
            id: motion_on
        sequence:
          - action: light.turn_on
            target:
              entity_id: light.hallway
      - conditions:
          - condition: trigger
            id: motion_off
        sequence:
          - action: light.turn_off
            target:
              entity_id: light.hallway
```

### Sunrise/Sunset Blinds

```yaml
triggers:
  - trigger: sun
    event: sunrise
    offset: "00:30:00"
    id: morning
  - trigger: sun
    event: sunset
    offset: "-00:30:00"
    id: evening
actions:
  - choose:
      - conditions:
          - condition: trigger
            id: morning
        sequence:
          - action: cover.open_cover
            target:
              entity_id: cover.living_room
      - conditions:
          - condition: trigger
            id: evening
        sequence:
          - action: cover.close_cover
            target:
              entity_id: cover.living_room
```

### Button Press Handler

```yaml
triggers:
  - trigger: event
    event_type: zha_event
    event_data:
      device_id: abc123
      command: "on"
    id: single
  - trigger: event
    event_type: zha_event
    event_data:
      device_id: abc123
      command: "off"
    id: double
actions:
  - choose:
      - conditions:
          - condition: trigger
            id: single
        sequence:
          - action: light.toggle
            target:
              entity_id: light.desk
      - conditions:
          - condition: trigger
            id: double
        sequence:
          - action: scene.turn_on
            target:
              entity_id: scene.work_mode
```

### Debounced Sensor

```yaml
# Only trigger if value stable for 1 minute
triggers:
  - trigger: numeric_state
    entity_id: sensor.temperature
    above: 25
    for: "00:01:00"
```

### Presence-Based Welcome

```yaml
triggers:
  - trigger: zone
    entity_id: person.john
    zone: zone.home
    event: enter
conditions:
  - condition: state
    entity_id: input_boolean.welcome_enabled
    state: "on"
  - condition: template
    value_template: >
      {{ (now() - state_attr('automation.welcome_home', 'last_triggered')).total_seconds() > 3600 }}
actions:
  - action: tts.speak
    target:
      entity_id: tts.google
    data:
      message: "Welcome home, {{ trigger.entity_id.split('.')[1] | replace('_', ' ') | title }}"
      media_player_entity_id: media_player.speaker
```

---

## Best Practices

### Use Trigger IDs

```yaml
# Always use IDs when you have multiple triggers
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "on"
    id: motion  # Descriptive ID
```

### Avoid Overly Broad Triggers

```yaml
# Bad: Triggers on ANY state change
triggers:
  - trigger: state
    entity_id: sensor.temperature

# Good: Specific threshold
triggers:
  - trigger: numeric_state
    entity_id: sensor.temperature
    above: 25
```

### Use Duration for Stability

```yaml
# Avoid false triggers from sensor noise
triggers:
  - trigger: numeric_state
    entity_id: sensor.power
    above: 1000
    for: "00:00:30"  # Must be above for 30 seconds
```

### Filter Unavailable States

```yaml
triggers:
  - trigger: state
    entity_id: sensor.temperature
    not_from:
      - unknown
      - unavailable
    not_to:
      - unknown
      - unavailable
```

### Document Complex Triggers

```yaml
triggers:
  # Motion detected in living room
  # Only triggers if motion was previously off
  - trigger: state
    entity_id: binary_sensor.living_room_motion
    from: "off"
    to: "on"
    id: motion_living
```

---

## Troubleshooting

### Trigger Not Firing

| Problem | Cause | Solution |
|---------|-------|----------|
| Wrong state value | States are strings | Use `"on"` not `on` |
| Entity unavailable | Entity not ready | Add `not_from: unavailable` |
| For duration not met | Entity changed too fast | Reduce `for` duration |
| Wrong entity_id | Typo in entity | Check entity in Developer Tools |

### Debug Triggers

```yaml
# Log all trigger data
automation:
  - id: debug_trigger
    triggers:
      - trigger: state
        entity_id: binary_sensor.test
    actions:
      - action: system_log.write
        data:
          message: >
            Trigger fired!
            Platform: {{ trigger.platform }}
            Entity: {{ trigger.entity_id }}
            From: {{ trigger.from_state.state }}
            To: {{ trigger.to_state.state }}
          level: info
```

### Check Trigger in Trace

```yaml
# Settings > Automations > (automation) > Traces
# Shows:
# - Which trigger fired
# - Trigger variables
# - Timestamp
```

### Common Mistakes

```jinja2
# Wrong: Boolean values not quoted
triggers:
  - trigger: state
    entity_id: switch.test
    to: on  # YAML boolean, not string "on"

# Correct
triggers:
  - trigger: state
    entity_id: switch.test
    to: "on"

# Wrong: Time without leading zero
triggers:
  - trigger: time
    at: "7:00"  # May not work

# Correct
triggers:
  - trigger: time
    at: "07:00:00"

# Wrong: Missing quotes in template
triggers:
  - trigger: template
    value_template: {{ is_state('light.test', 'on') }}  # Missing quotes

# Correct
triggers:
  - trigger: template
    value_template: "{{ is_state('light.test', 'on') }}"
```

### Test Triggers Manually

```yaml
# Developer Tools > Actions
# automation.trigger
action: automation.trigger
target:
  entity_id: automation.test_automation
data:
  skip_condition: true  # Skip conditions, run actions directly
```
