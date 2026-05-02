# ESP Board Reference

Complete reference for ESP32 and ESP8266 boards supported by ESPHome.

---

## Table of Contents

- [Board Selection Guide](#board-selection-guide)
- [ESP32 Family](#esp32-family)
  - [ESP32 (Original)](#esp32-original)
  - [ESP32-S2](#esp32-s2)
  - [ESP32-S3](#esp32-s3)
  - [ESP32-C3](#esp32-c3)
  - [ESP32-C6](#esp32-c6)
  - [ESP32-H2](#esp32-h2)
  - [ESP32-C61](#esp32-c61)
  - [ESP32-P4](#esp32-p4)
- [LibreTiny Family](#libretiny-family)
  - [LN882H](#ln882h)
- [ESP8266 Family](#esp8266-family)
  - [ESP-01 / ESP-01S](#esp-01--esp-01s)
  - [ESP-12E/F (NodeMCU)](#esp-12ef-nodemcu)
  - [Wemos D1 Mini](#wemos-d1-mini)
  - [ESP8285](#esp8285)
- [Pin Reference Tables](#pin-reference-tables)
- [Board Comparison Table](#board-comparison-table)
- [Common Development Boards](#common-development-boards)
- [Framework Selection](#framework-selection)
- [RP2040 / RP2350 (Raspberry Pi Pico)](#rp2040--rp2350-raspberry-pi-pico)
  - [RP2040 BLE (`rp2040_ble`)](#rp2040-ble-rp2040_ble)
- [nRF52 (Zephyr RTOS)](#nrf52-zephyr-rtos)
  - [Device Firmware Update (DFU)](#device-firmware-update-dfu)

---

## Board Selection Guide

### Quick Decision Tree

**Do you need Bluetooth?**
- BLE only: ESP32, ESP32-S3, ESP32-C3, ESP32-C6, ESP32-H2
- Bluetooth Classic: ESP32 only
- No Bluetooth needed: Any chip including ESP8266

**Do you need voice assistant capability?**
- Yes: ESP32-S3 (best), ESP32 with PSRAM (limited)

**Do you need Thread/Zigbee/Matter?**
- Yes: ESP32-C6 or ESP32-H2

**Is this a battery-powered device?**
- Yes: ESP32-C3 (lowest power), ESP8266 with deep sleep

**Budget project with simple sensors?**
- Yes: ESP8266 or ESP32-C3

**Converting a commercial device (Shelly/Sonoff)?**
- See [device-guides.md](device-guides.md)

### Feature Requirements Matrix

| Requirement | Recommended Chip |
|-------------|------------------|
| General IoT | ESP32 |
| Voice assistant | ESP32-S3 |
| BLE proxy/tracker | ESP32, ESP32-C3 |
| Thread/Matter device | ESP32-C6 |
| Zigbee coordinator | ESP32-H2 |
| Battery sensor | ESP32-C3 |
| Simple relay/switch | ESP8266 |
| Display with touch | ESP32-S3 |
| Camera project | ESP32-S3 |
| USB device | ESP32-S2, ESP32-S3 |
| Legacy/budget | ESP8266 |
| High-performance media | ESP32-P4 |

### Quick Board ID Mapping

Use this table to quickly find the correct `board:` ID for ESPHome configs based on what users typically say:

| User Says | Chip | Board ID |
|-----------|------|----------|
| ESP32 / generic | ESP32 | `esp32dev` |
| NodeMCU-32S | ESP32 | `nodemcu-32s` |
| ESP32-S3 | ESP32-S3 | `esp32-s3-devkitc-1` |
| ESP32-C3 | ESP32-C3 | `esp32-c3-devkitm-1` |
| ESP32-C6 | ESP32-C6 | `esp32-c6-devkitc-1` |
| ESP32-H2 | ESP32-H2 | `esp32-h2-devkitm-1` |
| NodeMCU / ESP8266 | ESP8266 | `nodemcuv2` |
| D1 Mini / Wemos | ESP8266 | `d1_mini` |
| ESP-01 | ESP8266 | `esp01_1m` |
| Sonoff Basic/Mini | ESP8285 | `esp8285` |
| Shelly 1/1PM/2.5 | ESP8266 | `esp01_1m` |
| Shelly Plus | ESP32 | `esp32doit-devkit-v1` |

**See detailed board sections below for complete specifications and additional board IDs.**

---

## ESP32 Family

### ESP32 (Original)

The most common and versatile ESP32 variant. Dual-core with WiFi and Bluetooth.

**Specifications:**
- Cores: 2 (Xtensa LX6)
- Clock: 240 MHz
- RAM: 520 KB SRAM
- Flash: 4-16 MB (external)
- WiFi: 802.11 b/g/n
- Bluetooth: Classic + BLE 4.2
- GPIOs: 34 (GPIO0-39)
- ADC: 18 channels (12-bit)
- DAC: 2 channels (8-bit)
- Touch: 10 capacitive touch pins

**Common Board IDs:**

| Board | ID | Notes |
|-------|-----|-------|
| Generic DevKit | `esp32dev` | Most common, use as default |
| NodeMCU-32S | `nodemcu-32s` | NodeMCU form factor |
| LOLIN32 | `lolin32` | Wemos D1 Mini form factor |
| ESP-WROVER-KIT | `esp-wrover-kit` | With PSRAM and display |
| Adafruit HUZZAH32 | `featheresp32` | Feather form factor |
| TTGO T-Display | `ttgo-t1` | Built-in TFT display |
| M5Stack Core | `m5stack-core-esp32` | With display and buttons |

**Capabilities & Limitations:**

### Capabilities

| Feature | Details |
|---|---|
| WiFi | 802.11 b/g/n |
| Bluetooth | Classic + BLE 4.2 |
| GPIO count | 34 usable (GPIO0-39) |
| ADC | 18 channels (12-bit), ADC1 (GPIO32-39) + ADC2 (GPIO0,2,4,12-15,25-27) |
| Touch | 10 capacitive touch pins |
| DAC | 2 channels, 8-bit (GPIO25, GPIO26) |
| USB | None (requires external USB-UART bridge) |
| Special | CAN, ULP coprocessor, Hall sensor, SPI x3, I2C x2, UART x3 |

### Limitations and Gotchas

- **Strapping pins**: GPIO0 (boot mode), GPIO2 (must be low at boot), GPIO5 (SDIO timing), GPIO12 (flash voltage, 3.3V when low), GPIO15 (UART0 log when high) - avoid for outputs
- **Reserved GPIO**: GPIO6-11 used by internal flash on WROOM modules - never use
- **ADC restriction**: ADC2 (GPIO0, 2, 4, 12-15, 25-27, 33) unavailable while WiFi active - use ADC1 only
- **Input-only pins**: GPIO34, 35, 36, 39 are INPUT ONLY - no output, no internal pullup/pulldown
- **No native USB**: Requires USB-UART bridge chip for flashing/serial

**Pin Categories:**

| Category | Pins | Notes |
|----------|------|-------|
| Input Only | GPIO34, 35, 36, 39 | No pullup, no output |
| Strapping | GPIO0, 2, 5, 12, 15 | Affect boot mode |
| Flash (NEVER USE) | GPIO6-11 | Internal flash |
| Touch Capable | GPIO0, 2, 4, 12-15, 27, 32, 33 | Capacitive touch |
| DAC Output | GPIO25, 26 | Analog output |
| ADC1 (WiFi safe) | GPIO32-39 | Works with WiFi |
| ADC2 (WiFi conflict) | GPIO0, 2, 4, 12-15, 25-27 | Unavailable when WiFi active |

**Safe GPIO Recommendations:**
- Best for outputs: GPIO16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33
- Best for inputs: GPIO16, 17, 18, 19, 21, 22, 23, 34, 35, 36, 39
- I2C default: SDA=GPIO21, SCL=GPIO22
- SPI default: MOSI=GPIO23, MISO=GPIO19, CLK=GPIO18, CS=GPIO5

**Example Configuration:**

```yaml
esp32:
  board: esp32dev
  framework:
    type: arduino
```

**Best For:** General IoT, BLE proxy, displays, most projects

---

### ESP32-S2

Single-core with native USB. No Bluetooth support.

**Specifications:**
- Cores: 1 (Xtensa LX7)
- Clock: 240 MHz
- RAM: 320 KB SRAM
- Flash: 4 MB+ (external)
- WiFi: 802.11 b/g/n
- Bluetooth: None
- GPIOs: 43 (GPIO0-21, GPIO26-46)
- ADC: 20 channels
- DAC: 2 channels (GPIO17-18)
- Touch: 20 capacitive touch pins (GPIO1-14 + more)
- USB: Native USB OTG

**Common Board IDs:**

| Board | ID | Notes |
|-------|-----|-------|
| ESP32-S2-Saola-1 | `esp32-s2-saola-1` | Standard dev board |
| LOLIN S2 Mini | `lolin_s2_mini` | Compact form factor |
| Adafruit Feather S2 | `adafruit_feather_esp32s2` | Feather form factor |
| Unexpected Maker TinyS2 | `um_tinys2` | Ultra compact |

**Capabilities & Limitations:**

### Capabilities

| Feature | Details |
|---|---|
| WiFi | 802.11 b/g/n |
| Bluetooth | None |
| GPIO count | 43 pins (GPIO0-21, GPIO26-46) |
| ADC | ADC1 (GPIO1-10) + ADC2 (GPIO11-20), 20 channels total |
| Touch | 20 capacitive touch pins (T1-T14 on GPIO1-14) |
| DAC | 2 channels (GPIO17, GPIO18) |
| USB | Native USB OTG |
| Special | Dual ULP (FSM + RISC-V), built-in temperature sensor, camera interface |

### Limitations and Gotchas

- **Strapping pins**: GPIO0 (boot, must be HIGH), GPIO45 (VDD_SPI voltage), GPIO46 (ROM log, INPUT ONLY)
- **Reserved GPIO**: GPIO33-37 used by SPI flash/PSRAM on WROOM modules - do not use
- **ADC restriction**: ADC2 unavailable while WiFi active
- **Input-only pins**: GPIO46 is input-only (ROM log strapping pin)
- **No Bluetooth**: No BLE at all - important distinction from S3
- **Single core**: CPU-intensive tasks can block WiFi

**Example Configuration:**

```yaml
esp32:
  board: esp32-s2-saola-1
  framework:
    type: arduino
```

**Best For:** USB devices, projects not needing Bluetooth

---

### ESP32-S3

Dual-core with AI acceleration. Best for voice assistants and cameras.

**Specifications:**
- Cores: 2 (Xtensa LX7)
- Clock: 240 MHz
- RAM: 512 KB SRAM + optional 8MB PSRAM
- Flash: 8-16 MB
- WiFi: 802.11 b/g/n
- Bluetooth: BLE 5.0
- GPIOs: 45 (GPIO0-21, GPIO26-48)
- ADC: 20 channels
- Touch: 14 capacitive touch pins (GPIO1-14)
- USB: Native USB OTG
- Special: Vector instructions for AI/ML

**Common Board IDs:**

| Board | ID | Notes |
|-------|-----|-------|
| ESP32-S3-DevKitC-1 | `esp32-s3-devkitc-1` | Standard dev board |
| Seeed XIAO ESP32S3 | `seeed_xiao_esp32s3` | Tiny form factor |
| ESP32-S3-BOX | `esp32s3box` | Voice assistant dev kit |
| Adafruit Feather S3 | `adafruit_feather_esp32s3` | Feather form factor |
| M5Stack AtomS3 | `m5stack-atoms3` | Ultra compact |
| LILYGO T-Display S3 | `lilygo-t-display-s3` | Built-in display |

**Capabilities & Limitations:**

### Capabilities

| Feature | Details |
|---|---|
| WiFi | 802.11 b/g/n |
| Bluetooth | BLE 5.0 (Long Range) |
| GPIO count | 45 pins (GPIO0-21, GPIO26-48) |
| ADC | ADC1 (GPIO1-10) + ADC2 (GPIO11-20) |
| Touch | 14 capacitive touch pins (GPIO1-14) |
| DAC | None |
| USB | Native USB OTG (GPIO19-20) |
| Special | AI/ML vector instructions (PIE), Octal/Quad PSRAM, camera interface, SPI x4, I2S x2, ULP |

### Limitations and Gotchas

- **Strapping pins**: GPIO0 (boot), GPIO45 (VDD_SPI), GPIO46 (ROM log, INPUT ONLY)
- **Reserved GPIO**: GPIO35-37 reserved for Octal PSRAM on WROOM-2 modules - check your module variant
- **ADC restriction**: ADC2 unavailable while WiFi active
- **Input-only pins**: GPIO46 is input-only
- **No DAC**: Unlike classic ESP32, S3 has no DAC channels
- **USB OTG on GPIO19-20**: Disable USB OTG if using GPIO19-20 as general GPIO
- **JTAG pins**: GPIO39-42 are JTAG pins - usable but complicates debugging

**Example Configuration:**

```yaml
esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf  # Recommended for S3
```

**Voice Assistant Configuration:**

```yaml
esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf
    sdkconfig_options:
      CONFIG_ESP32S3_DEFAULT_CPU_FREQ_240: "y"
      CONFIG_ESP32S3_SPIRAM_SUPPORT: "y"

psram:
  mode: octal
  speed: 80MHz
```

**Best For:** Voice assistants, cameras, AI edge, displays with touch

---

### ESP32-C3

RISC-V single-core. Low power and compact.

**Specifications:**
- Cores: 1 (RISC-V)
- Clock: 160 MHz
- RAM: 400 KB SRAM
- Flash: 4 MB
- WiFi: 802.11 b/g/n
- Bluetooth: BLE 5.0
- GPIOs: 22 (GPIO0-21)
- ADC: 6 channels
- USB: Built-in USB Serial/JTAG (GPIO18/GPIO19)

**Common Board IDs:**

| Board | ID | Notes |
|-------|-----|-------|
| ESP32-C3-DevKitM-1 | `esp32-c3-devkitm-1` | Standard dev board |
| Seeed XIAO ESP32C3 | `seeed_xiao_esp32c3` | Tiny form factor |
| ESP32-C3-MINI-1 | `esp32-c3-devkitc-02` | Module-based |
| LOLIN C3 Mini | `lolin_c3_mini` | D1 Mini form factor |
| Adafruit QT Py C3 | `adafruit_qtpy_esp32c3` | STEMMA QT connector |

**Capabilities & Limitations:**

### Capabilities

| Feature | Details |
|---|---|
| WiFi | 802.11 b/g/n |
| Bluetooth | BLE 5.0 (Long Range) |
| GPIO count | 22 pins (GPIO0-21) |
| ADC | ADC1 (GPIO0-4); ADC2 = GPIO5 only |
| Touch | None |
| DAC | None |
| USB | Built-in USB Serial/JTAG (GPIO18/GPIO19) |
| Special | Low-power sleep modes, RISC-V 160MHz, small package |

### Limitations and Gotchas

- **Strapping pins**: GPIO2 (boot), GPIO8 (boot mode), GPIO9 (must be HIGH at boot - boot button)
- **Reserved GPIO**: GPIO11-17 used by SPI flash on WROOM modules - do not use
- **ADC restriction**: ADC2 (GPIO5 only) unavailable while WiFi active - use ADC1 only
- **Input-only pins**: None beyond strapping constraints
- **No touch pins, no DAC**
- **GPIO18/19 = USB JTAG**: Repurposing disables USB debugging
- **RISC-V slower than Xtensa** for floating-point operations

**Pin Notes:**
- GPIO0-10: General purpose (some have boot functions)
- GPIO11-17: Not available on most modules (internal flash)
- GPIO18-21: Safe to use

**Example Configuration:**

```yaml
esp32:
  board: esp32-c3-devkitm-1
  framework:
    type: arduino
```

**Best For:** Battery devices, simple sensors, BLE beacons, compact projects

---

### ESP32-C6

WiFi 6 with Thread/Zigbee support. Matter-ready.

**Specifications:**
- Cores: 1 (RISC-V) + 1 low-power core
- Clock: 160 MHz
- RAM: 512 KB SRAM
- Flash: 4 MB
- WiFi: 802.11ax (WiFi 6)
- Bluetooth: BLE 5.3
- 802.15.4: Thread, Zigbee
- GPIOs: 31 (GPIO0-30)
- ADC: 7 channels (ADC1 only)
- USB: Built-in USB Serial/JTAG (GPIO12/GPIO13)

**Common Board IDs:**

| Board | ID | Notes |
|-------|-----|-------|
| ESP32-C6-DevKitC-1 | `esp32-c6-devkitc-1` | Standard dev board |
| Seeed XIAO ESP32C6 | `seeed_xiao_esp32c6` | Tiny form factor |

**Capabilities & Limitations:**

### Capabilities

| Feature | Details |
|---|---|
| WiFi | 802.11ax (WiFi 6), MU-MIMO, TWT |
| Bluetooth | BLE 5.3 |
| GPIO count | 31 pins (GPIO0-30) |
| ADC | ADC1 only (GPIO0-6, 7 channels) |
| Touch | None |
| DAC | None |
| USB | Built-in USB Serial/JTAG (GPIO12/GPIO13) |
| Special | Thread/Matter (802.15.4), Zigbee, LP core coprocessor, LP GPIO (GPIO0-7 survive deep sleep) |

### Limitations and Gotchas

- **Strapping pins**: GPIO8 (boot mode), GPIO9 (boot button), GPIO15 (JTAG source)
- **Reserved GPIO**: GPIO25-30 used by SPI flash on WROOM modules - do not use
- **ADC restriction**: ADC1 only (no ADC2), no ADC+WiFi conflict
- **Input-only pins**: None beyond strapping constraints
- **No touch pins, no DAC**
- **Thread/Zigbee and WiFi cannot run simultaneously**: Time-multiplexed radio
- **GPIO12/13 = USB JTAG**: Avoid when debugging

**Example Configuration:**

```yaml
esp32:
  board: esp32-c6-devkitc-1
  framework:
    type: esp-idf
```

**Best For:** Matter devices, Thread border router, WiFi 6 projects

---

### ESP32-H2

Thread/Zigbee only. No WiFi.

**Specifications:**
- Cores: 1 (RISC-V)
- Clock: 96 MHz
- RAM: 320 KB SRAM
- Flash: 4 MB
- WiFi: None
- Bluetooth: BLE 5.3
- 802.15.4: Thread, Zigbee
- GPIOs: 28 (GPIO0-27)
- ADC: 5 channels (GPIO0-4)
- USB: Built-in USB Serial/JTAG (GPIO26/GPIO27)
- LP core: Yes

**Common Board IDs:**

| Board | ID | Notes |
|-------|-----|-------|
| ESP32-H2-DevKitM-1 | `esp32-h2-devkitm-1` | Standard dev board |

**Capabilities & Limitations:**

### Capabilities

| Feature | Details |
|---|---|
| WiFi | None |
| Bluetooth | BLE 5.3 |
| GPIO count | 28 pins (GPIO0-27) |
| ADC | ADC1 (GPIO0-4, 5 channels) |
| Touch | None |
| DAC | None |
| USB | Built-in USB Serial/JTAG (GPIO26/GPIO27) |
| Special | Thread/Matter (802.15.4), Zigbee, LP core, LP GPIO (GPIO0-7) |

### Limitations and Gotchas

- **Strapping pins**: GPIO8 (boot mode), GPIO9 (boot button)
- **Reserved GPIO**: GPIO12-17 used by SPI flash - do not use
- **ADC restriction**: Only 5 ADC channels (GPIO0-4)
- **Input-only pins**: None beyond strapping constraints
- **No WiFi**: Thread/Zigbee/BLE only - needs border router (e.g. ESP32-C6) for IP connectivity
- **No touch pins, no DAC**
- **GPIO26/27 = USB JTAG**: Must pair with WiFi-capable device for Home Assistant integration via Thread

**Example Configuration:**

```yaml
esp32:
  board: esp32-h2-devkitm-1
  framework:
    type: esp-idf
```

**Best For:** Thread endpoints, Zigbee devices, low-power sensors

---

### ESP32-C61

*Added ESPHome 2026.4.0*

New ESP32 variant with RISC-V core (same architecture as C3/C6) and PSRAM support. Both quad-mode at 40 MHz and 80 MHz are supported.

**Specifications:**
- Cores: 1 (RISC-V)
- WiFi: 802.11 b/g/n
- Bluetooth: BLE 5.0
- PSRAM: Yes (quad-mode, 40 MHz or 80 MHz)
- Requires esp-idf framework

**Common Board IDs:**

| Board | ID | Notes |
|-------|-----|-------|
| ESP32-C61 DevKit | `esp32c61dev` | Generic dev board |

**Capabilities & Limitations:**

### Capabilities

| Feature | Details |
|---|---|
| WiFi | 802.11 b/g/n |
| Bluetooth | BLE 5.0 |
| GPIO count | Similar to C3 family (verify with your module) |
| ADC | ADC1 (verify channels with datasheet) |
| Touch | None |
| DAC | None |
| USB | Built-in USB Serial/JTAG |
| Special | PSRAM quad-mode (40 MHz or 80 MHz), RISC-V core |

### Limitations and Gotchas

- **Strapping pins**: GPIO2 (boot), GPIO8 (boot mode), GPIO9 (must be HIGH at boot) - follow C3 family conventions
- **Reserved GPIO**: Verify SPI flash pins with your specific module datasheet
- **ADC restriction**: ADC2 + WiFi conflict expected - verify with datasheet
- **Input-only pins**: Verify with module datasheet
- **No touch pins, no DAC**
- **esp-idf required**: Arduino framework not supported; PSRAM requires esp-idf
- **Very new chip**: Limited community board support, limited ESPHome component validation

**Example Configuration:**

```yaml
esp32:
  board: esp32c61dev
  framework:
    type: esp-idf

psram:
  mode: quad
  speed: 80MHz
```

**Notes:**
- Requires `esp-idf` framework (Arduino not supported)
- Board ID `esp32c61dev` is the generic fallback; verify with your specific module supplier

**Best For:** Projects requiring PSRAM with RISC-V core

---

### ESP32-P4

High-performance Xtensa LX7 dual-core chip focused on multimedia and display. No integrated wireless.

**Specifications:**
- Cores: 2 (Xtensa LX7)
- Clock: up to 400 MHz
- RAM: large (varies by module)
- PSRAM: up to 32 MB
- WiFi: None (requires companion chip)
- Bluetooth: None (requires companion chip)
- GPIOs: 55 (GPIO0-54)
- USB: USB OTG 2.0 high-speed
- Display: MIPI DSI (up to 1080p)
- Camera: MIPI CSI interface
- Video: H.264 hardware encoder, JPEG hardware codec
- LP core: Yes

**Common Board IDs:**

| Board | ID | Notes |
|-------|-----|-------|
| ESP32-P4 DevKit | (varies by supplier) | Verify with your module vendor |

**Capabilities & Limitations:**

### Capabilities

| Feature | Details |
|---|---|
| WiFi | None (requires companion chip) |
| Bluetooth | None (requires companion chip) |
| GPIO count | 55 pins (GPIO0-54) |
| ADC | Available (verify channels with datasheet) |
| Touch | None |
| DAC | None |
| USB | USB OTG 2.0 high-speed (GPIO24/GPIO25 = D-/D+) |
| Special | Dual-core Xtensa LX7 400MHz, up to 32MB PSRAM, MIPI DSI display (1080p), MIPI CSI camera, H.264 HW encoder, JPEG HW codec, hardware crypto accelerators, LP core |

### Limitations and Gotchas

- **Strapping pins**: GPIO28, GPIO29, GPIO30 - avoid for outputs
- **Reserved GPIO**: GPIO24/GPIO25 = USB D-/D+
- **ADC restriction**: High power draw may affect analog accuracy - verify with your design
- **Input-only pins**: Verify with datasheet
- **No integrated WiFi or Bluetooth**: Requires companion chip (e.g. ESP32-C6 via SPI for WiFi/BLE/Thread)
- **MIPI DSI requires compatible display modules**: Not compatible with standard SPI TFT displays
- **High power consumption**: Significantly higher than other variants; plan power budget accordingly
- **ESPHome component support still maturing (2026)**: Fewer validated components vs S3/C3
- **Most dev boards are dual-chip designs**: P4 + C6 two-chip PCB for wireless

**Example Configuration:**

```yaml
esp32:
  board: esp32p4dev  # Verify board ID with your supplier
  framework:
    type: esp-idf
```

**Best For:** High-performance displays, camera/video processing, multimedia edge applications where wireless is handled by a companion chip

---

## LibreTiny Family

### LN882H

*Added ESPHome 2026.4.0*

Lightning Semi LN882H is a newer LibreTiny-compatible chip, supported via the `libretiny:` platform block.

**Platform:** LibreTiny

**Example Configuration:**

```yaml
libretiny:
  board: ln882h-evb  # Verify board ID for your specific module
```

**Notes:**
- Uses `libretiny:` platform, not `esp32:` or `esp8266:`
- Part of the LibreTiny-supported family alongside BK7231, RTL8710, and similar chips
- Check the LibreTiny board catalog for available board IDs

**Best For:** Commercial IoT modules using the LN882H chip

---

## ESP8266 Family

### ESP-01 / ESP-01S

Minimal module with limited GPIOs.

**Specifications:**
- Clock: 80 MHz
- RAM: 80 KB
- Flash: 512 KB (ESP-01) or 1 MB (ESP-01S)
- WiFi: 802.11 b/g/n
- GPIOs: 4 usable (GPIO0, 1, 2, 3)
- ADC: None accessible

**Board IDs:**
- `esp01` - 512KB flash
- `esp01_1m` - 1MB flash (most common now)

**Available Pins:**
- GPIO0: Boot mode (use with caution)
- GPIO1: TX (Serial)
- GPIO2: Must be HIGH at boot
- GPIO3: RX (Serial)

**Example Configuration:**

```yaml
esp8266:
  board: esp01_1m
  restore_from_flash: true
```

**Best For:** Simple relay modules, single-sensor projects

---

### ESP-12E/F (NodeMCU)

Most common ESP8266 module. Full GPIO access.

**Specifications:**
- Clock: 80/160 MHz
- RAM: 80 KB
- Flash: 4 MB
- WiFi: 802.11 b/g/n
- GPIOs: 11 usable
- ADC: 1 channel (A0, 0-1V)

**Board IDs:**
- `nodemcuv2` - NodeMCU v2 (CH340 USB)
- `esp12e` - Generic ESP-12E module

**Pin Categories:**

| Category | Pins | Notes |
|----------|------|-------|
| Safe for general use | GPIO4, 5, 12, 13, 14 | Best choices |
| Boot sensitive | GPIO0, 2, 15 | Strapping pins |
| Serial | GPIO1 (TX), GPIO3 (RX) | Avoid if using serial |
| Flash (NEVER USE) | GPIO6-11 | Internal flash |
| No PWM | GPIO16 | Wake from deep sleep only |
| ADC | A0 | 0-1V input range |

**D-pin to GPIO mapping (NodeMCU):**

| D-Pin | GPIO | Notes |
|-------|------|-------|
| D0 | GPIO16 | No PWM, wake pin |
| D1 | GPIO5 | Safe, I2C SCL |
| D2 | GPIO4 | Safe, I2C SDA |
| D3 | GPIO0 | Boot pin, has pullup |
| D4 | GPIO2 | Boot pin, has pullup, LED |
| D5 | GPIO14 | Safe, SPI CLK |
| D6 | GPIO12 | Safe, SPI MISO |
| D7 | GPIO13 | Safe, SPI MOSI |
| D8 | GPIO15 | Boot pin, has pulldown |
| RX | GPIO3 | Serial RX |
| TX | GPIO1 | Serial TX |

**Example Configuration:**

```yaml
esp8266:
  board: nodemcuv2
```

**Best For:** DIY projects, learning, prototyping

---

### Wemos D1 Mini

Compact ESP8266 board with shield ecosystem.

**Specifications:**
- Same as ESP-12E/F
- Compact form factor
- 4MB flash
- CH340 USB chip

**Board IDs:**
- `d1_mini` - Standard D1 Mini
- `d1_mini_pro` - With external antenna connector
- `d1_mini_lite` - 1MB flash variant

**Example Configuration:**

```yaml
esp8266:
  board: d1_mini
```

**Best For:** Compact projects, shield-based designs

---

### ESP8285

ESP8266 with built-in 1MB flash. Used in commercial devices.

**Specifications:**
- Same as ESP8266
- 1MB internal flash
- No external flash chip

**Board IDs:**
- `esp8285` - Generic ESP8285

**Common Devices Using ESP8285:**
- Sonoff Basic, Mini, RF
- Many Tuya devices
- Some Shelly devices

**Example Configuration:**

```yaml
esp8266:
  board: esp8285
```

**Best For:** Flashing commercial devices (Sonoff, Tuya)

---

## Pin Reference Tables

### ESP32 Complete Pin Reference

| GPIO | Input | Output | ADC | Touch | Notes |
|------|-------|--------|-----|-------|-------|
| 0 | Yes | Yes | ADC2 | Yes | Strapping, boot button |
| 1 | Yes | Yes | - | - | TX0 (Serial) |
| 2 | Yes | Yes | ADC2 | Yes | Strapping, onboard LED |
| 3 | Yes | Yes | - | - | RX0 (Serial) |
| 4 | Yes | Yes | ADC2 | Yes | Safe |
| 5 | Yes | Yes | - | - | Strapping, VSPI CS |
| 6-11 | - | - | - | - | FLASH - Never use |
| 12 | Yes | Yes | ADC2 | Yes | Strapping (MTDI) |
| 13 | Yes | Yes | ADC2 | Yes | Safe |
| 14 | Yes | Yes | ADC2 | Yes | Safe |
| 15 | Yes | Yes | ADC2 | Yes | Strapping (MTDO) |
| 16 | Yes | Yes | - | - | Safe |
| 17 | Yes | Yes | - | - | Safe |
| 18 | Yes | Yes | - | - | VSPI CLK |
| 19 | Yes | Yes | - | - | VSPI MISO |
| 21 | Yes | Yes | - | - | I2C SDA |
| 22 | Yes | Yes | - | - | I2C SCL |
| 23 | Yes | Yes | - | - | VSPI MOSI |
| 25 | Yes | Yes | ADC2 | - | DAC1 |
| 26 | Yes | Yes | ADC2 | - | DAC2 |
| 27 | Yes | Yes | ADC2 | Yes | Safe |
| 32 | Yes | Yes | ADC1 | Yes | Safe |
| 33 | Yes | Yes | ADC1 | Yes | Safe |
| 34 | Input only | No | ADC1 | - | Input only |
| 35 | Input only | No | ADC1 | - | Input only |
| 36 | Input only | No | ADC1 | - | VP, input only |
| 39 | Input only | No | ADC1 | - | VN, input only |

### ESP8266 Complete Pin Reference

| GPIO | Input | Output | PWM | Notes |
|------|-------|--------|-----|-------|
| 0 | Yes | Yes | Yes | Boot, has internal pullup |
| 1 | Yes | Yes | Yes | TX, avoid if using serial |
| 2 | Yes | Yes | Yes | Boot, has internal pullup |
| 3 | Yes | Yes | Yes | RX, avoid if using serial |
| 4 | Yes | Yes | Yes | Safe, I2C SDA |
| 5 | Yes | Yes | Yes | Safe, I2C SCL |
| 6-11 | - | - | - | FLASH - Never use |
| 12 | Yes | Yes | Yes | Safe, SPI MISO |
| 13 | Yes | Yes | Yes | Safe, SPI MOSI |
| 14 | Yes | Yes | Yes | Safe, SPI CLK |
| 15 | Yes | Yes | Yes | Boot, has internal pulldown |
| 16 | Yes | Yes | No | Wake from deep sleep, no PWM |
| A0 | ADC | No | No | 0-1V input range |

---

## Board Comparison Table

| Chip | Cores | MHz | RAM | Flash | WiFi | BLE | USB | Thread | Price |
|------|-------|-----|-----|-------|------|-----|-----|--------|-------|
| ESP32 | 2 | 240 | 520KB | 4MB+ | Yes | 4.2 | No | No | $$ |
| ESP32-S2 | 1 | 240 | 320KB | 4MB+ | Yes | No | OTG | No | $ |
| ESP32-S3 | 2 | 240 | 512KB | 8MB+ | Yes | 5.0 | OTG | No | $$$ |
| ESP32-C3 | 1 | 160 | 400KB | 4MB | Yes | 5.0 | CDC | No | $ |
| ESP32-C6 | 1 | 160 | 512KB | 4MB | WiFi 6 | 5.3 | CDC | Yes | $$ |
| ESP32-H2 | 1 | 96 | 320KB | 4MB | No | 5.3 | CDC | Yes | $ |
| ESP32-C61 | 1 | 160 | 400KB | 4MB | Yes | 5.0 | CDC | No | $ |
| ESP32-P4 | 2 | 400 | varies | varies | No* | No* | OTG HS | No | $$$ |
| ESP8266 | 1 | 80 | 80KB | 1-4MB | Yes | No | No | No | $ |

*ESP32-P4 requires external companion chip (e.g. ESP32-C6) for WiFi/BLE.

### Use Case Recommendations

| Use Case | Best Choice | Alternative |
|----------|-------------|-------------|
| General IoT | ESP32 | ESP32-C3 |
| Voice Assistant | ESP32-S3 | - |
| BLE Proxy | ESP32 | ESP32-C3 |
| Battery Sensor | ESP32-C3 | ESP8266 |
| Display Project | ESP32-S3 | ESP32 |
| Camera | ESP32-S3 | ESP32-CAM |
| Thread/Matter | ESP32-C6 | ESP32-H2 |
| Zigbee Device | ESP32-H2 | ESP32-C6 |
| Budget/Simple | ESP8266 | ESP32-C3 |
| Commercial Device | ESP8285 | - |
| High-perf multimedia | ESP32-P4 | - |

---

## Common Development Boards

### ESP32 Development Boards

| Board Name | Board ID | Features |
|------------|----------|----------|
| ESP32 DevKit V1 | `esp32dev` | Standard, most common |
| NodeMCU-32S | `nodemcu-32s` | NodeMCU form factor |
| LOLIN D32 | `lolin_d32` | Battery connector |
| LOLIN D32 Pro | `lolin_d32_pro` | SD card, battery |
| ESP-WROVER-KIT | `esp-wrover-kit` | PSRAM, display |
| TTGO T-Display | `ttgo-t1` | Built-in 1.14" TFT |
| M5Stack Core | `m5stack-core-esp32` | Display, buttons, speaker |
| M5Stack Atom | `m5stack-atom` | Ultra compact |
| Adafruit HUZZAH32 | `featheresp32` | Feather form factor |
| SparkFun Thing | `esp32thing` | Battery charging |

### ESP32-S3 Development Boards

| Board Name | Board ID | Features |
|------------|----------|----------|
| ESP32-S3-DevKitC-1 | `esp32-s3-devkitc-1` | Standard |
| Seeed XIAO S3 | `seeed_xiao_esp32s3` | Tiny, camera |
| ESP32-S3-BOX | `esp32s3box` | Voice assistant kit |
| LILYGO T-Display S3 | `lilygo-t-display-s3` | Built-in display |
| M5Stack AtomS3 | `m5stack-atoms3` | Tiny with display |
| Adafruit Feather S3 | `adafruit_feather_esp32s3` | Feather form |

### ESP32-C3 Development Boards

| Board Name | Board ID | Features |
|------------|----------|----------|
| ESP32-C3-DevKitM-1 | `esp32-c3-devkitm-1` | Standard |
| Seeed XIAO C3 | `seeed_xiao_esp32c3` | Tiny |
| LOLIN C3 Mini | `lolin_c3_mini` | D1 Mini form |
| Adafruit QT Py C3 | `adafruit_qtpy_esp32c3` | STEMMA QT |
| ESP32-C3-MINI-1 | `esp32-c3-devkitc-02` | Module-based |

### ESP32-C6/H2 Development Boards

| Board Name | Board ID | Features |
|------------|----------|----------|
| ESP32-C6-DevKitC-1 | `esp32-c6-devkitc-1` | WiFi 6, Thread |
| Seeed XIAO C6 | `seeed_xiao_esp32c6` | Tiny |
| ESP32-H2-DevKitM-1 | `esp32-h2-devkitm-1` | Thread/Zigbee only |

### ESP8266 Development Boards

| Board Name | Board ID | Features |
|------------|----------|----------|
| NodeMCU v2 | `nodemcuv2` | Most common |
| NodeMCU v3 | `nodemcuv2` | Same as v2 |
| Wemos D1 Mini | `d1_mini` | Compact |
| D1 Mini Pro | `d1_mini_pro` | External antenna |
| ESP-01S | `esp01_1m` | Minimal, 1MB |
| ESP-12E Module | `esp12e` | Just module |

---

## Framework Selection

ESPHome supports two frameworks for ESP32:

### Arduino Framework (Default)

```yaml
esp32:
  board: esp32dev
  framework:
    type: arduino
```

**Pros:**
- Faster compile times
- More community examples
- Simpler

**Best for:** Most projects, beginners

### ESP-IDF Framework

```yaml
esp32:
  board: esp32dev
  framework:
    type: esp-idf
```

**Pros:**
- Full feature access
- Better for voice assistant
- Required for some S3/C6/H2 features

**Best for:** Voice assistants, advanced projects, ESP32-S3/C6/H2

### ESP8266 Framework

ESP8266 only supports Arduino framework:

```yaml
esp8266:
  board: nodemcuv2
```

---

## RP2040 / RP2350 (Raspberry Pi Pico)

*First-class platform support since ESPHome 2026.3 (pico-sdk 2.0)*

RP2040 (Pico W) and RP2350 (Pico 2 W) are now fully supported with WiFi, OTA, debug sensors, and captive portal. 143+ board definitions available.

### Basic Configuration

```yaml
rp2040:
  board: rpipicow  # Pico W (RP2040 + WiFi)
  # board: rpipico2w  # Pico 2 W (RP2350 + WiFi)

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
ota:
  platform: esphome
logger:
```

### Supported Boards

| Board ID | Chip | WiFi | Notes |
|----------|------|------|-------|
| `rpipicow` | RP2040 | Yes | Raspberry Pi Pico W |
| `rpipico2w` | RP2350 | Yes | Raspberry Pi Pico 2 W |
| `rpipico` | RP2040 | No | Requires external WiFi module |
| `rpipico2` | RP2350 | No | Requires external WiFi module |

### RP2040 BLE (`rp2040_ble`)

*Added ESPHome 2026.3.0*

Enables BLE on Raspberry Pi Pico W and Pico 2 W via BTstack (the CYW43 combo WiFi+BT chip). Required for BLE proxy functionality on RP2040/RP2350.

**Important:** Only works on Pico W and Pico 2 W. The plain Pico and Pico 2 have no wireless chip and cannot use BLE.

```yaml
rp2040_ble:

bluetooth_proxy:
  active: true
```

### Key Differences from ESP32

- **BLE requires `rp2040_ble` component** - Pico W / Pico 2 W only (CYW43 chip). Plain Pico has no wireless.
- **No ESP-IDF** - uses pico-sdk framework only
- **GPIO** - 26 GPIO pins (GP0-GP25), 3 ADC channels (GP26-GP28)
- **No strapping pins** - simpler GPIO usage than ESP32
- **Dual-core** - both RP2040 and RP2350 are dual-core (Cortex-M0+ / Cortex-M33)

### RP2040 with Sensors Example

```yaml
rp2040:
  board: rpipicow

i2c:
  sda: GPIO4
  scl: GPIO5

sensor:
  - platform: bme280_i2c
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    pressure:
      name: "Pressure"
```

---

## nRF52 (Zephyr RTOS)

nRF52-based devices run on the Zephyr RTOS platform. Primarily used for Zigbee and BLE devices.

### Basic Configuration

```yaml
nrf52:
  board: adafruit_nrf52840

# nRF52 does NOT support WiFi - uses BLE or Thread for connectivity
```

### Device Firmware Update (DFU)

*Added ESPHome 2025.9.0*

nRF52 supports Device Firmware Update under Zephyr RTOS via the mcumgr protocol. Both BLE DFU and serial DFU are supported.

```yaml
ota:
  platform: nrf52
  # Supports both BLE-based and serial-based DFU via mcumgr
```

**Compatible tools:**
- **nRF Connect** (mobile app) - BLE-based DFU, easiest for end users
- **mcumgr CLI** - command-line tool for both BLE and serial DFU

### BLE + Serial OTA (since 2026.3)

nRF52 also supports OTA updates via BLE and serial using the mcumgr protocol (builds on the same DFU stack):

```yaml
ota:
  platform: nrf52
  # Supports both BLE-based and serial-based OTA via mcumgr
```

### Key Notes

- **No WiFi** - nRF52 chips have no WiFi, use BLE or Thread/Zigbee
- **Zephyr RTOS** - different build system than ESP-IDF/Arduino
- **Thread/Zigbee** - primary use case for Matter-over-Thread devices
- **Limited component support** - not all ESPHome components work on nRF52

---

## Related Documentation

- [device-guides.md](device-guides.md) - Converting commercial devices
- [troubleshooting.md](troubleshooting.md) - Common hardware issues
- [power-management.md](power-management.md) - Deep sleep and battery
