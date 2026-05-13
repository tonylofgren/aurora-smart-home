# Aurora Skill — Validation-Before-Generation Design

**Status:** Draft for review (v2 - expanded with Tier A + B)
**Date:** 2026-05-13
**Author:** Granskning från nybörjar-perspektiv
**Scope:** Aurora skill arkitektur, alla agenter, fokus Volt (ESP32/ESPHome)

---

## 1. Bakgrund och problem

Aurora skill är ett orchestreringslager med 21 specialistagenter för smart home-utveckling. Skill har Iron Laws som styr varje agents disciplin, t.ex. Volts krav om "board first" innan YAML-generering.

**Identifierat kärnproblem:**
Iron Laws finns som *text*, inte som *tvingande struktur*. Detta betyder att en agent (särskilt Volt) kan generera kod som inte matchar den fysiska hårdvaran: felaktig GPIO-pin, fel board för uppgiften, eller pin-konflikter mellan komponenter.

**För en nybörjare:**
Den värsta besvikelsen är att aurora skill *lägger in fel portar i koden*. Detta resulterar i sensor som inte fungerar, skadad hårdvara, timmar bortkastade på felsökning, eller övergivet projekt.

**Designens mål:**
Garantera att aurora skill levererar *korrekt kod oavsett användare*, genom systemisk validering före generering.

---

## 2. Nuvarande tillstånd

### Vad som finns idag

- `aurora/SKILL.md`: routing och Iron Laws för 21 agenter
- `aurora/souls/volt.md`: Volts Iron Laws (board first, wiring diagram, calibration, power budget, troubleshooting)
- `aurora/references/platform-versions.md`: HA + ESPHome version info
- `aurora/references/workflows.md`: multi-skill workflow-mallar
- `esphome/references/pinouts.md`: GPIO-pinouts för 9 ESP-chip-familjer (markdown + ASCII)
- `esphome/references/boards.md`: board-information

### Identifierade luckor

1. Pin-data är inte machine-readable (markdown/ASCII, svår att parsa)
2. Aurora skill länkar inte till pin-data (Volt vet inte att referensen finns)
3. Ingen validering före generering (Volt litar på sin egen kunskap)
4. Endast pin-data, ingen capability-matrix (BLE/Thread/PSRAM saknas)
5. Ingen sensor/komponent-databas (sensor-krav kan brista)
6. Inga conflict-checks mellan komponenter
7. Mönstret saknas för andra agenter (Ada, Sage, River har samma risk)
8. Sensor-varianter blandas (BME280 vs BMP280, DHT22 vs DHT11)
9. GPIO Expander-stöd saknas (när pinnar tar slut)
10. Voltage level shifter-data saknas (5V sensorer på 3.3V boards)
11. I2C-adresskonflikter detekteras inte
12. Sleep mode och wake source-data saknas
13. OTA-safety check saknas (brick-risk)
14. Secrets-validering saknas (credentials i klartext)
15. External components-katalog saknas
16. Project templates saknas (helt blank start)
17. Hand-off protocol mellan agenter saknas
18. Data update mechanism saknas (hur uppdateras JSON?)
19. JSON Schema validation saknas (för JSON-filerna själva)
20. Community contribution path saknas
21. Schema versioning saknas (backward compatibility)
22. CI/CD för Iron Law Test Suite saknas

---

## 3. Föreslagen arkitektur

### 3.1 Ny katalogstruktur

```
aurora/references/
├── boards/                          # Board-profiler (komplett kapacitet)
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
├── components/                      # Sensor/aktuator-profiler
│   ├── _index.md
│   ├── temperature/
│   │   ├── dht22.json
│   │   ├── ds18b20.json
│   │   ├── bme280.json
│   │   ├── bmp280.json           # OBS: skild från BME280
│   │   └── ntc-thermistor.json
│   ├── moisture/
│   │   ├── capacitive-soil-v1.2.json
│   │   └── resistive-soil.json
│   ├── motion/
│   │   ├── pir-am312.json
│   │   └── radar-ld2410.json
│   ├── air-quality/
│   │   ├── mh-z19b.json
│   │   ├── mh-z19c.json          # OBS: skild kalibrering
│   │   └── scd40.json
│   ├── distance/
│   │   └── hc-sr04.json          # OBS: 5V sensor
│   ├── relays/
│   │   └── songle-srd-05vdc.json
│   └── displays/
│       ├── ili9341-tft.json
│       └── ssd1306-oled.json
│
├── expanders/                       # GPIO expanders (när pinnar tar slut)
│   ├── _index.md
│   ├── pcf8574.json                # 8-bit I2C expander
│   ├── mcp23017.json               # 16-bit I2C expander
│   ├── pca9685.json                # 16-channel PWM
│   └── tca9548a.json               # I2C multiplexer (för dubbletter)
│
├── voltage-shifters/                # Level shifters (5V <-> 3.3V)
│   ├── _index.md
│   ├── txs0108e.json               # 8-channel bidirectional
│   ├── bss138.json                 # MOSFET-based single channel
│   └── tx-rx-resistor-divider.json # Voltage divider för RX only
│
├── external-components/             # ESPHome community packages
│   ├── _index.md
│   ├── ld2410-empericalsoul.json
│   ├── tuya-mcu-jesserockz.json
│   └── nspanel-pro.json
│
├── templates/                       # Quick-start projekt-mallar
│   ├── _index.md
│   ├── bluetooth-proxy.yaml
│   ├── voice-assistant-s3.yaml
│   ├── air-quality-monitor.yaml
│   ├── presence-sensor-radar.yaml
│   ├── temp-humidity-room.yaml
│   ├── battery-soil-sensor.yaml
│   └── multi-relay-controller.yaml
│
├── schemas/                         # JSON Schema för validering av JSON
│   ├── board-profile.schema.json
│   ├── component-profile.schema.json
│   ├── expander-profile.schema.json
│   ├── voltage-shifter.schema.json
│   ├── external-component.schema.json
│   ├── project-snapshot.schema.json
│   └── _schema-version.md
│
├── validators/                      # Cross-agent validator-moduler
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

### 3.2 Board-profil JSON-schema (utökad)

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

### 3.3 Komponent-profil JSON-schema (utökad)

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
        "difference": "BMP280 saknar humidity sensor, identiskt utseende"
      }
    ],
    "knockoffs_known": true,
    "verification_method": "Läs chip ID register: 0x60 = BME280, 0x58 = BMP280"
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
    "pullup_resistor": {"value_ohm": 4700, "required": true, "note": "External pull-ups om board ej har"},
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

### 3.4 GPIO Expander-profil

När antal komponenter > tillgängliga GPIO på board, route till expander:

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
    "16 reläer på ESP32-C3 (22 GPIO total)",
    "Button matrix utan att slösa GPIO",
    "LED-status panels"
  ],

  "esphome": {
    "platform": "pcf8574",
    "min_version": "2022.1.0"
  }
}
```

### 3.5 Voltage Level Shifter-profil

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

### 3.6 External Components-katalog

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

### 3.7 Volts validerings-workflow (utökad)

```
INPUT: Användarens projekt-krav (sensor, BLE, batteri, voice, etc.)

STEG 1: Kravanalys
├── Identifiera behov: BLE? Battery? Voice? Camera? Matter?
├── Identifiera antal komponenter
└── Sätt capability filters

STEG 2: Template-check
├── Matchar kraven en befintlig template i templates/?
└── Om ja, föreslå template som startpunkt

STEG 3: Board-rekommendation
├── Läs alla *.json i boards/
├── Filtrera mot capability filters
├── Filtrera bort deprecated boards (varna om användare insisterar)
└── Föreslå 2-3 lämpliga boards med trade-offs

STEG 4: Användaren väljer board
└── Bekräftelse + load board-profil

STEG 5: Komponent-validering
├── För varje sensor/komponent: ladda components/*.json
├── Visa "easily_confused_with" varningar (BME280 vs BMP280)
├── Verifiera pin_requirements matchar board.gpio
├── Verifiera power-krav passar board (voltage_min/max)
├── Om komponent 5V och board 3.3V: kräv level shifter
└── Verifiera ESPHome-version stöder komponenten

STEG 6: GPIO-tillräcklighet
├── Räkna behövda pinnar vs board.gpio.valid_pins
├── Om otillräckligt: föreslå GPIO expander från expanders/
└── Om I2C-adresskonflikt: föreslå TCA9548A multiplexer

STEG 7: Pin-allokering
├── Föreslå GPIO från board.gpio.valid_pins
├── Undvik strapping_pins, reserved_for_usb, psram_blocks_gpio
├── Använd i2c_default / spi_default för bus-protokoll
└── Reservera pinnar per komponent

STEG 8: Conflict-validering (validators/conflict-validator.md)
├── Pin-collision check: Två komponenter på samma pin (ej I2C/OneWire)?
├── Bus-sharing check: I2C-adresser unika (validators/i2c-address-validator)?
├── Strapping-conflict: Komponent på 0/3/45/46 utan korrekt pull?
├── USB-conflict: 19/20 + USB CDC aktiv?
├── PSRAM-conflict: 26-32 + PSRAM aktiv?
├── Voltage-mismatch (validators/voltage-level-validator): 5V komponent på 3.3V-only pin?
└── ADC-conflict: ADC2 + WiFi (S2/C3 specific)?

STEG 9: Sleep mode-validering
├── Om deep_sleep används: wake-pin i board.gpio.wake_source_pins?
├── Om battery: är wake-strategi konsistent med power budget?
└── Flag Watt för power budget review

STEG 10: OTA-safety (validators/ota-safety-validator.md)
├── Är OTA-funktionen kvar i config?
├── Är USB-CDC kvar eller WiFi recovery möjlig?
├── Om ingen recovery-väg: VARNA om brick-risk
└── Kräv explicit override för att fortsätta

STEG 11: Secrets-validering (validators/secrets-validator.md)
├── Skanna YAML för strängar som ser ut som credentials
├── Verifiera att alla credentials använder !secret
└── Reject output om credentials i klartext

STEG 12: Version-validering (validators/version-validator.md)
├── ESPHome >= minimum för alla features?
├── Board stöder valt framework (arduino vs esp-idf)?
└── Chip-revision OK?

STEG 13: YAML-generering (endast om STEG 1-12 ✓)
├── Generera ESPHome YAML
├── Generera ASCII wiring diagram (Iron Law 2)
├── Generera calibration procedure om sensor kräver (Iron Law 3)
├── Generera troubleshooting med faktiska entity IDs (Iron Law 5)
└── Spara project-snapshot

OUTPUT:
├── ✅ Komplett, validerad YAML + diagram + docs
└── ❌ Tydligt felmeddelande med förklaring och förslag
```

### 3.8 OTA-Safety Validation

Förhindrar att Volt genererar config som kan göra board obrickbar:

```
INPUT: Genererad YAML + board-profil

CHECKS:
├── Är 'ota:' platform deklarerad i YAML?
├── Är WiFi konfigurerad (för OTA over WiFi)?
├── Är USB-CDC kvar (för fysisk recovery)?
├── Använder konfig 'factory_reset' button mappning?
└── Är inte OTA + WiFi + USB ALLA disablerade samtidigt?

OUTPUT:
├── ✅ Recovery-väg finns
└── ❌ "BRICK RISK: Den här konfigurationen saknar både OTA, USB-CDC och 
       WiFi recovery. Om något går fel kan du inte återflasha utan extern 
       programmerare. Lägg till minst en av: ota:, usb_cdc:, eller behåll WiFi."
```

### 3.9 Secrets-Validering

Förhindrar credentials i klartext:

```
INPUT: Genererad YAML

PATTERN MATCHING (regex för att flagga misstänkta strängar):
├── api_key|access_token|password|secret = "[^!secret]"
├── 'api: encryption: key' utan !secret
├── 'wifi: password' utan !secret
├── 'mqtt: password' utan !secret
└── Hex-strängar > 20 tecken som ser ut som API-nycklar

REGEL:
├── Alla credentials MÅSTE referera !secret name
├── secrets.yaml-template genereras separat
└── Output rejected om credentials hardcoded
```

### 3.10 Hand-off Protocol mellan agenter

I DEEP mode involveras 2+ agenter. Standardiserad data-overföring:

```json
{
  "$schema": "../schemas/project-snapshot.schema.json",
  "schema_version": "1.0",
  "project_context": {
    "project_id": "uuid-v4",
    "project_name": "Vardagsrum sensor",
    "user_requirements": ["temp", "humidity", "presence"],
    "selected_board": "esp32-c3-mini",
    "selected_components": ["bme280", "ld2410"],
    "gpio_allocation": {
      "bme280": {"sda": 8, "scl": 9},
      "ld2410": {"tx": 4, "rx": 5}
    },
    "entity_ids_generated": [
      "sensor.vardagsrum_temperature",
      "sensor.vardagsrum_humidity",
      "binary_sensor.vardagsrum_presence"
    ],
    "esphome_filename": "vardagsrum-sensor.yaml",
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

**Flöde:**
```
Volt completes → writes project_context → Sage reads it
Sage completes → updates entity_ids_used → Iris reads it
Iris completes → final project_snapshot saved
```

**Conflict resolution:**
Om Vera blockerar Volt's val: project_context.conflict_log loggas, användaren beslutar.

### 3.11 Project Templates Library

Quick-start för vanliga use-cases:

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
Användare: "Jag vill bygga bluetooth proxy"
→ Aurora matchar "bluetooth-proxy" template
→ Volt frågar: "Start från template eller bygg från grunden?"
→ Om template: variabler fylls i, validering körs, klar på 30 sekunder
```

### 3.12 Retroactive YAML Validation

Volt får förmåga att validera *befintlig* YAML:

```
Användare: *klistrar in YAML* "Funkar det här?"
→ Volt parsar YAML
→ Identifierar board + alla GPIO + alla komponenter
→ Kör STEG 5-12 i validerings-workflow
→ Output:
  ✅ "Allt ser korrekt ut"
  ⚠️ "Rad 23: GPIO 19 används men USB är aktiverat, konflikt"
  ❌ "Rad 45: GPIO 49 finns inte på ESP32-S3 (max 48)"
```

### 3.13 Tiered Error Messages för Nybörjare

```
❌ Problem (kort):
GPIO 19 kan inte användas på den här boarden

📚 Förklaring (medium):
ESP32-S3 har inbyggd USB-stöd som använder GPIO 19 och 20.
Om du använder dessa pinnar för en sensor, slutar USB att fungera.

🔧 Lösning (konkret):
Använd GPIO 8 istället, den är ledig och passar för din DHT22.

💡 Djupare (för den som vill veta):
USB-OTG-protokollet använder differentiella signaler D+/D-
mappade till GPIO 19/20. Du kan stänga av USB i config med
'usb_cdc: false', men då tappar du serial debug.
```

### 3.14 Cross-Agent Validation Pattern

| Agent | Validator-moduler | Resurs-bibliotek |
|-------|-------------------|-------------------|
| Volt | pin, conflict, version, ota-safety, secrets, i2c-address, voltage-level | boards/, components/, expanders/, voltage-shifters/ |
| Ada | python-syntax, async-correctness, entity-id, secrets | (HA Python API spec) |
| Sage | yaml-syntax, entity-id, version, secrets | (HA YAML schema) |
| River | node-red-syntax, version | (Node-RED nod-namn) |
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
└── (osv för alla agenter)
```

### 3.16 User Project History

```json
{
  "project_id": "uuid-v4",
  "name": "Vardagsrum sensor",
  "created": "2026-05-13",
  "board": "esp32-c3-mini",
  "components": ["bme280", "ld2410"],
  "esphome_version": "2026.4",
  "validation": {
    "status": "validated",
    "validated_at": "2026-05-13",
    "warnings": []
  },
  "files": ["vardagsrum-sensor.yaml"],
  "agents_involved": ["volt", "sage", "iris"]
}
```

### 3.17 Lifecycle/Deprecation Warnings

```json
"lifecycle": {
  "status": "deprecated",
  "since": "2024",
  "reason": "ESP8266 saknar BLE, Thread, Matter. Välj ESP32-C3 för nya projekt.",
  "successor": "esp32-c3-mini"
}
```

---

## 4. Data Management (NY sektion)

### 4.1 Data Source och Update Mechanism

**Auktoritativa källor (per board/component):**

| Datatyp | Primär källa | Sekundär | Update-frekvens |
|---------|--------------|----------|-----------------|
| Chip GPIO/specs | Espressif datasheets | Arduino-ESP32 repo | Per ny chip-revision |
| Dev board pinouts | Tillverkarens datasheet | Community wiki | Per ny board |
| Sensor specs | Tillverkarens datasheet | ESPHome docs | Sällan ändras |
| ESPHome support | ESPHome changelog | GitHub releases | Per ESPHome release |

**Update-process:**
1. JSON-fil har `last_verified: YYYY-MM-DD` och `verified_source`
2. Audit-script körs månadsvis, flaggar filer äldre än 6 månader
3. Vid ny chip-release: PR med ny board-profil + uppdaterad `_index.md`

### 4.2 JSON Schema Validation

`aurora/references/schemas/*.schema.json` definierar struktur för alla JSON-typer.

**Validation runs:**
- Pre-commit hook: alla nya/ändrade JSON valideras mot schema
- CI: heltäckande validation över alla JSON-filer
- Runtime (Volt): validera schema vid laddning, fall back om ogiltigt

### 4.3 Schema Versioning & Backward Compatibility

Varje JSON har `schema_version`:
```json
{
  "schema_version": "1.0",
  ...
}
```

**Versioneringsregler (semver):**
- MAJOR (2.0): breaking change, requires migration
- MINOR (1.1): nya optional fields, backward compatible
- PATCH (1.0.1): bugfix i dokumentation

**Migration scripts** lagras i `schemas/migrations/v1-to-v2.md`.

### 4.4 Community Contribution Path

`aurora/CONTRIBUTING.md` med:
- Mall för "Add new board" PR
- Mall för "Add new component" PR
- Verifieringskrav (datasheet link, last_verified, tester)
- Review-process (minst 1 maintainer + automatiserad test-suite)

PR-template med checklist:
```
- [ ] schema_version is set
- [ ] last_verified is current date
- [ ] verified_source is linked
- [ ] All required fields are present
- [ ] Passes schema validation (npm run validate)
- [ ] Iron Law tests pass
```

### 4.5 CI/CD för Iron Law Test Suite

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

## 5. Implementeringsplan (utökad)

### Fas 1: Foundation Data + Schema
1. Skriv JSON Schema för alla typer (boards, components, expanders, voltage-shifters, external-components, project-snapshots)
2. Konvertera `esphome/references/pinouts.md` till JSON-profiler för 9 chip-familjer
3. Skapa initial set av 10 vanliga sensor-profiler (inklusive varianter)
4. Skapa initial set av 4 GPIO-expander-profiler
5. Skapa initial set av 3 voltage shifter-profiler

### Fas 2: Validator-modulerna
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

### Fas 3: Volts integration
1. Uppdatera `aurora/souls/volt.md` med Iron Law 6: "Validate before generating"
2. Uppdatera `aurora/SKILL.md` med referens till boards/, components/, expanders/
3. Skapa Volts test-suite i `aurora/tests/volt/`
4. Implementera utökat validering-workflow (13 steg)

### Fas 4: Smart Home & Special boards
1. Shelly Plus 1, Plus 2PM
2. Sonoff Basic R3, Mini R3
3. LilyGo T-Display S3, M5Stack Atom, Heltec WiFi LoRa
4. RP2040 Pico, RP2350 Pico 2

### Fas 5: Project Templates Library
1. Bluetooth proxy template
2. Voice assistant template (ESP32-S3)
3. Air quality monitor template
4. Presence sensor (radar) template
5. Battery soil sensor template
6. Multi-relay controller template
7. Temp/humidity room template

### Fas 6: Hand-off Protocol & Cross-Agent
1. `handoff/_protocol.md`
2. `handoff/project-context.schema.json`
3. Ada validation (test-suite + validators)
4. Sage validation (test-suite + validators)
5. River validation (test-suite + validators)
6. Mira, Atlas, Iris: samma mönster

### Fas 7: External Components Catalog
1. `external-components/_index.md` med community-package guide
2. Initial set: LD2410, Tuya MCU, NSPanel Pro
3. Source URL-validering (GitHub repo finns)
4. Maintenance status-tracking

### Fas 8: Advanced features
1. Retroactive YAML validation (Volt parsar existerande YAML)
2. Tiered error message-system
3. Project snapshots (persistens mellan sessioner)
4. Lifecycle warnings

### Fas 9: Data Management
1. JSON Schema validation infrastructure
2. Audit-script för data freshness
3. `CONTRIBUTING.md` + PR-templates
4. CI/CD workflow för aurora validation

---

## 6. Förväntat resultat

### Före lösningen
> Nybörjare: "Jag vill bygga en bluetooth-proxy"
> → Volt: "Använd ESP32-S2"
> → Användare köper, flashar, fungerar inte (S2 har ingen BLE)
> → ❌ Besvikelse, projekt övergivet

### Efter lösningen
> Nybörjare: "Jag vill bygga en bluetooth-proxy"
> → Volt matchar template "bluetooth-proxy"
> → Volt filtrerar boards: capability `bluetooth_proxy: true`
> → Volt: "ESP32-C3 (billigast) eller ESP32-S3 (om voice senare)"
> → Användaren väljer C3
> → Volt laddar `esp32-c3-mini.json` + komponent-profiler
> → Volt kollar GPIO-tillräcklighet, conflicts, OTA-safety, secrets
> → Volt genererar YAML från template + diagram + troubleshooting
> → ✅ Användare flashar, bluetooth-proxy fungerar

---

## 7. Success Criteria

- ✅ Volt kan **inte** generera YAML med GPIO som inte finns på vald board
- ✅ Volt kan **inte** rekommendera board som saknar krävd capability
- ✅ Volt **upptäcker** pin-konflikter mellan komponenter före output
- ✅ Volt **varnar** för deprecated boards med tydlig successor
- ✅ Volt **varnar** för sensor-variant-förvirring (BME280 vs BMP280)
- ✅ Volt **föreslår** GPIO expander när pinnar tar slut
- ✅ Volt **kräver** voltage level shifter när 5V-komponent på 3.3V board
- ✅ Volt **detekterar** I2C-adresskonflikter mellan komponenter
- ✅ Volt **förhindrar** brick-risk via OTA-safety check
- ✅ Volt **kräver** !secret för alla credentials
- ✅ Project templates ger 30-sekunders quick-start för 7 vanliga use-cases
- ✅ Hand-off protocol fungerar mellan minst Volt → Sage → Iris
- ✅ Felmeddelanden är förståeliga för nybörjare (3 lager)
- ✅ JSON-data valideras mot schema vid commit
- ✅ Schema-versionering möjliggör backward compatibility
- ✅ CI/CD kör Iron Law Test Suite automatiskt på varje PR
- ✅ Community kan bidra med nya boards via dokumenterad process

---

## 8. Out of scope för denna version (Tier C, V2 roadmap)

- Hardware automation (BOM-generering, PCB-layout)
- Multi-board topology validation (3+ ESP32 som pratar med varandra)
- Pricing/availability data
- Compliance & certifiering (CE, FCC, RoHS) per board
- Industriprotokoll (Modbus RTU/TCP, BACnet, M-Bus, KNX, DLMS)
- Mass-produktion concerns (supply chain, lead times, MOQs)
- Migration path för befintliga ESPHome-projekt
- Internationalization (felmeddelanden på olika språk)
- Interactive board selector UI (CLI-only för v1)

---

## 9. Risker och mitigation

| Risk | Sannolikhet | Påverkan | Mitigation |
|------|-------------|----------|------------|
| JSON-databasen blir inaktuell | Hög | Hög | `last_verified` + audit-script + community PR-process |
| Volt ignorerar validering | Låg | Kritisk | Test-suite + Iron Law 6 explicit + CI |
| Nybörjare överväldigas av val | Medel | Medel | Tiered messages + templates som default |
| Maintenance overhead | Medel | Medel | Templater + bidragsguide + schema validation |
| Schema-breaking changes | Medel | Hög | schema_version + migration scripts |
| External component-data inaktuell | Hög | Medel | maintenance_status field + GitHub stars check |
| Falska positiva i secrets-scanner | Medel | Låg | Regex tweaks + opt-out per credential |
| OTA-safety för restriktiv | Låg | Medel | Explicit override-flagga med varning |
| I2C-multiplexer komplicerar | Medel | Låg | Endast vid riktig konflikt, transparent |
| GPIO expander glömmer constraints | Låg | Medel | Expander-profil deklarerar limitations |

---

## 10. Nästa steg

1. Användare granskar och godkänner detta spec
2. Vid godkännande: transition till `writing-plans` skill för detaljerad implementeringsplan
3. Implementation per fas, med test-coverage per fas

---

*Spec uppdaterad: 2026-05-13. Status: Draft v2 (expanded with Tier A + B). 22 saknade element från initial granskning, 15 inkluderade här, 9 i V2 roadmap.*
