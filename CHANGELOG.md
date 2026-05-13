# Changelog

All notable changes to Aurora Smart Home skills are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

## [1.6.0] - 2026-05-13

### Added

**Schemas and validators:**
- JSON Schema for board profile, component profile, GPIO expander, and voltage shifter (`aurora/references/schemas/`)
- Pin validator and conflict validator (`aurora/references/validators/`)
- Board selector validator for picking the right board per project requirements
- Volt Iron Law 6: validate before generating (with graceful fallback when reference data is missing)

**Board profiles (17 boards):**
- **ESP dev boards (7)**: ESP32-S3 DevKit C-1, ESP32 DevKit V1, ESP32-S2 Mini, ESP32-C3 Super Mini, ESP32-C6 DevKit, ESP32-H2 DevKit, Wemos D1 Mini (ESP8266, marked legacy with C3 Mini as successor)
- **Smart home boards (4)**: Shelly Plus 1, Shelly Plus 2PM, Sonoff Basic R3 (legacy), Sonoff Mini R3
- **Maker boards (4)**: LilyGo T-Display S3, M5Stack Atom Lite, M5Stack Core Basic, Heltec WiFi LoRa 32 V3
- **Raspberry Pi Pico (2)**: Pico W (RP2040 + WiFi), Pico 2 W (RP2350 + WiFi, marked experimental)
- Each profile carries: GPIO layout, capability matrix, OTA safety, lifecycle status, `recommended_for` / `not_recommended_for` use cases
- `experimental` added to `lifecycle.status` enum

**Project templates (7 ready-to-use scaffolds):**
- Bluetooth proxy, Voice assistant (ESP32-S3 + INMP441 mic + MAX98357A amp)
- Air quality monitor (SCD40), Presence sensor (LD2410 radar)
- Battery-powered soil moisture sensor, Multi-relay controller (PCF8574 + 8 relays)
- Temperature/humidity room monitor (BME280)
- Each template has YAML scaffold + customization guide with recommended board and external hardware list

**Component profiles (10 sensors):**
- Temperature: BME280, BMP280 (with mutual disambiguation), DHT22, DS18B20, NTC thermistor 10K
- Air quality: MH-Z19B, SCD40
- Motion: PIR AM312, LD2410 radar
- Moisture: capacitive soil v1.2

**GPIO expanders (4 chips):**
- PCF8574 (8-bit I2C IO), MCP23017 (16-bit I2C IO), PCA9685 (16-channel PWM), TCA9548A (I2C multiplexer)

**Voltage level shifters (2 chips):**
- TXS0108E (8-channel bidirectional), BSS138 (MOSFET-based, recommended for I2C)

**Cross-agent hand-off protocol:**
- JSON Schema for project snapshots (`aurora/references/schemas/project-snapshot.schema.json`)
- Hand-off protocol documentation (`aurora/references/handoff/_protocol.md`) defining storage location, lifecycle, per-field ownership, conflict handling
- Example multi-agent snapshot (`aurora/references/handoff/examples/living-room-sensor.json`) covering Volt → Sage → Iris workflow
- Orchestrator wiring in `aurora/SKILL.md` (Step 7: DEEP Mode Hand-Off) — when to create the snapshot, what initial fields to write, how to update between specialists, per-field ownership reminder, conflict handling, QUICK mode exemption
- `aurora/references/handoff/` registered in the Reference Data section so specialists discover the protocol
- Snapshot-Aware Coordination Iron Law added to every DEEP-mode specialist soul (Volt, Ada, Sage, Iris, Vera, Atlas, Mira, River). Each law is tailored to the agent's per-field ownership: writers list the fields they own, read-only agents (Iris, Vera) state the prohibition explicitly. All agents share the same QUICK-mode exemption and the `conflict_log` escape hatch instead of overwriting peer fields.

**Testing infrastructure:**
- pytest test suite covering schemas, data integrity, Volt workflow simulation, project snapshot hand-off, SKILL.md wiring, and per-soul snapshot awareness (333 tests)
- Schema validation in CI, negative tests, URI format enforcement

**Documentation and disclaimers:**
- DISCLAIMER.md with no-warranty, hardware safety, AI-content, and no-liability clauses
- ROADMAP.md with phased development plan
- README hero disclaimer block
- README validation flow diagram and hardware coverage tables

---

## [1.5.1] - 2026-05-11

### Added

#### Home Assistant: 2026.5 Coverage

- `references/integrations-esphome.md` - Radio Frequency (RF) Integration section: Broadlink RM4 Pro flow plus ESPHome CC1101 adoption flow, sub-GHz protocols (rc_switch, somfy, came, nice_flor_s), learning unknown codes
- `references/integrations-esphome.md` - Serial Port Proxy Integration section: auto-discovery flow for ESPHome `serial_proxy`, use cases (Modbus RS485, DLMS, Denon RS232), security considerations
- `references/dashboard-cards.md` - HA 2026.5 Card Features section: Media Player Tile features, Battery Maintenance Dashboard, Vacuum and Lawn Mower more-info redesign, dashboard background colors and card favorites, code editor autocomplete
- HA SKILL.md - What's new in HA 2026.5 section listing 12 new integrations plus core feature changes
- HA README.md - Target Version updated to 2024.x through 2026.5

#### ESPHome: HA 2026.5 Cross-references

- `references/remote-rf-ir.md` - CC1101 section now notes compatibility with HA 2026.5 Radio Frequency integration
- `references/communication.md` - Serial Proxy section now notes compatibility with HA 2026.5 Serial Port Proxy integration plus security guidance
- ESPHome SKILL.md - 2026.4.5 patch note (5 bugfixes: ha-addon toggle, secrets bundle, substitutions sibling refs, WiFi safe mode, Nextion text sensor) and HA 2026.5 cross-platform compatibility section
- ESPHome README.md - v1.3.1 entry covering the cross-references and patch note

### Changed

- Plugin version: 1.5.0 → 1.5.1
- ESPHome skill: v1.3.0 → v1.3.1 (cross-references only; no firmware-side changes)

### Notes

- ESPHome 2026.4.5 is the latest stable ESPHome release as of 2026-05-11. It is a bugfix-only patch with no new components or breaking changes.
- HA 2026.5's RF and Serial Port Proxy integrations consume already-stable ESPHome components (`cc1101` and `serial_proxy`), so no firmware upgrade is required.
- ESPHome 2026.5.0 stable release is expected the first Wednesday of June 2026. Any new components introduced there will be covered in a follow-up release.

---

## [1.2.0] - 2026-03-26

### Added

#### ESPHome: New Component Coverage (ESPHome 2025.2 - 2026.3)

**New Reference Files (3):**
- `references/alarm-security.md` - Alarm Control Panel (template platform, zones, bypass, code support), Lock (template, output), Valve (template, position control)
- `references/media-audio.md` - Redesigned media player architecture (2026.3): Speaker Media Player, Speaker Source, I2S Audio, Mixer/Resampler speakers, Microphone (I2S, UDP), Audio DAC (ES8311, ES8388), Audio File embedding, migration guide from legacy I2S Media Player
- `references/input-entities.md` - Datetime (date/time/datetime types), Event entity platform with on_event trigger

**New Templates (3):**
- `assets/templates/alarm-panel.yaml` - Template alarm control panel with PIR + door sensors, zone bypass, arming buzzer
- `assets/templates/media-player.yaml` - Speaker Media Player with ESP32-S3, MAX98357A DAC, INMP441 mic, rotary encoder volume
- `assets/templates/irrigation-controller.yaml` - 4-zone valve-based irrigation with pump safety, soil moisture sensor, scheduling

### Changed

**ESPHome: Updated Reference Files (7):**
- `references/boards.md` - RP2040/RP2350 first-class support (pico-sdk 2.0, 143+ boards, WiFi, BLE, OTA), nRF52 BLE+serial OTA via mcumgr
- `references/displays.md` - MIPI DSI Display Driver for ESP32-P4 high-performance displays
- `references/communication.md` - Z-Wave Proxy (network serial proxy), Serial Proxy (generic), DLMS Smart Meter (European smart meters)
- `references/sensors.md` - Dew Point (native computed sensor), HDC302x, SEN6x all-in-one environmental sensor
- `references/covers-fans.md` - Cover movement state triggers (on_open_started, on_close_completed, etc.)
- `references/home-assistant.md` - API action responses (bidirectional), conditional package inclusion
- `references/matter-bridge.md` - Zigbee platform expansion for ESP32-C6/H2

**ESPHome SKILL.md:**
- Version bump to v1.2.0
- Updated skill description with new component keywords
- Breaking changes section expanded to cover ESPHome 2025.2 - 2026.3
- Reference table updated with 3 new entries

---

## [1.5.0] - 2026-05-02

### Added

#### ESPHome: 2026.4.0 Updates

**Breaking Changes section (ESPHome 2026.4+):**
- ESP32 max CPU frequency as default — 33% faster API, no config changes required
- 40KB extra IRAM unlocked for ESP32
- Signed OTA verification (`ota: verify_signature: true`)
- Custom partition tables support in `esp32:` block
- GPIO Expander `interrupt_pin` — eliminates I2C/SPI polling entirely
- W5500/W5100/W5100S SPI Ethernet — five new chip types incl. RP2040 (WIZnet EVB-Pico)
- Client-side state logging — up to 46x faster sensor publishing, auto-enabled
- ESP8266 crash handler — now matches ESP32/RP2040

**New Components table:**
- `W5500/W5100 SPI Ethernet` — wired networking for ESP32/RP2040 without WiFi

**ESPHome SKILL.md:**
- Version bump to v1.3.0
- Breaking Changes heading updated to cover 2025.2 - 2026.4

**Aurora SKILL.md:**
- Version bump to v1.5.0
- Platform version updated to ESPHome 2026.4
- What's New highlight added after banner with ESPHome 2026.4 key features

---

## [1.4.0] - 2026-04-12

### Added

#### Aurora: Hardware Documentation Layer (IoT/ESPHome)

Closes the gap between firmware generation and physical hardware — Aurora now
delivers all three layers for IoT projects: hardware/dimensioning, installation,
and software.

**New agents (2):**
- `aurora/souls/watt.md` — **Watt**: Power budget specialist. Calculates full
  current draw table (µA/mA per state × time), battery runtime in days, and solar
  panel sizing with seasonal correction. Triggered automatically for any project
  using `deep_sleep`, battery, solar, or power bank. Model: haiku.
- `aurora/souls/manual.md` — **Manual**: Installation documentation specialist.
  Generates `INSTALL.md` and `TROUBLESHOOTING.md` with actual entity IDs and file
  names from the project — never generic placeholders. Model: haiku.

**New Iron Laws:**
- Volt: Generate wiring diagram for every GPIO — no GPIO without a diagram
- Volt: Generate calibration procedure (with actual entity IDs) for sensors that require it
- Volt: Flag Watt before finalising any BOM with battery, solar, or deep sleep
- Vera: Hardware Safety Review mandatory BEFORE Volt for battery/actuator/outdoor/>5V
- Watt: No battery/solar recommendation without a full power budget table
- Manual: Reference actual entity IDs and file names — never generic placeholders

**Updated agents:**
- `aurora/souls/volt.md` — 5 Iron Laws added (board-first, wiring diagram,
  calibration, power budget, troubleshooting)
- `aurora/souls/vera.md` — Hardware Safety Review (Mode 1) added: reviews battery
  protection, high-current safety, mixed voltages, ADC limits, outdoor IP rating,
  and mains isolation; blocks Volt if critical risks found

**ESPHome SKILL.md:**
- Updated process flow: Safety check → Power budget → YAML → Wiring diagram →
  Calibration → Troubleshooting → Checklist
- New **Wiring Diagrams** section with ASCII format and required additions table
  (flyback diodes, voltage dividers, pull-ups, common GND strategy)
- New **Calibration Register**: 7 sensor types with procedure template and
  entity ID references (capacitive moisture, NTC, CO₂, water level, pressure,
  LDR, CT clamp)
- Extended Pre-Completion Checklist with wiring, calibration, power, and
  troubleshooting categories

**Aurora SKILL.md:**
- Registry updated: 19 → 21 agents
- Watt added to Smart Home Hardware table
- Manual added to Development Support table
- 7 new Iron Laws in Iron Laws Reference section

**workflows.md:**
- New **Battery/Outdoor IoT Project** workflow:
  Vera (Safety) → Watt → Volt → Sage → Manual → Vera (WAF)
- Note added to New Sensor Device workflow for battery/actuator/outdoor projects

---

## [1.3.0] - 2026-04-09

### Added

#### Structural Improvements (All Skills)
- **Overview section** with announcement pattern in all SKILL.md files
- **Iron Law** - Non-negotiable rules for each skill domain
- **Red Flags tables** - Rationalization prevention patterns
- **Graphviz workflow diagrams** - Visual process flows
- **Pre-Completion Checklists** - Validation before declaring complete
- **Integration sections** - Cross-skill relationship documentation

#### New Reference Files

**ESPHome** (3 new):
- `references/ble-proxy.md` - BLE Proxy setup, Xiaomi sensors, presence detection
- `references/voice-local.md` - Local voice assistant with Micro Wake Word
- `references/matter-bridge.md` - Matter/Thread configuration for ESP32-C6

**HA Integration Dev** (2 new):
- `references/conversation-agent.md` - ConversationEntity, LLM agents, custom intents
- `references/multi-coordinator.md` - Multiple DataUpdateCoordinator patterns

**Home Assistant Automation** (4 new):
- `references/assist-patterns.md` - Custom sentences for Assist voice control
- `references/presence-detection.md` - PIR, mmWave, Bayesian presence
- `references/notification-patterns.md` - Actionable notifications, rate limiting
- `references/calendar-automation.md` - Calendar triggers, vacation mode, schedules

#### New Templates

**ESPHome** (3 new):
- `assets/templates/ble-proxy.yaml` - Production-ready BLE Proxy
- `assets/templates/voice-assistant.yaml` - Enhanced voice satellite with LED status
- `assets/templates/matter-light.yaml` - Matter-compatible light for ESP32-C6

**HA Integration Dev** (2 new template folders):
- `templates/bluetooth-integration/` - Complete BLE device integration (7 files)
  - Bluetooth discovery, passive/active scanning
  - Config flow with device picker
  - Coordinator with advertisement parsing
  - EntityDescription-based sensors
- `templates/conversation-agent/` - LLM-powered voice assistant (8 files)
  - Multi-provider support (Ollama, OpenAI, Anthropic)
  - Conversation history management
  - Home Assistant context injection
  - Action execution via JSON parsing

#### Documentation

- `SKILL-INTEGRATION.md` - Cross-skill integration guide with workflows
- `examples/complete-smart-room/` - Complete example project (6 files)
  - ESP32-S3 multi-sensor (mmWave, temp, humidity, light, LED strip)
  - ESP32-S3 voice satellite
  - HA automations (presence lighting, climate, modes)
  - Scenes (work, relax, movie, night)
  - Input helpers
- Updated `README.md` with "Getting Started" guide

### Changed

- Updated Quick Reference tables in all SKILL.md files with new references
- Updated template counts in README (ESPHome: 19, HA Integration: 8)
- Enhanced existing `voice-assistant.yaml` template with better documentation

---

## [1.0.0] - 2025-01-01

### Added

#### ESPHome Skill
- 26 reference guides covering 160+ ESPHome components
- 600+ example prompts for device configurations
- 19 ready-to-use templates
- Support for ESP32, ESP32-S3, ESP32-C3, ESP32-C6, ESP8266
- Device conversion guides (Shelly, Sonoff, Tuya)
- Arduino to ESPHome migration guide

#### Home Assistant Automation Skill
- 49 reference guides covering 50+ integrations
- 300+ example automation prompts
- 17 production-ready templates
- Blueprint creation and usage guides
- Dashboard and Mushroom card documentation
- Jinja2 template patterns

#### Home Assistant Integration Dev Skill
- 17 reference guides for custom integration development
- 129 development prompts
- 8 starter templates (basic, polling, push, OAuth2, hub, service, Bluetooth, conversation)
- DataUpdateCoordinator patterns
- Config flow and options flow guides
- HACS publishing workflow

---

## Version Numbering

- **Major** (X.0.0): Breaking changes, major restructuring
- **Minor** (0.X.0): New features, new references, new templates
- **Patch** (0.0.X): Bug fixes, documentation updates, minor improvements

---

## Contributing

When contributing, please update this changelog with your changes under the `[Unreleased]` section.

Categories:
- **Added** - New features, files, or capabilities
- **Changed** - Updates to existing functionality
- **Deprecated** - Features to be removed in future
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security-related changes
