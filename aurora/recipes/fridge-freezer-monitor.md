---
name: fridge-freezer-monitor
intent: Alert when a fridge or freezer drifts out of its safe temperature range
specialists: [Volt, Sage]
hardware: true
match_keywords: [fridge, freezer, refrigerator, temperature alert, ds18b20, food safety, door left open, defrost]
related_example: examples/battery-temp-sensor
---

# Fridge / Freezer Monitor

## What you get

A waterproof probe inside the appliance reports temperature to Home Assistant, and you get a loud alert if it warms past a safe threshold for long enough to matter, meaning a door left ajar, a power cut, or a failing compressor before the food spoils.

## Hardware

| Part | Purpose | LCSC | Notes |
|------|---------|------|-------|
| ESP32 dev board | MCU | TBD | Any ESP32 |
| DS18B20 (waterproof) | 1-Wire temperature probe | C9753 | Genuine Maxim; ROM family code 0x28. Waterproof lead version goes inside |
| 4.7k resistor | 1-Wire pull-up | TBD | Between data and 3V3 |

## Wiring

```
DS18B20      ESP32
Red   ------ 3V3
Black ------ GND
Yellow ----- GPIO4   (+ 4.7k pull-up to 3V3)
```

## Automation pattern

1. **trigger:** `sensor.<name>_temp` above the safe ceiling for a sustained window (15-30 min, not instantaneous, so a defrost cycle does not false-alarm).
2. **condition:** none, or suppress during a known manual-defrost boolean.
3. **action:** high-priority notification with the current temperature and how long it has been high.
4. **recovery:** clear/notify when it returns to range; log the excursion duration for the record.

## Dashboard skeleton

- Tile card with the current temperature and a color threshold.
- History graph over 7 days (excursions stand out).
- Stat showing time-above-threshold today.

## Customise

- **Ceiling:** fridge 8 C, freezer -15 C are conservative defaults.
- **Sustain window:** 30 min for a freezer (thermal mass), 15 for a fridge.
- **Probe count:** add a second DS18B20 on the same 1-Wire bus for fridge + freezer in one device.
- **Escalation:** repeat the alert every N minutes until acknowledged.

## Build it

Pick this and Volt generates the DS18B20 firmware (deep-sleep friendly for a battery build) and Sage generates the sustained-excursion alert with recovery. Read `examples/battery-temp-sensor` for the battery-powered, long-life variant.
