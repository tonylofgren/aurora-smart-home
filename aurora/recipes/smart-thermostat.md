---
name: smart-thermostat
intent: Turn a dumb heater into a scheduled, sensor-driven thermostat
specialists: [Volt, Sage]
hardware: true
match_keywords: [thermostat, heating, heater, climate, relay, temperature control, schedule, radiator, setpoint]
related_example: examples/smart-thermostat-relay
---

# Smart Thermostat

## What you get

A temperature probe plus a relay turns a plain electric heater or boiler call into a Home Assistant `climate` entity: setpoints, schedules, and away setback. The device measures and switches; HA owns the schedule so you tune it from your phone.

## Hardware

| Part | Purpose | LCSC | Notes |
|------|---------|------|-------|
| ESP32 dev board | MCU | TBD | Any ESP32 |
| DS18B20 | Room temperature probe | C9753 | Genuine Maxim; place away from the heater itself |
| Relay module | Switch the heater / boiler call | TBD | Match the load; mains switching triggers a safety review |

Switching mains or a boiler trips the safety gate: Vera reviews isolation and failure-safe state before Volt builds.

## Wiring

```
DS18B20 data -- GPIO4 (+ 4.7k pull-up to 3V3)
Relay IN     -- GPIO5
heater load through the relay contacts, NOT the ESP
```

## Automation pattern

1. Use ESPHome's `climate` (bang-bang or PID) with the DS18B20 as the sensor and the relay as the heater output, so basic control survives even if HA is down.
2. **Schedule in HA:** a `schedule` helper or time-based automations set the target temperature per period (morning, day, evening, night).
3. **Away setback:** drop the target when `presence-routine` reports the house empty.
4. **Failure-safe:** relay restores to OFF on boot/reset so a crash cannot leave the heater stuck on.

## Dashboard skeleton

- Thermostat card on the `climate` entity.
- Schedule editor (schedule helper) for the daily setpoints.
- History graph: temperature vs setpoint vs heater on/off.

## Customise

- **Setpoints:** per-period target temperatures.
- **Hysteresis:** bang-bang deadband (e.g. 0.5 C) to avoid relay chatter.
- **Away setback:** how far to drop when empty.
- **Control mode:** simple bang-bang vs PID for a slow radiator.

## Build it

Pick this and Vera reviews the mains/boiler switching, Volt generates the ESPHome `climate` firmware with failure-safe relay state, and Sage adds the schedule and away setback. Read `examples/smart-thermostat-relay` for the complete build.
