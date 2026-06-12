# Advanced Automation Patterns

## Table of Contents
- [State Machines](#state-machines)
- [Multi-Area Coordination](#multi-area-coordination)
- [Cascading Automations](#cascading-automations)
- [Timer & Debounce Patterns](#timer--debounce-patterns)
- [Error Handling & Retries](#error-handling--retries)
- [Smart Lighting Patterns](#smart-lighting-patterns)
- [Presence State Machines](#presence-state-machines)
- [Climate Control Patterns](#climate-control-patterns)
- [Event-Driven Architecture](#event-driven-architecture)
- [Performance Optimization](#performance-optimization)

---

## State Machines

State machines help manage complex automations with multiple states and transitions.

### Basic State Machine Structure

```yaml
# helpers.yaml
input_select:
  home_state:
    name: "Home State"
    options:
      - Home
      - Away
      - Night
      - Vacation
      - Guest
    icon: mdi:home-automation
```

```yaml
# automations/state_machine.yaml
automation:
  # Transition: Home -> Away
  - id: state_home_to_away
    alias: "State: Home to Away"
    triggers:
      - trigger: state
        entity_id: group.family
        to: "not_home"
        for: "00:15:00"
    conditions:
      - condition: state
        entity_id: input_select.home_state
        state: "Home"
    actions:
      - action: input_select.select_option
        target:
          entity_id: input_select.home_state
        data:
          option: "Away"

  # Transition: Away -> Home
  - id: state_away_to_home
    alias: "State: Away to Home"
    triggers:
      - trigger: state
        entity_id: group.family
        to: "home"
    conditions:
      - condition: state
        entity_id: input_select.home_state
        state: "Away"
    actions:
      - action: input_select.select_option
        target:
          entity_id: input_select.home_state
        data:
          option: "Home"

  # Transition: Home -> Night
  - id: state_home_to_night
    alias: "State: Home to Night"
    triggers:
      - trigger: time
        at: "23:00:00"
    conditions:
      - condition: state
        entity_id: input_select.home_state
        state: "Home"
    actions:
      - action: input_select.select_option
        target:
          entity_id: input_select.home_state
        data:
          option: "Night"

  # Transition: Night -> Home
  - id: state_night_to_home
    alias: "State: Night to Home"
    triggers:
      - trigger: time
        at: "07:00:00"
    conditions:
      - condition: state
        entity_id: input_select.home_state
        state: "Night"
    actions:
      - action: input_select.select_option
        target:
          entity_id: input_select.home_state
        data:
          option: "Home"
```

### State Entry Actions

```yaml
# Execute actions when entering a state
automation:
  - id: state_entered_away
    alias: "State Entry: Away Mode"
    triggers:
      - trigger: state
        entity_id: input_select.home_state
        to: "Away"
    actions:
      - parallel:
          - action: climate.set_temperature
            target:
              entity_id: all
            data:
              temperature: 16
          - action: light.turn_off
            target:
              entity_id: all
          - action: media_player.turn_off
            target:
              entity_id: all
          - delay: "00:05:00"
          - action: alarm_control_panel.alarm_arm_away
            target:
              entity_id: alarm_control_panel.home

  - id: state_entered_night
    alias: "State Entry: Night Mode"
    triggers:
      - trigger: state
        entity_id: input_select.home_state
        to: "Night"
    actions:
      - action: light.turn_off
        target:
          area_id:
            - living_room
            - kitchen
      - action: light.turn_on
        target:
          entity_id: light.hallway_night_light
        data:
          brightness_pct: 5
      - action: alarm_control_panel.alarm_arm_night
        target:
          entity_id: alarm_control_panel.home
```

### Complex Multi-State Machine

```yaml
# 5-state presence machine with timeout logic
input_select:
  presence_state:
    name: "Presence State Machine"
    options:
      - Present        # Someone actively detected
      - Recently_Left  # Just left, might return
      - Away          # Confirmed away
      - Extended_Away # Long-term away (vacation-like)
      - Arriving      # Detected approaching

input_datetime:
  last_presence_change:
    name: "Last Presence Change"
    has_date: true
    has_time: true

timer:
  recently_left_timeout:
    name: "Recently Left Timeout"
    duration: "00:30:00"

  extended_away_timeout:
    name: "Extended Away Timeout"
    duration: "24:00:00"
```

```yaml
automation:
  # Present -> Recently_Left
  - id: presence_to_recently_left
    alias: "Presence: To Recently Left"
    triggers:
      - trigger: state
        entity_id: binary_sensor.anyone_home
        to: "off"
    conditions:
      - condition: state
        entity_id: input_select.presence_state
        state: "Present"
    actions:
      - action: input_select.select_option
        target:
          entity_id: input_select.presence_state
        data:
          option: "Recently_Left"
      - action: timer.start
        target:
          entity_id: timer.recently_left_timeout

  # Recently_Left -> Present (quick return)
  - id: presence_quick_return
    alias: "Presence: Quick Return"
    triggers:
      - trigger: state
        entity_id: binary_sensor.anyone_home
        to: "on"
    conditions:
      - condition: state
        entity_id: input_select.presence_state
        state: "Recently_Left"
    actions:
      - action: timer.cancel
        target:
          entity_id: timer.recently_left_timeout
      - action: input_select.select_option
        target:
          entity_id: input_select.presence_state
        data:
          option: "Present"

  # Recently_Left -> Away (timeout)
  - id: presence_to_away
    alias: "Presence: To Away"
    triggers:
      - trigger: event
        event_type: timer.finished
        event_data:
          entity_id: timer.recently_left_timeout
    actions:
      - action: input_select.select_option
        target:
          entity_id: input_select.presence_state
        data:
          option: "Away"
      - action: timer.start
        target:
          entity_id: timer.extended_away_timeout

  # Away -> Extended_Away
  - id: presence_to_extended_away
    alias: "Presence: To Extended Away"
    triggers:
      - trigger: event
        event_type: timer.finished
        event_data:
          entity_id: timer.extended_away_timeout
    actions:
      - action: input_select.select_option
        target:
          entity_id: input_select.presence_state
        data:
          option: "Extended_Away"

  # Any Away State -> Arriving
  - id: presence_arriving
    alias: "Presence: Arriving"
    triggers:
      - trigger: numeric_state
        entity_id: sensor.phone_distance_home
        below: 1000  # 1km
    conditions:
      - condition: state
        entity_id: input_select.presence_state
        state:
          - "Away"
          - "Extended_Away"
    actions:
      - action: input_select.select_option
        target:
          entity_id: input_select.presence_state
        data:
          option: "Arriving"
      - action: climate.set_temperature
        target:
          entity_id: climate.home
        data:
          temperature: 21
```

---

## Multi-Area Coordination

### Area-Aware Automations

```yaml
# Turn off lights in empty areas only
automation:
  - id: area_based_lights_off
    alias: "Area: Turn Off Empty Area Lights"
    triggers:
      - trigger: state
        entity_id:
          - binary_sensor.living_room_occupied
          - binary_sensor.kitchen_occupied
          - binary_sensor.bedroom_occupied
        to: "off"
        for: "00:10:00"
    actions:
      - variables:
          area: "{{ trigger.entity_id.split('.')[1].replace('_occupied', '') }}"
      - action: light.turn_off
        target:
          area_id: "{{ area }}"
```

### Follow-Me Lighting

```yaml
# Lights follow person through house
automation:
  - id: follow_me_lights
    alias: "Follow Me: Lighting"
    triggers:
      - trigger: state
        entity_id:
          - binary_sensor.hallway_motion
          - binary_sensor.living_room_motion
          - binary_sensor.kitchen_motion
          - binary_sensor.bedroom_motion
        to: "on"
    conditions:
      - condition: sun
        after: sunset
    actions:
      - variables:
          current_area: "{{ trigger.entity_id.split('.')[1].replace('_motion', '') }}"
          all_areas:
            - hallway
            - living_room
            - kitchen
            - bedroom
      # Turn on current area
      - action: light.turn_on
        target:
          area_id: "{{ current_area }}"
        data:
          brightness_pct: 80
          transition: 1
      # Dim other areas (except bedrooms if night)
      - action: light.turn_on
        target:
          area_id: >
            {{ all_areas | reject('eq', current_area)
               | reject('search', 'bedroom') | list }}
        data:
          brightness_pct: 20
          transition: 3
```

### Coordinated Room Scenes

```yaml
# When living room enters movie mode, adjust adjacent areas
automation:
  - id: movie_mode_coordination
    alias: "Coordination: Movie Mode"
    triggers:
      - trigger: state
        entity_id: input_boolean.movie_mode
        to: "on"
    actions:
      # Living room - movie lighting
      - action: light.turn_on
        target:
          area_id: living_room
        data:
          brightness_pct: 10
          color_temp: 500
      # Kitchen - dim but functional
      - action: light.turn_on
        target:
          area_id: kitchen
        data:
          brightness_pct: 30
      # Hallway - night light mode
      - action: light.turn_on
        target:
          entity_id: light.hallway
        data:
          brightness_pct: 5
```

### All-Areas Sweep

```yaml
# Check all areas and turn off empty ones
script:
  sweep_empty_areas:
    alias: "Sweep Empty Areas"
    sequence:
      - repeat:
          for_each:
            - living_room
            - kitchen
            - bedroom
            - office
          sequence:
            - condition: state
              entity_id: "binary_sensor.{{ repeat.item }}_occupied"
              state: "off"
            - action: light.turn_off
              target:
                area_id: "{{ repeat.item }}"
```

---

## Cascading Automations

### Event-Triggered Cascade

```yaml
# Master automation triggers child automations via events
automation:
  # Master: Goodnight trigger
  - id: cascade_goodnight_master
    alias: "Cascade Master: Goodnight"
    triggers:
      - trigger: state
        entity_id: input_button.goodnight
    actions:
      - event: cascade_goodnight
        event_data:
          source: button
          timestamp: "{{ now().isoformat() }}"

  # Child: Lights
  - id: cascade_goodnight_lights
    alias: "Cascade Child: Goodnight Lights"
    triggers:
      - trigger: event
        event_type: cascade_goodnight
    actions:
      - action: light.turn_off
        target:
          entity_id: all
        data:
          transition: 30

  # Child: Climate
  - id: cascade_goodnight_climate
    alias: "Cascade Child: Goodnight Climate"
    triggers:
      - trigger: event
        event_type: cascade_goodnight
    actions:
      - action: climate.set_temperature
        target:
          entity_id: climate.bedroom
        data:
          temperature: 18

  # Child: Security
  - id: cascade_goodnight_security
    alias: "Cascade Child: Goodnight Security"
    triggers:
      - trigger: event
        event_type: cascade_goodnight
    actions:
      - delay: "00:05:00"
      - action: alarm_control_panel.alarm_arm_night
        target:
          entity_id: alarm_control_panel.home
```

### Dependency Chain

```yaml
# Chain with confirmation between steps
automation:
  - id: sequential_startup
    alias: "Sequential Startup Chain"
    triggers:
      - trigger: state
        entity_id: input_boolean.morning_routine
        to: "on"
    actions:
      # Step 1: Climate
      - action: climate.set_hvac_mode
        target:
          entity_id: climate.living_room
        data:
          hvac_mode: heat
      - wait_template: >
          {{ state_attr('climate.living_room', 'hvac_action') == 'heating' }}
        timeout: "00:02:00"

      # Step 2: Lights (only if climate started)
      - if:
          - condition: template
            value_template: "{{ wait.completed }}"
        then:
          - action: light.turn_on
            target:
              area_id: living_room
            data:
              brightness_pct: 50

      # Step 3: Coffee machine (only after lights)
      - delay: "00:00:30"
      - action: switch.turn_on
        target:
          entity_id: switch.coffee_machine

      # Step 4: Notification
      - action: notify.mobile_app
        data:
          message: "Morning routine complete!"
```

---

## Timer & Debounce Patterns

### Debounce Rapid Changes

```yaml
# Ignore rapid sensor changes
automation:
  - id: debounced_motion
    alias: "Debounced Motion Light"
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
    conditions:
      # Only trigger if last activation was > 30 seconds ago
      - condition: template
        value_template: >
          {{ (as_timestamp(now()) - as_timestamp(
              states.automation.debounced_motion.attributes.last_triggered
              | default(0))) > 30 }}
    actions:
      - action: light.turn_on
        target:
          entity_id: light.hallway
```

### Hold-Down Pattern

```yaml
# Require condition to be true for duration before acting
automation:
  - id: holddown_occupancy
    alias: "Hold-Down: Room Unoccupied"
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "off"
        for: "00:10:00"  # Must be off for 10 minutes
    conditions:
      # Double-check still off
      - condition: state
        entity_id: binary_sensor.motion
        state: "off"
    actions:
      - action: light.turn_off
        target:
          entity_id: light.room
```

### Timer-Based State Management

```yaml
# helpers.yaml
timer:
  motion_timeout:
    name: "Motion Timeout"
    duration: "00:05:00"
    restore: true

input_boolean:
  light_auto_controlled:
    name: "Light Auto Controlled"
```

```yaml
automation:
  # Motion detected - start/restart timer
  - id: timer_motion_detected
    alias: "Timer: Motion Detected"
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
    actions:
      - action: timer.start
        target:
          entity_id: timer.motion_timeout
      - action: input_boolean.turn_on
        target:
          entity_id: input_boolean.light_auto_controlled
      - action: light.turn_on
        target:
          entity_id: light.room

  # Motion continues - restart timer
  - id: timer_motion_continues
    alias: "Timer: Motion Continues"
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
    conditions:
      - condition: state
        entity_id: timer.motion_timeout
        state: "active"
    actions:
      - action: timer.start
        target:
          entity_id: timer.motion_timeout

  # Timer finished - turn off
  - id: timer_finished
    alias: "Timer: Motion Timeout"
    triggers:
      - trigger: event
        event_type: timer.finished
        event_data:
          entity_id: timer.motion_timeout
    actions:
      - action: light.turn_off
        target:
          entity_id: light.room
      - action: input_boolean.turn_off
        target:
          entity_id: input_boolean.light_auto_controlled
```

### Progressive Timeout

```yaml
# Longer timeout at night
automation:
  - id: adaptive_timeout
    alias: "Adaptive Motion Timeout"
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
    actions:
      - variables:
          timeout_minutes: >
            {% set hour = now().hour %}
            {% if hour >= 22 or hour < 6 %}
              15
            {% elif hour >= 6 and hour < 9 %}
              5
            {% else %}
              10
            {% endif %}
      - action: timer.start
        target:
          entity_id: timer.motion_timeout
        data:
          duration: "00:{{ '%02d' | format(timeout_minutes) }}:00"
```

---

## Error Handling & Retries

### Service Call with Retry

```yaml
script:
  reliable_service_call:
    alias: "Reliable Service Call with Retry"
    fields:
      service_name:
        description: "Service to call"
      target_entity:
        description: "Target entity"
      max_retries:
        description: "Maximum retry attempts"
        default: 3
    sequence:
      - variables:
          attempt: 0
          success: false
      - repeat:
          while:
            - condition: template
              value_template: "{{ attempt < max_retries and not success }}"
          sequence:
            - variables:
                attempt: "{{ attempt + 1 }}"
            - action: "{{ service_name }}"
              target:
                entity_id: "{{ target_entity }}"
              continue_on_error: true
            - delay: "00:00:02"
            # Check if command worked
            - if:
                - condition: template
                  value_template: >
                    {% if 'turn_on' in service_name %}
                      {{ is_state(target_entity, 'on') }}
                    {% elif 'turn_off' in service_name %}
                      {{ is_state(target_entity, 'off') }}
                    {% else %}
                      true
                    {% endif %}
              then:
                - variables:
                    success: true
              else:
                - action: system_log.write
                  data:
                    message: "Retry {{ attempt }}/{{ max_retries }} for {{ target_entity }}"
                    level: warning
                - delay: "00:00:05"
      - if:
          - condition: template
            value_template: "{{ not success }}"
        then:
          - action: notify.admin
            data:
              title: "Automation Failed"
              message: "Failed to {{ service_name }} {{ target_entity }} after {{ max_retries }} attempts"
```

### Fallback Actions

```yaml
automation:
  - id: light_with_fallback
    alias: "Light Control with Fallback"
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
    actions:
      # Try primary light
      - action: light.turn_on
        target:
          entity_id: light.primary
        continue_on_error: true
      - delay: "00:00:02"
      # If primary failed, use fallback
      - if:
          - condition: state
            entity_id: light.primary
            state: "unavailable"
        then:
          - action: light.turn_on
            target:
              entity_id: light.fallback
          - action: notify.admin
            data:
              message: "Primary light unavailable, using fallback"
```

### Error Notification

```yaml
automation:
  - id: error_handler
    alias: "Global Error Handler"
    triggers:
      - trigger: event
        event_type: system_log_event
        event_data:
          level: ERROR
    conditions:
      - condition: template
        value_template: >
          {{ 'automation' in trigger.event.data.message | lower
             or 'script' in trigger.event.data.message | lower }}
    actions:
      - action: notify.admin
        data:
          title: "Home Assistant Error"
          message: "{{ trigger.event.data.message[:200] }}"
```

---

## Smart Lighting Patterns

### Time + Presence + Ambient Aware

```yaml
automation:
  - id: smart_light_control
    alias: "Smart Light: Full Context"
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
    conditions:
      - condition: numeric_state
        entity_id: sensor.illuminance
        below: 100
    actions:
      - variables:
          hour: "{{ now().hour }}"
          anyone_home: "{{ is_state('group.family', 'home') }}"
          weather: "{{ states('weather.home') }}"
          # Calculate appropriate brightness
          brightness: >
            {% if hour < 6 or hour >= 23 %}
              10
            {% elif hour < 8 %}
              {{ 10 + ((hour - 6) * 25) }}
            {% elif hour >= 20 %}
              {{ 80 - ((hour - 20) * 20) }}
            {% elif weather in ['cloudy', 'rainy'] %}
              90
            {% else %}
              70
            {% endif %}
          # Calculate color temperature
          color_temp: >
            {% if hour < 8 or hour >= 20 %}
              400
            {% else %}
              250
            {% endif %}
      - action: light.turn_on
        target:
          entity_id: light.living_room
        data:
          brightness_pct: "{{ brightness }}"
          kelvin: "{{ color_temp }}"
          transition: 2
```

### Scene-Based Lighting Override

```yaml
# Track if user has manually changed lights
input_boolean:
  lights_manual_override:
    name: "Lights Manual Override"

automation:
  # Detect manual changes
  - id: detect_manual_light_change
    alias: "Detect Manual Light Change"
    triggers:
      - trigger: state
        entity_id: light.living_room
    conditions:
      - condition: template
        value_template: "{{ trigger.to_state.context.user_id is not none }}"
    actions:
      - action: input_boolean.turn_on
        target:
          entity_id: input_boolean.lights_manual_override
      # Reset after 2 hours
      - delay: "02:00:00"
      - action: input_boolean.turn_off
        target:
          entity_id: input_boolean.lights_manual_override

  # Skip automation if manual override active
  - id: auto_lights_with_override
    alias: "Auto Lights (With Override Check)"
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
    conditions:
      - condition: state
        entity_id: input_boolean.lights_manual_override
        state: "off"
    actions:
      - action: light.turn_on
        target:
          entity_id: light.living_room
```

---

## Presence State Machines

### Multi-Person Presence

```yaml
template:
  - binary_sensor:
      - name: "House Occupied"
        state: >
          {{ is_state('person.john', 'home')
             or is_state('person.jane', 'home')
             or is_state('person.guest', 'home') }}

      - name: "Only Guest Home"
        state: >
          {{ is_state('person.guest', 'home')
             and not is_state('person.john', 'home')
             and not is_state('person.jane', 'home') }}

  - sensor:
      - name: "People Home Count"
        state: >
          {% set people = ['person.john', 'person.jane', 'person.guest'] %}
          {{ people | map('states') | select('eq', 'home') | list | length }}

      - name: "Who Is Home"
        state: >
          {% set home = namespace(people=[]) %}
          {% for person in ['person.john', 'person.jane', 'person.guest'] %}
            {% if is_state(person, 'home') %}
              {% set home.people = home.people + [state_attr(person, 'friendly_name')] %}
            {% endif %}
          {% endfor %}
          {{ home.people | join(', ') if home.people else 'Nobody' }}
```

### Guest Mode Automation

```yaml
automation:
  - id: guest_mode_auto_enable
    alias: "Guest Mode: Auto Enable"
    triggers:
      - trigger: state
        entity_id: binary_sensor.only_guest_home
        to: "on"
    actions:
      - action: input_boolean.turn_on
        target:
          entity_id: input_boolean.guest_mode
      # Simplified automation mode for guests
      - action: automation.turn_off
        target:
          entity_id:
            - automation.advanced_lighting
            - automation.climate_schedule

  - id: guest_mode_auto_disable
    alias: "Guest Mode: Auto Disable"
    triggers:
      - trigger: state
        entity_id: binary_sensor.only_guest_home
        to: "off"
    actions:
      - action: input_boolean.turn_off
        target:
          entity_id: input_boolean.guest_mode
      - action: automation.turn_on
        target:
          entity_id:
            - automation.advanced_lighting
            - automation.climate_schedule
```

---

## Climate Control Patterns

### Multi-Zone Coordination

```yaml
automation:
  - id: climate_zone_coordination
    alias: "Climate: Zone Coordination"
    triggers:
      - trigger: state
        entity_id:
          - binary_sensor.living_room_occupied
          - binary_sensor.bedroom_occupied
          - binary_sensor.office_occupied
    actions:
      - variables:
          occupied_zones: >
            {% set zones = [] %}
            {% if is_state('binary_sensor.living_room_occupied', 'on') %}
              {% set zones = zones + ['climate.living_room'] %}
            {% endif %}
            {% if is_state('binary_sensor.bedroom_occupied', 'on') %}
              {% set zones = zones + ['climate.bedroom'] %}
            {% endif %}
            {% if is_state('binary_sensor.office_occupied', 'on') %}
              {% set zones = zones + ['climate.office'] %}
            {% endif %}
            {{ zones }}
          unoccupied_zones: >
            {% set all = ['climate.living_room', 'climate.bedroom', 'climate.office'] %}
            {{ all | reject('in', occupied_zones) | list }}
      # Heat occupied zones
      - action: climate.set_temperature
        target:
          entity_id: "{{ occupied_zones }}"
        data:
          temperature: "{{ states('input_number.comfort_temp') | float }}"
      # Reduce unoccupied zones
      - action: climate.set_temperature
        target:
          entity_id: "{{ unoccupied_zones }}"
        data:
          temperature: "{{ states('input_number.away_temp') | float }}"
```

### Weather-Responsive Climate

```yaml
automation:
  - id: climate_weather_adjustment
    alias: "Climate: Weather Adjustment"
    triggers:
      - trigger: state
        entity_id: weather.home
    actions:
      - variables:
          adjustment: >
            {% set condition = states('weather.home') %}
            {% if condition == 'sunny' %}
              -2
            {% elif condition == 'cloudy' %}
              0
            {% elif condition in ['rainy', 'snowy'] %}
              2
            {% else %}
              0
            {% endif %}
      - action: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: >
            {{ (states('input_number.base_temp') | float) + adjustment }}
```

---

## Event-Driven Architecture

### Custom Event Bus

```yaml
# Central event dispatcher
script:
  dispatch_event:
    alias: "Dispatch Custom Event"
    fields:
      event_name:
        description: "Event name"
      event_data:
        description: "Event data"
    sequence:
      - event: "ha_custom_{{ event_name }}"
        event_data: "{{ event_data }}"

# Usage in automations
automation:
  - id: dispatch_arrival
    alias: "Dispatch: Person Arrived"
    triggers:
      - trigger: state
        entity_id: person.john
        to: "home"
    actions:
      - action: script.dispatch_event
        data:
          event_name: "person_arrived"
          event_data:
            person: john
            time: "{{ now().isoformat() }}"

  # Listener automation
  - id: handle_arrival
    alias: "Handle: Person Arrival"
    triggers:
      - trigger: event
        event_type: ha_custom_person_arrived
    actions:
      - action: light.turn_on
        target:
          entity_id: light.hallway
      - action: notify.mobile_app
        data:
          message: "{{ trigger.event.data.person }} arrived home"
```

---

## Performance Optimization

### Efficient Condition Checking

```yaml
# Bad: Multiple separate automations
# Good: Single automation with choose

automation:
  - id: optimized_motion_handler
    alias: "Optimized Motion Handler"
    triggers:
      - trigger: state
        entity_id:
          - binary_sensor.living_room_motion
          - binary_sensor.kitchen_motion
          - binary_sensor.bedroom_motion
        to: "on"
    actions:
      - choose:
          - conditions:
              - condition: trigger
                id: living_room
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
          - conditions:
              - condition: trigger
                id: bedroom
            sequence:
              - condition: sun
                after: sunset
              - action: light.turn_on
                target:
                  entity_id: light.bedroom
                data:
                  brightness_pct: 30
```

### Avoid Template Overload

```yaml
# Bad: Complex template in trigger
# Good: Use template sensor + simple trigger

# Template sensor (evaluated periodically)
template:
  - binary_sensor:
      - name: "Climate Action Needed"
        state: >
          {% set temp = states('sensor.indoor_temp') | float(20) %}
          {% set target = states('input_number.target_temp') | float(21) %}
          {% set outside = states('sensor.outdoor_temp') | float(15) %}
          {{ (temp < target - 2 and outside < temp)
             or (temp > target + 2 and outside > temp) }}

# Simple trigger
automation:
  - id: climate_action
    triggers:
      - trigger: state
        entity_id: binary_sensor.climate_action_needed
        to: "on"
    actions:
      # ...
```

### Rate Limiting

```yaml
automation:
  - id: rate_limited_notification
    alias: "Rate Limited Notification"
    triggers:
      - trigger: state
        entity_id: binary_sensor.door
        to: "on"
    conditions:
      # Only notify once per hour
      - condition: template
        value_template: >
          {% set last = state_attr('automation.rate_limited_notification', 'last_triggered') %}
          {{ last is none or (now() - last).total_seconds() > 3600 }}
    actions:
      - action: notify.mobile_app
        data:
          message: "Door opened"
```
