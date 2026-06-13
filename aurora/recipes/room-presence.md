---
name: room-presence
intent: Detect that a room is occupied even when no one is moving
specialists: [Volt, Sage]
hardware: true
match_keywords: [presence, occupancy, mmwave, radar, ld2410, still, sitting, desk, room occupied, no motion]
related_example: examples/complete-smart-room
---

# Room Presence (mmWave)

## What you get

PIR sensors fail the moment you sit still at a desk and the lights snap off. An LD2410 24GHz radar detects a stationary body, so "occupied" stays true while you read, work, or watch TV. This is the upgrade path from motion-light when the off-too-soon problem annoys you.

## Hardware

| Part | Purpose | LCSC | Notes |
|------|---------|------|-------|
| ESP32 dev board | MCU | TBD | UART pins needed |
| HLK-LD2410-P | 24GHz presence radar | C5183133 | UART; LD2410B adds Bluetooth config, LD2410C is smaller |
| Dupont jumpers | UART + power | TBD | 4 wires |

## Wiring

```
LD2410       ESP32
VCC  ------- 5V     (module is 5V powered, logic 3.3V)
GND  ------- GND
TX   ------- GPIO16 (ESP RX)
RX   ------- GPIO17 (ESP TX)
```

## Automation pattern

1. **trigger:** `binary_sensor.<room>_presence` turns on -> keep the room "occupied".
2. **trigger:** presence clears for a short delay (mmWave is reliable, so 1-2 min, not 10) -> mark unoccupied.
3. **action:** drive lights, climate setback, or a media pause off the occupancy state rather than raw motion.
4. Combine with a PIR for instant-on plus stay-on: PIR for the fast rising edge, radar for holding the state.

## Dashboard skeleton

- Binary occupancy chip per room with a clear on/off color.
- Distance/energy gauge from the LD2410 gate data (for tuning the detection zone).
- History timeline of occupancy to sanity-check false holds.

## Customise

- **Clear delay:** 1-2 min; radar rarely drops a present person, so keep it short.
- **Detection gates:** trim the LD2410 max distance so it ignores the hallway through a doorway.
- **Sensitivity:** per-gate thresholds to reject a moving curtain or a fan.
- **Fusion:** add a PIR for the instant-on edge.

## Build it

Pick this and Volt generates the LD2410 UART firmware with the gate tuning exposed as numbers, and Sage rebuilds your room automations on the occupancy state. Read `examples/complete-smart-room` for presence fused with motion, climate, and scenes.
