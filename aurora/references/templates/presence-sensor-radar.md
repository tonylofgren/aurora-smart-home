# Presence Sensor (Radar) Template

True millimeter-wave radar presence detection. Unlike PIR sensors, radar detects sub-millimeter movement, so it stays ON when you're sitting still reading or sleeping.

## When to use

- Lighting that should not turn off while you're sitting on the couch
- Bedroom presence (PIR fails when you're asleep)
- Office desk presence (PIR fails when you're typing slowly)

## Recommended board

- **ESP32-C3 Super Mini**: minimal UART setup, BLE 5.0 if you want to extend

## External hardware

- **HLK-LD2410** or **LD2410B/C** radar module (~80 SEK)
- 5V VCC (with level shifter if board is 3.3V-only on UART) -- actually LD2410 works at 5V VCC but its UART logic is 3.3V tolerant on RX, OK for direct connect

## Customization

- Adjust LD2410 sensitivity via its native config (LD2410 Tool app or HA service)
- Combine with a light sensor to skip turning on lights in daylight
- Use the `detection_distance` sensor to trigger zone-based automations (only when person is at the desk vs couch)
