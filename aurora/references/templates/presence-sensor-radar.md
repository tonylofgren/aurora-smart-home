# Presence Sensor (Radar) Template

True millimeter-wave radar presence detection. Unlike PIR sensors, radar detects sub-millimeter movement, so it stays ON when you're sitting still reading or sleeping.

## When to use

- Lighting that should not turn off while you're sitting on the couch
- Bedroom presence (PIR fails when you're asleep)
- Office desk presence (PIR fails when you're typing slowly)

## Recommended board

- **ESP32-C3 Super Mini**: minimal UART setup, BLE 5.0 if you want to extend

## External hardware

For simple presence (on/off):
- **HLK-LD2410** or **LD2410B/C** radar module (~80 SEK)
- 5V VCC; UART logic is 3.3V tolerant on RX, direct connect is fine

For zone-based presence (which area of the room):
- **HLK-LD2450** (~120 SEK) — provides X/Y coordinates for up to 3 targets
- Same footprint as LD2410, drop-in hardware replacement, different YAML component

**Do NOT use LD2410 for zones.** LD2410 reports one distance value; it has no
spatial awareness and cannot distinguish room sectors. See
`aurora/references/sensors/radar-selector.md` for the full decision guide.

## Customization

- Adjust LD2410 sensitivity via its native config (LD2410 Tool app or HA service)
- Combine with a light sensor to skip turning on lights in daylight
- For zone logic with LD2450: define `x1/y1/x2/y2` rectangles in ESPHome YAML and
  use separate `binary_sensor` entries per zone
