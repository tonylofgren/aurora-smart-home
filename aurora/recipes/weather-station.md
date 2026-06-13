---
name: weather-station
intent: Measure indoor or outdoor temperature, humidity, and pressure
specialists: [Volt, Sage, Iris]
hardware: true
match_keywords: [weather, temperature, humidity, pressure, bme280, thermometer, climate sensor, barometer]
related_example: examples/epaper-weather-station
---

# Weather Station

## What you get

A single BME280 reports temperature, humidity, and barometric pressure to Home Assistant. Pressure trend gives you a simple homemade forecast (falling fast means weather is turning), and the readings feed comfort automations. Add an e-paper display later if you want a glanceable panel.

## Hardware

| Part | Purpose | LCSC | Notes |
|------|---------|------|-------|
| ESP32 dev board | MCU | TBD | Any ESP32 |
| Bosch BME280 | Temp + humidity + pressure | C92489 | I2C 0x76/0x77; BMP280 (C83291) has no humidity, looks identical |
| Dupont jumpers | I2C + power | TBD | 4 wires |

Verify the chip ID register: 0x60 is BME280 (humidity), 0x58 is BMP280 (no humidity). The boards look the same.

## Wiring

```
BME280       ESP32
VIN  ------- 3V3
GND  ------- GND
SDA  ------- GPIO21
SCL  ------- GPIO22
```

## Automation pattern

1. **trigger:** `sensor.<name>_pressure` numeric change.
2. **action:** update a template sensor that classifies the 3-hour pressure trend (rising / steady / falling).
3. A comfort automation: when humidity above 65% for 30 min, notify or run a dehumidifier/fan.

## Dashboard skeleton

- Three gauge or tile cards: temperature, humidity, pressure.
- History graph combining all three over 48h.
- Template-sensor chip showing the forecast word from the pressure trend.

## Customise

- **Placement:** indoor comfort vs outdoor (outdoor needs a vented, rain-shielded enclosure; see the OpenSCAD template).
- **Humidity threshold:** 65% default for the comfort alert.
- **Display:** add an e-paper panel (see related example) or stay HA-only.
- **Altitude offset:** set your elevation so pressure reads as sea-level equivalent.

## Build it

Pick this and Volt generates the BME280 firmware, Sage adds the pressure-trend template sensor and comfort automation, and Iris lays out the dashboard. Read `examples/epaper-weather-station` for the version with a battery and an e-paper display.
