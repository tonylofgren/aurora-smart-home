# Aurora Skill — Validation-Before-Generation Design

**Status:** Draft for review
**Date:** 2026-05-13
**Author:** Granskning från nybörjar-perspektiv
**Scope:** Aurora skill arkitektur — alla agenter, fokus Volt (ESP32/ESPHome)

---

## 1. Bakgrund och problem

Aurora skill är ett orchestreringslager med 21 specialistagenter för smart home-utveckling. Skill har Iron Laws som styr varje agents disciplin, t.ex. Volt's krav om "board first" innan YAML-generering.

**Identifierat kärnproblem:**
Iron Laws finns som **text**, inte som **tvingande struktur**. Detta betyder att en agent (särskilt Volt) kan generera kod som inte matchar den fysiska hårdvaran — felaktig GPIO-pin, fel board för uppgiften, eller pin-konflikter mellan komponenter.

**För en nybörjare:**
Den värsta besvikelsen är att aurora skill **lägger in fel portar i koden**. Detta resulterar i:
- Sensor som inte fungerar
- Skadad hårdvara
- Timmar bortkastade på felsökning
- Övergivet projekt

**Designens mål:**
Garantera att aurora skill levererar **korrekt kod oavsett användare**, genom systemisk validering före generering.

---

## 2. Nuvarande tillstånd

### Vad som finns idag

- `aurora/SKILL.md` — routing och Iron Laws för 21 agenter
- `aurora/souls/volt.md` — Volt's Iron Laws (board first, wiring diagram, calibration, power budget, troubleshooting)
- `aurora/references/platform-versions.md` — HA + ESPHome version info
- `aurora/references/workflows.md` — multi-skill workflow-mallar
- `esphome/references/pinouts.md` — GPIO-pinouts för 9 ESP-chip-familjer (markdown + ASCII)
- `esphome/references/boards.md` — board-information

### Identifierade luckor

1. **Pin-data är inte machine-readable** — pinouts.md är markdown/ASCII, svår att parsa
2. **Aurora skill länkar inte till pin-data** — Volt vet inte att referensen finns
3. **Ingen validering före generering** — Volt litar på sin egen kunskap
4. **Endast pin-data, ingen capability-matrix** — Volt vet inte vilken board som har BLE/Thread/PSRAM
5. **Ingen sensor/komponent-databas** — pin-validering räcker inte, sensor-krav kan brista
6. **Inga conflict-checks mellan komponenter** — två komponenter på samma pin upptäcks inte
7. **Mönstret saknas för andra agenter** — Ada, Sage, River har samma risk

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
│   │   ├── bme680.json
│   │   └── ntc-thermistor.json
│   ├── moisture/
│   │   ├── capacitive-soil-v1.2.json
│   │   └── resistive-soil.json
│   ├── motion/
│   │   ├── pir-am312.json
│   │   └── radar-ld2410.json
│   ├── air-quality/
│   │   ├── mh-z19.json
│   │   └── scd40.json
│   ├── relays/
│   │   └── songle-srd-05vdc.json
│   └── displays/
│       ├── ili9341-tft.json
│       └── ssd1306-oled.json
│
├── validators/                      # Cross-agent validator-moduler
│   ├── pin-validator.md
│   ├── conflict-validator.md
│   ├── yaml-syntax-validator.md
│   ├── python-validator.md
│   ├── entity-id-validator.md
│   └── version-validator.md
│
└── project-snapshots/               # User project history
    └── (skapas runtime per projekt)
```

### 3.2 Board-profil JSON-schema (komplett täckning)

```json
{
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
    "strapping_conflict_warnings": [
      "GPIO 0 must be HIGH at boot — pull-up if used as input",
      "GPIO 45 must be LOW at boot — affects flash voltage",
      "GPIO 46 must be LOW at boot — affects download mode"
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

### 3.3 Komponent-profil JSON-schema

```json
{
  "component_id": "dht22",
  "display_name": "DHT22 / AM2302",
  "type": "temperature_humidity",
  "category": "environment",
  "protocol": "single_wire_digital",

  "pin_requirements": {
    "count": 1,
    "type": "digital_io",
    "adc_required": false,
    "input_only_ok": false,
    "strapping_pin_ok": false,
    "5v_tolerant_required": false,
    "interrupt_capable_required": false
  },

  "external_components": {
    "pullup_resistor": {"value_ohm": 4700, "required": true},
    "decoupling_cap": null
  },

  "power": {
    "voltage": 3.3,
    "current_ma": 2.5,
    "current_sleep_ua": 50
  },

  "limitations": {
    "min_read_interval_s": 2,
    "operating_temp_c": "-40 to +80",
    "humidity_range": "0-100%",
    "accuracy_temp_c": "±0.5",
    "accuracy_humidity": "±2-5%"
  },

  "calibration": {
    "required": false,
    "type": null
  },

  "esphome": {
    "platform": "dht",
    "min_version": "2022.1.0",
    "config_template": "templates/dht22.yaml"
  },

  "datasheet_url": "https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf"
}
```

### 3.4 Volt's nya validerings-workflow

```
INPUT: Användarens projekt-krav (sensor, BLE, batteri, voice, etc.)

STEG 1 — Kravanalys
├── Identifiera behov: BLE? Battery? Voice? Camera? Matter?
└── Sätt capability filters

STEG 2 — Board-rekommendation
├── Läs alla *.json i aurora/references/boards/
├── Filtrera mot capability filters
├── Filtrera bort deprecated boards (varna om användare insisterar)
└── Föreslå 2-3 lämpliga boards med trade-offs

STEG 3 — Användaren väljer board
└── Bekräftelse + load board-profil

STEG 4 — Komponent-validering
├── För varje sensor/komponent: ladda components/*.json
├── Verifiera pin_requirements matchar board.gpio
├── Verifiera power-krav passar board
└── Verifiera ESPHome-version stöder komponenten

STEG 5 — Pin-allokering
├── Föreslå GPIO från board.gpio.valid_pins
├── Undvik strapping_pins, reserved_for_usb, psram_blocks_gpio
├── Använd i2c_default / spi_default för bus-protokoll
└── Reservera pinnar per komponent

STEG 6 — Conflict-validering (validators/conflict-validator.md)
├── Pin-collision check: Två komponenter på samma pin (ej I2C/OneWire)?
├── Bus-sharing check: I2C-adresser unika?
├── Strapping-conflict: Komponent på 0/3/45/46 utan korrekt pull?
├── USB-conflict: 19/20 + USB CDC aktiv?
├── PSRAM-conflict: 26-32 + PSRAM aktiv?
├── Voltage-mismatch: 5V komponent på 3.3V-only pin?
└── ADC-conflict: ADC2 + WiFi (S2/C3 specific)?

STEG 7 — Version-validering (validators/version-validator.md)
├── ESPHome ≥ minimum för alla features?
├── Board stöder valt framework (arduino vs esp-idf)?
└── Chip-revision OK?

STEG 8 — YAML-generering (endast om STEG 1-7 ✓)
├── Generera ESPHome YAML
├── Generera ASCII wiring diagram (Iron Law 2)
├── Generera calibration procedure om sensor kräver (Iron Law 3)
├── Generera troubleshooting med faktiska entity IDs (Iron Law 5)
└── Spara project-snapshot

OUTPUT: 
├── ✅ Komplett, validerad YAML + diagram + docs
└── ❌ Tydligt felmeddelande med förklaring och förslag
```

### 3.5 Retroactive YAML Validation

Volt får en ny förmåga: validera **befintlig** YAML.

```
Användare: *klistrar in YAML* "Funkar det här?"
→ Volt parsar YAML
→ Identifierar board + alla GPIO + alla komponenter
→ Kör STEG 4-7 i validerings-workflow
→ Output:
  ✅ "Allt ser korrekt ut"
  ⚠️ "Rad 23: GPIO 19 används men USB är aktiverat — konflikt"
  ❌ "Rad 45: GPIO 49 finns inte på ESP32-S3 (max 48)"
```

### 3.6 Tiered Error Messages för Nybörjare

Strukturerad feedback i 3 lager:

```
❌ Problem (kort):
GPIO 19 kan inte användas på den här boarden

📚 Förklaring (medium):
ESP32-S3 har inbyggd USB-stöd som använder GPIO 19 och 20.
Om du använder dessa pinnar för en sensor, slutar USB att fungera.

🔧 Lösning (konkret):
Använd GPIO 8 istället — den är ledig och passar för din DHT22.

💡 Djupare (för den som vill veta):
USB-OTG-protokollet använder differentiella signaler D+/D-
mappade till GPIO 19/20. Du kan stänga av USB i config med
'usb_cdc: false', men då tappar du serial debug.
```

### 3.7 Cross-Agent Validation Pattern

Samma validation-principer för alla agenter:

| Agent | Validator-moduler | Resurs-bibliotek |
|-------|-------------------|-------------------|
| **Volt** | pin, conflict, version | boards/, components/ |
| **Ada** | python-syntax, async-correctness, entity-id | (HA Python API spec) |
| **Sage** | yaml-syntax, entity-id, version | (HA YAML schema) |
| **River** | node-red-syntax, version | (Node-RED nod-namn) |
| **Mira** | python-syntax, llm-config | (LLM provider specs) |
| **Atlas** | api-endpoint, secrets-isolation | (API catalog) |
| **Iris** | lovelace-schema, card-types | (Lovelace specs) |

Skapa shared moduler i `aurora/references/validators/` så validering är **konsekvent** över alla agenter.

### 3.8 Iron Law Test Suite

För varje agent: explicit test-suite som verifierar att Iron Laws faktiskt följs.

```
aurora/tests/
├── volt/
│   ├── test-wiring-diagram-present.md
│   ├── test-calibration-procedure.md
│   ├── test-board-confirmed-before-yaml.md
│   ├── test-pin-validity.md
│   └── test-no-conflicts.md
├── ada/
│   ├── test-dt-util-not-datetime.md
│   ├── test-aiohttp-not-requests.md
│   └── test-json-serializable.md
├── sage/
│   ├── test-yaml-syntax-valid.md
│   └── test-entity-id-format.md
└── (osv för alla agenter)
```

Agent-output **rejected** om något test failar. Test-suite körs som del av agent's interna workflow.

### 3.9 User Project History

Persistens av användarens projekt mellan sessioner:

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

Sparas i `aurora/references/project-snapshots/{project_id}.json`.

Nästa session kan Aurora fråga: *"Vill du fortsätta på Vardagsrum sensor?"*

### 3.10 Lifecycle/Deprecation Warnings

Board-profiler har `lifecycle.status`:
- `active` — rekommenderas för nya projekt
- `legacy` — fungerar fortfarande, men nyare alternativ finns
- `deprecated` — varna användaren och rekommendera successor
- `obsolete` — blockera helt, kräv explicit override

Exempel:
```json
"lifecycle": {
  "status": "deprecated",
  "since": "2024",
  "reason": "ESP8266 saknar BLE, Thread, Matter. Välj ESP32-C3 för nya projekt.",
  "successor": "esp32-c3-mini"
}
```

Volt's output vid val av deprecated board:
> ⚠️ ESP8266 D1 Mini är ett legacy-val.
> 
> Anledning: ESP8266 saknar BLE, Thread och Matter. För nya projekt
> rekommenderar jag ESP32-C3 Mini — billigare, mer features.
> 
> Vill du fortsätta med D1 Mini ändå, eller byter vi till C3?

---

## 4. Implementeringsplan (faser)

### Fas 1 — Foundation Data
1. Konvertera `esphome/references/pinouts.md` till JSON-profiler för 9 chip-familjer
2. Skapa initial set av 10 vanliga sensor-profiler
3. Skriv board-profil JSON-schema dokumentation
4. Skriv komponent-profil JSON-schema dokumentation

### Fas 2 — Validation-modulerna
1. Skriv `validators/pin-validator.md`
2. Skriv `validators/conflict-validator.md`
3. Skriv `validators/version-validator.md`
4. Skriv `validators/yaml-syntax-validator.md`
5. Skriv `validators/python-validator.md`
6. Skriv `validators/entity-id-validator.md`

### Fas 3 — Volt's integration
1. Uppdatera `aurora/souls/volt.md` med nya Iron Laws (board capability filtering, validation workflow)
2. Uppdatera `aurora/SKILL.md` med referens till boards/ och components/
3. Lägg till Iron Law 6: "Validate before generating"
4. Skapa Volt's test-suite i `aurora/tests/volt/`

### Fas 4 — Smart Home & Special boards
1. Lägg till Shelly Plus 1, Plus 2PM
2. Lägg till Sonoff Basic R3, Mini R3
3. Lägg till LilyGo T-Display S3, M5Stack Atom, Heltec WiFi LoRa
4. Lägg till RP2040 Pico, RP2350 Pico 2

### Fas 5 — Andra agenter får validation-pattern
1. Ada: validation före Python-output (test-suite + validators)
2. Sage: validation före YAML-output (test-suite + validators)
3. River: validation före flow-output (test-suite + validators)
4. Mira, Atlas, Iris: samma mönster

### Fas 6 — Avancerade features
1. Retroactive YAML validation
2. Tiered error message-system
3. Project snapshots
4. Lifecycle warnings

---

## 5. Förväntat resultat

### Före lösningen

> Nybörjare: "Jag vill bygga en bluetooth-proxy"
> → Volt: "Använd ESP32-S2"
> → Användare köper, flashar, fungerar inte (S2 har ingen BLE)
> → ❌ Besvikelse, projekt övergivet

### Efter lösningen

> Nybörjare: "Jag vill bygga en bluetooth-proxy"
> → Volt filtrerar: capability `bluetooth_proxy: true`
> → Volt: "ESP32-C3 (billigast, BLE 5.0) eller ESP32-S3 (om voice senare)"
> → Användaren väljer C3
> → Volt laddar `esp32-c3-mini.json` + komponent-profiler
> → Volt validerar varje GPIO mot valid_pins
> → Volt kollar conflicts, version, syntax
> → Volt genererar YAML + diagram + troubleshooting + calibration
> → ✅ Användare flashar, bluetooth-proxy fungerar

---

## 6. Success Criteria

- ✅ Volt kan **inte** generera YAML med GPIO som inte finns på vald board
- ✅ Volt kan **inte** rekommendera board som saknar krävd capability
- ✅ Volt **upptäcker** pin-konflikter mellan komponenter före output
- ✅ Volt **varnar** för deprecated boards med tydlig successor
- ✅ Felmeddelanden är **förståeliga för nybörjare** (3 lager: problem/förklaring/lösning)
- ✅ Samma validation-pattern fungerar för Ada, Sage, River, Mira, Atlas, Iris
- ✅ Iron Law Test Suite kör automatiskt och fail på regression

---

## 7. Out of scope för denna version

- Hardware automation (BOM-generering, PCB-layout)
- Multi-board topology validation (3+ ESP32 som pratar med varandra)
- Pricing/availability data
- ESPHome custom components-kompatibilitet (förutom officiella)
- Interactive board selector UI (CLI-only för v1)

---

## 8. Risker och mitigation

| Risk | Sannolikhet | Påverkan | Mitigation |
|------|-------------|----------|------------|
| JSON-databasen blir inaktuell | Hög | Hög | Versioning + `last_verified` field + audit-process |
| Volt ignorerar validering | Låg | Kritisk | Test-suite + Iron Law 6 explicit |
| Nybörjare överväldigas av val | Medel | Medel | Tiered messages + "rekommenderat val" |
| Maintenance overhead | Medel | Medel | Templater + bidragsguide för community |
| Konflikt mellan board+komponent edge cases | Medel | Hög | Conflict-validator + manuella reviews |

---

## 9. Nästa steg

1. Användare granskar och godkänner detta spec
2. Vid godkännande: transition till `writing-plans` skill för detaljerad implementeringsplan
3. Implementation per fas, med test-coverage per fas

---

*Spec skapad: 2026-05-13. Status: Draft for review.*
