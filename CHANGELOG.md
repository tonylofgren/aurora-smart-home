# Changelog

All notable changes to Aurora Smart Home skills are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
