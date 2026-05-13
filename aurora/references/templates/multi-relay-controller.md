# Multi-Relay Controller Template

Drives 8 relays from an ESP32-C3 using only 2 GPIOs (I2C), via a PCF8574 expander. Add a second PCF8574 (different I2C address) for 16 relays.

## When to use

- Garden irrigation with multiple zones
- Aquarium pumps/lights/heaters
- Garage door + lights + bath fan from one controller
- Server room PDU automation

## Recommended board

- **ESP32-C3 Super Mini**: 22 GPIO total, freeing them up for buttons/sensors
- Alternative: any ESP32 you already have

## External hardware

- **PCF8574 I2C expander** (~10 SEK breakout)
- **8-channel relay board** (5V coils, with optocoupler isolation strongly recommended)
- **Separate 5V supply for relay coils** (do not power the relays from the ESP's 3.3V rail)
- **MANDATORY**: flyback diodes are usually on the relay board, but verify -- they prevent ESP damage from coil back-EMF

## Safety warnings (mains AC)

- If switching mains AC: use a properly rated relay board with **isolation**, and follow local electrical code
- DO NOT terminate mains wiring in a hobbyist enclosure unless you are qualified
- Consider a Shelly Pro 4PM or similar certified product instead of DIY for AC

## Customization

- Add a second PCF8574 at 0x21 for 16 relays
- Add momentary buttons on free GPIO for local override
- Add interlock logic in HA automations to prevent simultaneous activation of conflicting loads
