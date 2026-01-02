# Changelog

All notable changes to Aurora Smart Home skills are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

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
