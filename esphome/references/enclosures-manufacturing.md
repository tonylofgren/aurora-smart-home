# Enclosures, PCB Design & Manufacturing Guide

From prototype to production — enclosures, PCB design with KiCad, certification, and manufacturing.

## Table of Contents

1. [Enclosure Design](#enclosure-design)
2. [IP Ratings](#ip-ratings)
3. [PCB Design with KiCad](#pcb-design-with-kicad)
4. [PCB Manufacturing](#pcb-manufacturing)
5. [Certification (CE/FCC/RoHS)](#certification-cefccrohs)
6. [Manufacturing at Scale](#manufacturing-at-scale)
7. [Quality Control](#quality-control)

## Enclosure Design

### Methods by Volume

| Volume | Method | Cost/unit | Tooling | Lead Time | Quality |
|--------|--------|-----------|---------|-----------|---------|
| 1-20 | FDM 3D print | $2-10 | $0 | 1-4 hours | Functional |
| 20-100 | SLA/MJF 3D print | $5-15 | $0 | 1-2 days | Good finish |
| 100-500 | 3D print farm (JLCPCB, Craftcloud) | $3-8 | $0 | 5-10 days | Consistent |
| 500-2000 | Silicone mold + resin cast | $2-5 | $200-500 | 2-4 weeks | Good |
| 2000+ | Injection molding | $0.30-2 | $2000-8000 | 4-8 weeks | Professional |

### 3D Printing for Prototypes and Small Batches

**FDM Materials:**

| Material | Strength | Heat Resist | UV Resist | Ease | Best For |
|----------|----------|-------------|-----------|------|----------|
| PLA | Medium | 60°C | Poor | Easy | Indoor prototypes |
| PETG | Good | 80°C | Good | Medium | Indoor products |
| ASA | Good | 100°C | Excellent | Medium | Outdoor enclosures |
| ABS | Good | 100°C | Fair | Hard | Functional parts |
| Nylon (PA) | Excellent | 110°C | Good | Hard | Mechanical stress |

**Recommendation:** PETG for indoor products, ASA for outdoor.

**Design Rules for 3D Printed Enclosures:**
- Wall thickness: minimum 1.5mm (FDM), 1mm (SLA)
- Snap-fit tabs: 0.3mm interference, 45° lead-in angle
- Screw bosses: 6mm OD for M3 heat-set inserts ($0.05 each)
- PCB mounting: M2.5 standoffs, 3mm clearance under PCB
- Ventilation: Slot arrays (not round holes) for strength
- Text/logos: Emboss 0.5mm or deboss 0.3mm
- Tolerances: ±0.2mm (FDM), ±0.1mm (SLA)

### Off-the-Shelf Enclosures

For faster time-to-market, consider pre-made enclosures:

| Enclosure | Size (mm) | IP Rating | Price | Source |
|-----------|-----------|-----------|-------|--------|
| Hammond 1551-series | 35x35x20 to 80x80x40 | IP54 | $2-5 | Mouser |
| Bud Industries | Various | IP65 | $3-8 | Mouser |
| Gainta G-series | Various | IP65 | $2-6 | TME |
| Sonoff IP66 box | 100x68x50 | IP66 | $3 | AliExpress |
| DIN rail module | Various | — | $1-3 | AliExpress |

## IP Ratings

| Rating | Protection | Use Case |
|--------|-----------|----------|
| IP20 | Touch protection only | Indoor, dry |
| IP44 | Splash-proof | Bathroom, covered outdoor |
| IP54 | Dust-protected, splash | General outdoor |
| IP65 | Dust-tight, water jet | Outdoor, rain |
| IP67 | Dust-tight, immersion 1m | Underground, flooding risk |
| IP68 | Dust-tight, continuous submersion | Pool, irrigation |

### Achieving IP Ratings

| Rating | Method | Additional Cost |
|--------|--------|-----------------|
| IP44 | Tight-fitting lid, cable glands | $0.50 |
| IP54 | Foam gasket in lid groove | $0.30 |
| IP65 | Silicone gasket, M12 cable glands | $1.00 |
| IP67 | O-ring seal, potted cable entries | $2.00 |
| IP68 | Epoxy potting entire PCB | $3.00 |

**Cable glands:** PG7 (3-6.5mm cable) $0.10, PG9 (4-8mm) $0.10, PG11 (5-10mm) $0.12

## PCB Design with KiCad

### KiCad Workflow

```
Schematic (Eeschema) → Footprint assignment → PCB layout (Pcbnew) → Gerber export → Order
```

### Schematic Checklist for ESP32 Products

1. **MCU module** (use module, not bare chip — saves layout complexity)
   - Decoupling: 100nF + 10µF on each VCC
   - EN pin: 10kΩ pullup + 100nF to GND (RC delay for power-on reset)
   - Boot pin (GPIO0): 10kΩ pullup (pulled low only for flashing)
   - UART: TX/RX accessible for debugging

2. **Power supply**
   - Input protection: Schottky diode or P-MOSFET reverse polarity
   - Regulator: Input and output capacitors per datasheet
   - LED: Power indicator (green, 1kΩ resistor for 3.3V)

3. **Sensors** (per sensor datasheet)
   - I2C: Check if pullups needed (many breakouts include them)
   - Decoupling: 100nF close to sensor VCC
   - Bypass: 10µF if sensor has high transient current

4. **Actuators**
   - Relay: Flyback diode (1N4148) across coil
   - MOSFET: Gate resistor (100Ω) + pulldown (10kΩ)
   - Motor: Decoupling + TVS protection

5. **Connectors**
   - USB-C: ESD protection (USBLC6-2)
   - External GPIO: TVS diodes
   - Programming: JST-SH or Tag-Connect pads

### PCB Layout Rules

**Antenna clearance (critical!):**
```
┌──────────────────────────────┐
│          ESP32 Module         │
│  ┌─────┐                     │
│  │ MCU │    ▓▓▓▓▓▓▓▓▓ ←── Antenna
│  └─────┘    ▓▓▓▓▓▓▓▓▓       │
│             ▓▓▓▓▓▓▓▓▓       │
├─────────────┼───────────────┤
│ Components  │  NO copper    │ ← Keep this area clear
│ OK here     │  NO traces    │   (both layers!)
│             │  NO GND plane │
└─────────────┴───────────────┘
```

**General rules:**
- 2-layer PCB is sufficient for most ESPHome products
- Trace width: 0.25mm (signal), 0.5mm+ (power), 1mm+ (high current)
- Via size: 0.3mm drill, 0.6mm pad (standard)
- Ground plane on bottom layer, pour on both layers
- Keep I2C/SPI traces under 10cm
- Route UART away from high-speed signals
- Test points: 1mm pads for multimeter probes

### KiCad Libraries for ESP32

| Library | Contents | Source |
|---------|----------|--------|
| espressif-kicad | Official ESP32 symbols + footprints | GitHub: espressif/kicad-libraries |
| JLCPCB parts | Footprints matching JLCPCB's SMT library | easyeda2kicad converter |
| SnapEDA | Individual component models | snapeda.com |
| Ultra Librarian | Component models with 3D | ultralibrarian.com |

### EasyEDA as Alternative

If KiCad feels complex, EasyEDA (free, web-based) integrates directly with JLCPCB:
- LCSC component library built in
- One-click PCB ordering with SMT assembly
- Export to KiCad format if needed later

## PCB Manufacturing

### PCB-Only (you solder)

| Service | Min. 5 boards | Layers | Lead Time | Notes |
|---------|---------------|--------|-----------|-------|
| JLCPCB | $2 + $3 ship | 1-6 | 3-7 days | Cheapest, reliable |
| PCBWay | $5 + $5 ship | 1-6 | 3-7 days | Good quality, flex PCBs |
| OSH Park | $5/sq inch | 2-4 | 12 days | US-made, purple |
| Aisler | €6 + ship | 2-4 | 5-10 days | EU-based, fast EU ship |
| ALLPCB | $0 (promo) | 2 | 5-7 days | Regular free promos |

### PCB + SMT Assembly (they solder SMD components)

| Service | Setup Cost | Per-board | Min Qty | Lead Time |
|---------|-----------|-----------|---------|-----------|
| JLCPCB SMT | $8 stencil | $0.004/joint | 5 | 5-10 days |
| PCBWay SMT | $10 stencil | $0.005/joint | 5 | 5-10 days |
| MacroFab | $0 | $10+ per board | 1 | 10-15 days |
| Elecrow | $10 | $0.004/joint | 10 | 7-14 days |

**Tip:** JLCPCB's "Economic PCBA" option is cheapest for small runs. Use their "Basic Parts" (common resistors, caps, ICs) for lowest cost — "Extended Parts" have a $3/unique part fee.

### Design for Assembly (DFA)

- Use one side only for SMD (reduces cost)
- Prefer 0402 or 0603 resistors/caps (standard for JLCPCB)
- Use JLCPCB basic parts where possible
- Add fiducial marks (3 on board) for pick-and-place alignment
- Panel boards if < 50x50mm for easier handling

## Certification (CE/FCC/RoHS)

### When Do You Need Certification?

| Scenario | CE (EU) | FCC (US) | Notes |
|----------|---------|----------|-------|
| Personal use | No | No | |
| Gift/prototype | No | No | |
| Selling in EU | Yes | — | Required for commercial sale |
| Selling in US | — | Yes | Required for commercial sale |
| Selling in both | Yes | Yes | |
| Selling on Amazon/Etsy | Yes or Yes | Yes or Yes | Marketplace policies require it |

### Using Pre-Certified Modules

**This is the most important cost-saving tip:** ESP32 modules (WROOM, MINI, S3-WROOM) are already FCC/CE certified by Espressif. If you use the module without modifying the antenna or RF circuitry, you can reference their certification — this dramatically reduces your testing costs.

**Requirements for "modular" certification approach:**
- Use the exact certified module (not bare chip)
- Do not modify antenna or RF circuit
- Follow module datasheet for antenna clearance
- Include the module's FCC ID in your product label
- Still need EMC/safety testing for the rest of your circuit

### Certification Costs

| Test | Typical Cost | Lead Time | Notes |
|------|-------------|-----------|-------|
| EMC pre-scan | $500-1000 | 1 day | Find issues before formal test |
| CE EMC (EN 55032/35) | $2000-4000 | 2-3 weeks | Required for EU |
| CE Safety (LVD, if mains) | $1500-3000 | 2-3 weeks | Only for mains-powered |
| CE RED (radio) | $1500-3000 | 2-3 weeks | Usually covered by module cert |
| FCC Part 15 | $2000-5000 | 2-4 weeks | Can reference module FCC ID |
| RoHS declaration | $200-500 | Self-declaration possible | Based on component datasheets |
| **Total (typical)** | **$3000-8000** | **4-8 weeks** | |

### Reducing Certification Cost

1. **Use pre-certified WiFi/BLE module** (biggest savings — avoids RF testing)
2. **Low-voltage DC only** (avoid mains → skip LVD safety testing)
3. **EMC pre-scan first** ($500) — fix issues before paying for formal test
4. **Test one product, certify variants** — similar products can share test reports
5. **Self-declare RoHS** — based on component datasheets, no lab needed

### Documentation Required

- Technical file with schematics, PCB layout, BOM
- Risk assessment (basic for low-voltage products)
- Test reports from accredited lab (ILAC/ISO 17025)
- Declaration of Conformity (CE) — template available online
- User manual with safety information
- Product label with CE mark, FCC ID (module), model number

## Manufacturing at Scale

### Production Flow

```
Component sourcing → PCB + SMT assembly → Through-hole hand-solder
  → Firmware flashing → Functional test → Enclosure assembly
  → Final test → Packaging → Ship
```

### Firmware Flashing at Scale

**For 10-100 units:** USB-UART adapter + esptool.py script

```bash
# Flash one unit via serial
esptool.py --port /dev/ttyUSB0 write_flash 0x0 firmware.bin
```

**For 100+ units:** Test jig with pogo pins
- Design PCB pads for pogo pin contact (Tag-Connect TC2030 footprint)
- 3D print jig to align board
- Script auto-detects device, flashes, runs basic test
- Total flash + test time: ~30 seconds per unit

### Test Jig Design

```
┌─────────────────────┐
│   3D-printed cradle  │
│  ┌─────────────────┐ │
│  │  Pogo pins:     │ │
│  │  • 3V3 power    │ │
│  │  • GND          │ │
│  │  • TX (flash)   │ │
│  │  • RX (flash)   │ │
│  │  • GPIO0 (boot) │ │
│  │  • EN (reset)   │ │
│  └─────────────────┘ │
│  [Start Button]      │
└─────────────────────┘
```

### Automated Test Script

```python
#!/usr/bin/env python3
"""Production test script for ESPHome devices."""
import subprocess
import serial
import time

def test_device(port="/dev/ttyUSB0"):
    """Flash and test one unit."""
    # 1. Flash firmware
    subprocess.run([
        "esptool.py", "--port", port,
        "write_flash", "0x0", "firmware.bin"
    ], check=True)

    # 2. Wait for boot
    time.sleep(5)

    # 3. Check serial output for "WiFi connected"
    ser = serial.Serial(port, 115200, timeout=10)
    output = ser.read(2000).decode()
    assert "WiFi connected" in output, "WiFi failed"

    # 4. Check sensor readings
    assert "temperature:" in output, "Temp sensor not responding"

    print("PASS")
```

## Quality Control

### Incoming Inspection

- Check component reels against BOM (part numbers, values)
- Spot-check 5% of components with multimeter
- Verify PCB quality: solder mask, silkscreen, drill alignment

### In-Process QC

| Check | Method | Criteria |
|-------|--------|----------|
| Solder joints | Visual + magnifier | No cold joints, bridges, or voids |
| Power supply | Multimeter | 3.3V ±5% under load |
| Current draw | USB meter | Within expected range |
| WiFi | Scan from 5m away | RSSI > -70 dBm |
| Sensors | Compare to reference | Within datasheet tolerance |
| OTA update | Push test firmware | Completes in < 60 seconds |

### Final Test

Run automated test script on every unit:
1. Power on → LED lights
2. WiFi connects (< 15 seconds)
3. Sensors report valid data
4. OTA update succeeds
5. API connection from HA works

### Defect Rate Targets

| Volume | Acceptable defect rate |
|--------|------------------------|
| < 50 units | < 5% (manual QC) |
| 50-500 | < 2% |
| 500+ | < 1% (automated testing) |

---

For component recommendations, see `hardware-selection.md`.
For the full development lifecycle, see `product-development.md`.
