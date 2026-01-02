# Home Assistant YAML Cheat Sheet

Quick reference for common Home Assistant automation patterns.

## Automation Structure

```yaml
automation:
  - alias: "Descriptive Name"
    id: unique_id_here
    description: "What this automation does"
    mode: single  # single, restart, queued, parallel
    trigger:
      - ...
    condition:
      - ...
    action:
      - ...
```

## Common Triggers

```yaml
trigger:
  # State change
  - platform: state
    entity_id: binary_sensor.motion
    to: "on"
    from: "off"
    for:
      minutes: 5

  # Time
  - platform: time
    at: "07:00:00"

  # Sun
  - platform: sun
    event: sunset
    offset: "-00:30:00"

  # Numeric threshold
  - platform: numeric_state
    entity_id: sensor.temperature
    above: 25
    below: 30
    for:
      minutes: 10

  # Template
  - platform: template
    value_template: "{{ states('sensor.power') | float > 1000 }}"
    for:
      minutes: 5

  # Zone
  - platform: zone
    entity_id: device_tracker.phone
    zone: zone.home
    event: enter  # enter or leave

  # Event
  - platform: event
    event_type: esphome.doorbell_pressed

  # Webhook
  - platform: webhook
    webhook_id: my_webhook_id

  # MQTT
  - platform: mqtt
    topic: "home/sensor/motion"
    payload: "ON"

  # Device trigger
  - platform: device
    device_id: abc123
    domain: zha
    type: remote_button_short_press
    subtype: button_1
```

## Common Conditions

```yaml
condition:
  # State
  - condition: state
    entity_id: input_boolean.enabled
    state: "on"

  # Time
  - condition: time
    after: "08:00:00"
    before: "22:00:00"
    weekday:
      - mon
      - tue
      - wed
      - thu
      - fri

  # Sun
  - condition: sun
    after: sunset
    before: sunrise

  # Numeric
  - condition: numeric_state
    entity_id: sensor.temperature
    above: 15
    below: 25

  # Template
  - condition: template
    value_template: "{{ is_state('person.owner', 'home') }}"

  # Zone
  - condition: zone
    entity_id: device_tracker.phone
    zone: zone.home

  # AND/OR/NOT
  - condition: and
    conditions:
      - condition: state
        entity_id: light.living_room
        state: "on"
      - condition: time
        after: "20:00:00"

  - condition: or
    conditions:
      - condition: state
        entity_id: binary_sensor.door
        state: "on"
      - condition: state
        entity_id: binary_sensor.window
        state: "on"

  - condition: not
    conditions:
      - condition: state
        entity_id: alarm_control_panel.home
        state: "armed_away"
```

## Common Actions

```yaml
action:
  # Service call
  - service: light.turn_on
    target:
      entity_id: light.living_room
    data:
      brightness_pct: 80
      color_temp: 300

  # Multiple targets
  - service: switch.turn_off
    target:
      entity_id:
        - switch.fan
        - switch.heater
      area_id: living_room

  # Delay
  - delay:
      seconds: 30

  # Wait for trigger
  - wait_for_trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "off"
    timeout:
      minutes: 5
    continue_on_timeout: true

  # Wait for template
  - wait_template: "{{ is_state('binary_sensor.door', 'off') }}"
    timeout:
      minutes: 2

  # Choose (if/else)
  - choose:
      - conditions:
          - condition: state
            entity_id: input_select.mode
            state: "home"
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.all
      - conditions:
          - condition: state
            entity_id: input_select.mode
            state: "away"
        sequence:
          - service: light.turn_off
            target:
              entity_id: light.all
    default:
      - service: light.turn_on
        target:
          entity_id: light.hall

  # Repeat
  - repeat:
      count: 3
      sequence:
        - service: light.toggle
          target:
            entity_id: light.alert
        - delay:
            milliseconds: 500

  # Repeat while
  - repeat:
      while:
        - condition: state
          entity_id: binary_sensor.motion
          state: "on"
      sequence:
        - delay:
            seconds: 1

  # Notification
  - service: notify.notify
    data:
      title: "Alert"
      message: "Something happened!"

  # Scene
  - service: scene.turn_on
    target:
      entity_id: scene.movie_time

  # Script
  - service: script.my_script
    data:
      parameter: value

  # Variables
  - variables:
      brightness: "{{ states('input_number.brightness') | int }}"
  - service: light.turn_on
    data:
      brightness: "{{ brightness }}"
```

## Template Syntax

```yaml
# State
"{{ states('sensor.temperature') }}"

# State as number
"{{ states('sensor.temperature') | float }}"
"{{ states('sensor.count') | int }}"

# Attribute
"{{ state_attr('climate.living_room', 'current_temperature') }}"

# Comparisons
"{{ states('sensor.temp') | float > 20 }}"
"{{ is_state('light.kitchen', 'on') }}"
"{{ is_state_attr('climate.ac', 'hvac_mode', 'cool') }}"

# Time
"{{ now().hour }}"
"{{ now().strftime('%H:%M') }}"
"{{ as_timestamp(now()) }}"

# Math
"{{ (states('sensor.power') | float * 0.15) | round(2) }}"

# Lists
"{{ states.light | selectattr('state', 'eq', 'on') | list | count }}"

# Default values
"{{ states('sensor.maybe_missing') | default('unknown') }}"

# Conditional
"{{ 'hot' if states('sensor.temp') | float > 25 else 'cold' }}"
```

## Jinja Filters

```yaml
# Numbers
| int
| float
| round(2)
| abs

# Strings
| lower
| upper
| capitalize
| trim
| replace('old', 'new')

# Lists
| first
| last
| count
| sum
| min
| max
| sort
| unique
| join(', ')

# Time
| timestamp_local
| timestamp_utc
| as_datetime
| as_timestamp

# Default/fallback
| default('fallback')
| default(0, true)  # Also for empty strings
```

## Input Helpers

```yaml
# Input boolean (toggle)
input_boolean:
  guest_mode:
    name: "Guest Mode"
    icon: mdi:account-multiple

# Input number (slider)
input_number:
  brightness_level:
    name: "Brightness"
    min: 0
    max: 100
    step: 5
    unit_of_measurement: "%"

# Input select (dropdown)
input_select:
  house_mode:
    name: "House Mode"
    options:
      - Home
      - Away
      - Night
      - Vacation

# Input text
input_text:
  notification_message:
    name: "Message"
    max: 255

# Input datetime
input_datetime:
  wakeup_time:
    name: "Wake-up Time"
    has_time: true
    has_date: false
```

## Scripts

```yaml
script:
  flash_lights:
    alias: "Flash Lights"
    sequence:
      - repeat:
          count: 3
          sequence:
            - service: light.turn_on
              target:
                entity_id: "{{ light_entity }}"
              data:
                brightness: 255
            - delay:
                milliseconds: 500
            - service: light.turn_off
              target:
                entity_id: "{{ light_entity }}"
            - delay:
                milliseconds: 500
    fields:
      light_entity:
        description: "Light to flash"
        example: "light.living_room"
```

## Notification Patterns

```yaml
# Mobile notification with action
- service: notify.mobile_app_phone
  data:
    title: "Door Open"
    message: "Front door has been open for 5 minutes"
    data:
      actions:
        - action: "CLOSE_DOOR"
          title: "Ignore"
        - action: "LOCK_DOOR"
          title: "Lock Door"

# TTS announcement
- service: tts.google_translate_say
  target:
    entity_id: media_player.speaker
  data:
    message: "Welcome home!"

# Persistent notification
- service: persistent_notification.create
  data:
    title: "Reminder"
    message: "Check the garage door"
    notification_id: "garage_reminder"
```

## Blueprint Variables

```yaml
blueprint:
  name: Motion Light
  domain: automation
  input:
    motion_sensor:
      name: Motion Sensor
      selector:
        entity:
          domain: binary_sensor
          device_class: motion
    light_target:
      name: Light
      selector:
        target:
          entity:
            domain: light
    delay_time:
      name: Delay
      default: 120
      selector:
        number:
          min: 0
          max: 600
          unit_of_measurement: seconds

trigger:
  - platform: state
    entity_id: !input motion_sensor
    to: "on"

action:
  - service: light.turn_on
    target: !input light_target
  - wait_for_trigger:
      - platform: state
        entity_id: !input motion_sensor
        to: "off"
  - delay:
      seconds: !input delay_time
  - service: light.turn_off
    target: !input light_target
```

## Debugging

```yaml
# Log custom message
- service: system_log.write
  data:
    message: "Debug: {{ states('sensor.test') }}"
    level: warning

# Create persistent notification for debugging
- service: persistent_notification.create
  data:
    message: "Trigger: {{ trigger.to_state.state }}"
```

## Quick Reference

| Purpose | Template |
|---------|----------|
| Is it dark? | `{{ is_state('sun.sun', 'below_horizon') }}` |
| Anyone home? | `{{ states.person \| selectattr('state', 'eq', 'home') \| list \| count > 0 }}` |
| Lights on count | `{{ states.light \| selectattr('state', 'eq', 'on') \| list \| count }}` |
| Time since | `{{ (now() - states.binary_sensor.door.last_changed).seconds }}` |
| Weekday? | `{{ now().isoweekday() < 6 }}` |
| Working hours? | `{{ 9 <= now().hour < 17 }}` |
