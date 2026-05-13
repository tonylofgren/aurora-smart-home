<p align="center">
  <img src="assets/banner.png" alt="Aurora Smart Home - Claude Skills" width="100%">
</p>

# Aurora Smart Home

> **75,000+ lines** of documentation | **900+ example prompts** | **1,500+ code examples**
> **21 agents** | **6 Iron Laws** | **JSON-validated reference data**

The most comprehensive Claude Code skill pack for smart home development. **New in v1.6.0:** Volt validates ESPHome configs against machine-readable hardware profiles before generating YAML, instead of guessing from training memory. Covers automations, custom integrations, Node-RED flows, dashboards, and full product development from idea to manufacturing.

[![Claude Code](https://img.shields.io/badge/Claude_Code-Skills-7c3aed.svg)](https://docs.anthropic.com/en/docs/claude-code)
[![Home Assistant](https://img.shields.io/badge/Home_Assistant-2024.x--2026.x-41BDF5.svg)](https://www.home-assistant.io/)
[![ESPHome](https://img.shields.io/badge/ESPHome-2026.4.5-000000.svg)](https://esphome.io/)
[![Version](https://img.shields.io/badge/Version-v1.6.0-success.svg)](CHANGELOG.md)
[![Validated](https://img.shields.io/badge/Validated-against_datasheets-success.svg)](aurora/references/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

> ⚠️ **Use at your own risk.** Aurora generates code and recommendations for educational purposes. Smart home projects involve mains electricity, batteries, and devices that control locks, water, heating, and gas. AI-generated configurations can be plausible but wrong. The maintainers, contributors, and Anthropic accept no liability for property damage, personal injury, data loss, or any other harm. See [DISCLAIMER.md](DISCLAIMER.md) for full terms.

---

## 🔄 Already Installed? Update to v1.6.0

Claude Code does **not** auto-update installed plugins by default. New aurora releases ship validated boards, sensors, templates, and validator improvements regularly.

**Fast option — inside Claude Code:**

```
/reload-plugins
```

This pulls the latest version of every installed plugin (aurora included) and loads them into the current session.

**Targeted option — from your terminal (outside Claude Code):**

```
claude plugin update aurora@aurora-smart-home
```

Then restart Claude Code so the new files load.

**Note:** the slash command `/plugin` opens an interactive UI but does **not** accept arguments like `/plugin update <name>`. Only `/reload-plugins` or the CLI form above actually update aurora.

**Better solution:** enable auto-update once and forget. See [Enable Auto-Update](#enable-auto-update) below.

Aurora also self-reports its release date in the banner. If your aurora banner is more than 3 months past the date shown, it is time to update.

---

## At a Glance

|  | Home Assistant | Node-RED | ESPHome | Integration Dev | Aurora Orchestrator |
|---|:---:|:---:|:---:|:---:|:---:|
| **Reference Guides** | 49 | 12 | 38 | 17 | 21 agents + validators |
| **Example Prompts** | 300+ | 100+ | 600+ | 129 | Routing-driven |
| **Code Examples** | 700+ | 200+ | 1000+ | 200+ | (delegated) |
| **Ready Templates** | 17 | 15 | 30 | 10 | Project snapshots |
| **Coverage** | 50+ integrations | 31 nodes | 160+ components | Full HA framework | All skills |
| **Bonus** | Sections dashboard | Node-RED 4.x | **Product dev: idea → production** | HACS v2 | **Validates before generating** |

---

> **v1.3.0 - Breaking change:**
> Individual skill plugins have been removed. If you're upgrading from a previous version, copy and paste this entire block to reinstall:
> ```
> /plugin uninstall esphome@aurora-smart-home
> /plugin uninstall ha-yaml@aurora-smart-home
> /plugin uninstall node-red@aurora-smart-home
> /plugin uninstall ha-integration@aurora-smart-home
> /plugin marketplace add tonylofgren/aurora-smart-home
> /plugin install aurora@aurora-smart-home
> /reload-plugins
> ```

### What's New in v1.6.0

**Validation before generation**

Volt no longer relies on training memory for GPIO and component data. Aurora now ships machine-readable reference data and validators that Volt MUST consult before generating ESPHome YAML:

- JSON Schemas for board and component profiles (`aurora/references/schemas/`)
- ESP32-S3 DevKit C-1 board profile with full capability data (`aurora/references/boards/`)
- BME280 component profile with BMP280 disambiguation (`aurora/references/components/`)
- Pin validator and conflict validator (`aurora/references/validators/`)
- Iron Law 6 in Volt's soul: validate before generating
- pytest suite covering schemas, data integrity, and Volt workflow simulation (36 passing)

More hardware and sensors land in upcoming releases. See the validation coverage section below.

#### How Validation Works

```
You: "ESP32-S3 with BME280 on GPIO 19 + 20"
       |
       v
+----------------------------------------+
| Volt loads board profile:              |
|   aurora/references/boards/esp32/      |
|   esp32-s3-devkitc-1.json              |
| Volt loads component profile:          |
|   aurora/references/components/        |
|   temperature/bme280.json              |
+----------------------------------------+
       |
       v
+----------------------------------------+
| pin-validator + conflict-validator     |
| check every assignment:                |
|  - GPIO exists on this board?          |
|  - Reserved for USB / PSRAM / Flash?   |
|  - I2C addresses unique?               |
|  - Voltage compatible?                 |
+----------------------------------------+
       |
   Found a failure?
   /            \
  YES            NO
   |              |
   v              v
+-------+   +-------------------------+
| Refuse|   | Generate complete YAML +|
| YAML. |   | wiring diagram +        |
| Explain   | calibration procedure + |
| Suggest   | troubleshooting section |
| fix.  |   +-------------------------+
+-------+
```

Concrete example, GPIO 19/20 conflicting with USB-CDC on ESP32-S3:

> ❌ GPIO 19 is used by USB CDC on ESP32-S3 DevKit C-1. Either move the pin or set usb_cdc: false (loses serial debug).
> ❌ GPIO 20 is used by USB CDC on ESP32-S3 DevKit C-1. Either move the pin or set usb_cdc: false (loses serial debug).
> 🔧 Use GPIO 8 (SDA) and GPIO 9 (SCL) instead, the board's default I2C pins.

When data is not yet available for the requested hardware, Volt warns explicitly and proceeds with extra caution, double-checking against the manufacturer datasheet.

#### What is currently validated

Volt's validators check assignments against machine-readable profiles. When a profile exists, Volt cannot generate YAML that breaks against it. When a profile does not yet exist, Volt warns explicitly and falls back to training memory with extra caution.

**Validated today (v1.6.0):**

| Category | Hardware |
|----------|----------|
| **ESP dev boards** | ESP32 DevKit V1, ESP32-S2 Mini, ESP32-S3 DevKit C-1, ESP32-C3 Super Mini, ESP32-C6 DevKit, ESP32-H2 DevKit, Wemos D1 Mini (ESP8266, legacy) |
| **Smart home boards** | Shelly Plus 1, Shelly Plus 2PM, Sonoff Basic R3 (legacy), Sonoff Mini R3 |
| **Maker boards** | LilyGo T-Display S3, M5Stack Atom Lite, M5Stack Core Basic, Heltec WiFi LoRa 32 V3 |
| **Raspberry Pi Pico** | Pico W (RP2040 + WiFi), Pico 2 W (RP2350 + WiFi, experimental) |
| **Temperature sensors** | BME280, BMP280, DHT22, DS18B20, NTC thermistor 10K |
| **Air quality sensors** | MH-Z19B, SCD40 |
| **Motion sensors** | PIR AM312, LD2410 radar |
| **Moisture sensors** | Capacitive soil v1.2 |
| **GPIO expanders** | PCF8574, MCP23017, PCA9685, TCA9548A multiplexer |
| **Level shifters** | TXS0108E, BSS138 |
| **Project templates** | Bluetooth proxy, Voice assistant (S3), Air quality monitor, Presence sensor (radar), Battery soil sensor, Multi-relay controller, Temp/humidity room |

Every board profile carries pin layouts, capability matrices, voltage requirements, `recommended_for` / `not_recommended_for` use cases, and lifecycle status. Volt uses the board selector to pick the right board for a project, or to tell users what an existing board can and cannot do. Project templates provide a 30-second quick start for common use cases.

**Coming in future releases:**

| Hardware | Notes |
|----------|-------|
| ESP32-P4, ESP32-C61 | Pending stable ESPHome support (currently experimental) |
| Retroactive YAML validation for existing configs | "Does my YAML look right?" mode |
| Cross-agent validation (Ada, Sage, River) | Same pattern for other agents |

The full development roadmap with technical detail lives in [ROADMAP.md](ROADMAP.md).

---

### What's New in v1.5.1 (2026-05-11)

#### Home Assistant 2026.5

- **Radio Frequency (RF) integration** - sub-GHz RC device control via Broadlink RM4 Pro or ESPHome with a CC1101 module (around 10 USD)
- **Serial Port Proxy integration** - auto-discovers ESPHome devices running `serial_proxy` and exposes the UART as if locally attached
- **Battery Maintenance Dashboard** - central low-battery view across all devices
- **Media Player Tile features** - transport, volume, and source selection in the tile card
- **Vacuum and Lawn Mower more-info redesign** - automatic map view and zone selection
- **12 new integrations** including EARN-E P1, OMIE energy prices, Denon RS232, Honeywell String Lights, Novy Cooker Hood, Victron GX

#### ESPHome 2026.4.5

Bugfix-only patch (no new components). Cross-references added so CC1101 (`references/remote-rf-ir.md`) and serial_proxy (`references/communication.md`) sections note compatibility with HA 2026.5's new integrations.

ESPHome 2026.5.0 stable is expected the first Wednesday of June 2026; any new components will be covered in a follow-up release.

---

### What's New in v1.3.0

#### Aurora - A New Way to Work

Start with `/aurora:aurora` - Aurora opens, asks what you want to build, and takes it from there.

No need to know which skill to use. Describe your project in plain language and Aurora routes to the right specialist(s), recommends the right Claude model for your subscription tier, and builds a step-by-step workflow if the task spans multiple skills.

**21 specialist agents** - Volt (ESP32 firmware), Sage (automations), Ada (custom integrations), Iris (dashboards), Glitch (debugging), Grid (network/VLANs), Forge (infrastructure), and 14 more. Each agent has a defined domain, a soul, and a voice.

#### Home Assistant 2026.4

- **IR Proxy** - Native infrared entity platform. ESPHome IR devices expose `InfraredEntity`, HA sends commands through them
- **Cross-domain automation triggers** - More intuitive trigger syntax aligned to how people think (Labs)
- **Matter lock PIN management** - Full PIN code control for Matter locks
- **Dashboard** - Section background colors and card favorites
- **Voice** - Ask Assist to clean a specific room area
- **New integrations** - UniFi Access, WiiM, Solarman, TRMNL (e-paper display)

#### ESPHome 2026.3

- **IR/RF Proxy** (`ir_rf_proxy`) - Runtime IR/RF without reflashing. Learns and replays commands via `remote_transmitter` / `remote_receiver`
- **RP2040/RP2350** - First-class Raspberry Pi Pico support (143+ boards, WiFi, BLE, OTA)
- **Media Player redesign** - Pluggable sources, playlists, Ogg Opus support
- **Performance** - Main loop up to 99x faster, API protobuf 6-12x faster, 11-20KB flash savings. Just reflash - no config changes needed
- **ESP8266 heap crash fix** - Long-standing LWIP use-after-free bug resolved
- **Alarm Control Panel**, **Lock & Valve**, **MIPI DSI displays**, **Z-Wave Proxy**, **Zigbee expansion**

See [CHANGELOG.md](CHANGELOG.md) for full details.

---

## Choosing the Right Skill

| I want to... | Use this skill |
|--------------|----------------|
| **Not sure, or task spans multiple areas** | `aurora` |
| Create **YAML automations** (automations.yaml, blueprints, dashboards) | `ha-yaml` |
| Build **visual Node-RED flows** (drag-and-drop, JSON) | `node-red` |
| Configure **ESP device firmware** or **design a new IoT product** | `esphome` |
| Develop **Python custom components** (HACS) | `ha-integration` |

> **New to Aurora?** Start with `/aurora:aurora` - it routes to the right skill and recommends the right model for your task.

---

## Quick Start

```bash
# 1. Add the marketplace
/plugin marketplace add tonylofgren/aurora-smart-home

# 2. Install Aurora
/plugin install aurora@aurora-smart-home
```

```
# 3. Start here
/aurora:aurora
```

Aurora asks what you want to build and takes it from there.

<details>
<summary><strong>Advanced: install per-project or per-team instead</strong></summary>

By default, skills install globally (`--scope user`). You can also scope them:

```bash
# Shared with your team via git (committed to .claude/settings.json)
/plugin install aurora@aurora-smart-home --scope project

# Only for you in this project (gitignored, .claude/settings.local.json)
/plugin install aurora@aurora-smart-home --scope local
```

| Scope | Stored in | Shared? | Use when |
|-------|-----------|---------|----------|
| `user` (default) | `~/.claude/settings.json` | No | Personal use across all projects |
| `project` | `.claude/settings.json` | Yes, via git | Team wants same skills |
| `local` | `.claude/settings.local.json` | No (gitignored) | Testing, personal project config |

</details>

---

## How Skills Activate

### Primary: `/aurora:aurora`

Type `/aurora:aurora` for any smart home task. Aurora opens, asks what you want to build, and routes to the right specialist(s) - recommending the right Claude model for your subscription tier.

Works for single tasks and multi-step projects alike.

### Also: Automatic (Contextual)

Individual skills also activate automatically when you mention relevant keywords - without going through Aurora:

| Skill | Triggers on |
|-------|-------------|
| `esphome` | "ESPHome", "ESP32", "ESP8266", device firmware |
| `ha-yaml` | "YAML automation", "blueprint", "automations.yaml" |
| `node-red` | "Node-RED", "flow", "function node" |
| `ha-integration` | "custom integration", "HACS", "custom_components" |

> **Language-independent:** Product names like "Node-RED" and "ESPHome" trigger skills in any language.

---

## Getting Started with Your First Project

Type `/aurora:aurora` - Aurora opens and asks what you want to build. Then describe your project:

```
Aurora: What do you want to build or fix?

💬 "I want a temperature sensor with OLED display on ESP32"
   → Routes to Volt, confirms board, generates ESPHome config

💬 "Automation that turns lights on at sunset and off at midnight"
   → Routes to Sage, clarifies format, creates YAML automation

💬 "Motion-activated lights - sensor on ESP32, automation in HA"
   → Plans full workflow: Volt (firmware) → Sage (automation)

💬 "Python integration for the Acme cloud API, publishable to HACS"
   → Routes to Ada, guides through architecture and config flow
```

You can also skip Aurora and invoke skills directly by mentioning keywords like "ESPHome", "Node-RED flow", or "YAML automation" - the right skill activates automatically.

### Example Projects

The `examples/` folder contains complete, working projects:

| Example | Description |
|---------|-------------|
| [complete-smart-room](./examples/complete-smart-room/) | Full room with sensors, voice control, automations |
| [smart-greenhouse](./examples/smart-greenhouse/) | Automated irrigation, climate monitoring, grow lights |
| [smart-garage](./examples/smart-garage/) | Garage door control, car detection, safety features |
| [energy-monitor](./examples/energy-monitor/) | CT clamp power monitoring, cost tracking, alerts |

### How Skills Work Together

See [SKILL-INTEGRATION.md](./SKILL-INTEGRATION.md) for detailed workflows showing how ESPHome → HA Integration → HA Automation skills connect.

---

## What's Included

### Home Assistant YAML Skill (`ha-yaml`)

Create **YAML-based automations**, scripts, blueprints, templates, and dashboards.

| Feature | Count |
|---------|-------|
| Reference guides | 49 |
| Example prompts | 300+ |
| YAML code examples | 700+ |
| Production-ready templates | 17 |
| Integrations covered | 50+ |

**Covers:** Automations, scripts, blueprints, template sensors, Sections dashboards, Mushroom cards, Jinja2, helpers, packages, presence detection, voice Assist, calendar automations, notification patterns, energy monitoring. Integrations: MQTT, Zigbee2MQTT, ZHA, Z-Wave, Matter, Bluetooth, Frigate, Tuya, Shelly, Tasmota, and more. Uses modern HA 2024.8+ syntax (`action:`, plural keys, `template:` integration).

[View Home Assistant documentation](./home-assistant/README.md)

---

### Node-RED Skill (`node-red`)

Build **visual automation flows** using node-red-contrib-home-assistant-websocket v0.80+ on Node-RED 4.x.

| Feature | Count |
|---------|-------|
| Reference guides | 12 |
| Example prompts | 100+ |
| Flow examples | 200+ |
| Ready-to-import templates | 15 |
| Nodes covered | 31 |

**Covers:** trigger-state, api-call-service, current-state, events, number/select/text/time-entity nodes, function nodes, context storage, timer patterns, error handling, subflows, JSONata, MQTT integration, and state machines.

[View Node-RED documentation](./node-red/README.md)

---

### ESPHome Skill (`esphome`)

Configure **ESP device firmware** and **design new IoT products** - from sensor configs to production-ready hardware.

| Feature | Count |
|---------|-------|
| Reference guides | 28 |
| Project prompts | 600+ |
| Configuration examples | 1000+ |
| Device templates | 27 |
| Components covered | 160+ |

**Component categories:**

| Category | Examples |
|----------|---------|
| Sensors | Temperature, humidity, pressure, CO2, VOC, PM2.5, light, UV, distance, weight |
| Presence | PIR, mmWave radar (LD2410/2450), BLE tracking, Doppler |
| Displays | OLED, e-ink, TFT, LVGL, HUB75 LED matrix, LCD |
| Lighting | LED strips (WS2812, SK6812), PWM dimmers, RGBW, effects |
| Climate | HVAC, thermostats, fans, covers, motorized blinds |
| Audio | I2S microphone, speaker, media player, voice assistant |
| Communication | I2C, SPI, UART, CAN bus, RS485, IR/RF remote, BLE, Zigbee, Thread, Matter |
| Power | Energy monitoring (CT clamp, HLW8012), battery management, solar |
| Motors | Stepper, servo, DC motor, H-bridge drivers |
| Devices | Shelly, Sonoff, Tuya, commercial device conversions |

**Product development:** Hardware selection with live pricing, KiCad PCB design, 3D-printed enclosures, CE/FCC certification, BOM optimization, and manufacturing from prototype to production.

**Platforms:** ESP32, ESP32-S3, ESP32-C3, ESP32-C6, ESP32-H2, ESP32-P4, ESP8266, RP2040, nRF52, LibreTiny

[View ESPHome documentation](./esphome/README.md)

---

### Integration Development Skill (`ha-integration`)

Develop **Python custom components** for Home Assistant (custom_components, HACS).

| Feature | Count |
|---------|-------|
| Reference guides | 17 |
| Development prompts | 129 |
| Code examples | 200+ |
| Starter templates | 10 |

**Covers:** Typed ConfigEntry with `runtime_data`, DataUpdateCoordinator, config flows (setup, reauth, reconfigure, subentries), entity platforms (20+), EntityDescription (`frozen=True`), action responses (`SupportsResponse`), repair issues, diagnostics, device registry, OAuth2, conversation agents, AI Task entities, Integration Quality Scale, HACS v2 publishing.

**Templates:** Basic, polling, push, OAuth2, multi-device hub, service, Bluetooth, conversation agent, media player, webhook.

[View Integration Dev documentation](./ha-integration-dev/README.md)

---

### Aurora Orchestrator & Reference Data (`aurora`)

The orchestration layer that routes requests to the right specialist agent (21 total) and consults machine-readable reference data to keep generated code correct.

**21 specialist agents** organized by domain:
- **Hardware**: Volt (ESP32), Nano (Matter/Thread), Echo (voice), Watt (power)
- **Home Assistant logic**: Sage (YAML), Ada (Python), Mira (LLM), River (Node-RED), Iris (dashboards)
- **External data**: Atlas (APIs)
- **Quality**: Glitch (debug), Probe (QA), Vera (WAF), Lens (security), Manual (docs)
- **Research**: Scout, Lore
- **Infrastructure**: Forge (deploy), Grid (network)
- **Design**: Canvas

**Reference data validated against authoritative sources:**
- `aurora/references/boards/`: per-chip GPIO layouts, capability matrices, OTA safety
- `aurora/references/components/`: sensor profiles with variant disambiguation
- `aurora/references/schemas/`: JSON Schema definitions every profile must conform to
- `aurora/references/validators/`: pin and conflict validators run before YAML generation

**Iron Law 6**: Volt MUST consult the validators and refuse to generate YAML when failures are detected. The data is the source of truth, not training memory.

[View Aurora documentation](./aurora/SKILL.md)

---

## Why This Skill Pack?

### Correct by construction

Aurora ships **machine-readable reference data** for boards and components plus **validators that agents must consult before generating code**. Volt cannot output ESPHome YAML with a GPIO that does not exist on the selected board, cannot pair a 5V sensor with a 3.3V board without flagging a level shifter, and cannot silently put two I2C devices on the same address.

The reference data is versioned, schema-validated in CI, and traceable to manufacturer datasheets via `last_verified` and `verified_source` fields. When Espressif releases a new chip variant, a single PR adds a board profile and every agent that touches GPIO gets the new data immediately.

This is different from skill packs that rely on the model's training memory: training memory drifts and produces plausible but wrong configs. Aurora's validators stop wrong configs from being emitted at all.

### Everything else

- **Saves hours** - No more searching through docs and forums
- **Always current** - Covers HA 2024.x-2026.x, ESPHome 2026.3, Node-RED 4.x
- **Copy-paste ready** - 54 templates you can use immediately
- **Battle-tested patterns** - Based on community best practices
- **Complete coverage** - From beginner to advanced use cases

<details>
<summary><strong>Full Capability Map - everything these skills can do</strong></summary>

### Home Assistant YAML

| Capability | Details |
|-----------|---------|
| Automations | Triggers, conditions, actions, multi-trigger, `choose`, `if/then`, parallel |
| Blueprints | Inputs, selectors, domain filtering, shareable templates |
| Scripts | Sequences, variables, response data, rate limiting |
| Scenes | State snapshots, transition control |
| Template sensors | Trigger-based, time-based, aggregation, statistics |
| Dashboards | Sections view, Tile cards, Mushroom cards, energy, climate, security |
| Voice Assist | Custom sentences, intent scripts, Speech-to-Phrase, multi-wake word |
| Helpers | Input boolean/number/select/text/datetime, counters, timers, groups |
| Packages | Split config by room/function, includes |
| Presence | Device tracker, zones, person, BLE, GPS |
| Notifications | Actionable, images, TTS, persistent, priority routing |
| Calendar | Schedule automations from HA calendar |
| Energy | Utility meter, cost tracking, solar, EV charging |
| Modern syntax | `action:` (not `service:`), plural keys, `template:` integration |
| Integrations | MQTT, Zigbee2MQTT, ZHA, Z-Wave, Matter, Bluetooth, Frigate, Shelly, Tuya, Tasmota |

### ESPHome - Device Configuration

| Capability | Details |
|-----------|---------|
| 10 platforms | ESP32, S3, C3, C6, H2, P4, ESP8266, RP2040, nRF52, LibreTiny |
| Sensors (50+) | Temperature, humidity, pressure, CO2, VOC, PM2.5, light, UV, distance, weight, power |
| Presence | PIR (HC-SR501, AM312), mmWave (LD2410, LD2450), BLE tracking, Doppler |
| Displays | OLED (SSD1306), e-ink, TFT (ILI9341), LVGL graphics, HUB75 LED matrix |
| Lighting | WS2812B, SK6812, PWM, RGBW, addressable effects, color temperature |
| Audio/Voice | I2S mic/speaker, media player, Micro Wake Word, Assist satellite |
| Protocols | WiFi, BLE, Zigbee, Thread, Matter, I2C, SPI, UART, CAN bus, RS485, IR, RF 433MHz |
| Climate | PID thermostat, bang-bang, fan speed, cover position, motorized blinds |
| Power | CT clamp, HLW8012, PZEM, INA219, battery level, solar charge |
| OTA | Local, HA-managed (dashboard_import), HTTP self-update, fleet management |
| Devices | Shelly, Sonoff, Tuya conversion, Arduino migration |

### ESPHome - Product Development

| Capability | Details |
|-----------|---------|
| Hardware selection | MCU comparison, 60+ sensors with prices and I2C addresses, live price lookup |
| Power design | USB-C, LiPo battery (TP4056), solar, PoE, mains (Hi-Link modules) |
| PCB design | KiCad workflow, schematic checklist, layout rules, antenna clearance |
| Enclosures | 3D printing (FDM/SLA materials), IP ratings, off-the-shelf options |
| Prototyping | Breadboard → perfboard → custom PCB progression |
| Production firmware | `project:` block, `dashboard_import:`, WiFi provisioning, fallback AP |
| Fleet OTA | GitHub-hosted updates, self-hosted HTTP OTA, ESPHome Dashboard |
| Certification | CE/FCC/RoHS, pre-certified module strategy, cost reduction tips |
| Manufacturing | JLCPCB/PCBWay SMT assembly, test jig design, QC process |
| Cost estimation | BOM template, volume pricing, retail price calculation |
| Component sourcing | LCSC, Mouser, DigiKey, JLCPCB parts, AliExpress |

### Node-RED

| Capability | Details |
|-----------|---------|
| HA nodes | trigger-state, api-call-service, current-state, events, poll-state |
| Entity nodes | number, select, text, time-entity (stable since v0.71) |
| Flow patterns | Motion lights, presence detection, notifications, climate, media |
| Function nodes | JavaScript, async patterns, `node.send()`/`node.done()`, global context |
| State machines | Context storage, flow/global scope, persistence |
| Error handling | Catch nodes, retry patterns, scoped error handling |
| Advanced | Subflows, JSONata, MQTT, HTTP requests, timer with extend |
| Compatibility | Node-RED 4.x, Node.js 18+, HA websocket v0.80+ |

### Integration Development (Python)

| Capability | Details |
|-----------|---------|
| Architecture | Typed `ConfigEntry[T]`, `runtime_data`, platform forwarding |
| Config flows | Setup, reauth, reconfigure, options, subentries |
| Data fetching | DataUpdateCoordinator with `_async_setup`, `config_entry` arg, `always_update` |
| Entities (20+) | Sensor, binary sensor, switch, light, climate, cover, fan, media player, camera, etc. |
| EntityDescription | `frozen=True`, `kw_only=True`, custom value functions |
| Actions | `SupportsResponse`, `response_variable`, schema validation |
| AI/Voice | ConversationEntity, LLM API, AI Task entity, subentry-based config |
| Device registry | DeviceInfo, connections, identifiers, configuration URL |
| Repair issues | `async_create_issue`, fixable repairs, RepairsFlow |
| Diagnostics | Config entry + device diagnostics, sensitive data redaction |
| Security | HTTPS enforcement, input validation, credential handling, rate limiting |
| OAuth2 | Token refresh, `OAuth2TokenRequestReauthError`, application credentials |
| Testing | pytest-homeassistant-custom-component, MockConfigEntry, fixtures |
| Publishing | HACS v2, manifest.json, CI validation, GitHub topics, Quality Scale |
| Templates | 10 starter templates (basic, polling, push, OAuth2, hub, BLE, voice, etc.) |

</details>

---

## Installation

See individual skill READMEs for detailed installation and usage:
- [Home Assistant Installation](./home-assistant/INSTALLATION.md)
- [ESPHome Installation](./esphome/INSTALLATION.md)

## Update & Uninstall

Aurora ships as one plugin (`aurora@aurora-smart-home`) since v1.3 — there are no separate skill plugins to update.

```bash
# Update — inside Claude Code (refreshes all installed plugins)
/reload-plugins

# Update — from your terminal (CLI), targeted at aurora
claude plugin update aurora@aurora-smart-home

# Uninstall — use the interactive UI
/plugin
```

---

## Enable Auto-Update

Auto-update keeps your skills current automatically.

1. Run `/plugin` to open the plugin manager
2. Go to **Marketplaces** tab
3. Select `aurora-smart-home`
4. Choose **Enable auto-update**

Skills will update automatically when Claude Code starts.

---

## Change Installation Scope

To move a plugin from one scope to another (e.g., user → local):

1. Run `/plugin` to open the plugin manager
2. Go to **Installed** tab
3. Select the plugin and choose **Uninstall**
4. Reinstall with new scope:
   ```bash
   /plugin install aurora@aurora-smart-home --scope local
   ```

**Note:** Use the interactive UI to uninstall - the CLI command `/plugin uninstall` only disables plugins.

---

## Troubleshooting

Having issues? Check the [Troubleshooting Guide](./TROUBLESHOOTING.md) for common problems and solutions across all skills.

---

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history and recent updates.

---

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Credits

Aurora's agent personas are inspired by the people building the Open Home.

| Agent | Inspired by |
|-------|-------------|
| **Aurora** | Otto Privacyhaus - believes your home should work without asking the cloud for permission. |
| **Ada** + **Lens** | Hendrik Nomerge - your PR is not ready. He knows. He will tell you. |
| **Atlas** | Lars Hacsworth - built the store everyone uses to share their builds. |
| **Iris** + **Lore** | Penelope Crowwhisperer - tamer of crows. Bridge between humans and their smart homes. |
| **Mira** | François Backlogeau - has opinions about roadmaps. Very French ones. |

---

Every release, every fix, every new integration - funded by Nabu Casa. If your home runs on HA, consider giving back. [nabucasa.com](https://www.nabucasa.com)

*Community project. Not affiliated with or endorsed by Nabu Casa or the Open Home Foundation. Agent personas are fictional.*

---

Created for use with [Claude Code](https://docs.anthropic.com/en/docs/claude-code) by Anthropic.
