# ESPHome Product Development Guide

From idea to finished product — how to design professional Home Assistant devices with ESPHome.

## Table of Contents

1. [Development Lifecycle](#development-lifecycle)
2. [Phase 1: Concept & Requirements](#phase-1-concept--requirements)
3. [Phase 2: Component Selection](#phase-2-component-selection)
4. [Phase 3: Prototyping](#phase-3-prototyping)
5. [Phase 4: Firmware Development](#phase-4-firmware-development)
6. [Phase 5: Testing & Validation](#phase-5-testing--validation)
7. [Phase 6: Enclosure & Industrial Design](#phase-6-enclosure--industrial-design)
8. [Phase 7: Production & Distribution](#phase-7-production--distribution)
9. [BOM Template](#bom-template)
10. [Cost Estimation](#cost-estimation)

## Project Output Structure

When developing a product, create all files inside a named project folder in the user's
current working directory. This keeps everything organized and easy to find.

```
my-product/                          ← Named after the product
├── README.md                        ← Product overview, specs, how to build
├── firmware/
│   ├── my-product.yaml              ← ESPHome configuration
│   └── secrets.yaml.example         ← Template for user's credentials
├── hardware/
│   ├── bom.md                       ← Bill of materials with component links
│   ├── schematic-notes.md           ← Circuit description, pin mapping
│   └── wiring-diagram.md            ← Connection guide (ASCII or description)
├── production/
│   ├── test-plan.md                 ← Test matrix and pass criteria
│   └── flash-instructions.md        ← How to flash firmware
└── enclosure/
    └── requirements.md              ← Dimensions, IP rating, mounting
```

After creating files, always print a summary:
```
Project created: my-product/
├── firmware/my-product.yaml      (ESPHome config — ready to flash)
├── hardware/bom.md               (12 components, est. $8.50/unit)
├── hardware/schematic-notes.md   (pin mapping, I2C addresses)
├── production/test-plan.md       (8 test cases)
└── README.md                     (product overview)

Next steps:
1. Review the BOM and order components
2. Wire prototype on breadboard using schematic-notes.md
3. Flash firmware: esphome run firmware/my-product.yaml
```

For simpler requests (just a YAML config, not full product), skip the project folder
and save directly to the current directory as before.

## Development Lifecycle

```
Idea → Requirements → Component Selection → Breadboard Prototype
  → ESPHome Firmware → Perfboard/DevKit Test → PCB Design
  → 3D Print Enclosure → Validation → Small Batch → Production
```

Each phase has a **gate** — don't proceed until the gate criteria are met.

## Phase 1: Concept & Requirements

Define the product before touching hardware.

### Requirements Checklist

| Category | Questions |
|----------|-----------|
| **Function** | What does it sense/control? What data does it produce? |
| **Environment** | Indoor/outdoor? Temperature range? Humidity? Dust? |
| **Power** | Mains? Battery? Solar? PoE? What's the power budget? |
| **Connectivity** | WiFi? Thread? Zigbee? BLE? Range requirements? |
| **Size** | Max dimensions? Wall-mount? DIN rail? Portable? |
| **Certification** | CE? FCC? RoHS? (required for commercial sale in EU/US) |
| **Volume** | 1-10 (personal), 10-100 (small batch), 100+ (production)? |
| **Price target** | BOM cost per unit? Retail price? |
| **HA integration** | Which entity types? What dashboard cards? |

### Product Brief Template

```markdown
# Product: [Name]

## Purpose
[One sentence: what problem does this solve?]

## Specifications
- Sensors: [list with accuracy requirements]
- Actuators: [list with power ratings]
- Connectivity: WiFi / Thread / Zigbee / BLE
- Power: [source, voltage, estimated consumption]
- Environment: IP[xx], [temp range]
- Target BOM cost: $[xx]

## User Stories
1. As a homeowner, I want to [action] so that [benefit]
2. As a Home Assistant user, I want [entity type] so that [automation]

## Constraints
- [Size, budget, regulatory, timeline]
```

### Gate 1: Proceed when you have clear requirements and a feasible concept.

## Phase 2: Component Selection

See `hardware-selection.md` for detailed component recommendations.

### Selection Process

1. **Start with the MCU** — determines available GPIO, protocols, flash/RAM
2. **Select sensors/actuators** — match to requirements, check ESPHome support
3. **Design power supply** — voltage regulation, battery management if needed
4. **Plan connectivity** — antenna type, range, protocol
5. **List external circuits** — level shifters, protection, drivers

### Key Decision: MCU Selection

| If you need... | Use |
|----------------|-----|
| General purpose, WiFi, proven | ESP32 (WROOM or WROVER) |
| Camera, USB, voice, PSRAM | ESP32-S3 |
| Smallest, cheapest WiFi | ESP32-C3 |
| Thread/Zigbee + WiFi 6 | ESP32-C6 |
| Thread/Zigbee only (no WiFi) | ESP32-H2 |
| High-performance, displays | ESP32-P4 |
| Ultra-low cost, Tuya replacement | BK7231N (LibreTiny) |
| Legacy, very simple | ESP8266 (not recommended for new products) |

### Gate 2: Proceed when BOM is complete and all components have ESPHome support confirmed.

## Phase 3: Prototyping

### Stage 3a: Breadboard

- Wire components on breadboard with development board
- Write initial ESPHome YAML
- Verify sensor readings, actuator control, connectivity
- Measure power consumption with USB meter or INA219

**Tools needed:** Breadboard, jumper wires, multimeter, USB power meter

### Stage 3b: Perfboard / Protoboard

- Solder components for reliable testing
- Test for 48+ hours continuous operation
- Verify OTA updates work reliably
- Test WiFi range with intended enclosure material

### Stage 3c: Custom PCB (if volume > ~20 units)

- Design schematic in KiCad or EasyEDA
- Key considerations:
  - Keep antenna area clear of copper (ground plane cutout)
  - Add test points for UART (TX, RX, GND) for debugging
  - Add programming header (USB-C or tag-connect)
  - Decoupling capacitors: 100nF on every VCC pin, 10µF on regulator output
  - Route I2C/SPI traces short and direct
  - Add ESD protection on exposed connectors
- Order prototype PCBs (JLCPCB, PCBWay — $2-5 for 5 boards)
- Assemble and test

### Gate 3: Prototype works reliably for 48+ hours, OTA works, sensors accurate.

## Phase 4: Firmware Development

### ESPHome Configuration Strategy

```yaml
# Use substitutions for product variants
substitutions:
  device_name: "my-product"
  friendly_name: "My Product"
  hw_version: "1.0"
  sw_version: "2024.1.0"

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}
  project:
    name: "mycompany.my-product"
    version: ${sw_version}
  on_boot:
    priority: 600
    then:
      - logger.log: "Hardware: ${hw_version}, Firmware: ${sw_version}"
```

### Production Firmware Features

- **`project:` block** — enables device discovery and firmware updates via HA
- **`dashboard_import:`** — lets users adopt device without manual YAML
- **`esp32_improv:`** or **`improv_serial:`** — WiFi provisioning via Bluetooth/serial
- **Fallback AP** — always include `ap:` block for recovery
- **Safe mode** — enables OTA recovery from bad configs
- **Status LED** — visual feedback for WiFi/API connection status

### Firmware Template for Products

```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    ssid: "${device_name}-fallback"
    password: "fallback123"

captive_portal:

api:
  encryption:
    key: !secret api_key

ota:
  platform: esphome
  password: !secret ota_password

logger:
  level: INFO  # DEBUG for development, INFO for production

button:
  - platform: restart
    name: "Restart"
  - platform: safe_mode
    name: "Safe Mode"

sensor:
  - platform: wifi_signal
    name: "WiFi Signal"
    update_interval: 60s
  - platform: uptime
    name: "Uptime"
```

### Gate 4: Firmware is feature-complete, OTA-updateable, and has fallback recovery.

## Phase 5: Testing & Validation

### Test Matrix

| Test | Method | Pass Criteria |
|------|--------|---------------|
| Sensor accuracy | Compare to reference instrument | Within spec sheet tolerance |
| Power consumption | USB meter or INA219 | Under power budget |
| WiFi range | Move device away from AP | Reliable at intended distance |
| OTA update | Push 10 updates in sequence | All succeed without brick |
| Recovery | Corrupt config, reboot | Fallback AP activates |
| Thermal | Run 24h in target environment | Components within rated temp |
| Long-term | Run 7+ days continuously | No crashes, memory leaks, drift |
| HA integration | Add to HA, create automations | All entities work correctly |

### Power Consumption Targets

| Mode | ESP32 typical | Target for battery |
|------|---------------|--------------------|
| Active WiFi | 100-240 mA | Minimize active time |
| Modem sleep | 20-30 mA | Default between readings |
| Light sleep | 2-5 mA | For battery devices |
| Deep sleep | 10-150 µA | Between long intervals |

### Gate 5: All tests pass, no crashes in 7-day soak test.

## Phase 6: Enclosure & Industrial Design

See `enclosures-manufacturing.md` for detailed guidance.

### Quick Decisions

| Factor | Hobby/Small batch | Production |
|--------|-------------------|------------|
| Method | 3D print (FDM/SLA) | Injection molding |
| Cost per unit | $2-10 | $0.50-2 (after $2000+ tooling) |
| IP rating | Gaskets + silicone | Ultrasonic welding |
| Finish | Sand + paint/spray | Textured mold |
| Time | 1-4 hours print | 30 seconds per unit |

### Gate 6: Enclosure fits, accessible for assembly, passes environmental requirements.

## Phase 7: Production & Distribution

### Small Batch (10-100 units)

1. Order PCBs with SMT assembly (JLCPCB, PCBWay)
2. Hand-solder through-hole components
3. Flash firmware via USB
4. 3D print enclosures
5. Assemble and test each unit
6. Package and ship

### Medium Batch (100-1000 units)

1. Order fully assembled PCBs (turnkey)
2. Injection-molded enclosures (or high-volume 3D print service)
3. Flash firmware via UART test jig
4. Automated testing with script
5. CE/FCC testing at accredited lab ($3000-8000)
6. Distribution via website or Tindie/Crowd Supply

### Gate 7: Units assembled, tested, certified (if commercial), ready to ship.

## BOM Template

When building a BOM, use WebSearch to look up current prices from LCSC/Mouser/DigiKey.
See `hardware-selection.md` → "Live Price Lookup" for search query formats.

```
| # | Component | Part Number | Specs | Qty | Unit Cost | Source |
|---|-----------|-------------|-------|-----|-----------|--------|
| 1 | MCU Module | ESP32-C3-MINI-1 | 4MB flash, WiFi+BLE | 1 | $1.50 | LCSC |
| 2 | Temp Sensor | BME280 | ±1°C, ±3% RH, I2C | 1 | $2.80 | LCSC |
| 3 | Regulator | AMS1117-3.3 | 3.3V, 1A | 1 | $0.10 | LCSC |
| 4 | USB-C | TYPE-C-31-M-12 | Power + data | 1 | $0.15 | LCSC |
| 5 | Caps | 100nF 0402 | Decoupling | 4 | $0.01 | LCSC |
| 6 | Caps | 10µF 0805 | Bulk | 2 | $0.02 | LCSC |
| 7 | Resistors | 10kΩ 0402 | I2C pullup | 2 | $0.01 | LCSC |
| 8 | LED | 0603 Green | Status | 1 | $0.02 | LCSC |
| 9 | PCB | Custom 2-layer | 50x30mm, 1.6mm | 1 | $0.50 | JLCPCB |
| 10| Enclosure | Custom 3D print | PLA/PETG | 1 | $1.50 | In-house |
|   | **TOTAL** | | | | **~$6.60** | |
```

## Cost Estimation

### BOM Cost Scaling

| Volume | Typical BOM multiplier | Example ($6.60 BOM) |
|--------|------------------------|---------------------|
| 1-10 | 2-3x (dev board + breakouts) | $15-20 |
| 10-50 | 1.5x (custom PCB, hand assembly) | $10 |
| 50-200 | 1.2x (SMT assembly) | $8 |
| 200-1000 | 1.0x (turnkey, volume pricing) | $6.60 |
| 1000+ | 0.7-0.8x (bulk negotiation) | $5 |

### Total Product Cost

```
BOM cost + Assembly labor + Enclosure + Packaging + Certification amortized
+ Shipping + Returns/warranty buffer (5%) = Unit cost

Retail price = Unit cost × 2.5-4x (for margin + distribution)
```

### Example: Air Quality Monitor

| Item | Cost (100 units) |
|------|------------------|
| BOM (ESP32-C3 + BME680 + PMS5003 + SGP41) | $18 |
| PCB assembly | $3 |
| Enclosure (3D printed PETG) | $4 |
| Packaging | $2 |
| Testing + QC | $1 |
| **Unit cost** | **$28** |
| CE/FCC amortized | $50 |
| **Total unit cost** | **$78** |
| **Retail price (3x)** | **$84** |

---

For component recommendations, see `hardware-selection.md`.
For enclosure and manufacturing details, see `enclosures-manufacturing.md`.
