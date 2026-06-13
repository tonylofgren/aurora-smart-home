---
name: vacation-mode
intent: Make an empty house look lived-in and stay safe while you are away
specialists: [Sage]
hardware: false
match_keywords: [vacation, holiday, away, presence simulation, lights random, security, empty house, burglar, lived in]
related_example: examples/complete-smart-room
---

# Vacation Mode

## What you get

One switch that puts the house into a believable lived-in pattern: lights come on and off on a plausible schedule, blinds move, and security alerts get sharper. No new hardware: it orchestrates the lights, covers, and sensors you already have.

## Automation pattern

1. **Enable:** an `input_boolean.vacation_mode` (or the long-absence path from `presence-routine`) is the master switch.
2. **Lighting simulation:** in the evening, turn a rotating subset of lights on/off at slightly randomised times around your normal pattern (not the obvious "7pm every day" tell).
3. **Covers:** open in the morning, close at dusk, jittered by a few minutes.
4. **Security sharpening:** any motion or door event while in vacation mode sends a high-priority notification with a camera snapshot if available.
5. **Energy:** water heater to eco, climate to a deep setback.

Randomise with a template using `range` and the minute of the hour so the schedule is not identical day to day.

## Dashboard skeleton

- Master vacation toggle, prominent.
- "Last activity" panel: most recent motion/door events with timestamps.
- Map or people card confirming nobody is actually home.

## Customise

- **Light set:** which lights participate in the simulation.
- **Jitter window:** how many minutes around the base schedule to randomise.
- **Quiet vs alert:** whether routine simulation events notify you (usually no) versus security events (always).
- **Climate setback:** how far to let temperature drift while away.

## Build it

Pick this and Sage generates the vacation toggle, the randomised lighting/cover simulation, and the sharpened security automations. No device to build. Pair with `presence-routine` so a 24-hour absence can arm vacation mode automatically.
