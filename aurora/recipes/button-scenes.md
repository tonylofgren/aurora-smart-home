---
name: button-scenes
intent: Trigger scenes and routines from a button, single or double press
specialists: [Sage]
hardware: false
match_keywords: [button, scene, switch, remote, ikea, zigbee button, double press, long press, controller, dimmer]
related_example: examples/led-strip-controller
---

# Button Scene Controller

## What you get

One physical button drives several outcomes: single press runs a scene, double press runs another, long press does a third (all-off, say). Works with any button HA already sees: a Zigbee remote (IKEA, Hue, Aqara), an ESPHome button, or a dashboard tile. No new hardware required if you own a remote.

## Automation pattern

1. **trigger:** the button's event entity or device trigger, branched by `event_type` (single / double / hold).
2. **choose:** map each press type to an action:
   - single -> activate a scene (e.g. "Evening").
   - double -> a second scene (e.g. "Movie").
   - hold -> all-off or a household goodnight routine.
3. Keep the mapping in one automation with a `choose` block so the whole controller is one file to edit.
4. Optional: a `counter` so a third tap cycles brightness, for dimmer-style remotes.

Modern syntax: `triggers:` with the device/event trigger, `actions:` with a `choose:` on the press type.

## Dashboard skeleton

- A virtual mushroom-chips card mirroring the same scenes, so the button and the dashboard share behavior.
- An entity row showing the button's last-pressed action for debugging.

## Customise

- **Mapping:** which scene each press type runs.
- **Button source:** Zigbee remote, ESPHome button, or dashboard only.
- **Long-press action:** all-off, goodnight, or a specific scene.
- **Per-room copies:** clone the automation per room with different scenes.

## Build it

Pick this and Sage generates the button automation with the single/double/hold `choose` mapping and the matching dashboard chips. No device to build (bring your own remote). Read `examples/led-strip-controller` for buttons driving lighting effects end to end.
