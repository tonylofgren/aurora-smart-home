---
name: greenhouse
intent: Keep plants happy with soil, temperature, and humidity automation
specialists: [Volt, Sage]
hardware: true
match_keywords: [greenhouse, plant, soil moisture, watering, irrigation, grow, humidity, vent fan, garden]
related_example: examples/smart-greenhouse
---

# Greenhouse Controller

## What you get

Soil moisture, air temperature, and humidity from one device, with automations that vent when it gets too hot and remind you (or trigger a pump) when the soil dries out. A practical multi-sensor build that grows from "just watch the numbers" to "act on them".

## Hardware

| Part | Purpose | LCSC | Notes |
|------|---------|------|-------|
| ESP32 dev board | MCU | TBD | Spare ADC + I2C pins |
| Capacitive soil moisture v1.2 | Soil moisture (analog) | TBD | Hobby breakout, not stocked at JLCPCB; buy the genuine v1.2 with the 555 timer and gold traces |
| Bosch BME280 | Air temp + humidity | C92489 | I2C 0x76 |
| Relay or MOSFET | Drive a vent fan or pump | TBD | Match coil/load voltage; mains needs a safety review |

A pump or mains fan trips the safety gate: Vera reviews before Volt builds.

## Wiring

```
Soil sensor AOUT -- ESP32 GPIO34 (ADC1)
BME280 SDA/SCL   -- GPIO21/22
Relay IN         -- GPIO5
power/ground rails shared at 3V3 / GND (relay coil per its spec)
```

## Automation pattern

1. **Vent:** when BME280 temp above the ceiling, switch the fan relay on; off below ceiling minus hysteresis.
2. **Dry soil:** when soil moisture below threshold for a sustained window, notify or pulse the pump for a fixed, capped duration (never an open-ended "on").
3. **Safety cap:** a hard maximum watering time and a daily limit so a stuck sensor cannot flood the bed.

## Dashboard skeleton

- Gauges: soil moisture %, temperature, humidity.
- Fan and pump state with manual override buttons.
- History over a week to see watering cycles and day/night swings.

## Customise

- **Moisture threshold:** calibrate dry/wet against your soil; defaults are a starting point.
- **Vent ceiling:** target max temperature and hysteresis.
- **Watering pulse:** seconds per pulse and the daily cap.
- **Notify vs auto-water:** start notification-only, enable the pump once you trust the calibration.

## Build it

Pick this and Vera reviews any pump/mains element, Volt generates the multi-sensor firmware with the watering caps, and Sage builds the vent and watering automations. Read `examples/smart-greenhouse` for the full version.
