# ESPHome: Alarm Control Panel, Lock, and Valve Components

Reference documentation for alarm_control_panel, lock, and valve components.
Source: https://esphome.io/components/

---

## 1. Alarm Control Panel

### 1.1 Base Component Configuration

All alarm control panel platforms inherit these options:

```yaml
alarm_control_panel:
  - platform: ...
    id: my_alarm
    name: "Home Alarm"
    on_state:
      - logger.log: "Alarm state changed"
    on_arming:
      - logger.log: "Alarm is arming"
    on_pending:
      - logger.log: "Alarm pending (entry delay)"
    on_armed_home:
      - logger.log: "Alarm armed home"
    on_armed_night:
      - logger.log: "Alarm armed night"
    on_armed_away:
      - logger.log: "Alarm armed away"
    on_triggered:
      - logger.log: "Alarm triggered!"
    on_cleared:
      - logger.log: "Alarm cleared"
    on_disarmed:
      - logger.log: "Alarm disarmed"
    on_chime:
      - logger.log: "Chime zone opened"
```

**Base Configuration Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `id` | ID | | Manually specify the ID. At least one of `id` and `name` required. |
| `name` | string | | The name of the alarm control panel. At least one of `id` and `name` required. |
| `on_state` | Automation | | Trigger when alarm changes any state. |
| `on_arming` | Automation | | Trigger when state changes to arming. |
| `on_pending` | Automation | | Trigger when state changes to pending (entry delay). |
| `on_armed_home` | Automation | | Trigger when state changes to armed_home. |
| `on_armed_night` | Automation | | Trigger when state changes to armed_night. |
| `on_armed_away` | Automation | | Trigger when state changes to armed_away. |
| `on_triggered` | Automation | | Trigger when alarm is triggered. |
| `on_cleared` | Automation | | Trigger when alarm clears (returns to armed or disarmed). |
| `on_disarmed` | Automation | | Trigger when alarm is disarmed. |
| `on_chime` | Automation | | Trigger when a chime-flagged zone opens. |

### 1.2 Template Alarm Control Panel Platform

```yaml
alarm_control_panel:
  - platform: template
    id: acp1
    name: "Home Alarm"

    # Codes for arming/disarming
    codes:
      - "1234"
      - "5678"
    requires_code_to_arm: false

    # Timing
    arming_away_time: 30s
    arming_home_time: 5s
    arming_night_time: 5s
    pending_time: 30s
    trigger_time: 300s

    # Restore behavior
    restore_mode: ALWAYS_DISARMED

    # Binary sensor zones
    binary_sensors:
      - input: front_door
        bypass_armed_home: false
        bypass_armed_night: false
        bypass_auto: false
        chime: true
        trigger_mode: delayed
      - input: living_room_pir
        bypass_armed_home: true
        bypass_armed_night: false
        bypass_auto: false
        chime: false
        trigger_mode: delayed_follower
      - input: window_sensor
        bypass_armed_home: false
        bypass_armed_night: false
        bypass_auto: false
        chime: false
        trigger_mode: instant
      - input: tamper_sensor
        trigger_mode: instant_always

    on_triggered:
      - switch.turn_on: siren
    on_cleared:
      - switch.turn_off: siren
```

**Template Platform Configuration Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `codes` | list of string | `[]` | List of codes for disarming (and arming if `requires_code_to_arm` is true). |
| `requires_code_to_arm` | boolean | `false` | Whether a code is required to arm the alarm. |
| `arming_away_time` | Time | `0s` | Exit delay before entering armed_away state. |
| `arming_home_time` | Time | `0s` | Exit delay before entering armed_home state. |
| `arming_night_time` | Time | `0s` | Exit delay before entering armed_night state. |
| `pending_time` | Time | `0s` | Entry delay before triggering the alarm. |
| `trigger_time` | Time | `0s` | Duration alarm stays triggered before auto-resetting if sensors clear. |
| `restore_mode` | enum | `ALWAYS_DISARMED` | `ALWAYS_DISARMED` or `RESTORE_DEFAULT_DISARMED`. |
| `binary_sensors` | list | `[]` | List of binary sensor zone configurations. |

**Binary Sensor Zone Configuration:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `input` | string | **Required** | Binary sensor component ID. |
| `bypass_armed_home` | boolean | `false` | Sensor will not trigger alarm in armed_home state. |
| `bypass_armed_night` | boolean | `false` | Sensor will not trigger alarm in armed_night state. |
| `bypass_auto` | boolean | `false` | Sensor auto-bypassed if open at arming time. |
| `chime` | boolean | `false` | Calls chime callback when sensor goes from closed to open. |
| `trigger_mode` | enum | `delayed` | One of: `delayed`, `instant`, `instant_always`, `delayed_follower`. |

**Trigger Modes Explained:**

- **`delayed`**: For exterior doors with entry keypads. Triggers pending state first (entry delay), then triggered.
- **`instant`**: For windows/glass break. Goes directly from armed to triggered (no pending delay).
- **`instant_always`**: For tamper inputs. Triggers alarm regardless of armed/disarmed state.
- **`delayed_follower`**: For interior PIR/microwave sensors. Goes directly to triggered when armed, but stays in pending when panel is already pending (following a delayed zone).

### 1.3 Alarm Control Panel Actions

```yaml
# Arm away
- alarm_control_panel.arm_away:
    id: acp1
    code: "1234"    # Optional, required if requires_code_to_arm is true

# Arm home
- alarm_control_panel.arm_home:
    id: acp1
    code: "1234"

# Arm night
- alarm_control_panel.arm_night:
    id: acp1
    code: "1234"

# Disarm
- alarm_control_panel.disarm:
    id: acp1
    code: "1234"    # Required if codes list is not empty

# Force to pending state
- alarm_control_panel.pending: acp1

# Force to triggered state
- alarm_control_panel.triggered: acp1
```

### 1.4 Alarm Control Panel Conditions

```yaml
# Check if alarm is armed (any armed state)
- alarm_control_panel.is_armed: acp1
```

### 1.5 Alarm Control Panel States

| State | Description |
|-------|-------------|
| `DISARMED` | Alarm is off |
| `ARMING` | Exit delay countdown |
| `ARMED_HOME` | Armed in home mode |
| `ARMED_AWAY` | Armed in away mode |
| `ARMED_NIGHT` | Armed in night mode |
| `PENDING` | Entry delay countdown |
| `TRIGGERED` | Alarm is triggered |

---

## 2. Lock Component

### 2.1 Base Component Configuration

All lock platforms inherit these options:

```yaml
lock:
  - platform: ...
    id: my_lock
    name: "Front Door Lock"
    on_lock:
      - logger.log: "Lock locked"
    on_unlock:
      - logger.log: "Lock unlocked"
```

**Base Configuration Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `id` | ID | | Manually specify the ID. |
| `name` | string | | The name of the lock. |
| `on_lock` | Automation | | Trigger when lock is locked. |
| `on_unlock` | Automation | | Trigger when lock is unlocked. |

### 2.2 Template Lock Platform

```yaml
lock:
  - platform: template
    id: my_lock
    name: "Template Lock"
    optimistic: true
    assumed_state: false

    # Lambda returning current state (optional with optimistic)
    lambda: |-
      if (id(lock_sensor).state) {
        return LOCK_STATE_LOCKED;
      } else {
        return LOCK_STATE_UNLOCKED;
      }

    # Action when lock is requested
    lock_action:
      - output.turn_on: lock_output
      - lock.template.publish:
          id: my_lock
          state: LOCKED

    # Action when unlock is requested
    unlock_action:
      - output.turn_off: lock_output
      - lock.template.publish:
          id: my_lock
          state: UNLOCKED

    # Action when open (unlatch) is requested
    open_action:
      - output.turn_off: lock_output
      - delay: 2s
      - output.turn_on: lock_output
```

**Template Lock Configuration Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `lambda` | lambda | | Lambda evaluated repeatedly to get current lock state. Return `LOCK_STATE_LOCKED` or `LOCK_STATE_UNLOCKED`. |
| `lock_action` | Action | | Action performed when remote requests lock. |
| `unlock_action` | Action | | Action performed when remote requests unlock. |
| `open_action` | Action | | Action performed when remote requests open/unlatch. |
| `optimistic` | boolean | `false` | If true, commands immediately update reported state (no lambda needed). |
| `assumed_state` | boolean | `false` | If true, HA frontend shows both LOCK and UNLOCK buttons always. |

**Publishing State (from lambdas or automations):**

```yaml
# From YAML automation
- lock.template.publish:
    id: my_lock
    state: LOCKED    # or UNLOCKED

# From C++ lambda
id(my_lock).publish_state(lock::LOCK_STATE_LOCKED);
```

### 2.3 Output Lock Platform

Uses any binary output component as a lock.

```yaml
output:
  - platform: gpio
    pin: GPIO15
    id: lock_output_pin

lock:
  - platform: output
    name: "Generic Lock"
    output: lock_output_pin
```

**Output Lock Configuration Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `output` | ID | **Required** | ID of the binary output component to use. |

### 2.4 Lock Actions

```yaml
# Lock the lock
- lock.lock: my_lock

# Unlock the lock
- lock.unlock: my_lock

# Open (unlatch) the lock
- lock.open: my_lock
```

### 2.5 Lock Conditions

```yaml
# Check if locked
- lock.is_locked: my_lock

# Check if unlocked
- lock.is_unlocked: my_lock
```

### 2.6 Lock States

| State | Description |
|-------|-------------|
| `LOCKED` | Lock is locked |
| `UNLOCKED` | Lock is unlocked |
| `JAMMED` | Lock is jammed (error state) |
| `LOCKING` | Lock is in process of locking |
| `UNLOCKING` | Lock is in process of unlocking |

---

## 3. Valve Component

### 3.1 Base Component Configuration

All valve platforms inherit these options:

```yaml
valve:
  - platform: ...
    id: my_valve
    name: "Water Valve"
    on_fully_open:
      - logger.log: "Valve fully open"
    on_fully_closed:
      - logger.log: "Valve fully closed"
```

**Base Configuration Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `id` | ID | | Manually specify the ID. |
| `name` | string | | The name of the valve. |
| `device_class` | string | | Device class (e.g., `water`, `gas`). |
| `on_fully_open` | Automation | | Trigger when valve reaches fully open. |
| `on_fully_closed` | Automation | | Trigger when valve reaches fully closed. |

### 3.2 Template Valve Platform

```yaml
valve:
  - platform: template
    id: garden_valve
    name: "Garden Water Valve"
    optimistic: true

    # For position-aware valves
    has_position: true

    open_action:
      - output.turn_on: valve_open_pin
    close_action:
      - output.turn_on: valve_close_pin
    stop_action:
      - output.turn_off: valve_open_pin
      - output.turn_off: valve_close_pin
    position_action:
      - logger.log:
          format: "Setting valve position to %.1f%%"
          args: ['pos * 100.0']

    # Lambda returning current position (0.0=closed, 1.0=open)
    lambda: |-
      if (id(valve_sensor).state) {
        return VALVE_OPEN;
      } else {
        return VALVE_CLOSED;
      }
```

**Template Valve Configuration Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `lambda` | lambda | | Lambda evaluated repeatedly to get current valve state/position. Return `VALVE_OPEN`, `VALVE_CLOSED`, or a float 0.0-1.0. |
| `open_action` | Action | | Action when remote requests valve open. |
| `close_action` | Action | | Action when remote requests valve close. |
| `stop_action` | Action | | Action when remote requests valve stop. |
| `position_action` | Action | | Action when remote requests specific position. Variable `pos` available (0.0-1.0). Requires `has_position: true`. |
| `has_position` | boolean | `false` | Whether this valve publishes position as float. |
| `optimistic` | boolean | `false` | If true, commands immediately update reported state. |
| `assumed_state` | boolean | `false` | If true, HA frontend always shows both open/close buttons. |

**Publishing State (from lambdas or automations):**

```yaml
# Publish simple state
- valve.template.publish:
    id: garden_valve
    state: OPEN       # or CLOSED

# Publish position (0.0 to 1.0)
- valve.template.publish:
    id: garden_valve
    position: 0.5     # 50% open
```

### 3.3 Valve Actions

```yaml
# Open the valve
- valve.open: my_valve

# Close the valve
- valve.close: my_valve

# Stop the valve
- valve.stop: my_valve

# Toggle: cycles close/stop/open/stop...
- valve.toggle: my_valve

# Generic control action
- valve.control:
    id: my_valve
    position: 0.5     # Set to 50%
```

### 3.4 Valve Conditions

```yaml
# Check if valve is open
- valve.is_open: my_valve

# Check if valve is closed
- valve.is_closed: my_valve
```

### 3.5 Valve States and Properties

| Property | Type | Description |
|----------|------|-------------|
| `position` | float | 0.0 (fully closed) to 1.0 (fully open). |
| `current_operation` | enum | `IDLE`, `OPENING`, or `CLOSING`. |

### 3.6 Note on Time-Based Valve

ESPHome does NOT have a dedicated `time_based` valve platform (unlike covers which have `time_based` cover). To achieve time-based valve control, use the **template valve** with timer logic in lambdas or automations, or use the **sprinkler controller** component for irrigation use cases.

---

## 4. Complete Working Example

A realistic example combining all three components:

```yaml
esphome:
  name: home-security-node
  platform: ESP32
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

logger:

# --- Binary Sensors (alarm zones) ---
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO16
      mode: INPUT_PULLUP
      inverted: true
    id: front_door
    name: "Front Door"
    device_class: door

  - platform: gpio
    pin:
      number: GPIO17
      mode: INPUT_PULLUP
      inverted: true
    id: window_sensor
    name: "Living Room Window"
    device_class: window

  - platform: gpio
    pin:
      number: GPIO18
      mode: INPUT_PULLUP
    id: pir_sensor
    name: "Hallway PIR"
    device_class: motion

# --- Output pins ---
output:
  - platform: gpio
    pin: GPIO25
    id: siren_output

  - platform: gpio
    pin: GPIO26
    id: door_lock_pin

  - platform: gpio
    pin: GPIO27
    id: valve_pin

# --- Siren switch ---
switch:
  - platform: output
    id: siren
    name: "Alarm Siren"
    output: siren_output

# --- Alarm Control Panel ---
alarm_control_panel:
  - platform: template
    id: home_alarm
    name: "Home Alarm System"
    codes:
      - !secret alarm_code
    requires_code_to_arm: false
    arming_away_time: 30s
    arming_home_time: 5s
    arming_night_time: 5s
    pending_time: 30s
    trigger_time: 300s
    restore_mode: RESTORE_DEFAULT_DISARMED

    binary_sensors:
      - input: front_door
        chime: true
        trigger_mode: delayed
      - input: window_sensor
        trigger_mode: instant
      - input: pir_sensor
        bypass_armed_home: true
        trigger_mode: delayed_follower

    on_triggered:
      - switch.turn_on: siren
      - logger.log: "ALARM TRIGGERED!"
    on_cleared:
      - switch.turn_off: siren
    on_chime:
      - rtttl.play: "chime:d=4,o=5,b=100:e6"

# --- Door Lock ---
lock:
  - platform: output
    id: front_door_lock
    name: "Front Door Lock"
    output: door_lock_pin

# --- Water Shut-off Valve ---
valve:
  - platform: template
    id: water_shutoff
    name: "Main Water Valve"
    optimistic: true
    open_action:
      - output.turn_on: valve_pin
    close_action:
      - output.turn_off: valve_pin
    on_fully_closed:
      - logger.log: "Water shut off"
```

---

## Sources

- [Alarm Control Panel Component](https://esphome.io/components/alarm_control_panel/)
- [Template Alarm Control Panel](https://esphome.io/components/alarm_control_panel/template/)
- [Lock Component](https://esphome.io/components/lock/)
- [Template Lock](https://esphome.io/components/lock/template/)
- [Output Lock](https://esphome.io/components/lock/output/)
- [Valve Component](https://esphome.io/components/valve/)
- [Template Valve](https://esphome.io/components/valve/template/)
