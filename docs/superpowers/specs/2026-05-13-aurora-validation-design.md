# Aurora Skill — Validation-Before-Generation Design

**Status:** Draft for review (v2, expanded with Tier A + B)
**Date:** 2026-05-13
**Author:** Review from a beginner's perspective
**Scope:** Aurora skill architecture, all agents, focus on Volt (ESP32/ESPHome)

---

## 1. Background and problem

Aurora skill is an orchestration layer with 21 specialist agents for smart home development. The skill defines Iron Laws that govern each agent's discipline, e.g. Volt's "board first" requirement before YAML generation.

**Identified core problem:**
Iron Laws exist as *text*, not as *enforced structure*. This means an agent (particularly Volt) can generate code that does not match the physical hardware: wrong GPIO pin, wrong board for the task, or pin conflicts between components.

**For a beginner:**
The worst disappointment is that the aurora skill *writes the wrong pins into the code*. The result is a sensor that does not work, damaged hardware, hours wasted on debugging, or an abandoned project.

**Design goal:**
Guarantee that the aurora skill produces *correct code regardless of who uses it*, through systemic validation before generation.

---

## 2. Current state

### What exists today

- `aurora/SKILL.md`: routing and Iron Laws for 21 agents
- `aurora/souls/volt.md`: Volt's Iron Laws (board first, wiring diagram, calibration, power budget, troubleshooting)
- `aurora/references/platform-versions.md`: HA + ESPHome version info
- `aurora/references/workflows.md`: multi-skill workflow templates
- `esphome/references/pinouts.md`: GPIO pinouts for 9 ESP chip families (markdown + ASCII)
- `esphome/references/boards.md`: board information

### Identified gaps

1. Pin data is not machine-readable (markdown/ASCII, hard to parse)
2. Aurora skill does not link to the pin data (Volt does not know the reference exists)
3. No validation before generation (Volt relies on its own knowledge)
4. Only pin data, no capability matrix (BLE/Thread/PSRAM missing)
5. No sensor/component database (sensor requirements may break)
6. No conflict checks between components
7. Pattern missing for other agents (Ada, Sage, River carry the same risk)
8. Sensor variants get mixed up (BME280 vs BMP280, DHT22 vs DHT11)
9. GPIO expander support missing (when pins run out)
10. Voltage level shifter data missing (5V sensors on 3.3V boards)
11. I2C address conflicts not detected
12. Sleep mode and wake source data missing
13. OTA safety check missing (brick risk)
14. Secrets validation missing (credentials in plaintext)
15. External components catalog missing
16. Project templates missing (completely blank start)
17. Hand-off protocol between agents missing
18. Data update mechanism missing (how is JSON refreshed?)
19. JSON Schema validation missing (for the JSON files themselves)
20. Community contribution path missing
21. Schema versioning missing (backward compatibility)
22. CI/CD for Iron Law Test Suite missing

---

## 3. Proposed architecture

### 3.1 New directory structure

```
aurora/references/
├── boards/                          # Board profiles (full capability)
│   ├── _index.md
│   ├── esp32/
│   │   ├── esp32-devkit-v1.json
│   │   ├── esp32-s2-mini.json
│   │   ├── esp32-s3-devkitc-1.json
│   │   ├── esp32-c3-mini.json
│   │   ├── esp32-c6-devkit.json
│   │   ├── esp32-h2-devkit.json
│   │   ├── esp32-p4-devkit.json
│   │   └── esp32-c61-devkit.json
│   ├── esp8266/
│   │   ├── d1-mini.json
│   │   └── nodemcu-v3.json
│   ├── rp/
│   │   ├── rp2040-pico.json
│   │   └── rp2350-pico2.json
│   ├── smart-home/
│   │   ├── shelly-plus-1.json
│   │   ├── shelly-plus-2pm.json
│   │   ├── sonoff-basic-r3.json
│   │   └── sonoff-mini-r3.json
│   └── special/
│       ├── lilygo-t-display-s3.json
│       ├── m5stack-atom.json
│       └── heltec-wifi-lora32.json
│
├── components/                      # Sensor/actuator profiles
│   ├── _index.md
│   ├── temperature/
│   │   ├── dht22.json
│   │   ├── ds18b20.json
│   │   ├── bme280.json
│   │   ├── bmp280.json           # NOTE: distinct from BME280
│   │   └── ntc-thermistor.json
│   ├── moisture/
│   │   ├── capacitive-soil-v1.2.json
│   │   └── resistive-soil.json
│   ├── motion/
│   │   ├── pir-am312.json
│   │   └── radar-ld2410.json
│   ├── air-quality/
│   │   ├── mh-z19b.json
│   │   ├── mh-z19c.json          # NOTE: different calibration
│   │   └── scd40.json
│   ├── distance/
│   │   └── hc-sr04.json          # NOTE: 5V sensor
│   ├── relays/
│   │   └── songle-srd-05vdc.json
│   └── displays/
│       ├── ili9341-tft.json
│       └── ssd1306-oled.json
│
├── expanders/                       # GPIO expanders (when pins run out)
│   ├── _index.md
│   ├── pcf8574.json                # 8-bit I2C expander
│   ├── mcp23017.json               # 16-bit I2C expander
│   ├── pca9685.json                # 16-channel PWM
│   └── tca9548a.json               # I2C multiplexer (for duplicates)
│
├── voltage-shifters/                # Level shifters (5V <-> 3.3V)
│   ├── _index.md
│   ├── txs0108e.json               # 8-channel bidirectional
│   ├── bss138.json                 # MOSFET-based single channel
│   └── tx-rx-resistor-divider.json # Voltage divider for RX only
│
├── external-components/             # ESPHome community packages
│   ├── _index.md
│   ├── ld2410-empericalsoul.json
│   ├── tuya-mcu-jesserockz.json
│   └── nspanel-pro.json
│
├── templates/                       # Quick-start project templates
│   ├── _index.md
│   ├── bluetooth-proxy.yaml
│   ├── voice-assistant-s3.yaml
│   ├── air-quality-monitor.yaml
│   ├── presence-sensor-radar.yaml
│   ├── temp-humidity-room.yaml
│   ├── battery-soil-sensor.yaml
│   └── multi-relay-controller.yaml
│
├── schemas/                         # JSON Schema for validation of JSON
│   ├── board-profile.schema.json
│   ├── component-profile.schema.json
│   ├── expander-profile.schema.json
│   ├── voltage-shifter.schema.json
│   ├── external-component.schema.json
│   ├── project-snapshot.schema.json
│   └── _schema-version.md
│
├── validators/                      # Cross-agent validator modules
│   ├── pin-validator.md
│   ├── conflict-validator.md
│   ├── yaml-syntax-validator.md
│   ├── python-validator.md
│   ├── entity-id-validator.md
│   ├── version-validator.md
│   ├── ota-safety-validator.md
│   ├── secrets-validator.md
│   ├── i2c-address-validator.md
│   └── voltage-level-validator.md
│
├── handoff/                         # Agent hand-off protocol
│   ├── _protocol.md
│   └── project-context.schema.json
│
└── project-snapshots/               # User project history (runtime)
```

### 3.2 Board profile JSON schema (expanded)

```json
{
  "$schema": "../schemas/board-profile.schema.json",
  "schema_version": "1.0",
  "board_id": "esp32-s3-devkitc-1",
  "display_name": "ESP32-S3 DevKit C-1",
  "chip": "ESP32-S3",
  "manufacturer": "Espressif",

  "wireless": {
    "wifi": ["2.4GHz"],
    "wifi_standard": "WiFi 4 (b/g/n)",
    "bluetooth": "BLE 5.0",
    "bluetooth_classic": false,
    "thread": false,
    "zigbee": false,
    "lora": null,
    "ethernet": null
  },

  "power": {
    "usb_type": "USB-C",
    "operating_voltage": 3.3,
    "input_voltage_range": "5V (USB) or 3.3V",
    "battery_connector": null,
    "charging_ic": null,
    "vbat_monitor_pin": null,
    "deep_sleep_current_ua": 7,
    "light_sleep_current_ma": 0.8,
    "modem_sleep_current_ma": 20,
    "solar_input": false,
    "gpio_5v_tolerant": false
  },

  "memory": {
    "flash_mb": 8,
    "psram_mb": 8,
    "psram_type": "OPI",
    "ram_kb": 512
  },

  "gpio": {
    "valid_pins": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48],
    "strapping_pins": [0,3,45,46],
    "reserved_for_usb": [19,20],
    "reserved_for_flash": [],
    "input_only": [],
    "adc1_pins": [1,2,3,4,5,6,7,8,9,10],
    "adc2_pins": [11,12,13,14,15,16,17,18,19,20],
    "touch_pins": [1,2,3,4,5,6,7,8,9,10,11,12,13,14],
    "dac_pins": [],
    "wake_source_pins": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21],
    "i2c_default": {"sda": 8, "scl": 9},
    "spi_default": {"mosi": 11, "miso": 13, "sck": 12, "cs": 10}
  },

  "onboard_components": {
    "led_gpio": 38,
    "led_type": "RGB WS2812",
    "boot_button_gpio": 0,
    "reset_button": "EN pin",
    "display": null,
    "imu": null,
    "buzzer": null
  },

  "smart_home_capabilities": {
    "bluetooth_proxy": true,
    "voice_assistant": true,
    "matter_controller": true,
    "matter_device": true,
    "zigbee_coordinator": false,
    "thread_border_router": false,
    "ble_tracker": true,
    "camera_support": true,
    "battery_powered": false,
    "ir_blaster": true,
    "rf_proxy_cc1101": true
  },

  "ota_safety": {
    "factory_reset_pin": 0,
    "external_programmer_needed": false,
    "usb_cdc_recovery": true,
    "min_required_features_for_unbricking": ["wifi", "ota OR usb_cdc"]
  },

  "form_factor": {
    "antenna": "PCB",
    "ipex_connector": false,
    "dimensions_mm": "63 x 25.5",
    "certifications": ["FCC", "CE"],
    "operating_temp_c": "-40 to +85"
  },

  "limitations": {
    "max_cpu_mhz": 240,
    "no_dac": true,
    "usb_blocks_gpio": [19,20],
    "psram_blocks_gpio": [26,27,28,29,30,31,32],
    "adc2_blocked_when_wifi_active": true,
    "strapping_conflict_warnings": [
      "GPIO 0 must be HIGH at boot, pull-up if used as input",
      "GPIO 45 must be LOW at boot, affects flash voltage",
      "GPIO 46 must be LOW at boot, affects download mode"
    ]
  },

  "lifecycle": {
    "status": "active",
    "released": "2022-11",
    "deprecated_since": null,
    "reason": null,
    "successor": null
  },

  "esphome": {
    "platform": "esp32",
    "variant": "ESP32S3",
    "framework": "esp-idf",
    "min_version": "2023.6.0"
  },

  "datasheet_url": "https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf",
  "last_verified": "2026-05-13",
  "verified_source": "Espressif official + Arduino-ESP32 v3.0"
}
```

### 3.3 Component profile JSON schema (expanded)

```json
{
  "$schema": "../schemas/component-profile.schema.json",
  "schema_version": "1.0",
  "component_id": "bme280",
  "display_name": "BME280 Temperature/Humidity/Pressure",
  "type": "environment_combined",
  "category": "environment",
  "protocol": "i2c",

  "variants": {
    "primary": "bme280",
    "easily_confused_with": [
      {
        "component_id": "bmp280",
        "difference": "BMP280 lacks humidity sensor, identical appearance"
      }
    ],
    "knockoffs_known": true,
    "verification_method": "Read chip ID register: 0x60 = BME280, 0x58 = BMP280"
  },

  "i2c": {
    "default_addresses": ["0x76", "0x77"],
    "address_strap_pin": "SDO (LOW=0x76, HIGH=0x77)",
    "max_speed_khz": 400
  },

  "pin_requirements": {
    "count": 2,
    "type": "i2c",
    "must_use_default_i2c_pins": false,
    "adc_required": false,
    "input_only_ok": false,
    "strapping_pin_ok": false,
    "5v_tolerant_required": false,
    "interrupt_capable_required": false
  },

  "external_components": {
    "pullup_resistor": {"value_ohm": 4700, "required": true, "note": "External pull-ups if board does not provide them"},
    "decoupling_cap": {"value_uf": 0.1, "required": true}
  },

  "power": {
    "voltage_min": 1.8,
    "voltage_max": 3.6,
    "tolerates_5v": false,
    "level_shifter_required_on_5v_board": true,
    "current_ma_active": 0.7,
    "current_sleep_ua": 0.1
  },

  "limitations": {
    "min_read_interval_s": 0.5,
    "operating_temp_c": "-40 to +85",
    "humidity_range": "0-100%",
    "pressure_range_hpa": "300-1100",
    "accuracy_temp_c": "±0.5",
    "accuracy_humidity": "±3%",
    "accuracy_pressure_hpa": "±1"
  },

  "calibration": {
    "required": false,
    "type": null
  },

  "esphome": {
    "platform": "bme280_i2c",
    "min_version": "2022.1.0",
    "config_template": "templates/components/bme280.yaml"
  },

  "datasheet_url": "https://www.bosch-sensortec.com/products/environmental-sensors/humidity-sensors-bme280/"
}
```

### 3.4 GPIO expander profile

When component count exceeds available GPIO on the board, route to an expander:

```json
{
  "$schema": "../schemas/expander-profile.schema.json",
  "schema_version": "1.0",
  "expander_id": "pcf8574",
  "display_name": "PCF8574 8-bit I2C IO Expander",
  "protocol": "i2c",
  "channels": 8,
  "channel_type": "digital_io",

  "i2c": {
    "default_addresses": ["0x20-0x27", "0x38-0x3F"],
    "address_pins": ["A0", "A1", "A2"],
    "max_speed_khz": 400
  },

  "limitations": {
    "no_pwm": true,
    "open_drain_only": true,
    "max_current_per_pin_ma": 20,
    "no_adc": true,
    "interrupt_pin_available": true
  },

  "use_cases": [
    "16 relays on ESP32-C3 (only 22 GPIO total)",
    "Button matrix without wasting GPIO",
    "LED status panels"
  ],

  "esphome": {
    "platform": "pcf8574",
    "min_version": "2022.1.0"
  }
}
```

### 3.5 Voltage level shifter profile

```json
{
  "$schema": "../schemas/voltage-shifter.schema.json",
  "schema_version": "1.0",
  "shifter_id": "txs0108e",
  "display_name": "TXS0108E 8-channel Bidirectional Level Shifter",
  "channels": 8,
  "direction": "bidirectional",
  "speed_max_mhz": 110,

  "voltage_a_range": "1.4V to 3.6V",
  "voltage_b_range": "1.65V to 5.5V",

  "use_cases": [
    "5V HC-SR04 distance sensor on 3.3V ESP32",
    "5V relay module signal level to ESP32 GPIO",
    "5V I2C/SPI bus communication"
  ],

  "limitations": {
    "no_open_drain_pulls_strongly": true,
    "auto_direction_can_oscillate_on_i2c": true,
    "prefer_bss138_for_i2c": true
  }
}
```

### 3.6 External components catalog

```json
{
  "$schema": "../schemas/external-component.schema.json",
  "schema_version": "1.0",
  "package_id": "ld2410-empericalsoul",
  "display_name": "LD2410 Radar Sensor (community)",
  "source_url": "https://github.com/empericalsoul/esphome-ld2410",
  "supported_boards": ["esp32-*", "esp8266", "rp2040"],
  "min_esphome_version": "2023.4.0",
  "last_verified": "2026-05-13",
  "license": "MIT",
  "stars": 145,
  "maintenance_status": "active",
  "config_snippet": "external_components:\n  - source: github://empericalsoul/esphome-ld2410\n    components: [ ld2410 ]"
}
```

### 3.7 Volt's validation workflow (expanded)

```
INPUT: User project requirements (sensor, BLE, battery, voice, etc.)

STEP 1: Requirement analysis
├── Identify needs: BLE? Battery? Voice? Camera? Matter?
├── Identify number of components
└── Set capability filters

STEP 2: Template check
├── Do the requirements match an existing template in templates/?
└── If yes, suggest the template as a starting point

STEP 3: Board recommendation
├── Read all *.json in boards/
├── Filter against capability filters
├── Filter out deprecated boards (warn if user insists)
└── Suggest 2-3 suitable boards with trade-offs

STEP 4: User selects a board
└── Confirm + load board profile

STEP 5: Component validation
├── For each sensor/component: load components/*.json
├── Display "easily_confused_with" warnings (BME280 vs BMP280)
├── Verify pin_requirements match board.gpio
├── Verify power requirements match board (voltage_min/max)
├── If component is 5V and board is 3.3V: require level shifter
└── Verify ESPHome version supports the component

STEP 6: GPIO sufficiency
├── Count required pins vs board.gpio.valid_pins
├── If insufficient: suggest GPIO expander from expanders/
└── If I2C address conflict: suggest TCA9548A multiplexer

STEP 7: Pin allocation
├── Suggest GPIO from board.gpio.valid_pins
├── Avoid strapping_pins, reserved_for_usb, psram_blocks_gpio
├── Use i2c_default / spi_default for bus protocols
└── Reserve pins per component

STEP 8: Conflict validation (validators/conflict-validator.md)
├── Pin collision check: two components on the same pin (excluding I2C/OneWire)?
├── Bus sharing check: I2C addresses unique (validators/i2c-address-validator)?
├── Strapping conflict: component on 0/3/45/46 without correct pull?
├── USB conflict: 19/20 + USB CDC active?
├── PSRAM conflict: 26-32 + PSRAM active?
├── Voltage mismatch (validators/voltage-level-validator): 5V component on 3.3V-only pin?
└── ADC conflict: ADC2 + WiFi (S2/C3 specific)?

STEP 9: Sleep mode validation
├── If deep_sleep used: wake pin in board.gpio.wake_source_pins?
├── If battery powered: is wake strategy consistent with power budget?
└── Flag Watt for power budget review

STEP 10: OTA safety (validators/ota-safety-validator.md)
├── Is the OTA platform still present in the config?
├── Is USB-CDC still active or WiFi recovery available?
├── If no recovery path remains: WARN about brick risk
└── Require explicit override to continue

STEP 11: Secrets validation (validators/secrets-validator.md)
├── Scan YAML for strings that look like credentials
├── Verify that all credentials use !secret
└── Reject output if credentials are in plaintext

STEP 12: Version validation (validators/version-validator.md)
├── ESPHome >= minimum for all features?
├── Board supports the chosen framework (arduino vs esp-idf)?
└── Chip revision OK?

STEP 13: YAML generation (only if STEP 1-12 ✓)
├── Generate ESPHome YAML
├── Generate ASCII wiring diagram (Iron Law 2)
├── Generate calibration procedure if a sensor requires it (Iron Law 3)
├── Generate troubleshooting with actual entity IDs (Iron Law 5)
└── Save project snapshot

OUTPUT:
├── ✅ Complete, validated YAML + diagram + docs
└── ❌ Clear error message with explanation and suggested fix
```

### 3.8 OTA safety validation

Prevents Volt from generating configurations that can brick a board:

```
INPUT: Generated YAML + board profile

CHECKS:
├── Is an 'ota:' platform declared in the YAML?
├── Is WiFi configured (for OTA over WiFi)?
├── Is USB-CDC still active (for physical recovery)?
├── Does the config use a 'factory_reset' button mapping?
└── Are OTA + WiFi + USB NOT all disabled at the same time?

OUTPUT:
├── ✅ A recovery path exists
└── ❌ "BRICK RISK: This configuration lacks OTA, USB-CDC and WiFi recovery.
       If something goes wrong you cannot reflash without an external
       programmer. Add at least one of: ota:, usb_cdc:, or keep WiFi."
```

### 3.9 Secrets validation

Prevents credentials in plaintext:

```
INPUT: Generated YAML

PATTERN MATCHING (regex to flag suspicious strings):
├── api_key|access_token|password|secret = "[^!secret]"
├── 'api: encryption: key' without !secret
├── 'wifi: password' without !secret
├── 'mqtt: password' without !secret
└── Hex strings > 20 chars that look like API keys

RULE:
├── All credentials MUST reference a !secret name
├── secrets.yaml template is generated separately
└── Output rejected if credentials are hardcoded
```

### 3.10 Agent hand-off protocol

In DEEP mode, 2+ agents are involved. Standardized data transfer:

```json
{
  "$schema": "../schemas/project-snapshot.schema.json",
  "schema_version": "1.0",
  "project_context": {
    "project_id": "uuid-v4",
    "project_name": "Living room sensor",
    "user_requirements": ["temp", "humidity", "presence"],
    "selected_board": "esp32-c3-mini",
    "selected_components": ["bme280", "ld2410"],
    "gpio_allocation": {
      "bme280": {"sda": 8, "scl": 9},
      "ld2410": {"tx": 4, "rx": 5}
    },
    "entity_ids_generated": [
      "sensor.living_room_temperature",
      "sensor.living_room_humidity",
      "binary_sensor.living_room_presence"
    ],
    "esphome_filename": "living-room-sensor.yaml",
    "current_agent": "volt",
    "next_agents": ["sage", "iris"],
    "validation_results": {
      "volt": "passed",
      "sage": "pending",
      "iris": "pending"
    },
    "conflict_log": []
  }
}
```

**Flow:**
```
Volt completes → writes project_context → Sage reads it
Sage completes → updates entity_ids_used → Iris reads it
Iris completes → final project_snapshot saved
```

**Conflict resolution:**
If Vera blocks Volt's choice: project_context.conflict_log is updated and the user decides.

### 3.11 Project templates library

Quick start for common use cases:

```yaml
# templates/bluetooth-proxy.yaml
# Variables: ${board_id}, ${device_name}
esphome:
  name: ${device_name}

esp32:
  board: ${board_id}
  framework:
    type: esp-idf

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password

bluetooth_proxy:
  active: true

esp32_ble_tracker:
```

**Workflow:**
```
User: "I want to build a bluetooth proxy"
→ Aurora matches the "bluetooth-proxy" template
→ Volt asks: "Start from template or build from scratch?"
→ If template: variables are filled in, validation runs, done in 30 seconds
```

### 3.12 Retroactive YAML validation

Volt gains the ability to validate *existing* YAML:

```
User: *pastes YAML* "Does this work?"
→ Volt parses the YAML
→ Identifies board + all GPIO + all components
→ Runs STEP 5-12 of the validation workflow
→ Output:
  ✅ "Looks correct"
  ⚠️ "Line 23: GPIO 19 used while USB is active, conflict"
  ❌ "Line 45: GPIO 49 does not exist on ESP32-S3 (max 48)"
```

### 3.13 Tiered error messages for beginners

```
❌ Problem (short):
GPIO 19 cannot be used on this board

📚 Explanation (medium):
The ESP32-S3 has built-in USB support that uses GPIO 19 and 20.
If you use these pins for a sensor, USB stops working.

🔧 Solution (concrete):
Use GPIO 8 instead, it is free and works for your DHT22.

💡 Deeper (for the curious):
The USB-OTG protocol uses differential signals D+/D-
mapped to GPIO 19/20. You can disable USB in the config via
'usb_cdc: false', but you lose serial debug.
```

### 3.14 Cross-agent validation pattern

| Agent | Validator modules | Resource library |
|-------|-------------------|------------------|
| Volt | pin, conflict, version, ota-safety, secrets, i2c-address, voltage-level | boards/, components/, expanders/, voltage-shifters/ |
| Ada | python-syntax, async-correctness, entity-id, secrets | (HA Python API spec) |
| Sage | yaml-syntax, entity-id, version, secrets | (HA YAML schema) |
| River | node-red-syntax, version | (Node-RED node names) |
| Mira | python-syntax, llm-config, secrets | (LLM provider specs) |
| Atlas | api-endpoint, secrets | (API catalog) |
| Iris | lovelace-schema, card-types | (Lovelace specs) |

### 3.15 Iron Law Test Suite

```
aurora/tests/
├── volt/
│   ├── test-wiring-diagram-present.md
│   ├── test-calibration-procedure.md
│   ├── test-board-confirmed-before-yaml.md
│   ├── test-pin-validity.md
│   ├── test-no-conflicts.md
│   ├── test-ota-safety.md
│   └── test-no-hardcoded-secrets.md
├── ada/
│   ├── test-dt-util-not-datetime.md
│   ├── test-aiohttp-not-requests.md
│   └── test-json-serializable.md
├── sage/
│   ├── test-yaml-syntax-valid.md
│   └── test-entity-id-format.md
└── (and so on for all agents)
```

### 3.16 User project history

```json
{
  "project_id": "uuid-v4",
  "name": "Living room sensor",
  "created": "2026-05-13",
  "board": "esp32-c3-mini",
  "components": ["bme280", "ld2410"],
  "esphome_version": "2026.4",
  "validation": {
    "status": "validated",
    "validated_at": "2026-05-13",
    "warnings": []
  },
  "files": ["living-room-sensor.yaml"],
  "agents_involved": ["volt", "sage", "iris"]
}
```

### 3.17 Lifecycle/Deprecation warnings

```json
"lifecycle": {
  "status": "deprecated",
  "since": "2024",
  "reason": "ESP8266 lacks BLE, Thread, Matter. Choose ESP32-C3 for new projects.",
  "successor": "esp32-c3-mini"
}
```

---

## 4. Data management (new section)

### 4.1 Data source and update mechanism

**Authoritative sources (per board/component):**

| Data type | Primary source | Secondary | Update cadence |
|-----------|---------------|-----------|----------------|
| Chip GPIO/specs | Espressif datasheets | Arduino-ESP32 repo | Per new chip revision |
| Dev board pinouts | Manufacturer datasheet | Community wiki | Per new board |
| Sensor specs | Manufacturer datasheet | ESPHome docs | Rarely changes |
| ESPHome support | ESPHome changelog | GitHub releases | Per ESPHome release |

**Update process:**
1. Each JSON file has `last_verified: YYYY-MM-DD` and `verified_source`
2. An audit script runs monthly and flags files older than 6 months
3. On new chip release: PR with the new board profile + updated `_index.md`

### 4.2 JSON schema validation

`aurora/references/schemas/*.schema.json` defines the structure for all JSON types.

**Validation runs:**
- Pre-commit hook: all new or changed JSON validated against the schema
- CI: full validation across all JSON files
- Runtime (Volt): validate the schema at load time, fall back if invalid

### 4.3 Schema versioning and backward compatibility

Every JSON file carries `schema_version`:
```json
{
  "schema_version": "1.0",
  ...
}
```

**Versioning rules (semver):**
- MAJOR (2.0): breaking change, requires migration
- MINOR (1.1): new optional fields, backward compatible
- PATCH (1.0.1): documentation bugfix

**Migration scripts** live in `schemas/migrations/v1-to-v2.md`.

### 4.4 Community contribution path

`aurora/CONTRIBUTING.md` contains:
- Template for "Add new board" PRs
- Template for "Add new component" PRs
- Verification requirements (datasheet link, last_verified, tests)
- Review process (at least 1 maintainer + automated test suite)

PR template checklist:
```
- [ ] schema_version is set
- [ ] last_verified is the current date
- [ ] verified_source is linked
- [ ] All required fields are present
- [ ] Passes schema validation (npm run validate)
- [ ] Iron Law tests pass
```

### 4.5 CI/CD for the Iron Law Test Suite

GitHub Actions workflow `.github/workflows/aurora-validation.yml`:

```yaml
name: Aurora Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate JSON schemas
        run: ./scripts/validate-all-schemas.sh
      - name: Run Iron Law test suite
        run: ./scripts/run-iron-law-tests.sh
      - name: Verify data freshness
        run: ./scripts/check-last-verified.sh
```

---

## 5. Implementation plan (expanded)

### Phase 1: Foundation data + schema
1. Write JSON Schema for all types (boards, components, expanders, voltage-shifters, external-components, project-snapshots)
2. Convert `esphome/references/pinouts.md` into JSON profiles for 9 chip families
3. Create an initial set of 10 common sensor profiles (including variants)
4. Create an initial set of 4 GPIO expander profiles
5. Create an initial set of 3 voltage shifter profiles

### Phase 2: Validator modules
1. `validators/pin-validator.md`
2. `validators/conflict-validator.md`
3. `validators/version-validator.md`
4. `validators/yaml-syntax-validator.md`
5. `validators/python-validator.md`
6. `validators/entity-id-validator.md`
7. `validators/ota-safety-validator.md`
8. `validators/secrets-validator.md`
9. `validators/i2c-address-validator.md`
10. `validators/voltage-level-validator.md`

### Phase 3: Volt integration
1. Update `aurora/souls/volt.md` with Iron Law 6: "Validate before generating"
2. Update `aurora/SKILL.md` with references to boards/, components/, expanders/
3. Create Volt's test suite in `aurora/tests/volt/`
4. Implement the expanded validation workflow (13 steps)

### Phase 4: Smart home and special boards
1. Shelly Plus 1, Plus 2PM
2. Sonoff Basic R3, Mini R3
3. LilyGo T-Display S3, M5Stack Atom, Heltec WiFi LoRa
4. RP2040 Pico, RP2350 Pico 2

### Phase 5: Project templates library
1. Bluetooth proxy template
2. Voice assistant template (ESP32-S3)
3. Air quality monitor template
4. Presence sensor (radar) template
5. Battery soil sensor template
6. Multi-relay controller template
7. Temp/humidity room template

### Phase 6: Hand-off protocol and cross-agent
1. `handoff/_protocol.md`
2. `handoff/project-context.schema.json`
3. Ada validation (test suite + validators)
4. Sage validation (test suite + validators)
5. River validation (test suite + validators)
6. Mira, Atlas, Iris: same pattern

### Phase 7: External components catalog
1. `external-components/_index.md` with community package guide
2. Initial set: LD2410, Tuya MCU, NSPanel Pro
3. Source URL validation (GitHub repo exists)
4. Maintenance status tracking

### Phase 8: Advanced features
1. Retroactive YAML validation (Volt parses existing YAML)
2. Tiered error message system
3. Project snapshots (persistence between sessions)
4. Lifecycle warnings

### Phase 9: Data management
1. JSON Schema validation infrastructure
2. Audit script for data freshness
3. `CONTRIBUTING.md` + PR templates
4. CI/CD workflow for aurora validation

---

## 6. Expected outcome

### Before the solution
> Beginner: "I want to build a bluetooth proxy"
> → Volt: "Use ESP32-S2"
> → User buys it, flashes, it does not work (S2 has no BLE)
> → ❌ Disappointment, project abandoned

### After the solution
> Beginner: "I want to build a bluetooth proxy"
> → Volt matches the "bluetooth-proxy" template
> → Volt filters boards by capability `bluetooth_proxy: true`
> → Volt: "ESP32-C3 (cheapest) or ESP32-S3 (if voice later)"
> → User picks C3
> → Volt loads `esp32-c3-mini.json` + component profiles
> → Volt checks GPIO sufficiency, conflicts, OTA safety, secrets
> → Volt generates YAML from template + diagram + troubleshooting
> → ✅ User flashes, bluetooth proxy works

---

## 7. Success criteria

- ✅ Volt **cannot** generate YAML with GPIO that does not exist on the selected board
- ✅ Volt **cannot** recommend a board missing a required capability
- ✅ Volt **detects** pin conflicts between components before output
- ✅ Volt **warns** about deprecated boards with a clear successor
- ✅ Volt **warns** about easily confused sensor variants (BME280 vs BMP280)
- ✅ Volt **suggests** a GPIO expander when pins run out
- ✅ Volt **requires** a voltage level shifter when a 5V component is paired with a 3.3V board
- ✅ Volt **detects** I2C address conflicts between components
- ✅ Volt **prevents** brick risk via the OTA safety check
- ✅ Volt **requires** !secret for all credentials
- ✅ Project templates provide a 30-second quick start for 7 common use cases
- ✅ Hand-off protocol works for at least Volt → Sage → Iris
- ✅ Error messages are understandable for beginners (3 layers)
- ✅ JSON data validates against the schema on commit
- ✅ Schema versioning supports backward compatibility
- ✅ CI/CD runs the Iron Law Test Suite automatically on every PR
- ✅ The community can contribute new boards via a documented process

---

## 8. Out of scope for this version (Tier C, V2 roadmap)

- Hardware automation (BOM generation, PCB layout)
- Multi-board topology validation (3+ ESP32 devices communicating)
- Pricing/availability data
- Compliance and certification (CE, FCC, RoHS) per board
- Industrial protocols (Modbus RTU/TCP, BACnet, M-Bus, KNX, DLMS)
- Mass-production concerns (supply chain, lead times, MOQs)
- Migration path for existing ESPHome projects
- Internationalization (error messages in multiple languages)
- Interactive board selector UI (CLI only for v1)

---

## 9. Risks and mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| JSON database goes stale | High | High | `last_verified` + audit script + community PR process |
| Volt ignores validation | Low | Critical | Test suite + Iron Law 6 explicit + CI |
| Beginners overwhelmed by choices | Medium | Medium | Tiered messages + templates as default |
| Maintenance overhead | Medium | Medium | Templates + contributor guide + schema validation |
| Schema-breaking changes | Medium | High | schema_version + migration scripts |
| External component data stale | High | Medium | maintenance_status field + GitHub stars check |
| False positives in secrets scanner | Medium | Low | Regex tweaks + per-credential opt-out |
| OTA safety too restrictive | Low | Medium | Explicit override flag with warning |
| I2C multiplexer adds complexity | Medium | Low | Only when there is a real conflict, transparent |
| GPIO expander forgets constraints | Low | Medium | Expander profile declares limitations |

---

## 10. Next steps

1. User reviews and approves this spec
2. On approval: transition to the `writing-plans` skill for a detailed implementation plan
3. Implementation per phase, with test coverage per phase

---

*Spec updated: 2026-05-13. Status: Draft v2 (expanded with Tier A + B). 22 missing elements from the initial review, 15 included here, 9 in the V2 roadmap.*
