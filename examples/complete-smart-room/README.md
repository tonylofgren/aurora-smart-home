# Complete Smart Room Example

This example demonstrates how the three Aurora Smart Home skills work together to create a fully automated smart room.

## Project Overview

A smart room with:
- **Motion-activated lighting** with brightness based on time of day
- **Climate control** based on presence and schedule
- **Voice control** via local voice assistant
- **Presence detection** using mmWave radar

## Skills Used

| Component | Skill | Purpose |
|-----------|-------|---------|
| ESP32-S3 Multi-Sensor | `esphome` | Motion, temperature, light level |
| ESP32-S3 Voice Satellite | `esphome` | Wake word + voice control |
| Climate Automation | `ha-yaml` | Smart thermostat control |
| Presence Lighting | `ha-yaml` | Motion-triggered scenes |
| Room Mode Scenes | `ha-yaml` | Scene management |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         SMART ROOM                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────┐     ┌────────────────────┐              │
│  │  Multi-Sensor      │     │  Voice Satellite   │              │
│  │  (ESP32-S3)        │     │  (ESP32-S3)        │              │
│  ├────────────────────┤     ├────────────────────┤              │
│  │ • mmWave presence  │     │ • Microphone       │              │
│  │ • Temperature      │     │ • Speaker          │              │
│  │ • Humidity         │     │ • Wake word        │              │
│  │ • Light level      │     │ • LED status       │              │
│  │ • LED strip ctrl   │     └────────────────────┘              │
│  └────────────────────┘              │                          │
│           │                          │                          │
│           └──────────────┬───────────┘                          │
│                          │                                       │
│                    ┌─────▼─────┐                                │
│                    │   WiFi    │                                │
│                    └─────┬─────┘                                │
│                          │                                       │
└──────────────────────────│───────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Home Assist │
                    │   (YAML)    │
                    ├─────────────┤
                    │ Automations │
                    │ Scenes      │
                    │ Scripts     │
                    └─────────────┘
```

## Files in This Example

| File | Description |
|------|-------------|
| `esphome-multisensor.yaml` | ESP32-S3 with sensors + LED strip |
| `esphome-voice-satellite.yaml` | ESP32-S3 voice assistant |
| `automations.yaml` | All HA automations for the room |
| `scenes.yaml` | Room scenes (work, relax, movie, night) |
| `scripts.yaml` | Reusable scripts |

## Quick Start

### 1. Flash ESPHome Devices

```bash
# Flash multi-sensor
esphome run esphome-multisensor.yaml

# Flash voice satellite
esphome run esphome-voice-satellite.yaml
```

### 2. Add to Home Assistant

Devices are auto-discovered via ESPHome integration.

### 3. Import Automations

Copy `automations.yaml` content to your HA automations, or use packages:

```yaml
# configuration.yaml
homeassistant:
  packages:
    smart_room: !include packages/smart-room.yaml
```

### 4. Configure Voice Assistant

1. Settings → Voice Assistants → Create Pipeline
2. Set wake word to "OK Nabu"
3. Select your Whisper + Piper instances
4. Assign pipeline to the voice satellite

## Room Modes

| Mode | Lighting | Climate | Trigger |
|------|----------|---------|---------|
| **Work** | 100% cool white | 22°C | Voice or button |
| **Relax** | 50% warm white | 23°C | Voice or button |
| **Movie** | 10% warm, bias lighting | 23°C | Voice or Plex webhook |
| **Night** | Off (nightlight on motion) | 20°C | Schedule 22:00 |
| **Away** | Off | Eco mode | No presence 30min |

## Voice Commands

The voice satellite supports:

- "OK Nabu, turn on the lights"
- "OK Nabu, set work mode"
- "OK Nabu, what's the temperature?"
- "OK Nabu, turn off everything"

## Sensor Data Flow

```
mmWave Presence Detected
         │
         ▼
┌─────────────────────┐
│ Automation triggers │
│ based on:           │
│ • Time of day       │
│ • Current mode      │
│ • Light level       │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Set lighting scene  │
│ + climate target    │
└─────────────────────┘
```

## Customization

### Change Sensor GPIOs

In `esphome-multisensor.yaml`, update the substitutions:

```yaml
substitutions:
  sda_pin: "GPIO21"  # Your I2C SDA
  scl_pin: "GPIO22"  # Your I2C SCL
  led_pin: "GPIO48"  # Your LED strip pin
```

### Add More Sensors

The multi-sensor template supports adding:
- Air quality (SGP30, BME680)
- CO2 (SCD40)
- Additional temperature sensors

### Different Wake Words

In `esphome-voice-satellite.yaml`:

```yaml
micro_wake_word:
  models:
    - model: hey_jarvis  # or alexa, hey_mycroft
```

---

*Generated with [aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
