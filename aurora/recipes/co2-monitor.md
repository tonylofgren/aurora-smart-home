---
name: co2-monitor
intent: Track indoor CO2 and get alerted when the air gets stuffy
specialists: [Volt, Sage]
hardware: true
match_keywords: [co2, carbon dioxide, air quality, stuffy, ventilation, scd40, indoor air]
related_example: examples/air-quality-multi
---

# CO2 Monitor

## What you get

A small sensor that reports indoor CO2, temperature, and humidity to Home Assistant, with an automation that nudges you to open a window when CO2 climbs above a comfortable level. The canonical first build: one I2C sensor, no wiring drama, and an immediately useful number.

## Hardware

| Part | Purpose | LCSC | Notes |
|------|---------|------|-------|
| Seeed XIAO ESP32-C3 | MCU, USB-C | TBD | Any ESP32 works; C3 is small and cheap |
| Sensirion SCD40 | CO2 + temp + humidity (true NDIR) | C3659421 | I2C 0x62; do not confuse with SCD41 (5000 ppm range) |
| Dupont jumpers | SDA/SCL/3V3/GND | TBD | 4 wires |

## Wiring

```
SCD40        XIAO ESP32-C3
VDD  ------- 3V3
GND  ------- GND
SDA  ------- GPIO6
SCL  ------- GPIO7
```

## Automation pattern

1. **trigger:** `sensor.<name>_co2` rises above the threshold for 5 minutes (debounce avoids flapping at the boundary).
2. **condition:** someone is home and it is not the middle of the night.
3. **action:** send an actionable notification ("CO2 is 1200 ppm in the office - open a window?") and optionally turn on a ventilation fan.
4. A second automation clears the alert when CO2 drops back below threshold minus hysteresis.

## Dashboard skeleton

- Gauge card on `sensor.<name>_co2` with green/amber/red bands at 800 / 1200 ppm.
- History graph for CO2 over 24h.
- Entity row for temperature and humidity from the same sensor.

## Customise

- **Threshold:** 1000 ppm is a sensible default; 800 for sensitive sleepers, 1400 to reduce nagging.
- **Hysteresis:** how far CO2 must fall before the alert re-arms (default 200 ppm).
- **Room name:** drives entity IDs and the notification text.
- **Ventilation:** wire the action to a fan/window actuator, or leave notification-only.

## Build it

Pick this and Volt generates the ESPHome project (SCD40 on I2C, deep-sleep optional) plus Sage's CO2 automation and the dashboard. Read `examples/air-quality-multi` for a finished multi-sensor version with PM2.5 and VOC.
