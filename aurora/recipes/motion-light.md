---
name: motion-light
intent: Turn a light on when someone enters a room and off when they leave
specialists: [Volt, Sage]
hardware: true
match_keywords: [motion, pir, light, hallway, automatic light, occupancy, am312, walk in]
related_example: examples/complete-smart-room
---

# Motion-Activated Light

## What you get

The first automation almost everyone wants: a light that turns on when you walk in and off a few minutes after you leave, but only when the room is actually dark. A PIR sensor reports motion; Home Assistant owns the logic so the rule is easy to tune.

## Hardware

| Part | Purpose | LCSC | Notes |
|------|---------|------|-------|
| ESP32 dev board | MCU | TBD | Any ESP32; reuse one you have |
| PIR AM312 | Motion detection (3.3V) | C114881 | Small, fixed sensitivity; HC-SR501 if you need range/pots |
| Dupont jumpers | VCC/OUT/GND | TBD | 3 wires |

If the room light is already a smart bulb or smart switch, you only need the PIR sensor reporting to HA; the light is whatever entity you already have.

## Wiring

```
AM312        ESP32
VCC  ------- 3V3
OUT  ------- GPIO4   (digital input)
GND  ------- GND
```

## Automation pattern

1. **trigger:** `binary_sensor.<room>_motion` turns on.
2. **condition:** `sensor.<room>_illuminance` below the lux threshold (skip in daylight); optionally only when home.
3. **action:** turn the light on at the chosen brightness.
4. **off path:** `wait_for_trigger` on motion clearing for N minutes, then turn off. Use `mode: restart` so re-entry resets the timer.
5. Guard: do not turn on if a manual override boolean is set (so movie night is not interrupted).

## Dashboard skeleton

- Tile card for the light with a brightness slider.
- Entity row: motion sensor state, illuminance, last-triggered timestamp.
- Toggle for the manual-override `input_boolean`.

## Customise

- **Off delay:** 3 minutes is typical; 1 for a hallway, 10 for a desk.
- **Lux threshold:** below which the rule fires (default 40 lux); set high to always fire. The reading needs a real light sensor: add a BH1750 (C78960) for `sensor.<room>_illuminance`, or see the `daylight-lights` recipe to drive lights off lux directly.
- **Brightness:** 100% day, 20% night via a time condition.
- **Override:** an `input_boolean` that pauses the automation.

## Build it

Pick this and Volt generates the PIR firmware while Sage generates the motion-light automation with the override guard and the dashboard. Read `examples/complete-smart-room` for motion combined with presence, climate, and scenes in one room.
