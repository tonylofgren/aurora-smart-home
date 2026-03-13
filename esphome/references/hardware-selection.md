# Hardware Selection Guide for ESPHome Products

Detailed component recommendations with prices, interfaces, and ESPHome compatibility.

## Table of Contents

1. [MCU Comparison](#mcu-comparison)
2. [Temperature & Humidity Sensors](#temperature--humidity-sensors)
3. [Air Quality Sensors](#air-quality-sensors)
4. [Motion & Presence Sensors](#motion--presence-sensors)
5. [Light Sensors](#light-sensors)
6. [Distance & Level Sensors](#distance--level-sensors)
7. [Power & Energy Sensors](#power--energy-sensors)
8. [Actuators & Drivers](#actuators--drivers)
9. [Power Supply Design](#power-supply-design)
10. [Communication & External Peripherals](#communication--external-peripherals)
11. [Connectors & Protection](#connectors--protection)
12. [Component Sourcing](#component-sourcing)

## MCU Comparison

### ESP32 Family

| Module | CPU | Flash | RAM | WiFi | BLE | Thread/Zigbee | USB | Price | ESPHome FW |
|--------|-----|-------|-----|------|-----|---------------|-----|-------|------------|
| ESP32-WROOM-32E | Dual Xtensa 240MHz | 4-16MB | 520KB | 802.11 b/g/n | 4.2 | No | No | $2.20 | Arduino/IDF |
| ESP32-WROVER-E | Dual Xtensa 240MHz | 4-16MB | 520KB+8MB PSRAM | 802.11 b/g/n | 4.2 | No | No | $2.80 | Arduino/IDF |
| ESP32-S3-WROOM-1 | Dual Xtensa 240MHz | 4-16MB | 512KB+8MB PSRAM | 802.11 b/g/n | 5.0 | No | USB OTG | $2.50 | Arduino/IDF |
| ESP32-C3-MINI-1 | Single RISC-V 160MHz | 4MB | 400KB | 802.11 b/g/n | 5.0 | No | USB Serial | $1.50 | Arduino/IDF |
| ESP32-C6-MINI-1 | Single RISC-V 160MHz | 4MB | 512KB | WiFi 6 | 5.0 | Yes | USB Serial | $2.00 | IDF only |
| ESP32-H2-MINI-1 | Single RISC-V 96MHz | 4MB | 320KB | No | 5.0 | Yes | USB Serial | $1.80 | IDF only |

### When to Use Which

| Use Case | Recommended MCU | Why |
|----------|-----------------|-----|
| General sensor device | ESP32-C3 | Cheapest, sufficient GPIO, small |
| Camera / display | ESP32-S3 | PSRAM for frame buffers, USB |
| Voice assistant | ESP32-S3 | I2S audio, PSRAM for models |
| Matter/Thread device | ESP32-C6 | Native Thread + WiFi 6 |
| Zigbee end device | ESP32-H2 or ESP32-C6 | Native Zigbee stack |
| Multi-sensor hub | ESP32 (WROOM) | Most GPIO, dual core |
| Battery device | ESP32-C3 or H2 | Lowest deep sleep current |
| Budget product | ESP32-C3 | $1.50, good enough for most |
| Legacy replacement | ESP8266 | Only if cost-critical at scale |

### Other Platforms

| Platform | Module | Price | Best For |
|----------|--------|-------|----------|
| RP2040 | Raspberry Pi Pico W | $6.00 | PIO peripherals, dual core |
| nRF52840 | Various | $3-5 | Zigbee, ultra-low power BLE |
| BK7231N | CB2S, WB2S | $0.80 | Tuya device replacement |
| RTL8720CF | W302 | $1.20 | Dual-band WiFi budget |

## Temperature & Humidity Sensors

| Sensor | Interface | Accuracy | Range | Price | I2C Addr | ESPHome Component | Best For |
|--------|-----------|----------|-------|-------|----------|-------------------|----------|
| **BME280** | I2C/SPI | ±1°C, ±3% RH | -40..85°C | $2.80 | 0x76/0x77 | `bme280_i2c` | General purpose, weather |
| **BME680** | I2C/SPI | ±1°C, ±3% RH + VOC | -40..85°C | $8.50 | 0x76/0x77 | `bme680_bsec` | Air quality + temp/hum |
| **SHT4x** | I2C | ±0.2°C, ±1.8% RH | -40..125°C | $3.50 | 0x44 | `sht4x` | High accuracy, fast |
| **SHT3x** | I2C | ±0.3°C, ±2% RH | -40..125°C | $2.50 | 0x44/0x45 | `sht3xd` | Good accuracy, common |
| **AHT20** | I2C | ±0.3°C, ±2% RH | -40..85°C | $0.80 | 0x38 | `aht10` | Budget, good enough |
| **DHT22** | Single-wire | ±0.5°C, ±2% RH | -40..80°C | $2.00 | GPIO | `dht` | Legacy, avoid for new |
| **DS18B20** | 1-Wire | ±0.5°C | -55..125°C | $1.00 | GPIO | `dallas_temp` | Waterproof probe, multi |
| **MCP9808** | I2C | ±0.25°C | -40..125°C | $1.50 | 0x18-0x1F | `mcp9808` | Precision temperature |
| **TMP117** | I2C | ±0.1°C | -55..150°C | $3.50 | 0x48-0x4B | `tmp117` | Lab-grade accuracy |

**Recommendation:** SHT4x for new products (best accuracy/price). BME280 if you also need pressure. AHT20 for budget.

## Air Quality Sensors

| Sensor | Measures | Interface | Price | ESPHome | Notes |
|--------|----------|-----------|-------|---------|-------|
| **SGP41** | VOC + NOx index | I2C (0x59) | $5.00 | `sgp4x` | Best VOC sensor, needs SHT4x for compensation |
| **SGP30** | eCO2 + TVOC | I2C (0x58) | $6.00 | `sgp30` | Older, use SGP41 for new designs |
| **SCD40/41** | True CO2 + T + RH | I2C (0x62) | $25/$35 | `scd4x` | Photoacoustic, very accurate CO2 |
| **MH-Z19B** | CO2 (NDIR) | UART | $15.00 | `mhz19` | Cheaper NDIR CO2, needs calibration |
| **SenseAir S8** | CO2 (NDIR) | UART/I2C | $25.00 | `senseair` | Professional-grade CO2 |
| **PMS5003** | PM1.0/2.5/10 | UART | $12.00 | `pmsx003` | Particulate matter, laser scattering |
| **PMS7003** | PM1.0/2.5/10 | UART | $15.00 | `pmsx003` | Thinner than PMS5003 |
| **SPS30** | PM1.0/2.5/4/10 | I2C/UART | $30.00 | `sps30` | Sensirion, self-cleaning fan |
| **BME680** | VOC (gas resistance) | I2C | $8.50 | `bme680_bsec` | Combined sensor, less accurate VOC |
| **ENS160** | eCO2 + TVOC + AQI | I2C (0x52/0x53) | $4.00 | `ens160` | Budget multi-gas, needs external T/RH |

**Recommendation for air quality monitor:**
- Budget: AHT20 + ENS160 (~$5)
- Mid-range: SHT41 + SGP41 + SCD40 (~$33)
- Pro: SHT41 + SGP41 + SCD41 + PMS7003 (~$65)

## Motion & Presence Sensors

| Sensor | Type | Range | Interface | Price | ESPHome | Notes |
|--------|------|-------|-----------|-------|---------|-------|
| **HC-SR501** | PIR | 7m, 120° | GPIO | $1.00 | `gpio` binary_sensor | Basic, cheap, high false positives |
| **AM312** | PIR (mini) | 3m, 100° | GPIO | $0.80 | `gpio` binary_sensor | Tiny (10mm), 3.3V compatible |
| **LD2410** | mmWave 24GHz | 6m | UART/GPIO | $3.00 | `ld2410` | Presence + motion, through walls |
| **LD2412** | mmWave 24GHz | 6m | UART/GPIO | $3.50 | `ld2412` | LD2410 successor, better zones |
| **LD2450** | mmWave 24GHz | 6m | UART | $5.00 | `ld2450` | Multi-target tracking (x,y,speed) |
| **HLK-LD2410B** | mmWave 24GHz | 5m | BLE+UART | $4.00 | `ld2410` | BLE configuration |
| **SEN0395** | mmWave 24GHz | 9m | UART/GPIO | $12.00 | `dfrobot_sen0395` | Long range, DFRobot |
| **VL53L0X** | ToF laser | 2m | I2C (0x29) | $2.50 | `vl53l0x` | Precise distance, not presence |
| **RCWL-0516** | Doppler radar | 7m | GPIO | $0.80 | `gpio` binary_sensor | Cheap, detects through plastic |

**Recommendation:** LD2410 for presence detection (can detect stationary people, unlike PIR). Add PIR for fast motion trigger.

## Light Sensors

| Sensor | Range | Interface | Price | I2C Addr | ESPHome | Notes |
|--------|-------|-----------|-------|----------|---------|-------|
| **BH1750** | 1-65535 lux | I2C | $1.00 | 0x23/0x5C | `bh1750` | Most popular, good accuracy |
| **TSL2591** | 188µlux-88klux | I2C | $3.00 | 0x29 | `tsl2591` | High dynamic range, IR channel |
| **VEML7700** | 0-120klux | I2C | $1.50 | 0x10 | `veml7700` | Auto-range, very low power |
| **LTR-390** | UV + ambient | I2C | $2.00 | 0x53 | `ltr390` | UV index for outdoor stations |
| **LDR** | Relative | ADC | $0.05 | GPIO | `adc` + `sensor` | Cheapest, non-linear, uncalibrated |

**Recommendation:** BH1750 for indoor lux. VEML7700 for battery devices. TSL2591 for wide-range outdoor.

## Distance & Level Sensors

| Sensor | Range | Accuracy | Interface | Price | ESPHome | Best For |
|--------|-------|----------|-----------|-------|---------|----------|
| **HC-SR04** | 2-400cm | ±3mm | GPIO (trig+echo) | $1.00 | `ultrasonic` | Tank level, parking |
| **JSN-SR04T** | 25-450cm | ±1cm | GPIO | $4.00 | `ultrasonic` | Waterproof ultrasonic |
| **VL53L0X** | 3-200cm | ±3% | I2C | $2.50 | `vl53l0x` | Precise short range |
| **VL53L1X** | 4-400cm | ±2% | I2C | $4.00 | `vl53l1x` | Medium range ToF |
| **TFMini Plus** | 10-1200cm | ±1% | UART | $25.00 | `tfmini` | Long range lidar |

## Power & Energy Sensors

| Sensor | Measures | Max Current | Interface | Price | ESPHome | Notes |
|--------|----------|-------------|-----------|-------|---------|-------|
| **HLW8012** | V, I, P, E | 20A | GPIO pulse | $0.50 | `hlw8012` | Used in Sonoff POW |
| **BL0940** | V, I, P, E | 40A | UART | $0.80 | `bl0940` | Used in Shelly devices |
| **CSE7766** | V, I, P, E | 20A | UART | $0.60 | `cse7766` | Used in Sonoff POW R2 |
| **ADE7953** | V, I, P, E (2ch) | 30A | SPI/I2C | $2.50 | `ade7953_i2c` | Dual channel, Shelly 2.5 |
| **INA219** | V, I, P | 3.2A | I2C (0x40-0x4F) | $1.00 | `ina219` | DC measurement, debug tool |
| **INA226** | V, I, P | 36V, 20A | I2C | $1.50 | `ina226` | High-side/low-side sensing |
| **PZEM-004T** | V, I, P, E, PF | 100A (CT) | UART | $8.00 | `pzem004t` | Whole-house via CT clamp |
| **CT clamp** | Current only | 30-100A | ADC | $3.00 | `ct_clamp` | Non-invasive, with ADC |

## Actuators & Drivers

### Relays

| Type | Voltage | Current | Price | Notes |
|------|---------|---------|-------|-------|
| SRD-05VDC (mechanical) | 250V AC | 10A | $0.50 | Audible click, needs driver transistor |
| HF32F (mechanical) | 250V AC | 10A | $1.00 | Compact, direct 3.3V coil available |
| G3MB-202P (SSR) | 240V AC | 2A | $1.50 | Silent, no moving parts, limited current |
| SSR-40DA (SSR) | 480V AC | 40A | $5.00 | High power, needs heatsink |

### MOSFETs for DC Control

| MOSFET | Vds | Id | Rds(on) | Price | Notes |
|--------|-----|-----|---------|-------|-------|
| IRLZ44N | 55V | 47A | 22mΩ | $0.30 | Logic level, LED strips |
| AO3400A | 30V | 5.7A | 40mΩ | $0.05 | SOT-23, small loads |
| IRF540N | 100V | 33A | 44mΩ | $0.40 | Needs gate driver for 3.3V |

### Motor Drivers

| Driver | Type | Voltage | Current | Interface | Price | ESPHome |
|--------|------|---------|---------|-----------|-------|---------|
| L298N | H-bridge dual | 46V | 2A/ch | GPIO | $1.50 | `output` + GPIO |
| DRV8833 | H-bridge dual | 10.8V | 1.5A/ch | GPIO | $0.80 | `output` + GPIO |
| TB6612FNG | H-bridge dual | 15V | 1.2A/ch | GPIO | $1.00 | `output` + GPIO |
| A4988 | Stepper | 35V | 2A | Step/Dir | $1.50 | `stepper` |
| TMC2209 | Stepper (silent) | 29V | 2A | UART/Step | $3.00 | `stepper` + `tmc2209` |

## Power Supply Design

### USB-C Power (5V input)

```
USB-C connector → ESD protection (USBLC6-2) → AMS1117-3.3 → ESP32
                                              or
                → ME6211 (LDO, 500mA, low dropout) → ESP32 (recommended)
```

- **AMS1117-3.3**: $0.10, 1A, 1V dropout — cheap but wastes heat
- **ME6211C33**: $0.15, 500mA, 0.1V dropout — efficient, recommended
- **AP2112K-3.3**: $0.20, 600mA, low noise — good for analog sensors

### Battery Power (LiPo/Li-Ion)

```
18650 cell (3.7V) → TP4056 (charger) → ME6211 → ESP32
                   ↑ USB-C (charging)
```

| Component | Purpose | Price |
|-----------|---------|-------|
| TP4056 | Li-Ion charger IC, 1A, with protection | $0.15 |
| DW01A + FS8205 | Battery protection (OVP, UVP, OCP) | $0.10 |
| ME6211 | 3.3V LDO from battery voltage | $0.15 |
| Voltage divider | Battery level via ADC (100kΩ + 100kΩ) | $0.02 |

### Mains Power (AC input)

**Use pre-made modules for safety:**

| Module | Output | Price | Notes |
|--------|--------|-------|-------|
| Hi-Link HLK-PM01 | 5V/600mA | $2.50 | Certified, small, reliable |
| Hi-Link HLK-PM03 | 3.3V/600mA | $2.50 | Direct 3.3V, no LDO needed |
| Hi-Link HLK-5M05 | 5V/1A | $3.00 | Higher current for relays |
| Mean Well IRM-05-3.3 | 3.3V/1.51A | $5.00 | High quality, medical rated |

**Warning:** Mains power design requires proper isolation, creepage distances, and certification. Use pre-certified modules unless you have EE expertise.

### Solar Power

```
Solar panel (6V/1W+) → Schottky diode → TP4056 → LiPo → ME6211 → ESP32
```

| Component | Specs | Price |
|-----------|-------|-------|
| Solar panel | 6V, 1-3W (110x60mm to 150x130mm) | $3-6 |
| Schottky diode | SS34 (3A, 40V) — reverse protection | $0.05 |
| LiPo cell | 3.7V, 2000-6000mAh | $3-8 |

### PoE (Power over Ethernet)

| Module | Standard | Power | Price | Notes |
|--------|----------|-------|-------|-------|
| AG9905M | 802.3af | 5V/2.4A | $4.00 | Common for ESP32 PoE boards |
| Olimex ESP32-POE | Full board | 5V/2A | $25.00 | Ready-to-use PoE ESP32 |
| WT32-ETH01 | No PoE | Ethernet only | $8.00 | Add external PoE splitter |

## Communication & External Peripherals

### I2C Devices — Address Planning

When using multiple I2C devices, check for address conflicts:

| Address | Common Devices |
|---------|---------------|
| 0x10 | VEML7700 |
| 0x23 | BH1750 (ADDR=L) |
| 0x29 | VL53L0X, TSL2591 |
| 0x38 | AHT20 |
| 0x3C/0x3D | SSD1306 OLED |
| 0x40 | INA219, SHT4x |
| 0x44/0x45 | SHT3x |
| 0x48-0x4B | TMP117, ADS1115 |
| 0x52/0x53 | ENS160, LTR-390 |
| 0x58/0x59 | SGP30/SGP41 |
| 0x62 | SCD40/41 |
| 0x68/0x69 | MPU6050 |
| 0x76/0x77 | BME280/BME680, BMP280 |

**Conflict resolution:** Use TCA9548A I2C multiplexer ($0.50) if you have address conflicts.

### I2C Pullup Resistors

| Bus speed | Cable length | Recommended pullup |
|-----------|-------------|-------------------|
| 100kHz | < 30cm | 4.7kΩ |
| 400kHz | < 10cm | 2.2kΩ |
| Any | > 30cm | 1kΩ (with caution) |

Most breakout boards have pullups built in. Check before adding external pullups — too many paralleled reduces the resistance too much.

### Level Shifters

| Scenario | Solution | Price |
|----------|----------|-------|
| 5V sensor → 3.3V MCU | Voltage divider (1kΩ + 2kΩ) | $0.01 |
| Bidirectional I2C/SPI | TXS0108E or BSS138 MOSFET | $0.20 |
| 5V GPIO output | 74HCT125 buffer | $0.15 |
| RS485 | MAX485 or SP3485 | $0.30 |

### ADC Expansion

ESP32 ADC is 12-bit but non-linear. For accurate analog readings:

| ADC | Resolution | Channels | Interface | Price | ESPHome |
|-----|------------|----------|-----------|-------|---------|
| ADS1115 | 16-bit | 4 differential | I2C | $1.50 | `ads1115` |
| ADS1015 | 12-bit | 4 differential | I2C | $1.00 | `ads1015` |
| MCP3008 | 10-bit | 8 single-ended | SPI | $1.00 | `mcp3008` |

## Connectors & Protection

### ESD Protection

| Scenario | Component | Price |
|----------|-----------|-------|
| USB-C | USBLC6-2SC6 | $0.10 |
| GPIO (exposed) | TVS diode PESD3V3S1UB | $0.03 |
| Antenna | Low-capacitance TVS | $0.05 |

### Recommended Connectors

| Use | Connector | Price | Notes |
|-----|-----------|-------|-------|
| Power | USB-C | $0.15 | Standard, easy to source cables |
| Debug | JST-SH 1.25mm 4-pin | $0.10 | UART: VCC, TX, RX, GND |
| Sensors | JST-XH 2.54mm | $0.08 | Through-hole, locking |
| Sensors (SMD) | Molex Pico-SPOX | $0.15 | Small, reliable |
| Programming | Tag-Connect TC2030 | $0.00 (pads only) | No connector needed, pogo pin cable |

## Component Sourcing

| Source | Best For | Shipping | Min Order |
|--------|----------|----------|-----------|
| **LCSC** | SMD components, Chinese ICs | $3-8 (5-15 days) | 1 pc |
| **Mouser** | Western brands, datasheets | $5-20 (2-5 days) | 1 pc |
| **DigiKey** | Largest selection, fast | $5-20 (2-5 days) | 1 pc |
| **AliExpress** | Breakout boards, dev kits | Free (15-30 days) | 1 pc |
| **JLCPCB Parts** | Combined with PCB order | Free (with PCB) | — |
| **TME** | European stock, fast EU ship | $3-10 (1-3 days EU) | 1 pc |
| **Reichelt** | German stock, fast DE ship | $5 (1-2 days DE) | 1 pc |

**Tip:** For prototyping, buy breakout boards from AliExpress. For production, source bare ICs from LCSC/Mouser and design them onto your PCB.

---

For the full product development process, see `product-development.md`.
For enclosure and manufacturing guidance, see `enclosures-manufacturing.md`.
