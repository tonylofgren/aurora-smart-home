# Home Assistant Actions Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Service Calls](#service-calls)
- [Response Variables](#response-variables)
- [Delay](#delay)
- [Wait Template](#wait-template)
- [Wait for Trigger](#wait-for-trigger)
- [Choose](#choose)
- [If Then Else](#if-then-else)
- [Repeat](#repeat)
- [Parallel](#parallel)
- [Stop](#stop)
- [Variables](#variables)
- [Fire Event](#fire-event)
- [Device Actions](#device-actions)
- [Scene Actions](#scene-actions)
- [Dashboard Actions](#dashboard-actions)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Actions are the things that happen when an automation runs. They execute in sequence unless you use parallel actions.

### Key Terms

| Term | Description |
|------|-------------|
| **Action** | Single step in automation sequence |
| **Service** | Function to call on entity/domain |
| **Target** | Entity/area/device to act on |
| **Data** | Parameters for the service call |
| **Sequence** | Ordered list of actions |

### Action Structure

```yaml
actions:
  # Actions run in sequence
  - action: light.turn_on
    target:
      entity_id: light.living_room
  - delay: "00:00:05"
  - action: light.turn_off
    target:
      entity_id: light.living_room
```

---

## Service Calls

Call Home Assistant services to control entities.

### Basic Service Call

```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.living_room
```

### With Data

```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.living_room
    data:
      brightness_pct: 80
      color_temp: 400
```

### Target Options

```yaml
# Single entity
target:
  entity_id: light.living_room

# Multiple entities
target:
  entity_id:
    - light.living_room
    - light.kitchen

# By area
target:
  area_id: living_room

# By device
target:
  device_id: abc123def456

# Combined (all receive the service call)
target:
  entity_id: light.hallway
  area_id: bedroom
```

### Dynamic Entity (Template)

```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: "{{ trigger.entity_id }}"

# Multiple dynamic entities
actions:
  - action: light.turn_off
    target:
      entity_id: >
        {{ states.light
           | selectattr('state', 'eq', 'on')
           | map(attribute='entity_id')
           | list }}
```

### Dynamic Service

```yaml
actions:
  - action: "light.turn_{{ 'on' if is_state('sun.sun', 'below_horizon') else 'off' }}"
    target:
      entity_id: light.porch
```

### Template Data

```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.bedroom
    data:
      brightness_pct: >
        {% if now().hour < 7 %}
          20
        {% elif now().hour < 21 %}
          100
        {% else %}
          50
        {% endif %}
```

### Common Services

```yaml
# Lights
- action: light.turn_on
  target:
    entity_id: light.lamp
  data:
    brightness_pct: 80
    transition: 2

- action: light.turn_off

- action: light.toggle

# Switches
- action: switch.turn_on
- action: switch.turn_off
- action: switch.toggle

# Climate
- action: climate.set_temperature
  target:
    entity_id: climate.thermostat
  data:
    temperature: 22

- action: climate.set_hvac_mode
  data:
    hvac_mode: heat

# Media player
- action: media_player.play_media
  target:
    entity_id: media_player.speaker
  data:
    media_content_id: "spotify:playlist:123"
    media_content_type: playlist

# Notifications
- action: notify.mobile_app_phone
  data:
    title: "Alert"
    message: "Motion detected"

# Scripts
- action: script.turn_on
  target:
    entity_id: script.morning_routine

# Scenes
- action: scene.turn_on
  target:
    entity_id: scene.movie_mode
```

### Response Variable

```yaml
# Capture service response
actions:
  - action: weather.get_forecasts
    target:
      entity_id: weather.home
    data:
      type: daily
    response_variable: forecast
  - action: notify.mobile_app
    data:
      message: "Tomorrow: {{ forecast['weather.home'].forecast[0].condition }}"
```

---

## Response Variables

**Source:** https://www.home-assistant.io/actions/

Certain actions return structured data when called. Store that data in a named variable using the `response_variable:` key, then reference the variable in subsequent template steps within the same automation or script run.

Not all actions produce responses. The ones that do include `weather.get_forecasts`, `calendar.get_events`, `todo.get_items`, and some integration-specific actions. Check Developer Tools or the action's documentation to confirm a response is available.

The returned data structure is action-specific. Use automation traces to inspect the exact shape before building templates against it.

### Calendar events worked example

Fetch upcoming calendar events and send a summary notification:

```yaml
actions:
  - action: calendar.get_events
    target:
      entity_id: calendar.family
    data:
      duration:
        hours: 24
    response_variable: todays_events

  - action: notify.notify
    data:
      title: "Today's schedule"
      message: >
        {% set items = todays_events['calendar.family'].events %}
        {% if items %}
          {{ items | length }} event(s). First: {{ items[0].summary }} at {{ items[0].start }}.
        {% else %}
          Nothing on the calendar today.
        {% endif %}
```

### Weather forecast example

```yaml
actions:
  - action: weather.get_forecasts
    target:
      entity_id: weather.home
    data:
      type: daily
    response_variable: forecast

  - action: notify.notify
    data:
      message: >
        Tomorrow: {{ forecast['weather.home'].forecast[0].condition }},
        high {{ forecast['weather.home'].forecast[0].temperature }}.
```

### Key rules

- The variable is only available within the same automation or script run; it does not persist between runs.
- Use `| default([])` or guard with `{% if %}` before iterating, since an empty calendar returns an empty list rather than raising an error.
- When targeting multiple entities, each entity's results are keyed by its `entity_id` string inside the response dict.

---

## Delay

Pause execution for a duration.

### Fixed Delay

```yaml
actions:
  - delay: "00:00:30"  # 30 seconds

  - delay: "00:05:00"  # 5 minutes

  - delay: "01:00:00"  # 1 hour
```

### Structured Delay

```yaml
actions:
  - delay:
      hours: 1
      minutes: 30
      seconds: 0
      milliseconds: 0
```

### Template Delay

```yaml
actions:
  - delay:
      minutes: "{{ states('input_number.delay_minutes') | int }}"

  - delay: "{{ states('input_text.delay_duration') }}"
```

### Dynamic Duration

```yaml
actions:
  - delay:
      seconds: >
        {% if is_state('input_boolean.quick_mode', 'on') %}
          5
        {% else %}
          30
        {% endif %}
```

---

## Wait Template

Wait until a condition becomes true.

### Basic Wait Template

```yaml
actions:
  - wait_template: "{{ is_state('binary_sensor.door', 'off') }}"
```

### With Timeout

```yaml
actions:
  - wait_template: "{{ is_state('binary_sensor.motion', 'off') }}"
    timeout: "00:10:00"
    continue_on_timeout: true  # Continue if timeout reached
```

### Check If Timed Out

```yaml
actions:
  - wait_template: "{{ is_state('lock.door', 'locked') }}"
    timeout: "00:01:00"
    continue_on_timeout: true
  - if:
      - condition: template
        value_template: "{{ wait.completed }}"
    then:
      - action: notify.mobile_app
        data:
          message: "Door is locked"
    else:
      - action: notify.mobile_app
        data:
          message: "Door lock timed out!"
```

### Complex Wait Condition

```yaml
actions:
  - wait_template: >
      {{ is_state('binary_sensor.motion', 'off') and
         is_state('binary_sensor.door', 'off') }}
    timeout: "00:05:00"
```

---

## Wait for Trigger

Wait for a specific event to occur.

### Basic Wait for Trigger

```yaml
actions:
  - wait_for_trigger:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "off"
```

### With Timeout

```yaml
actions:
  - wait_for_trigger:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "off"
        for: "00:05:00"
    timeout: "00:30:00"
    continue_on_timeout: true
```

### Multiple Triggers

```yaml
actions:
  - wait_for_trigger:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "off"
        id: motion_off
      - trigger: state
        entity_id: input_boolean.override
        to: "on"
        id: override
    timeout: "00:10:00"
  - choose:
      - conditions: "{{ wait.trigger.id == 'motion_off' }}"
        sequence:
          - action: light.turn_off
      - conditions: "{{ wait.trigger.id == 'override' }}"
        sequence:
          - action: notify.mobile_app
            data:
              message: "Override activated"
```

### Access Wait Trigger Data

```yaml
actions:
  - wait_for_trigger:
      - trigger: state
        entity_id: sensor.temperature
    timeout: "01:00:00"
  - action: notify.mobile_app
    data:
      message: >
        Temperature changed to {{ wait.trigger.to_state.state }}°C
```

---

## Choose

Execute different actions based on conditions.

### Basic Choose

```yaml
actions:
  - choose:
      - conditions:
          - condition: state
            entity_id: input_select.mode
            state: "Home"
        sequence:
          - action: light.turn_on
            target:
              entity_id: light.living_room
      - conditions:
          - condition: state
            entity_id: input_select.mode
            state: "Away"
        sequence:
          - action: light.turn_off
            target:
              entity_id: all
```

### With Default

```yaml
actions:
  - choose:
      - conditions:
          - condition: numeric_state
            entity_id: sensor.temperature
            above: 25
        sequence:
          - action: climate.set_hvac_mode
            data:
              hvac_mode: cool
      - conditions:
          - condition: numeric_state
            entity_id: sensor.temperature
            below: 18
        sequence:
          - action: climate.set_hvac_mode
            data:
              hvac_mode: heat
    default:
      - action: climate.set_hvac_mode
        data:
          hvac_mode: "off"
```

### Shorthand Conditions

```yaml
actions:
  - choose:
      - conditions: "{{ trigger.to_state.state == 'on' }}"
        sequence:
          - action: light.turn_on
      - conditions: "{{ trigger.to_state.state == 'off' }}"
        sequence:
          - action: light.turn_off
```

### Based on Trigger ID

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.motion_living
    to: "on"
    id: living
  - trigger: state
    entity_id: binary_sensor.motion_kitchen
    to: "on"
    id: kitchen
actions:
  - choose:
      - conditions:
          - condition: trigger
            id: living
        sequence:
          - action: light.turn_on
            target:
              entity_id: light.living_room
      - conditions:
          - condition: trigger
            id: kitchen
        sequence:
          - action: light.turn_on
            target:
              entity_id: light.kitchen
```

---

## If Then Else

Conditional execution with clearer syntax.

### Basic If

```yaml
actions:
  - if:
      - condition: state
        entity_id: input_boolean.notifications_enabled
        state: "on"
    then:
      - action: notify.mobile_app
        data:
          message: "Alert!"
```

### If Then Else

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

### Nested If

```yaml
actions:
  - if:
      - condition: state
        entity_id: binary_sensor.motion
        state: "on"
    then:
      - if:
          - condition: sun
            after: sunset
        then:
          - action: light.turn_on
            data:
              brightness_pct: 100
        else:
          - action: light.turn_on
            data:
              brightness_pct: 50
```

### Shorthand Condition

```yaml
actions:
  - if: "{{ is_state('binary_sensor.motion', 'on') }}"
    then:
      - action: light.turn_on
```

---

## Repeat

Loop actions multiple times.

### Repeat Count

```yaml
actions:
  - repeat:
      count: 3
      sequence:
        - action: light.toggle
          target:
            entity_id: light.alert
        - delay: "00:00:01"
```

### Repeat While

```yaml
actions:
  - repeat:
      while:
        - condition: state
          entity_id: binary_sensor.door
          state: "on"
        - condition: template
          value_template: "{{ repeat.index <= 10 }}"
      sequence:
        - action: notify.mobile_app
          data:
            message: "Door still open! (attempt {{ repeat.index }})"
        - delay: "00:01:00"
```

### Repeat Until

```yaml
actions:
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
        - condition: template
          value_template: "{{ repeat.index < 3 }}"  # Max 3 attempts
```

### Repeat For Each

```yaml
actions:
  - repeat:
      for_each:
        - light.living_room
        - light.kitchen
        - light.bedroom
      sequence:
        - action: light.turn_on
          target:
            entity_id: "{{ repeat.item }}"
        - delay: "00:00:01"
```

### For Each with Templates

```yaml
actions:
  - repeat:
      for_each: >
        {{ states.light
           | selectattr('state', 'eq', 'on')
           | map(attribute='entity_id')
           | list }}
      sequence:
        - action: light.turn_off
          target:
            entity_id: "{{ repeat.item }}"
        - delay: "00:00:00.5"
```

### Repeat Variables

```yaml
# Available in repeat block:
# repeat.index - Current iteration (1-based)
# repeat.first - True on first iteration
# repeat.last - True on last iteration (for_each only)
# repeat.item - Current item (for_each only)

actions:
  - repeat:
      count: 5
      sequence:
        - action: notify.mobile_app
          data:
            message: "Iteration {{ repeat.index }} of 5"
```

---

## Parallel

Run actions simultaneously.

### Basic Parallel

```yaml
actions:
  - parallel:
      - action: light.turn_on
        target:
          entity_id: light.living_room
      - action: light.turn_on
        target:
          entity_id: light.kitchen
      - action: media_player.turn_on
        target:
          entity_id: media_player.tv
```

### Parallel Sequences

```yaml
actions:
  - parallel:
      - sequence:
          - action: light.turn_on
            target:
              entity_id: light.living_room
          - delay: "00:00:05"
          - action: light.turn_off
            target:
              entity_id: light.living_room
      - sequence:
          - action: notify.mobile_app
            data:
              message: "Light sequence started"
```

### Mixed Parallel

```yaml
actions:
  - parallel:
      # Service call
      - action: light.turn_on
        target:
          entity_id: light.lamp
      # Sequence
      - sequence:
          - delay: "00:00:02"
          - action: switch.turn_on
            target:
              entity_id: switch.fan
      # Another service
      - action: media_player.volume_set
        target:
          entity_id: media_player.speaker
        data:
          volume_level: 0.5
```

---

## Stop

Stop automation execution.

### Basic Stop

```yaml
actions:
  - if:
      - condition: state
        entity_id: input_boolean.disabled
        state: "on"
    then:
      - stop: "Automation disabled by user"
  - action: light.turn_on
```

### Stop with Error

```yaml
actions:
  - if:
      - condition: template
        value_template: "{{ states('sensor.battery') | float < 10 }}"
    then:
      - stop: "Battery too low"
        error: true
```

### Stop in Choose

```yaml
actions:
  - choose:
      - conditions:
          - condition: state
            entity_id: alarm_control_panel.home
            state: armed_away
        sequence:
          - stop: "Cannot run while alarm is armed"
```

### Response Variables (for Scripts)

```yaml
script:
  calculate_something:
    sequence:
      - stop: "Calculation complete"
        response_variable: result
    variables:
      result: "{{ some_calculation }}"
```

---

## Variables

Define and use local variables.

### Set Variables

```yaml
actions:
  - variables:
      light_entity: light.living_room
      brightness: 80
  - action: light.turn_on
    target:
      entity_id: "{{ light_entity }}"
    data:
      brightness_pct: "{{ brightness }}"
```

### Dynamic Variables

```yaml
actions:
  - variables:
      target_temp: >
        {% if now().hour < 7 %}
          18
        {% elif now().hour < 22 %}
          22
        {% else %}
          20
        {% endif %}
  - action: climate.set_temperature
    target:
      entity_id: climate.thermostat
    data:
      temperature: "{{ target_temp }}"
```

### Variables from Trigger

```yaml
actions:
  - variables:
      entity: "{{ trigger.entity_id }}"
      old_state: "{{ trigger.from_state.state }}"
      new_state: "{{ trigger.to_state.state }}"
  - action: notify.mobile_app
    data:
      message: "{{ entity }} changed from {{ old_state }} to {{ new_state }}"
```

### Computed Variables

```yaml
actions:
  - variables:
      lights_on: >
        {{ states.light
           | selectattr('state', 'eq', 'on')
           | map(attribute='entity_id')
           | list }}
      count: "{{ lights_on | count }}"
  - action: notify.mobile_app
    data:
      message: "{{ count }} lights are on"
```

---

## Fire Event

Trigger custom events.

### Basic Event

```yaml
actions:
  - event: custom_event
    event_data:
      message: "Something happened"
```

### With Data

```yaml
actions:
  - event: motion_detected
    event_data:
      location: living_room
      timestamp: "{{ now().isoformat() }}"
      person: "{{ trigger.to_state.attributes.friendly_name }}"
```

### Listen for Event

```yaml
# In another automation
triggers:
  - trigger: event
    event_type: motion_detected
    event_data:
      location: living_room
actions:
  - action: notify.mobile_app
    data:
      message: "Motion in {{ trigger.event.data.location }}"
```

---

## Device Actions

Device-specific actions from the UI.

### Basic Device Action

```yaml
actions:
  - device_id: abc123def456
    domain: light
    type: turn_on
```

### With Options

```yaml
actions:
  - device_id: abc123def456
    domain: light
    type: turn_on
    brightness_pct: 80
```

### Multiple Devices

```yaml
actions:
  - device_id: abc123
    domain: cover
    type: close
  - device_id: def456
    domain: lock
    type: lock
```

---

## Scene Actions

Activate scenes.

### Activate Scene

```yaml
actions:
  - action: scene.turn_on
    target:
      entity_id: scene.movie_mode
```

### With Transition

```yaml
actions:
  - action: scene.turn_on
    target:
      entity_id: scene.evening
    data:
      transition: 5
```

### Create Scene on the Fly

```yaml
actions:
  - action: scene.create
    data:
      scene_id: before_change
      snapshot_entities:
        - light.living_room
        - light.kitchen
  # Make changes
  - action: light.turn_off
    target:
      entity_id: all
  - delay: "00:00:30"
  # Restore
  - action: scene.turn_on
    target:
      entity_id: scene.before_change
```

---

## Dashboard Actions

**Source:** https://www.home-assistant.io/actions/

Lovelace dashboard cards support interactive actions on `tap_action`, `hold_action`, and `double_tap_action`. Each accepts an `action:` key that names the behavior, plus any additional keys that behavior requires.

### Action types

| Action type | What it does |
|---|---|
| `more-info` | Opens the entity detail dialog. Default for most cards. |
| `toggle` | Toggles the card's primary entity where the domain supports toggling. |
| `perform-action` | Calls a Home Assistant action, equivalent to an automation action step. |
| `navigate` | Navigates to another dashboard path within the UI. |
| `url` | Opens a URL, optionally in a new browser tab. |
| `assist` | Opens the Assist voice/text dialog. |
| `none` | Does nothing. Useful for disabling the default tap behavior. |

### Examples for each type

#### more-info

```yaml
tap_action:
  action: more-info
```

#### toggle

```yaml
tap_action:
  action: toggle
```

#### perform-action

Calls any Home Assistant action. Use `perform_action:` for the action name, `target:` for entities/areas/devices, and `data:` for parameters.

```yaml
tap_action:
  action: perform-action
  perform_action: light.turn_on
  target:
    entity_id: light.living_room
  data:
    brightness_pct: 70
    transition: 1
```

#### navigate

```yaml
tap_action:
  action: navigate
  navigation_path: /lovelace/cameras
```

#### url

```yaml
tap_action:
  action: url
  url_path: https://home-assistant.io
```

#### assist

```yaml
tap_action:
  action: assist
```

#### none

```yaml
hold_action:
  action: none
```

### Confirmation dialog

For actions with significant side effects, attach a confirmation prompt. Use `confirmation: true` for a generic dialog, or `confirmation.text` to show a custom message.

```yaml
hold_action:
  action: perform-action
  perform_action: homeassistant.restart
  confirmation:
    text: "Restart Home Assistant? This will interrupt all automations."
```

```yaml
double_tap_action:
  action: perform-action
  perform_action: alarm_control_panel.alarm_disarm
  target:
    entity_id: alarm_control_panel.home
  data:
    code: !secret alarm_code
  confirmation:
    text: "Disarm the alarm?"
```

Treat restart, stop, alarm disarm, lock/unlock, and valve controls as high-impact actions that warrant confirmation dialogs in dashboards.

---

## Common Patterns

### Notification with Timeout

```yaml
actions:
  - action: notify.mobile_app
    data:
      title: "Door Open"
      message: "Front door has been open for 5 minutes"
      data:
        actions:
          - action: "ACKNOWLEDGE"
            title: "OK"
  - wait_for_trigger:
      - trigger: event
        event_type: mobile_app_notification_action
        event_data:
          action: ACKNOWLEDGE
      - trigger: state
        entity_id: binary_sensor.front_door
        to: "off"
    timeout: "00:05:00"
  - if:
      - condition: template
        value_template: "{{ not wait.completed }}"
    then:
      - action: notify.mobile_app
        data:
          message: "Door still open!"
```

### Retry Logic

```yaml
actions:
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
        - if:
            - condition: template
              value_template: "{{ repeat.index >= 3 }}"
          then:
            - action: notify.mobile_app
              data:
                message: "Failed to lock door after 3 attempts"
            - stop: "Lock failed"
```

### Fade Light

```yaml
actions:
  - variables:
      start: 100
      end: 0
      steps: 10
  - repeat:
      count: "{{ steps }}"
      sequence:
        - action: light.turn_on
          target:
            entity_id: light.bedroom
          data:
            brightness_pct: >
              {{ start - ((start - end) / steps * repeat.index) | int }}
        - delay: "00:00:01"
```

### Sequential Device Control

```yaml
actions:
  - repeat:
      for_each:
        - entity_id: light.light_1
          brightness: 100
        - entity_id: light.light_2
          brightness: 80
        - entity_id: light.light_3
          brightness: 60
      sequence:
        - action: light.turn_on
          target:
            entity_id: "{{ repeat.item.entity_id }}"
          data:
            brightness_pct: "{{ repeat.item.brightness }}"
        - delay: "00:00:00.5"
```

### Conditional Notification

```yaml
actions:
  - if:
      - condition: state
        entity_id: input_boolean.notifications_enabled
        state: "on"
    then:
      - choose:
          - conditions:
              - condition: state
                entity_id: person.john
                state: home
            sequence:
              - action: tts.speak
                target:
                  entity_id: tts.google
                data:
                  message: "{{ message }}"
                  media_player_entity_id: media_player.speaker
          - conditions:
              - condition: state
                entity_id: person.john
                state: not_home
            sequence:
              - action: notify.mobile_app
                data:
                  message: "{{ message }}"
```

### Save and Restore State

```yaml
actions:
  # Save current state
  - action: scene.create
    data:
      scene_id: temp_state
      snapshot_entities:
        - light.living_room
        - light.kitchen
  # Do something
  - action: light.turn_on
    target:
      area_id: living_room
    data:
      color_name: red
      brightness_pct: 100
  - delay: "00:00:10"
  # Restore
  - action: scene.turn_on
    target:
      entity_id: scene.temp_state
```

---

## Best Practices

### Use Meaningful Variable Names

```yaml
# Good
actions:
  - variables:
      target_brightness: 80
      notification_message: "Motion detected in {{ area }}"

# Avoid
actions:
  - variables:
      x: 80
      msg: "Motion"
```

### Handle Errors Gracefully

```yaml
actions:
  - if:
      - condition: template
        value_template: >
          {{ states('sensor.api_data') not in ['unknown', 'unavailable'] }}
    then:
      - action: notify.mobile_app
        data:
          message: "{{ states('sensor.api_data') }}"
    else:
      - action: system_log.write
        data:
          message: "API data unavailable"
          level: warning
```

### Avoid Long Delays

```yaml
# Avoid: Long blocking delay
actions:
  - delay: "01:00:00"  # Blocks for 1 hour
  - action: light.turn_off

# Better: Use wait_for_trigger with timeout
actions:
  - wait_for_trigger:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "off"
    timeout: "01:00:00"
  - action: light.turn_off
```

### Use Parallel for Independent Actions

```yaml
# Slow: Sequential
actions:
  - action: light.turn_on
    target:
      entity_id: light.1
  - action: light.turn_on
    target:
      entity_id: light.2
  - action: light.turn_on
    target:
      entity_id: light.3

# Fast: Parallel
actions:
  - parallel:
      - action: light.turn_on
        target:
          entity_id: light.1
      - action: light.turn_on
        target:
          entity_id: light.2
      - action: light.turn_on
        target:
          entity_id: light.3

# Best: Single call with multiple targets
actions:
  - action: light.turn_on
    target:
      entity_id:
        - light.1
        - light.2
        - light.3
```

---

## Troubleshooting

### Action Not Executing

| Problem | Cause | Solution |
|---------|-------|----------|
| Service not found | Typo in service name | Check service in Developer Tools |
| Entity not found | Wrong entity_id | Verify entity exists |
| No target | Missing target | Add target section |
| Invalid data | Wrong data format | Check service documentation |

### Debug Actions

```yaml
# Add logging
actions:
  - action: system_log.write
    data:
      message: "Starting action sequence"
      level: info
  - action: light.turn_on
    target:
      entity_id: light.test
  - action: system_log.write
    data:
      message: "Light turn_on called"
      level: info
```

### Check Service in Developer Tools

```yaml
# Go to Developer Tools > Actions
# Enter service name and parameters
# Click "Call Service" to test

action: light.turn_on
target:
  entity_id: light.living_room
data:
  brightness_pct: 80
```

### Common Mistakes

```jinja2
# Wrong: target inside data
actions:
  - action: light.turn_on
    data:
      entity_id: light.lamp  # Wrong location

# Correct: target separate from data
actions:
  - action: light.turn_on
    target:
      entity_id: light.lamp
    data:
      brightness_pct: 80

# Wrong: Missing quotes on template
actions:
  - delay:
      minutes: {{ states('input_number.delay') }}  # Missing quotes

# Correct
actions:
  - delay:
      minutes: "{{ states('input_number.delay') | int }}"
```

### Trace Analysis

```yaml
# Check automation trace:
# Settings > Automations > (automation) > Traces

# Trace shows:
# - Each action executed
# - Variables at each step
# - Errors and their location
# - Time taken per action
```
