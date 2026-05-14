<p align="center">
  <img src="assets/banner.png" alt="Aurora Smart Home - Claude Skills" width="100%">
</p>

# Aurora Smart Home

> **75,000+ lines** of documentation | **900+ example prompts** | **1,500+ code examples**
> **21 agents** | **6 Iron Laws** | **JSON-validated reference data**

The most comprehensive Claude Code skill pack for smart home development. **New for users since v1.6.0:** paste an existing ESPHome or Home Assistant config and Aurora reviews it line by line with concrete fixes; agents like Ada, Sage, and Mira refuse to ship code with bad async patterns, missing `!secret` references, or invented entity IDs; cross-agent projects (Volt → Sage → Iris) stay in sync via a structured handoff so the dashboard agent never references entities the firmware agent never produced. Covers automations, custom integrations, Node-RED flows, dashboards, and full product development from idea to manufacturing.

> **No runtime dependencies.** Aurora is a Claude Code plugin made of markdown and JSON. The agents (Claude) read the files directly; nothing is executed on your machine. Python + pytest are only needed if a developer wants to run the test suite locally.

[![Claude Code](https://img.shields.io/badge/Claude_Code-Skills-7c3aed.svg)](https://docs.anthropic.com/en/docs/claude-code)
[![Home Assistant](https://img.shields.io/badge/Home_Assistant-2024.x--2026.x-41BDF5.svg)](https://www.home-assistant.io/)
[![ESPHome](https://img.shields.io/badge/ESPHome-2026.4.5-000000.svg)](https://esphome.io/)
[![Version](https://img.shields.io/badge/Version-v1.6.7-success.svg)](CHANGELOG.md)
[![Validated](https://img.shields.io/badge/Validated-against_datasheets-success.svg)](aurora/references/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

> ⚠️ **Use at your own risk.** Aurora generates code and recommendations for educational purposes. Smart home projects involve mains electricity, batteries, and devices that control locks, water, heating, and gas. AI-generated configurations can be plausible but wrong. The maintainers, contributors, and Anthropic accept no liability for property damage, personal injury, data loss, or any other harm. See [DISCLAIMER.md](DISCLAIMER.md) for full terms.

> 💚 **Support Home Assistant.** Aurora is a Claude Code skill for working with Home Assistant. HA's core development is funded by [Nabu Casa](https://www.nabucasa.com) — every release, every fix, every new integration. If your home runs on HA, please consider supporting them. *(Aurora itself is an independent community project, not affiliated with or funded by Nabu Casa.)*

---

## 🔄 Already Installed? Update to v1.6.7

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

## Meet the Aurora team

Aurora runs like a small smart home agency. 1 orchestrator + 20 named specialists across 7 departments. Each specialist has a defined domain, a soul, and a voice — these are the people you will see check in during a project, not feature labels. When Aurora routes a request, she hands it off to the right teammate by name.

🏠 **Aurora** — Founder & orchestrator. *"Your home should work for you — locally, privately, without asking permission."*

**Hardware department**

- ⚡ **Volt** — ESP32/ESP8266/Shelly firmware + IR proxy. *"Board first — then we build."*
- 📡 **Nano** — Matter, Thread, BLE, embedded protocols. *"Matter over Thread is the right call here. Let me explain why."*
- 🎙️ **Echo** — Voice, audio, wake word, Assist pipeline. *"Let's make sure your voice pipeline is solid end to end."*
- 🔋 **Watt** — Power budget, battery sizing, solar dimensioning. *"Before we spec the battery — what's the duty cycle?"*

**Home Assistant department**

- 🧙 **Sage** — YAML automations, blueprints, scripts, helpers. *"Automation, blueprint, or script? Each one has a different shape."*
- ❤️ **Ada** — Python custom integrations, coordinators, config flows. *"This will fail in production. You need `dt_util.now()`."*
- 🤖 **Mira** — LLM, AI, conversation agents. *"Are we responding to commands, or inferring intent?"*
- 🌊 **River** — Node-RED visual automation flows. *"Map the flow first — trigger → condition → action."*
- 🦄 **Iris** — Dashboard visual design. *"Imagine walking into the room. What do you want to know at a glance?"*

**Field intelligence**

- 🏪 **Atlas** — External API patterns, OAuth, community integrations. *"Someone's already solved this. Let me show you how the community does it."*

**Quality desk**

- 🐛 **Glitch** — Cross-skill debugging. *"Paste the full log. Not the part you think matters — all of it."*
- ✅ **Probe** — QA, testing, validation. *"Looks right — but let's test the edge cases first."*
- 🏡 **Vera** — WAF + hardware safety review. *"What happens when the motion sensor misses? Can someone turn the light on manually?"*
- 🔬 **Lens** — Code review, security audit. *"Three things need fixing here. Not suggestions — these will cause incidents."*
- 📖 **Manual** — Installation guides, troubleshooting docs. *"The firmware is done. Now let's make sure someone else can install it."*

**Research library**

- 🔭 **Scout** — Research, investigation. *"Give me a moment — I've seen this discussed somewhere."*
- 📚 **Lore** — Documentation writing. *"The setup section assumes the user already has HACS installed."*

**Operations**

- 🔧 **Forge** — Deploy, Docker, server, backups. *"Before we update — do you have a full backup from today?"*
- 🌐 **Grid** — Network, UniFi, firewall, VLAN. *"That device is probably on the wrong VLAN."*

**Design studio**

- 🎨 **Canvas** — Graphic design, UI beyond dashboards. *"The layout works but it has seven things asking for attention at once."*

---

### What's New in v1.6.7

🛠️ **Infrastructure release — no user-facing changes.** 1.6.7 ships internal improvements to how Aurora is developed and tested (pytest now runs in CI, schema-versioning rules are documented). Users on 1.6.6 do not need to upgrade for any functional benefit. See [CHANGELOG.md](CHANGELOG.md) for technical detail.

### What's New in v1.6.6

**Paste-YAML review.** Volt and Sage used to be generation-only — give them requirements, get back YAML. Now you can paste an existing config and ask "does this work?". Aurora identifies the board / components / GPIO from the YAML, runs the full validator suite against it, and reports back with every finding anchored to the line in your source — so the fix message points at line 23 of your file, not at an abstract pin number. Auto-fixing the YAML is deliberately not done; the Fix lines are specific enough that you apply them manually and stay in control.

Volt covers ESPHome YAML, Sage covers Home Assistant YAML. Clean passes list which validators actually ran so "no findings" never gets mistaken for "did not look".

### What's New in v1.6.5

**Aurora no longer invents community components.** When you name an ESPHome `external_components` module or a HACS integration Aurora hasn't seen before, agents used to silently make up the configuration from training memory — often plausible, sometimes wrong. Now they ask you three things: source URL, version requirements, documentation link. Aurora uses your answers as the only source of truth for the generated config, and adds a visible caution block so you know the result is based on what you supplied rather than verified reference data.

If you don't have all three answers, Aurora stops there rather than guessing.

### What's New in v1.6.4

**Mira (LLM/AI) and River (Node-RED) validate before shipping.** When Mira sets up a conversation agent, it checks the provider name spelling, the endpoint URL, whether the prompt template fits in the token budget, and whether `expose:` lists reference entities that actually exist. Cloud providers get a privacy warning when they're about to receive sensitive entity state — so you know before you ship that OpenAI is about to see your camera entities. When River builds a Node-RED flow, it catches legacy node type names (`ha-state-changed`, `ha-call-service`) that silently fail to deploy on current Node-RED, confirms every Home Assistant node points at a configured server, and flags function nodes that contain hardcoded credentials.

### What's New in v1.6.3

**Tiered error messages across every validator**

Validator output used to be one line: `❌ GPIO 19 conflicts with USB`. Beginners hit that and didn't know whether to move the pin, disable USB, or use a different board. Experienced users skipped past the explanation. This release introduces a four-tier output format every validator now emits:

```
❌ Problem (short):
GPIO 19 cannot be used on ESP32-S3 DevKit C-1 while USB CDC is enabled.

📚 Explanation (medium):
The ESP32-S3 routes USB D+/D- to GPIO 19/20. With usb_cdc: enabled,
these pins are reserved and any assignment to them collides with USB.

🔧 Fix (concrete):
Move the sensor to GPIO 8 (SDA) and GPIO 9 (SCL), the board's default
I2C pins. In living-room-sensor.yaml change line 12 from sda: 19 to
sda: 8 and line 13 from scl: 20 to scl: 9.

💡 Deeper (optional):
USB-OTG uses differential signalling on D+/D- mapped to these GPIOs.
You can set usb_cdc: false to free them, but you lose USB serial
console — only OTA-over-WiFi remains for log inspection.
```

Tiers 1 and 3 are mandatory for every failure (so you always get "what's wrong, what to do"); tiers 2 and 4 add context when you want it. Warnings use the same shape with `⚠️ Warning` instead of `❌ Problem`.

### What's New in v1.6.2

**Five more things Aurora catches before shipping code.**

- **OTA safety.** Refuses to ship ESPHome YAML that would leave the board unrecoverable — for example, disabling WiFi on a board without USB recovery.
- **I²C address collisions.** Catches the classic BME280 + BMP280 collision at `0x76`, calls out reserved address ranges, and suggests routing around conflicts via address-strap pins or a TCA9548A multiplexer.
- **Voltage levels.** Flags 5V sensors connected to 3.3V-only boards and recommends the right level shifter (BSS138 for I²C, TXS0108E otherwise) with the right part on the wiring diagram.
- **Platform version.** Cross-checks every referenced ESPHome or Home Assistant feature against your running version, including deprecation warnings.
- **Async correctness (Python).** Catches the eighty-percent of HA async bugs LLM-generated integrations ship: `datetime.now()` instead of `dt_util.now()`, `requests` instead of `aiohttp`, `time.sleep` in coroutines, sync `open()` inside async functions.

**Iron Law 2 propagates to three more specialists**

Following the Sage Iron Law 2 pattern from v1.6.1, three more specialist souls now have their own "Validate Before Generating" law:

- **Ada** (full) — runs `async-correctness-validator` on every Python file and `entity-id-validator` in producer mode for every entity the integration creates.
- **Iris** (thin) — runs `entity-id-validator` in consumer mode for every card reference. Iris is read-only of `entity_ids_generated`; missing references become `conflict_log` entries.
- **Atlas** (thin) — runs `secrets-validator` on every YAML snippet that wires an external API.

Mira and River intentionally stay at Iron Law 1 (snapshot-aware coordination) until their domain validators (`llm-config-validator`, `node-red-syntax-validator`) ship — adding the law to a soul before the validator exists creates dead references.

**Volt's Iron Law 6 expanded**

Volt now invokes all eight applicable validators on every YAML output: pin, conflict, i2c-address, voltage-level, ota-safety, version, entity-id (producer mode), secrets. The graceful fallback for missing reference data is unchanged.

### What's New in v1.6.1

**Multi-agent projects stay in sync.** When you build something that spans firmware + automations + dashboard, Aurora used to route to Volt, Sage, and Iris in sequence — and each agent had to re-derive shared context from chat history. Now Aurora writes a project snapshot to disk that travels between specialists. The dashboard agent sees the exact entity IDs the firmware agent produced; the automation agent sees which board was actually picked. If one agent disagrees with another, the conflict surfaces to you instead of being silently overridden.

Single-agent tasks skip the snapshot — no overhead for the common case.

**Update instructions fixed.** The `/plugin update <name>` slash command never accepted arguments inside Claude Code, so update instructions across the docs were broken. Fixed: use `/reload-plugins` inside Claude Code, or `claude plugin update aurora@aurora-smart-home` from your terminal. Both verified working.

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

**Validated today (v1.6.7):**

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

The orchestration layer that routes requests to the right specialist agent (21 total) and consults machine-readable reference data to keep generated code correct. The full team roster lives at the top of this README under [Meet the Aurora team](#meet-the-aurora-team).

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

**Aurora helps you work with Home Assistant.** Home Assistant's core development is funded by Nabu Casa — every release, every fix, every new integration. If your home runs on HA, consider supporting them: it keeps the upstream platform alive. [nabucasa.com](https://www.nabucasa.com)

*Aurora is an independent community project. Not affiliated with, endorsed by, or funded by Nabu Casa, the Open Home Foundation, or Anthropic. Agent personas are fictional.*

---

Created for use with [Claude Code](https://docs.anthropic.com/en/docs/claude-code) by Anthropic.
