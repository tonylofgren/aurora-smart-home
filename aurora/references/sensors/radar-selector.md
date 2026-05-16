# Radar Sensor Selector

Helps Volt choose the correct mmWave radar module. Run this **before** generating any YAML when
the project involves presence detection, occupancy, or zone-based automation.

## Decision Rule

```
User mentions "zone", "area", "region", "room sector", "multi-zone",
"X/Y position", or "which part of the room"?
  YES → LD2450 (or LD2461 if native zone firmware is preferred)
  NO  → LD2410 / LD2410B / LD2410C
```

Never recommend LD2410 for zone-based detection. LD2410 is single-point: it reports
one distance value and a presence/movement flag. It has no spatial awareness.

## Sensor Profiles

### HLK-LD2410 / LD2410B / LD2410C

| Property | Value |
|----------|-------|
| Frequency | 24 GHz mmWave |
| Targets | 1 (nearest) |
| Output | presence bool + detection distance (cm) |
| Zone support | No — global sensitivity gates only |
| ESPHome component | `ld2410` (stable, well-documented) |
| Price | ~80 SEK |
| Form factor | 35 × 10 mm |
| Use when | Simple on/off presence, PIR replacement, desk presence |
| Do NOT use when | User wants zones, sectors, or multi-area logic |

Gates on LD2410 are sensitivity bands (0-8), not physical zones. They adjust how
sensitive the radar is at each distance step — they do not identify which zone a
person is in.

### HLK-LD2450

| Property | Value |
|----------|-------|
| Frequency | 24 GHz mmWave |
| Targets | Up to 3 simultaneous |
| Output | X/Y coordinates + speed per target |
| Zone support | Yes — define rectangular zones in ESPHome YAML |
| ESPHome component | `ld2450` (stable as of ESPHome 2024.6) |
| Price | ~120 SEK |
| Form factor | 35 × 10 mm (same footprint as LD2410) |
| Use when | Zone-based presence, multi-person tracking, directional logic |
| Do NOT use when | Only simple on/off presence needed (LD2410 is cheaper and simpler) |

ESPHome zone configuration:

```yaml
ld2450:
  id: ld2450_radar
  uart_id: uart_ld2450

binary_sensor:
  - platform: ld2450
    ld2450_id: ld2450_radar
    zone_1:
      x1: -100  # cm from sensor center
      y1: 0
      x2: 100
      y2: 200
    name: "Zone 1 Presence"
```

### HLK-LD2461

| Property | Value |
|----------|-------|
| Frequency | 24 GHz mmWave |
| Targets | Up to 3 |
| Output | Zone presence (native firmware) |
| Zone support | Yes — zones configured in module firmware |
| ESPHome component | Limited (community, not in ESPHome core as of 2024) |
| Price | ~150 SEK |
| Form factor | 35 × 10 mm |
| Use when | Native zone firmware preferred, not using ESPHome zone YAML |
| Do NOT use when | Standard ESPHome setup (use LD2450 instead) |

## Volt Integration

Run this selector during **Step 2: Clarify Requirements**, before board selection
and before any YAML is written.

Trigger words that require running this selector:
- "zone", "zones", "area", "sector"
- "which part of the room", "corner", "desk vs couch"
- "multi-zone", "zone-based", "room zones"
- "track position", "X/Y", "coordinates"
- Any request combining radar + voice assistant + rooms (voice assist implies zones)

When LD2450 is selected, also:
1. Ask user to sketch or describe the zones (coordinates or plain description)
2. Translate to `x1/y1/x2/y2` values in the YAML (LD2450 origin = sensor center, +Y = away from sensor)
3. Add a calibration note: place a person in each zone and verify `target_x`, `target_y` sensors in HA

## Common Mistake

Using LD2410 when the user says "zone-based" is incorrect. The LD2410
`detection_distance` sensor can be used in HA automations to approximate zones
(e.g., "if distance < 150 cm → desk zone"), but this is a workaround with
significant limitations:
- Only one distance reading (nearest target)
- No X/Y discrimination (cannot distinguish left side vs. right side)
- Fails with multiple people

Always use LD2450 when the user explicitly asks for zones.
