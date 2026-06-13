---
name: daylight-lights
intent: Dim or switch lights to match the daylight in the room
specialists: [Volt, Sage]
hardware: true
match_keywords: [light, lux, ambient light, daylight, dim, brightness, bh1750, automatic brightness, cloudy, blinds]
related_example: examples/complete-smart-room
---

# Daylight-Adaptive Lights

## What you get

A lux sensor reports how bright the room actually is, so lights only come on when it is genuinely dark and can track the daylight: full on at dusk, off on a sunny afternoon, a nudge brighter when a cloud rolls over. This is the missing piece for the motion-light recipe, which wants a real lux reading instead of guessing from sunset time.

## Hardware

| Part | Purpose | LCSC | Notes |
|------|---------|------|-------|
| ESP32 dev board | MCU | TBD | Any ESP32 |
| ROHM BH1750 | Ambient light (lux) over I2C | C78960 | Address 0x23 (or 0x5C); 2.4-3.6V, use a 3.3V board |
| Dupont jumpers | I2C + power | TBD | 4 wires |

## Wiring

```
BH1750       ESP32
VCC  ------- 3V3
GND  ------- GND
SDA  ------- GPIO21
SCL  ------- GPIO22
ADDR ------- GND   (0x23; tie to 3V3 for 0x5C)
```

## Automation pattern

1. **trigger:** `sensor.<room>_illuminance` drops below the dark threshold for a short debounce.
2. **condition:** the room is occupied (pair with `motion-light` or `room-presence`).
3. **action:** turn the light on, optionally setting brightness inversely to lux so dim rooms get more light.
4. **daylight tracking (optional):** a second automation lowers or turns off the light when lux rises above the bright threshold, so afternoon sun does not leave lights burning.

## Dashboard skeleton

- Gauge or sensor tile for current lux.
- History graph of lux over 24h to pick good thresholds.
- The controlled light tile with a brightness slider.

## Customise

- **Dark threshold:** lux below which lights are allowed on (default 40).
- **Bright threshold:** lux above which lights turn off (default 200), with a gap from the dark threshold so it does not oscillate.
- **Brightness curve:** fixed brightness, or scale it inversely to measured lux.
- **Pairing:** combine with motion or presence so lights only follow daylight when someone is there.

## Build it

Pick this and Volt generates the BH1750 firmware while Sage generates the lux-driven lighting automations and the dashboard. Read `examples/complete-smart-room` for lighting combined with motion, presence, and scenes.
