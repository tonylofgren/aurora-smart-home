# Recipe Index

Curated starting points Aurora can suggest and then generate into a full project. Format spec: `_recipe-format.md`. When a user describes an intent, match it against the keywords below and offer the 3-5 closest recipes per the Question Rule, always including "or start from scratch".

Hardware recipes cite verified components from `aurora/references/components/`; HA-only recipes need no device.

| Recipe | Intent | Hardware | Specialists | Match keywords |
|--------|--------|----------|-------------|----------------|
| [co2-monitor](co2-monitor.md) | Track indoor CO2 and get alerted when air gets stuffy | yes (SCD40) | Volt, Sage | co2, carbon dioxide, air quality, ventilation, stuffy |
| [motion-light](motion-light.md) | Light on when someone enters, off when they leave | yes (PIR AM312) | Volt, Sage | motion, pir, hallway, automatic light, occupancy |
| [weather-station](weather-station.md) | Temperature, humidity, and pressure sensing | yes (BME280) | Volt, Sage, Iris | weather, temperature, humidity, pressure, barometer |
| [fridge-freezer-monitor](fridge-freezer-monitor.md) | Alert when a fridge or freezer drifts out of range | yes (DS18B20) | Volt, Sage | fridge, freezer, food safety, temperature alert |
| [room-presence](room-presence.md) | Detect a room is occupied even when no one moves | yes (LD2410) | Volt, Sage | presence, occupancy, mmwave, radar, sitting still |
| [presence-routine](presence-routine.md) | Run home/away routines as people come and go | no | Sage | home, away, arrive, leave, geofence, person |
| [energy-dashboard](energy-dashboard.md) | See where electricity goes and what it costs | no | Iris, Sage | energy, power, electricity, cost, kwh, usage |
| [notification-hub](notification-hub.md) | Useful, actionable phone notifications without spam | no | Sage | notification, alert, push, actionable, quiet hours |
| [vacation-mode](vacation-mode.md) | Make an empty house look lived-in and stay safe | no | Sage | vacation, holiday, presence simulation, security |
| [greenhouse](greenhouse.md) | Soil, temperature, and humidity automation for plants | yes (soil + BME280) | Volt, Sage | greenhouse, plant, soil moisture, watering, vent |
| [smart-thermostat](smart-thermostat.md) | Turn a dumb heater into a scheduled thermostat | yes (DS18B20 + relay) | Volt, Sage | thermostat, heating, heater, climate, schedule |
| [button-scenes](button-scenes.md) | Trigger scenes from a button (single/double/hold) | no | Sage | button, scene, remote, zigbee button, double press |

## How Aurora uses this

1. **Opening question:** offer recipes when the user's intent is broad ("I want to do something about air quality") rather than already-specified ("build an SCD40 on a XIAO C3").
2. **Suggest 3-5:** rank by keyword overlap with the user's description; present per the Question Rule with a recommendation and "start from scratch" as an option.
3. **Recipe-to-project:** load the recipe's `specialists`, then generate the full project folder exactly as if the user had described it, using the recipe's hardware, automation pattern, and dashboard skeleton as the starting point. The user customises the listed parameters afterward.

Recipes are deliberately fewer and more opinionated than the 27 worked projects in `examples/`. When a recipe has a `related_example`, point the user there for the complete reference build.
