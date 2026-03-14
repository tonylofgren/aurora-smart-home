# Aurora Smart Home — User Guide

> **The practical guide to getting great results from every skill**

This guide shows you *how to use* Aurora Smart Home — what to say, how to prompt, and how to get the best results from Claude. No need to read it cover to cover; jump to the skill you're working with.

---

## Table of Contents

### Getting Started
1. [What Can These Skills Do?](#1-what-can-these-skills-do)
2. [Installation in 2 Minutes](#2-installation-in-2-minutes)
3. [How to Activate a Skill](#3-how-to-activate-a-skill)
4. [How to Write Good Prompts](#4-how-to-write-good-prompts)
5. [When You're Stuck — How to Iterate with Claude](#5-when-youre-stuck--how-to-iterate-with-claude)

### Home Assistant YAML
6. [What the HA YAML Skill Does](#6-what-the-ha-yaml-skill-does)
7. [Example Prompts — Automations](#7-example-prompts--automations)
8. [Example Prompts — Blueprints](#8-example-prompts--blueprints)
9. [Example Prompts — Dashboards](#9-example-prompts--dashboards)
10. [Example Prompts — Templates and Helpers](#10-example-prompts--templates-and-helpers)
11. [Organizing Your Config — Packages and Includes](#11-organizing-your-config--packages-and-includes)
12. [Tips for Better HA Automations](#12-tips-for-better-ha-automations)

### ESPHome
13. [What the ESPHome Skill Does](#13-what-the-esphome-skill-does)
14. [Handling Secrets and Credentials](#14-handling-secrets-and-credentials)
15. [Example Prompts — Sensor Configs](#15-example-prompts--sensor-configs)
16. [Example Prompts — Lighting and Displays](#16-example-prompts--lighting-and-displays)
17. [Example Prompts — Advanced Features](#17-example-prompts--advanced-features)
18. [Designing a New Product (Idea → Production)](#18-designing-a-new-product-idea--production)
19. [Example Prompts — Product Development](#19-example-prompts--product-development)
20. [What a Product Design Conversation Looks Like](#20-what-a-product-design-conversation-looks-like)
21. [OTA Updates — Keeping Devices Updated](#21-ota-updates--keeping-devices-updated)
22. [Setting Up an OTA Update Server](#22-setting-up-an-ota-update-server)
23. [Tips for Better ESPHome Configs](#23-tips-for-better-esphome-configs)

### Node-RED
24. [What the Node-RED Skill Does](#24-what-the-node-red-skill-does)
25. [Example Prompts — Basic Flows](#25-example-prompts--basic-flows)
26. [Example Prompts — Logic and State](#26-example-prompts--logic-and-state)
27. [Example Prompts — External Data and APIs](#27-example-prompts--external-data-and-apis)
28. [Tips for Better Node-RED Flows](#28-tips-for-better-node-red-flows)

### HA Integration Dev
29. [What the Integration Dev Skill Does](#29-what-the-integration-dev-skill-does)
30. [Who Is This For?](#30-who-is-this-for)
31. [Example Prompts — Getting Started](#31-example-prompts--getting-started)
32. [Example Prompts — Advanced Integrations](#32-example-prompts--advanced-integrations)
33. [How to Share Your API with Claude](#33-how-to-share-your-api-with-claude)
34. [Tips for Integration Development](#34-tips-for-integration-development)

### Putting It All Together
35. [Cross-Skill Workflows](#35-cross-skill-workflows)
36. [Real-World Project Examples](#36-real-world-project-examples)
37. [Frequently Asked Questions](#37-frequently-asked-questions)

---

---

## Getting Started

---

## 1. What Can These Skills Do?

Aurora Smart Home gives Claude deep expertise in four areas of home automation:

| Skill | What You Use It For |
|-------|---------------------|
| **ha-yaml** | Writing YAML automations, blueprints, scenes, and dashboards for Home Assistant |
| **esphome** | Configuring ESP32/ESP8266 devices AND designing new IoT products from scratch |
| **node-red** | Building visual Node-RED flows (the output is importable JSON you paste into Node-RED) |
| **ha-integration** | Writing Python custom components for Home Assistant (for developers) |

**Without these skills**, Claude has general knowledge but may use outdated syntax, miss modern patterns, or give generic advice. **With these skills**, Claude has detailed, current knowledge — right down to correct GPIO pins, exact YAML syntax for HA 2026.x, and which ESPHome component handles which sensor chip.

---

## 2. Installation in 2 Minutes

Run these commands in Claude Code (one at a time):

```bash
/plugin marketplace add tonylofgren/aurora-smart-home
/plugin install aurora@aurora-smart-home
/plugin install ha-yaml@aurora-smart-home
/plugin install esphome@aurora-smart-home
/plugin install node-red@aurora-smart-home
/plugin install ha-integration@aurora-smart-home
```

That's it. Skills are now available in every project.

> **Auto-update:** Run `/plugin` → Marketplaces → aurora-smart-home → Enable auto-update, and your skills stay current automatically.

---

## 3. How to Activate a Skill

### Automatic — just mention the topic

Skills activate when you use relevant keywords. You don't need to do anything special:

- Say **"ESPHome"**, **"ESP32"**, **"GPIO"** → ESPHome skill loads
- Say **"Node-RED"**, **"flow"** → Node-RED skill loads
- Say **"YAML automation"**, **"blueprint"**, **"automations.yaml"** → HA YAML skill loads
- Say **"custom integration"**, **"HACS"**, **"custom_components"** → Integration skill loads

### Manual — slash commands

If a skill doesn't activate automatically, use the explicit command:

```
/aurora:ha-yaml
/aurora:esphome
/aurora:node-red
/aurora:ha-integration
```

Type `/aurora:` and you'll see all available commands.

---

## 4. How to Write Good Prompts

The skills work best when you give enough context upfront. You don't need to be technical — just describe what you want clearly.

### Be specific

| Vague | Better |
|-------|--------|
| "Make a light automation" | "Turn on light.kitchen when motion is detected on binary_sensor.kitchen_motion, only after sunset, turn it off 5 minutes after motion stops" |
| "Create an ESPHome config" | "ESP32-C3 with a BME280 on I2C, SDA on GPIO5, SCL on GPIO6. I want temperature, humidity, and pressure in HA" |
| "Make a Node-RED flow" | "Send me a mobile notification when my front door has been open for more than 2 minutes" |

### Tell the skill what you have

- **ESPHome:** Always say what board you're using. ESP32 has 12+ variants — the config is different for each.
- **HA YAML:** Say your entity IDs if you know them. If not, describe what the device is.
- **Node-RED:** Describe the trigger and the result. What starts the flow? What should happen?
- **Integration Dev:** Share an example API response or link to the API docs.

### The skill will ask clarifying questions — that's normal

Skills ask a few questions before generating anything. This is by design — the wrong config is slower than asking first. Answer as specifically as you can.

---

## 5. When You're Stuck — How to Iterate with Claude

Skills are built for back-and-forth. You don't have to get everything right in the first message.

### Paste error messages directly

If a config fails to compile or an automation doesn't work, paste the error:

```
My ESPHome config gives this error when compiling:
  [ERROR] Component 'bme280' not found.
  Did you mean 'bme280_i2c'?

Here's the relevant part of my config: [paste YAML]

Please fix it.
```

```
My automation triggers at the wrong time. Here's the YAML: [paste YAML]
It fires even during the day — I only want it after sunset. What's wrong?
```

### Ask for modifications, not rewrites

You don't have to start over when you want a change:

```
The flow you generated works, but I want to add a condition:
only trigger if input_boolean.guest_mode is off.
Here's the current flow JSON: [paste]
```

### Show Claude what your data looks like

For integrations and Node-RED, showing the actual data structure gets much better results:

```
Here's the JSON my API returns:
{
  "devices": [
    {"id": "abc123", "name": "Living Room", "temp": 21.5, "hum": 45},
    {"id": "def456", "name": "Bedroom", "temp": 19.2, "hum": 50}
  ]
}

Create sensor entities for each device.
```

### Iterate step by step

For complex projects, build one piece at a time:

```
Step 1: Create the ESPHome config (done ✓)
Step 2: Now create the HA automation that uses the sensors from that config
Step 3: Then create the dashboard card
```

---

---

## Home Assistant YAML

---

## 6. What the HA YAML Skill Does

The `ha-yaml` skill generates correct, modern Home Assistant YAML for:

- **Automations** — triggers, conditions, actions, multi-trigger logic
- **Blueprints** — reusable templates you can share and import
- **Scripts** — reusable action sequences
- **Scenes** — saved device states
- **Template sensors** — calculated sensors using Jinja2
- **Dashboards** — Lovelace layouts, Mushroom cards, Sections views
- **Helpers** — input_boolean, input_number, counters, timers
- **Packages** — organize your config by room or function

The skill always uses modern HA syntax (`action:` not `service:`, plural keys like `triggers:`).

---

## 7. Example Prompts — Automations

### Motion light with timeout
```
Create an automation that turns on light.hallway when binary_sensor.motion_hall
detects motion. Turn it off 3 minutes after motion stops. Only activate
between sunset and sunrise.
```

### Away mode
```
Write an automation that turns off all lights and sets the thermostat to
eco mode when everyone leaves home. Use person.john and person.jane.
Wait 5 minutes before acting to avoid false triggers when I just step outside.
```

### Washing machine done notification
```
Create an automation that notifies me when the washing machine finishes.
It's a smart plug: sensor.washing_machine_power.
"Done" means power drops below 5W after having been above 50W.
```

### Morning routine
```
Write an automation that runs every weekday at 07:00:
1. Gradually raise light.bedroom from 10% to 80% over 10 minutes
2. Start my morning playlist on media_player.bedroom_speaker at 30% volume
3. Announce today's weather via TTS
Only run if input_boolean.alarm_active is on.
```

### Door left open alert
```
Send a notification if any of these doors have been open for more than 10 minutes:
- binary_sensor.front_door
- binary_sensor.back_door
- binary_sensor.garage_door
Include which door it is in the notification message.
```

### Adaptive lighting based on time
```
Create an automation that adjusts light.living_room color temperature
automatically throughout the day:
- 06:00–10:00: warm white 2700K at 40%
- 10:00–17:00: daylight 4000K at 80%
- 17:00–22:00: warm white 3000K at 60%
- 22:00–06:00: dim warm 2200K at 20%
```

### Energy price-based device control
```
Write an automation that:
- Turns on switch.dishwasher when electricity price (sensor.nordpool_price)
  drops below 0.50 kr/kWh
- Turns it off if price rises above 1.20 kr/kWh mid-cycle
- Never runs between 07:00 and 09:00 regardless of price
```

---

## 8. Example Prompts — Blueprints

Blueprints are useful when you want the same logic applied to multiple rooms — configure once, reuse everywhere.

### Motion light blueprint
```
Create a blueprint for motion-activated lights with configurable timeout.
Let the user pick any motion sensor and any target light(s).
Include an option to restrict it to certain hours or only when the sun is down.
```

### Low battery alert blueprint
```
Write a blueprint that notifies when any sensor's battery drops below a
configurable threshold (default 20%). Should work with any device that
has a battery_level attribute.
```

### Thermostat schedule blueprint
```
Create a blueprint for a weekly thermostat schedule. Users should be able
to set different temperatures for weekdays vs weekends, and day vs night.
```

### Guest mode blueprint
```
Create a blueprint that enables a "guest mode" on a chosen input_boolean.
When enabled: raise lights to 80%, disable presence-based automations,
set thermostat to 21°C. When disabled: restore previous states.
```

---

## 9. Example Prompts — Dashboards

### Room overview card
```
Create a Mushroom room card for my living room showing:
- Room name and current temperature (sensor.living_room_temp)
- Quick toggles for the main light and TV
- Color changes to amber when any light is on
- Tap to navigate to a living-room detail view
```

### Climate dashboard
```
Generate a Sections dashboard for climate monitoring. Sensors:
- sensor.bedroom_temp / sensor.bedroom_humidity
- sensor.living_room_temp / sensor.living_room_humidity
- sensor.outdoor_temp / sensor.outdoor_humidity
Include a graph card for temperature history over the last 24 hours.
```

### Energy overview
```
Create an energy monitoring dashboard with:
- Current power consumption (sensor.total_power_w)
- Daily and monthly energy use (sensor.energy_today_kwh, sensor.energy_month_kwh)
- Electricity price (sensor.nordpool_price) and estimated daily cost
- A gauge card showing if we're above the daily average
```

### Security panel
```
Create a security dashboard showing:
- All door/window sensors with open/closed state (I have 6 sensors)
- Camera feeds from camera.front_door and camera.backyard
- Alarm state and arm/disarm buttons
- Last motion event time for each camera
```

---

## 10. Example Prompts — Templates and Helpers

### Average temperature sensor
```
Create a template sensor that averages temperature across all rooms:
sensor.bedroom_temp, sensor.living_room_temp, sensor.kitchen_temp.
Call it "Average Home Temperature". Show 1 decimal place.
```

### Window open + heating interlock
```
Create a binary sensor that is "on" when any window is open AND the heating
is active. Windows: binary_sensor.window_1 through binary_sensor.window_4.
Heating is climate.living_room in heat mode.
Use it in an automation to alert me.
```

### Time-of-day helper
```
Create an input_select with values: Morning, Day, Evening, Night.
Write an automation that automatically updates it:
- Morning: 06:00–09:00
- Day: 09:00–17:00
- Evening: 17:00–22:00
- Night: 22:00–06:00
```

### Calculated energy cost sensor
```
Create a template sensor that calculates the running electricity cost today.
Formula: sensor.energy_today_kwh × sensor.nordpool_price (current price).
Show as currency in SEK with 2 decimal places.
```

---

## 11. Organizing Your Config — Packages and Includes

As your Home Assistant config grows, splitting it into files by room or function keeps it manageable. The `ha-yaml` skill can help you set this up.

### Ask for a package structure
```
My configuration.yaml is getting too long. Help me split it into packages
organized by room. I have: living room, bedroom, kitchen, and outdoor.
Each package should contain the automations, scripts, and helpers for that room.
```

### Ask to organize an existing config
```
Here's my current automations.yaml: [paste content]
Split it into packages — one file per topic:
lighting.yaml, climate.yaml, security.yaml, notifications.yaml.
Show me the configuration.yaml includes too.
```

### How packages work (for reference)

```yaml
# configuration.yaml — the only file you edit after setup
homeassistant:
  packages:
    living_room: !include packages/living_room.yaml
    bedroom:     !include packages/bedroom.yaml
    climate:     !include packages/climate.yaml
    security:    !include packages/security.yaml
```

Each package file contains all the YAML for that area — automations, scripts, helpers, sensors — all in one place.

---

## 12. Tips for Better HA Automations

**Give your entity IDs.** Even approximate ones help. If you're unsure, describe the device — "my kitchen ceiling light" is enough for Claude to use a placeholder you can easily replace.

**Describe the logic in plain language first.** You don't need to know YAML. "Turn on when motion, but only at night, off after 5 minutes with no motion" is a perfect prompt.

**Mention edge cases.** What if two automations conflict? What if someone's already home when the away mode triggers? Name the edge case and the skill handles it.

**Ask for blueprints** when you'll apply the same logic to multiple rooms or devices.

**Ask for the UI editor format** if you'd rather click than edit files. Say "generate this for the Home Assistant UI editor" and the skill adjusts the output format.

**Paste your existing YAML** when you want to fix or extend something rather than starting fresh.

---

---

## ESPHome

---

## 13. What the ESPHome Skill Does

The `esphome` skill does two things:

1. **Configure existing devices** — generate correct ESPHome YAML for your specific hardware
2. **Design new IoT products** — guide you from idea to finished product, including hardware selection, PCB design, enclosure, certifications, and manufacturing

For device configs, it creates ready-to-flash YAML files. For product development, it creates a complete project folder with firmware, bill of materials, wiring guide, and production instructions.

---

## 14. Handling Secrets and Credentials

ESPHome uses a `secrets.yaml` file to keep sensitive values — WiFi passwords, API keys, OTA passwords — out of your main config files. This is important because your `.yaml` device files can be shared safely; `secrets.yaml` never leaves your machine.

### How secrets work

Your device config references secrets by name:
```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password
```

Your `secrets.yaml` (in the same folder, never shared) holds the actual values:
```yaml
wifi_ssid: "MyHomeNetwork"
wifi_password: "mysecretpassword123"
api_encryption_key: "base64encodedkey=="
ota_password: "myotapassword"
```

### Ask Claude for a secrets template
```
Generate a secrets.yaml.example file for my ESPHome config.
Use placeholder values so I can fill in my own credentials.
```

### Important rules

- **Never paste real credentials** into the chat. Use `!secret wifi_password` in any YAML you share.
- The skill **never asks for your actual passwords**. If it needs values, it uses `!secret` references.
- Keep `secrets.yaml` out of git: add it to `.gitignore`.
- The skill always generates `secrets.yaml.example` for product development projects.

---

## 15. Example Prompts — Sensor Configs

### Temperature and humidity sensor
```
Create an ESPHome config for an ESP32-C3 DevKit with a BME280 on I2C.
SDA on GPIO5, SCL on GPIO6. I want temperature, humidity, and pressure in HA.
```

### CO2 monitor with display
```
ESP32-S3 with:
- SCD40 CO2 sensor on I2C (default pins)
- SSD1306 OLED (128x64, I2C 0x3C) showing CO2, temp, and humidity
- LED on GPIO8 that goes red when CO2 is above 1000ppm
```

### mmWave presence sensor
```
ESP32-C3 with an LD2410 radar on UART (TX=GPIO17, RX=GPIO16).
Separate binary sensors in HA for motion, still presence, and occupancy.
```

### Outdoor weather station
```
ESP32 weather station with BME280 (temp/hum/pressure), BH1750 (light level),
and a rain sensor on GPIO34 (analog). 5V solar + LiPo backup.
Deep sleep with 5-minute wake intervals to save power.
```

### Smart plug with energy monitoring
```
DIY smart plug with ESP32-C3 and HLW8012 energy monitoring chip.
Power, voltage, current, and energy sensors plus relay switch.
Same pinout as Sonoff S31.
```

### Multi-room CO2 network
```
I want 4 identical sensor nodes, one per room.
Each: ESP32-C3 + SCD40 CO2 + SHT4x for temperature/humidity.
Create one base config using substitutions so I can set device name
and room name per device. Shared secrets.yaml for all.
```

---

## 16. Example Prompts — Lighting and Displays

### WS2812B LED strip
```
ESP32 with WS2812B strip on GPIO13, 60 LEDs.
Full RGBW color control in HA, plus rainbow, color wipe, and fire effects.
```

### LVGL touchscreen thermostat
```
ESP32-S3 with ILI9341 TFT and touch controller.
LVGL thermostat UI showing: current temp (BME280), setpoint control,
on/off toggle, and clock in the corner.
```

### E-ink home status display
```
Waveshare 2.9" e-ink on ESP32-C3.
Show: who's home, lights on/off count, current temp, and today's date.
Update every 5 minutes. Deep sleep between updates.
```

### LED matrix dashboard
```
ESP32 driving a 64x32 HUB75 LED matrix (4 panels in a row = 256x32).
Scroll through: time, outdoor temperature, electricity price, and next
calendar event pulled from HA. Update every 30 seconds.
```

---

## 17. Example Prompts — Advanced Features

### Voice assistant satellite
```
Local voice assistant satellite on ESP32-S3:
- INMP441 I2S microphone (GPIO10/9/8)
- MAX98357A speaker (GPIO11)
- Micro Wake Word detection
Connected to my HA Assist pipeline.
```

### BLE tracker / proxy
```
ESP32 as Bluetooth proxy for room presence detection.
Forward all BLE advertisements to HA and track specific devices.
```

### Matter light switch
```
ESP32-C6 Matter light switch that works with Apple Home, Google Home,
and Home Assistant without a separate hub.
```

### Commercial device conversion
```
Convert my Shelly 1 Mini to ESPHome.
Keep the relay on the correct pin, expose the switch input.
```

### Irrigation controller
```
ESP32 controlling 6 irrigation zones via relay board (GPIO14–19).
Each zone: name, run duration (configurable from HA), and last-run timestamp.
Rain sensor on GPIO34 that blocks watering.
Schedule via HA calendar entity.
```

---

## 18. Designing a New Product (Idea → Production)

When you want to design an entirely new device — not just configure existing hardware — the ESPHome skill becomes a full product development guide.

It walks you through:

1. **Requirements** — what it does, power source, environment, certifications needed
2. **Component selection** — MCU, sensors, and power supply with real prices from LCSC/Mouser
3. **Prototyping** — breadboard first, then PCB
4. **PCB design** — KiCad workflow, layout rules, what files to send to JLCPCB
5. **Firmware** — production-ready config with OTA updates
6. **Enclosure** — 3D print recommendations or off-the-shelf options with IP ratings
7. **Certification** — CE/FCC strategy, pre-certified module approach
8. **Manufacturing** — small batch vs production scale, assembly instructions and cost

The skill creates a complete project folder with all files organized.

---

## 19. Example Prompts — Product Development

### Simple product
```
I want to design a small indoor air quality monitor to sell as a kit.
CO2, temperature, humidity, small OLED display, USB-C powered.
Target BOM cost: around $20. Guide me through the full design.
```

### Detailed brief
```
Design a complete ESPHome product:

Product: Smart greenhouse sensor node
Sensors: soil moisture, air temp/humidity, light level, CO2
Power: Solar + LiPo backup, outdoor, 1 week without sun
Connectivity: WiFi to Home Assistant
IP rating: IP65 minimum
Volume: 10 units for myself, possibly 50-100 later
CE certification: not needed (personal use)

Create the full project: BOM with prices, ESPHome config, wiring diagram,
and enclosure recommendations.
```

### Hardware advice only
```
I'm building a battery-powered door sensor.
Compare ESP32-C3, ESP32-H2, and nRF52840 for lowest power consumption.
Include estimated battery life with a CR2032 for each.
```

### Selling a device
```
I want to sell a plug-and-play indoor air quality monitor.
CO2 + temp/hum + OLED, USB-C powered. Under $40 retail, first batch 25 units.
I need CE marking for EU sales.
Create the complete product: BOM, firmware, enclosure spec, cost estimate.
```

---

## 20. What a Product Design Conversation Looks Like

Product development is always a conversation. Here's what a typical session looks like:

---

**You:** I want to design a battery-powered soil moisture sensor for outdoor use.

**Claude:** Great, I'll help you design this. A few questions to make sure we get it right:

1. How long should the battery last between charges? (e.g., 1 week, 1 month, 1 season)
2. What's the target environment — just outdoor, or could it be partially submerged?
3. Do you need WiFi (for real-time data) or is it fine to only sync occasionally?
4. How many units are you planning — just 1-2 for yourself, or more?

---

**You:** Battery life 1 month minimum. IP67, it'll be buried partially. WiFi is fine but can sleep most of the time. Just for myself, maybe 3-4 units.

**Claude:** Perfect. Here's what I recommend:

- **MCU:** ESP32-C3 — cheapest option with WiFi, excellent deep sleep (10µA)
- **Sensor:** Capacitive soil moisture sensor (no corrosion vs resistive)
- **Power:** 18650 Li-ion + TP4056 charger, solar optional
- **Enclosure:** IP67-rated ABS box with cable gland for sensor probe

Estimated battery life at 15-min readings: ~45 days. Want me to proceed and generate the full project folder?

---

**You:** Yes, let's go. Add a temperature sensor too.

**Claude:** *[Creates project folder with firmware, BOM, wiring guide, and enclosure spec]*

```
soil-moisture-sensor/
├── README.md                  (overview, specs)
├── firmware/
│   ├── soil-sensor.yaml       (ESPHome config — ready to flash)
│   └── secrets.yaml.example   (credentials template)
├── hardware/
│   ├── bom.md                 (6 components, est. $12/unit at LCSC)
│   └── wiring-diagram.md      (GPIO assignments, power circuit)
└── enclosure/
    └── requirements.md        (IP67, 80×45×30mm, cable gland M12)

Next steps:
1. Order parts from bom.md
2. Wire on breadboard using wiring-diagram.md
3. Flash: esphome run firmware/soil-sensor.yaml
```

---

This back-and-forth is normal and expected. Claude asks what it needs, you answer, and together you arrive at a precise design.

---

## 21. OTA Updates — Keeping Devices Updated

OTA (Over-the-Air) updates let you update firmware without physical access to the device.

### Which strategy should I use?

| Situation | Strategy |
|-----------|----------|
| Single device at home, on your network | Local OTA via ESPHome Dashboard or CLI |
| Device given to others (10–100 units) | GitHub + `dashboard_import` — users update via HA |
| Commercial product, automatic updates | Self-hosted HTTP OTA server |
| Fleet in one building (office, hotel) | ESPHome Dashboard on local network |

### Asking Claude to set up OTA

```
Set up GitHub-based OTA for my ESPHome product. I want customers to see
"Update available" in Home Assistant when I push a new version to GitHub.
My GitHub username is myuser, repo is my-sensor.
```

```
Add automatic OTA update checking to my firmware. The device should
check my server (updates.mycompany.com) every 6 hours and update itself
if a newer version is available. Include safe rollback.
```

---

## 22. Setting Up an OTA Update Server

### Option A: GitHub (Free, No Server Needed)

The easiest approach for consumer products. Home Assistant fetches your firmware YAML from GitHub and notifies users when the version changes.

**ESPHome config:**
```yaml
esphome:
  name: my-product
  project:
    name: "mycompany.my-product"
    version: "1.2.0"          # Bump this to release an update

dashboard_import:
  package_import_url: github://mycompany/my-product/firmware/my-product.yaml@main
  import_full_config: false
```

**To release an update:**
1. Bump `version: "1.2.0"` → `"1.3.0"` in your YAML
2. Commit and push to GitHub
3. Home Assistant detects the change and shows "Update available" to all users

No server, no cost, no maintenance.

---

### Option B: Self-Hosted HTTP OTA Server

For commercial products where you want devices to update themselves automatically — no user action needed. Devices periodically check a server, compare versions, and download new firmware if available.

**What you need:** Any static file host. Options from simplest to most control:

| Host | Cost | Setup |
|------|------|-------|
| Cloudflare Pages | Free | Connect GitHub repo, auto-deploys |
| AWS S3 / Cloudflare R2 | ~$0.02/GB | Upload files via CLI |
| VPS with nginx | ~$5/month | Full control, most flexible |

**Server file structure:**
```
/my-product/
├── manifest.json     ← Current version + firmware location
└── firmware.bin      ← Compiled ESPHome binary
```

**manifest.json:**
```json
{
  "name": "My Product",
  "version": "1.3.0",
  "builds": [{
    "chipFamily": "ESP32-C3",
    "parts": [{"path": "firmware.bin", "offset": 0}]
  }]
}
```

**ESPHome config (ask Claude to generate the full version):**
```yaml
esphome:
  name: my-product
  project:
    name: "mycompany.my-product"
    version: "1.2.0"

update:
  - platform: http_request
    name: "Firmware Update"
    source: https://updates.mycompany.com/my-product/manifest.json

ota:
  - platform: http_request

safe_mode:
  reboot_timeout: 3min
  num_attempts: 5
```

With this setup, HA shows an Update entity for each device. You can also trigger the update from ESPHome itself without any user involvement.

**Building and deploying a new version:**
```bash
# 1. Bump version in YAML, then compile
esphome compile firmware/my-product.yaml

# 2. The binary is at:
#    .esphome/build/my-product/.pioenvs/my-product/firmware.bin

# 3. Upload to your server (nginx example)
scp .esphome/build/my-product/.pioenvs/my-product/firmware.bin \
    user@yourserver:/var/www/ota/my-product/firmware.bin

# 4. Update manifest.json with new version number
# 5. Done — devices check in within their update interval
```

**If using nginx**, here's a minimal config:
```nginx
server {
    listen 443 ssl;
    server_name updates.mycompany.com;
    root /var/www/ota;

    ssl_certificate /etc/letsencrypt/live/updates.mycompany.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/updates.mycompany.com/privkey.pem;

    location / {
        try_files $uri =404;
        add_header Access-Control-Allow-Origin *;
    }
}
```

Get a free SSL certificate: `sudo certbot --nginx -d updates.mycompany.com`

---

### Option C: ESPHome Dashboard (Local Network)

Best for a fleet in one location — no internet needed. You control when devices update.

```bash
docker run -d \
  --name esphome \
  --network host \
  -v /path/to/configs:/config \
  --restart unless-stopped \
  ghcr.io/esphome/esphome
```

Access at `http://your-server-ip:6052`. To update all devices:
```bash
# Update every device in your config folder
for yaml in /config/*.yaml; do
  esphome run "$yaml"
done
```

---

### OTA Strategy Summary

| Strategy | Cost | Automatic? | Scale | Best For |
|----------|------|-----------|-------|---------|
| GitHub + `dashboard_import` | Free | User clicks "Update" | 10–100 | Consumer products |
| Cloudflare Pages + HTTP OTA | Free | Yes | 100–10,000+ | Commercial, easy setup |
| S3 + HTTP OTA | ~$0.02/GB | Yes | Unlimited | Scalable commercial |
| nginx + HTTP OTA | ~$5/month | Yes | 100–10,000+ | Full control |
| ESPHome Dashboard (LAN) | Free | Admin clicks | 10–50 | Single location |
| `esphome run` (local) | Free | No | 1–10 | Development |

---

## 23. Tips for Better ESPHome Configs

**Always say your board.** `esp32dev` and `esp32-s3-devkitc-1` are completely different. Wrong board = wrong pin numbers.

**Give pin numbers if you've already wired things up.** "SDA on GPIO5, SCL on GPIO6" is perfect. If you haven't wired yet, the skill picks sensible defaults.

**Never share real passwords.** Use `!secret wifi_password` in any YAML you paste into the chat.

**Ask for a secrets template.** Say "also generate a secrets.yaml.example" and the skill creates a safe template with placeholder values.

**Describe unusual setups.** "I'm using GPIO21/22 for a display so I2C has to go elsewhere" helps the skill avoid conflicts.

---

---

## Node-RED

---

## 24. What the Node-RED Skill Does

The `node-red` skill generates importable Node-RED flow JSON. You paste the output directly into Node-RED (Menu → Import → Clipboard).

The skill uses current node names (`trigger-state`, `api-call-service`) — not the old names that silently fail. Every generated flow includes a comment node explaining what to configure and leaves the HA server field empty for you to fill in.

---

## 25. Example Prompts — Basic Flows

### Motion light with auto-off
```
Node-RED flow: turn on light.kitchen when binary_sensor.motion_kitchen detects motion.
Turn it off 5 minutes after motion stops. Reset the timer if motion is
detected again before the 5 minutes are up.
```

### Doorbell announcement
```
When binary_sensor.doorbell is pressed, play a TTS announcement on:
media_player.kitchen, media_player.living_room, media_player.bedroom.
Message: "Someone is at the door."
Only between 08:00 and 22:00.
```

### Presence-based heating
```
Node-RED flow for thermostat control:
- Set climate.living_room to "home" preset when any person arrives home
- Set to "away" when ALL persons have been gone for more than 10 minutes

Persons: person.john, person.jane
```

### Security alarm trigger
```
Create a Node-RED flow that:
1. Monitors all door/window sensors (binary_sensor.door_1 through binary_sensor.door_4)
2. When the alarm is armed (alarm_control_panel.home = armed_away) and any sensor opens:
   - Trigger a 30-second countdown
   - If alarm_control_panel isn't disarmed within 30 seconds: send a notification
     and trigger alarm_control_panel.trigger
3. Cancel everything if disarmed during countdown
```

### Adaptive scene controller
```
Create a flow that watches input_select.time_of_day and activates the right scene
when it changes:
- Morning → scene.morning_lights
- Day → scene.day_lights
- Evening → scene.evening_lights
- Night → scene.night_lights
```

---

## 26. Example Prompts — Logic and State

### Washing machine state machine
```
Track washing machine states using sensor.washing_machine_power:
- "standby": power < 5W
- "running": power > 50W
- "done": was running, now back to standby

Send a notification when it transitions to "done".
Store the current state in flow context so it survives a Node-RED restart.
```

### Multi-sensor averaging
```
Create a flow that calculates the average temperature across:
sensor.bedroom_temp, sensor.living_room_temp, sensor.kitchen_temp

Update input_number.average_home_temp in HA every minute with the result.
```

### Time-based mode switching
```
Create a flow that automatically sets input_select.home_mode based on time:
- 06:00: set to "Morning"
- 09:00: set to "Day"
- 17:00: set to "Evening"
- 23:00: set to "Night"
Also listen for person entities — if everyone leaves, set to "Away" regardless of time.
```

### Lockout prevention
```
Flow that prevents the heating from running when any window has been open
for more than 5 minutes. Windows: binary_sensor.window_1 to window_5.
Climate: climate.living_room. Resume heating when all windows are closed.
```

---

## 27. Example Prompts — External Data and APIs

Node-RED's HTTP request node makes it easy to pull data from external services and push it into Home Assistant.

### Electricity price automation
```
Create a flow that:
1. Fetches current electricity price from the Tibber API every hour
   (I'll provide my API token)
2. Stores the price in input_number.electricity_price in HA
3. If the price is below 0.50 kr/kWh, turn on switch.dishwasher
4. If above 1.50 kr/kWh, turn off switch.dishwasher and send a notification
```

### Weather-based automation
```
Every morning at 06:00, fetch today's weather forecast from the OpenWeatherMap API.
If rain is expected, send a notification: "Rain today — remember umbrella."
Only on weekdays. My API key will be in the flow as a variable.
```

### Public transit alerts
```
Create a flow that checks my bus line (line 42, stop "City Center") every 5 minutes
using the local transit API. If the next bus is delayed more than 5 minutes,
send a push notification with the new departure time.
```

### Smart energy management with price signal
```
Create a flow that reads hourly Nordpool electricity prices (fetched from a REST API),
finds the cheapest 2-hour window between 22:00 and 06:00, and automatically
schedules switch.water_heater to run during that window.
```

### Home status webhook
```
Create a flow triggered by a webhook that returns the current home status as JSON:
- Who is home (from person entities)
- Current temperature (sensor.living_room_temp)
- Lights on (count)
- Alarm state
I want to call this from an external script.
```

---

## 28. Tips for Better Node-RED Flows

**Describe trigger and outcome in plain language.** "When X happens, do Y" is the perfect Node-RED prompt. The skill handles the node wiring.

**Mention entity IDs.** Node-RED flows are entity-specific. The more precise you are, the less you'll need to edit the JSON afterward.

**For API flows, share the response format.** Paste an example of what the API returns — the skill maps it to HA entities exactly right.

**Ask for a plain-language description first.** Say "explain the flow before generating the JSON" if you want to verify the logic before getting the code.

**Keep flows focused.** One flow per automation is easier to debug than everything in one big flow. Ask for separate flows and connect them via link-in/link-out nodes.

---

---

## HA Integration Dev

---

## 29. What the Integration Dev Skill Does

The `ha-integration` skill writes Python code for Home Assistant custom components. This is how you connect a device or cloud service to HA in a way that looks and works just like a built-in integration — with a config UI, proper entities, update logic, and HACS publishing support.

---

## 30. Who Is This For?

This skill is for people who are comfortable with (or want to learn) Python. You don't need to be an expert — Claude writes the code — but you do need to be able to run Python, install files, and restart Home Assistant.

**Use this skill when:**
- You have a cloud service or local device that doesn't have an existing HA integration
- You want something that installs cleanly through HACS and looks professional
- YAML automations or Node-RED can't get the data you need (e.g., the service requires OAuth2 or a persistent connection)

**You probably don't need this skill if:**
- The service already has a HACS integration — search [HACS](https://hacs.xyz) first
- A REST sensor or MQTT sensor in YAML is enough for what you need
- You just want to call a webhook — the `rest_command:` in YAML handles that

---

## 31. Example Prompts — Getting Started

### Connect a simple REST API
```
Create a Home Assistant integration that polls this API every 5 minutes:
GET https://api.example.com/v1/sensors
Headers: Authorization: Bearer {api_key}

Example response:
{
  "sensors": [
    {"id": "abc", "name": "Living Room", "temp": 21.5, "humidity": 45},
    {"id": "def", "name": "Bedroom", "temp": 19.2, "humidity": 52}
  ]
}

I want temperature and humidity sensor entities for each room.
Auth via API key, entered in the config UI when adding the integration.
Save to custom_components/my_sensors/.
```

### Local device pushing data
```
Build a HA integration for a local device that sends JSON to a webhook.
The device POSTs to HA every 30 seconds:
{"device_id": "sensor-01", "temp": 22.1, "co2": 850, "battery": 87}

Create sensor entities for temp, CO2, and battery. Auto-discover new device IDs.
```

### Make it HACS-ready
```
Create a Home Assistant integration for the Tibber electricity API.
Auth: OAuth2. Entities: current price (sensor), today's prices (forecast),
and cost so far today.
Make it HACS-ready. My GitHub username is myuser.
```

---

## 32. Example Prompts — Advanced Integrations

### Device with multiple entity types
```
Integration for a smart thermostat API. The device has:
- Current temperature and humidity (sensors)
- Target temperature (climate entity, with heat/cool/auto modes)
- On/off switch
- Error state and last-seen timestamp

Polling every 60 seconds. API key auth. HACS-ready.
```

### Voice assistant / conversation agent
```
Build a HA integration that adds a conversation agent using the Anthropic API.
Users configure their API key in the HA UI. The agent should be available
as an Assist pipeline option. Store conversation history per session.
```

### Push-based websocket integration
```
Create an integration for a device that uses WebSocket.
The device connects to ws://device-ip:8765 and streams JSON events.
Map each event type to the correct HA entity (sensor, binary_sensor, switch).
Reconnect automatically if the connection drops.
```

---

## 33. How to Share Your API with Claude

The more you can tell Claude about the API, the better the generated code. Here's what helps most:

### Paste an example response
```
Here's what the API returns for GET /api/v1/status:
{
  "device": {
    "id": "abc123",
    "name": "My Device",
    "online": true,
    "last_seen": "2026-03-14T10:23:00Z"
  },
  "sensors": {
    "temperature": 21.5,
    "humidity": 45.2,
    "co2": 812
  },
  "settings": {
    "target_temp": 22.0,
    "mode": "heat"
  }
}

Create sensor entities for all sensor values, a climate entity for settings,
and a binary_sensor for the online state.
```

### Describe the authentication
```
Auth is Bearer token. Token never expires. User enters it in the config UI.
Include it in every request as: Authorization: Bearer {token}
```

```
Auth is OAuth2. The service uses authorization code flow.
Client ID and secret are entered in HA's application credentials.
Access tokens expire after 1 hour, refresh tokens after 30 days.
```

### Share the error responses
```
The API returns 401 when the token is invalid.
Returns 429 when rate-limited (max 60 requests/minute).
Returns 503 when the service is down.
Make sure the integration handles all three gracefully.
```

---

## 34. Tips for Integration Development

**Search HACS first.** Someone may have already built what you need. Check [hacs.xyz](https://hacs.xyz) before starting from scratch.

**Paste an API response.** This single step makes the biggest difference in output quality. Claude can map real JSON fields to correct entity types automatically.

**Ask for HACS-ready files upfront.** It's easier to include them from the start than to add them later. Just say "make it HACS-ready and my GitHub username is X."

**Ask for tests too.** Claude can generate pytest test files. Useful for verifying that entity values map correctly and error handling works.

**Iterate with error messages.** If the integration fails to load, paste the HA log error. Claude fixes it directly:
```
The integration fails with this error in HA logs:
AttributeError: 'NoneType' object has no attribute 'data'
  File ".../coordinator.py", line 47, in _async_update_data

Here's coordinator.py: [paste]
```

---

---

## Putting It All Together

---

## 35. Cross-Skill Workflows

Skills work best together. A typical project touches multiple layers:

```
Physical hardware
  → ESPHome firmware        (esphome skill)
      → HA entities
          → Automations     (ha-yaml skill)      — simple if/then logic
          → Node-RED flows  (node-red skill)     — complex state machines, API calls
  Cloud/local service
  → Custom integration      (ha-integration skill) — when no integration exists
      → HA entities
          → Automations or Node-RED
```

You can work on one layer at a time and reference what you've built in the next prompt.

---

## 36. Real-World Project Examples

### Project 1: Smart Room Sensor

A wall-mounted sensor for temperature, CO2, and presence that controls ventilation and lights.

**Step 1 — ESPHome config:**
```
Wall-mounted sensor: ESP32-C3, SHT4x (temp/hum), SCD40 (CO2),
LD2410 mmWave radar (presence), SSD1306 OLED. USB-C powered.
Create the full config with secrets template.
```

**Step 2 — Automation:**
```
Using sensors from my room sensor (sensor.co2, binary_sensor.presence):
- Turn on switch.ventilation when CO2 > 1000ppm
- Turn off when CO2 < 800ppm
- Notify me if CO2 stays above 1200ppm for more than 10 minutes
```

**Step 3 — Dashboard card:**
```
Mushroom card for the room sensor: CO2 level, temperature, presence state.
Color the CO2 display: green < 800, yellow < 1200, red above.
```

---

### Project 2: Energy Price Automation

Automatically run appliances when electricity is cheap.

**Step 1 — Integration for electricity price** (if no existing integration):
```
Create a HA integration that fetches hourly Nordpool prices for SE3.
Expose as sensor.nordpool_current_price and sensor.nordpool_prices_today (list).
```

**Step 2 — Node-RED flow:**
```
Flow that monitors sensor.nordpool_current_price and:
- Turns on switch.dishwasher and switch.water_heater when price < 0.50 kr/kWh
- Turns them off when price > 1.20 kr/kWh
- Never activates between 07:00–09:00 or 17:00–19:00
- Sends a daily summary of total cost saved
```

**Step 3 — Dashboard:**
```
Energy dashboard showing today's hourly prices as a bar chart,
current price highlighted, and which devices are currently active.
```

---

### Project 3: Selling an ESPHome Device

**Step 1 — Full product design:**
```
Design a plug-and-play indoor air quality monitor to sell.
CO2 + temp/hum + OLED, USB-C. Under $40 retail, first batch 25 units.
Need CE marking for EU. Full project: BOM, firmware, enclosure, cost estimate.
```

**Step 2 — OTA for customers:**
```
Add GitHub-based OTA to my air quality monitor.
Customers should see "Update available" in HA when I push to GitHub.
GitHub: myuser, repo: aq-monitor.
```

**Step 3 — Customer documentation:**
```
Write a quick-start guide for customers: how to add the device to HA,
what entities to expect, and how updates work.
```

---

## 37. Frequently Asked Questions

**Q: The skill asks a lot of questions before generating anything. Is that normal?**

Yes, and it's the right behavior. The wrong config wastes more time than a few clarifying questions. For ESPHome, the board type determines every GPIO number. For HA YAML, automation vs blueprint changes the entire output format.

---

**Q: Can I paste my existing code for Claude to fix or extend?**

Absolutely — this is one of the best ways to use the skills:
```
Here's my existing automation: [paste YAML]
It fires during the day but should only run after sunset. What's wrong?
```
```
Here's my Node-RED flow JSON: [paste]
Add a condition that skips it on weekends.
```

---

**Q: Can Claude read my actual entity IDs from Home Assistant?**

Not directly — Claude doesn't connect to your HA instance. But you can paste your entity list, or describe devices in plain language ("my kitchen ceiling light"). Claude uses whatever you give it.

---

**Q: How do I get files Claude generates onto my system?**

The skill will ask: save to disk or show in chat?

- **Save to disk** — Claude writes files directly to your current working directory in Claude Code
- **Show in chat** — Claude displays the code and you copy-paste it

For ESPHome product development, the skill always creates an organized project folder.

---

**Q: What if the code has an error?**

Paste the error back:
```
ESPHome compilation error:
  [ERROR] 'bme280' is not a valid component. Did you mean 'bme280_i2c'?
Can you fix it?
```
```
HA shows this error in the logs when loading my integration:
  ConfigEntryNotReady: Cannot connect to device
[paste the relevant Python file]
```
The skill debugs and fixes its own output.

---

**Q: Can I use these skills in my own language?**

Yes. Communicate with Claude in any language — Swedish, English, German, etc. The generated YAML, JSON, and Python will always be in English (required by the tools), but you can write prompts in any language.

---

**Q: How do I reuse a Node-RED flow pattern across multiple rooms?**

Ask for a subflow:
```
Create a Node-RED subflow for my motion light pattern so I can reuse it
in multiple rooms. The subflow should accept: sensor entity ID, light entity ID,
and timeout as configurable inputs.
```

---

**Q: Can the integration skill help if I don't know Python?**

Yes — Claude writes all the Python. You need to be able to: copy files to your `custom_components/` folder, restart Home Assistant, and paste error messages back when something goes wrong. The actual code is generated for you.

---

**Q: How do I share entity IDs efficiently when I have many sensors?**

Go to Home Assistant → Developer Tools → States, filter by domain, and paste the list:
```
Here are all my sensor entities:
sensor.bedroom_temp, sensor.bedroom_humidity, sensor.living_room_temp,
sensor.living_room_humidity, sensor.kitchen_temp, sensor.outdoor_temp
Create template sensors for the average of each type.
```

---

**Q: What's the difference between an automation and a Node-RED flow for the same task?**

Both can accomplish most things. Choose based on workflow:
- **HA Automation (YAML):** Simple triggers and actions, lives in HA, editable in the UI, version-controlled with your HA config
- **Node-RED flow:** Visual debugging, complex multi-step logic, external API calls, stateful workflows that track history

For simple "when X, do Y" tasks: use HA automation. For anything with state tracking, conditions based on external data, or complex branching: Node-RED is often cleaner.

---

**Q: Can I ask Claude to generate a complete project at once?**

Yes, especially for ESPHome products. A prompt like:

```
Design a complete smart soil moisture sensor project:
ESP32-C3, capacitive moisture sensor, DS18B20 temp probe, solar+LiPo.
Include: ESPHome config, BOM with prices, wiring diagram, HA automation
that alerts me when moisture drops below 30%.
```

...will produce all the pieces in one go. For complex projects, working step by step gives you more control and easier debugging.

---

*Aurora Smart Home v1.1.0 · [github.com/tonylofgren/aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
