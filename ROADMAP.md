# Aurora Validation Roadmap

This document tracks the incremental rollout of Aurora's validation-before-generation pipeline. Each phase delivers working, tested software on its own and is reviewed against the design spec in `docs/superpowers/specs/2026-05-13-aurora-validation-design.md`.

User-facing coverage (what works today, what is coming) lives in [README.md](README.md). This file is for contributors, maintainers, and anyone curious about the engineering plan behind each release.

## Phases

| Phase | Scope | Status | Released |
|-------|-------|--------|----------|
| 1 | Foundation: JSON Schemas + pin/conflict validators + ESP32-S3 DevKit C-1 + BME280 + Iron Law 6 + pytest suite | ✅ Complete | v1.6.0 (2026-05-13) |
| 2 | Foundation expansion: ESP32 classic, S2, C3, C6, H2, P4, C61, ESP8266 + 9+ common sensors + GPIO expanders (PCF8574, MCP23017, PCA9685, TCA9548A) + voltage level shifters (TXS0108E, BSS138) | 🔵 Next | TBD |
| 3 | Smart home boards: Shelly Plus 1/2PM, Sonoff Basic R3 / Mini R3, LilyGo T-Display S3, M5Stack Atom / Core, Heltec WiFi LoRa, Raspberry Pi Pico W (RP2040 + WiFi), Pico 2 W (RP2350 + WiFi, preliminary) | ⏳ Planned | TBD |
| 4 | Project templates library: bluetooth proxy, voice assistant (ESP32-S3), air quality monitor, presence sensor (radar), battery soil sensor, multi-relay controller, temp/humidity room | ⏳ Planned | TBD |
| 5 | Cross-agent validation: hand-off protocol + Ada/Sage/River/Mira/Atlas/Iris validation modules | ⏳ Planned | TBD |
| 6 | External components catalog: community ESPHome packages (LD2410, Tuya MCU, NSPanel Pro, etc.) with source URL validation and maintenance status tracking | ⏳ Planned | TBD |
| 7 | Advanced features: retroactive YAML validation, tiered error messages (problem / explanation / solution / deeper), project snapshots between sessions, lifecycle/deprecation warnings | ⏳ Planned | TBD |
| 8 | Data management infrastructure: JSON Schema validation in CI, audit script for data freshness, schema versioning + migration scripts, community contribution path with PR templates, GitHub Actions for Iron Law Test Suite | ⏳ Planned | TBD |

## Phase 1 details (released v1.6.0)

Delivered:
- `aurora/references/schemas/board-profile.schema.json` (JSON Schema Draft 2020-12)
- `aurora/references/schemas/component-profile.schema.json`
- `aurora/references/boards/esp32/esp32-s3-devkitc-1.json` (full capability data)
- `aurora/references/components/temperature/bme280.json` (with BMP280 disambiguation)
- `aurora/references/validators/pin-validator.md` (7 checks)
- `aurora/references/validators/conflict-validator.md` (7 checks)
- Iron Law 6 in `aurora/souls/volt.md` with graceful fallback when reference data is missing
- `aurora/SKILL.md` Reference Data section + v1.6.0 banner
- `aurora/tests/` (36 passing pytest tests)

Implementation plan: `docs/superpowers/plans/2026-05-13-aurora-validation-foundation.md`

## Design source

`docs/superpowers/specs/2026-05-13-aurora-validation-design.md` is the canonical design document. Phases above implement the spec in slices. Items deferred to a V2 roadmap (out of scope for the 8 phases) are listed in the spec's `Out of scope` section.

## Contributing

Until Phase 8 lands, the contribution process is informal. Open an issue first to coordinate. Once Phase 8 ships, the formal `CONTRIBUTING.md` and PR templates take over.
