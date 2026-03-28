# ESPHome: Datetime and Event Components

Reference documentation for datetime and event entity platforms.
Source: https://esphome.io/components/

> **Note:** For Number, Select, and Text entities, see `buttons-inputs.md`.

---

## 1. Datetime

The datetime component creates date, time, or datetime entities that can be controlled from Home Assistant or automations.

### 1.1 Template Date

```yaml
datetime:
  - platform: template
    name: "Scheduled Date"
    id: scheduled_date
    type: date
    optimistic: true
    initial_value: "2024-01-01"
    restore_value: true
    on_value:
      then:
        - logger.log:
            format: "Date changed to %04d-%02d-%02d"
            args: ['x.year', 'x.month', 'x.day_of_month']
```

### 1.2 Template Time

```yaml
datetime:
  - platform: template
    name: "Wake Up Time"
    id: wake_time
    type: time
    optimistic: true
    initial_value: "07:30:00"
    restore_value: true
    on_value:
      then:
        - logger.log:
            format: "Wake time set to %02d:%02d:%02d"
            args: ['x.hour', 'x.minute', 'x.second']
```

### 1.3 Template Datetime

```yaml
datetime:
  - platform: template
    name: "Next Appointment"
    id: next_appointment
    type: datetime
    optimistic: true
    restore_value: true
    on_value:
      then:
        - logger.log: "Appointment time updated"
```

### 1.4 Configuration Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `type` | string | **Required** | `date`, `time`, or `datetime` |
| `optimistic` | boolean | `false` | Immediately apply set values without confirmation |
| `initial_value` | string | | Initial value (format depends on type) |
| `restore_value` | boolean | `false` | Restore last value on boot |
| `set_action` | Action | | Action to run when value is set (non-optimistic mode) |
| `on_value` | Trigger | | Trigger when value changes |

### 1.5 Actions

```yaml
# Set date
- datetime.date.set:
    id: scheduled_date
    date: "2024-06-15"

# Set from individual components
- datetime.date.set:
    id: scheduled_date
    date:
      year: 2024
      month: 6
      day: 15

# Set time
- datetime.time.set:
    id: wake_time
    time: "08:00:00"

# Set datetime
- datetime.datetime.set:
    id: next_appointment
    datetime: "2024-06-15 14:30:00"
```

### 1.6 Lambda Access

```cpp
// Date
auto date = id(scheduled_date).state_as_esptime();
ESP_LOGD("date", "Year: %d, Month: %d, Day: %d", date.year, date.month, date.day_of_month);

// Time
auto time = id(wake_time).state_as_esptime();
ESP_LOGD("time", "Hour: %d, Minute: %d", time.hour, time.minute);
```

### 1.7 Practical Example: Irrigation Scheduler

```yaml
datetime:
  - platform: template
    name: "Irrigation Start Time"
    id: irrigation_start
    type: time
    optimistic: true
    initial_value: "06:00:00"
    restore_value: true

time:
  - platform: homeassistant
    id: ha_time
    on_time:
      - seconds: 0
        then:
          - if:
              condition:
                lambda: |-
                  auto now = id(ha_time).now();
                  auto start = id(irrigation_start).state_as_esptime();
                  return now.hour == start.hour && now.minute == start.minute;
              then:
                - switch.turn_on: irrigation_pump
```

---

## 2. Event

The event component allows ESPHome devices to fire event entities that are visible in Home Assistant. Unlike sensors that hold state, events are stateless triggers.

### 2.1 Template Event

```yaml
event:
  - platform: template
    name: "Doorbell"
    id: doorbell_event
    device_class: doorbell
    event_types:
      - "single_press"
      - "double_press"
      - "long_press"
```

### 2.2 on_event Trigger

```yaml
event:
  - platform: template
    name: "Button Events"
    id: button_events
    event_types:
      - "single_press"
      - "double_press"
    on_event:
      then:
        - lambda: |-
            ESP_LOGD("event", "Event type: %s", event_type.c_str());
        - if:
            condition:
              lambda: 'return event_type == "double_press";'
            then:
              - light.toggle: my_light
```

### 2.3 Configuration Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `event_types` | list | **Required** | List of event type strings this entity can fire |
| `device_class` | string | | Device class: `doorbell`, `button`, `motion` |

### 2.3 Actions

Fire an event from any automation:

```yaml
# Fire a specific event type
- event.fire:
    id: doorbell_event
    event_type: "single_press"
```

Lambda:
```cpp
// Trigger event from C++ lambda
id(doorbell_event).trigger("single_press");
```

### 2.4 Practical Example: Multi-Press Button

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO0
    name: "Button"
    id: physical_button
    on_multi_click:
      - timing:
          - ON for at most 0.5s
          - OFF for at least 0.3s
        then:
          - event.fire:
              id: button_event
              event_type: "single_press"
      - timing:
          - ON for at most 0.5s
          - OFF for at most 0.3s
          - ON for at most 0.5s
          - OFF for at least 0.3s
        then:
          - event.fire:
              id: button_event
              event_type: "double_press"
      - timing:
          - ON for at least 1s
        then:
          - event.fire:
              id: button_event
              event_type: "long_press"

event:
  - platform: template
    name: "Button Events"
    id: button_event
    device_class: button
    event_types:
      - "single_press"
      - "double_press"
      - "long_press"
```

### 2.5 GPIO Binary Sensor Events (since 2025.x)

Binary sensors can directly emit events without a separate event entity:

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO0
    name: "Button"
    on_press:
      then:
        - event.fire:
            id: my_event
            event_type: "pressed"
```

---

## Quick Reference

| Component | Platforms | Key Actions |
|-----------|----------|-------------|
| `datetime` (date) | template | `datetime.date.set` |
| `datetime` (time) | template | `datetime.time.set` |
| `datetime` (datetime) | template | `datetime.datetime.set` |
| `event` | template | `event.fire` |

## See Also

- `buttons-inputs.md` -- Number, Select, Text, Button entities
- `automations.md` -- Automation triggers, conditions, and actions
- `home-assistant.md` -- HA integration and entity configuration
