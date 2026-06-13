---
name: dc-power-monitor
intent: Measure the current and power a DC device or circuit is drawing
specialists: [Volt, Sage]
hardware: true
match_keywords: [power, current, energy, dc, ina219, consumption, amps, watts, solar, battery draw, 12v]
related_example: examples/energy-monitor
---

# DC Power Monitor

## What you get

An INA219 sits in line with a DC load and reports voltage, current, and power to Home Assistant. Use it to see what a 12V pump, a Pi, an LED strip, or a solar feed actually draws, spot a device that is stuck on, or log battery drain over time. This is the DC counterpart to the AC energy work in the energy-dashboard recipe.

## Hardware

| Part | Purpose | LCSC | Notes |
|------|---------|------|-------|
| ESP32 dev board | MCU | TBD | Any ESP32 |
| TI INA219 | High-side current + bus voltage over I2C | C2155799 | Address 0x40; bus voltage up to 26V; 0.1 ohm shunt on common breakouts |
| Dupont jumpers | I2C + power | TBD | 4 wires |

The INA219 measures up to 26V on the bus; the load current flows through its shunt, the ESP32 only reads it over I2C. Anything mains or above 5V switching still triggers a Vera safety review.

## Wiring

```
INA219       ESP32
VCC  ------- 3V3
GND  ------- GND
SDA  ------- GPIO21
SCL  ------- GPIO22

Vin+ / Vin- : in series with the DC load (high side), through the shunt
```

## Automation pattern

1. **read:** ESPHome's `ina219` platform exposes current (A), power (W), and bus voltage (V) sensors directly.
2. **trigger:** `sensor.<name>_power` above a ceiling for a sustained window means something is drawing more than expected.
3. **action:** notify, or cut a switch feeding the load.
4. **energy total (optional):** feed the power sensor into a `utility_meter` for Wh/day, same pattern as the energy-dashboard recipe.

## Dashboard skeleton

- Three tiles: current (A), power (W), bus voltage (V).
- History graph of power over 24h.
- Daily energy total from the utility meter.

## Customise

- **Shunt value:** match `shunt_resistance` to the board (0.1 ohm default) so current reads correctly.
- **Max current:** set `max_current` in the ESPHome config to the expected range for best resolution.
- **Power ceiling:** the over-draw alert threshold.
- **Cutoff:** whether a high reading just notifies or also switches the load off.

## Build it

Pick this and Volt generates the INA219 firmware with the shunt and max-current set, and Sage adds the over-draw alert and optional energy total. Read `examples/energy-monitor` for the AC, whole-house power-monitoring version.
