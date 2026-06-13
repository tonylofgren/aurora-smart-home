---
name: presence-routine
intent: Run home and away routines automatically as people come and go
specialists: [Sage]
hardware: false
match_keywords: [presence, home, away, arrive, leave, device tracker, person, geofence, coming home, last person]
related_example: examples/complete-smart-room
---

# Home / Away Routine

## What you get

The house notices when the last person leaves and when the first person returns, and runs a routine for each: lights and heating down on departure, a welcome on arrival. No new hardware: it builds on the phone trackers and `person` entities Home Assistant already has.

## Automation pattern

1. **Everyone left:** trigger when a `group` or `binary_sensor` of all `person` entities goes to `not_home` for a buffer (10-15 min avoids a quick trip to the bin). Action: lights off, climate to away preset, optional confirmation notification.
2. **First person home:** trigger when the group flips back to `home`. Condition: after sunset for the welcome lights. Action: hallway/living lights on, climate to comfort, optional announcement.
3. **Long absence:** trigger on `not_home for: hours: 24`. Action: water heater to eco, vacation boolean on.

Use a 10-15 minute departure buffer to absorb a tracker briefly dropping to `not_home`. Combine GPS with router or BLE presence for reliability (see the presence-detection reference).

## Dashboard skeleton

- People card showing who is home with avatars.
- Mode chip: Home / Away / Vacation from an `input_select`.
- Quick-action buttons to force a mode manually.

## Customise

- **Departure buffer:** 10-15 min default.
- **Welcome trigger:** sunset offset, or always.
- **Climate presets:** which away/comfort temperatures to use.
- **Who counts:** which `person` entities are in the household group (exclude guests).

## Build it

Pick this and Sage generates the home/away/vacation automations plus the helpers and dashboard. No device to build. Pair with `room-presence` or `motion-light` for room-level behavior on top of house-level modes.
