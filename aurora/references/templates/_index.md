# Aurora Project Templates

Ready-to-use ESPHome scaffolds for common smart home projects. Volt offers them as a 30-second quick start.

## Templates

| Template | Use case | Board | External hardware |
|----------|----------|-------|-------------------|
| [bluetooth-proxy](bluetooth-proxy.md) | Extend BLE coverage room-to-room | ESP32-C3 Super Mini | None |
| [voice-assistant-s3](voice-assistant-s3.md) | Local-first voice satellite with wake word | ESP32-S3 DevKit C-1 | INMP441 mic + MAX98357A amp |
| [air-quality-monitor](air-quality-monitor.md) | CO2 + temp + humidity per room | ESP32-C3 Super Mini | SCD40 |
| [presence-sensor-radar](presence-sensor-radar.md) | Sub-mm presence detection (stays ON while sitting still) | ESP32-C3 Super Mini | HLK-LD2410 |
| [battery-soil-sensor](battery-soil-sensor.md) | Long-life plant moisture monitor | ESP32-C3 Super Mini | Capacitive soil v1.2 + battery |
| [multi-relay-controller](multi-relay-controller.md) | 8 relays from 2 GPIOs | ESP32-C3 Super Mini | PCF8574 + 8-relay board |
| [temp-humidity-room](temp-humidity-room.md) | First-time-user climate monitor | ESP32-C3 Super Mini | BME280 |

## Variable substitution

All templates use `${variable_name}`. Volt substitutes when you ask for a project:

- Common: `${device_name}` (kebab-case, used in esphome.name), `${friendly_name}` (human-readable), `${board_id}` (must be a profile)
- Per-template: see each template's `.md` file

## How Volt uses templates

When a project description matches a template, Volt:
1. Loads the matching `.yaml` and `.md`
2. Asks the user to confirm board selection (or accepts the recommended one)
3. Substitutes variables based on the user's stated room/device names
4. Runs the standard validation flow (pin-validator, conflict-validator)
5. Outputs the completed YAML + wiring diagram + a pointer to the `.md` for customization notes
