# ESP Board Pinout Reference

Quick reference for common ESP board pinouts with ASCII diagrams.

## ESP32 DevKit V1 (30-pin)

```
                    ┌──────────────┐
                    │    USB-C     │
                    └──────────────┘
            EN   [ ]              [ ] GPIO23  (MOSI)
            GPIO36 (VP/ADC0) [ ]  [ ] GPIO22  (SCL)
            GPIO39 (VN/ADC3) [ ]  [ ] GPIO1   (TX)
            GPIO34 (ADC6)  [ ]    [ ] GPIO3   (RX)
            GPIO35 (ADC7)  [ ]    [ ] GPIO21  (SDA)
            GPIO32 (ADC4)  [ ]    [ ] GND
            GPIO33 (ADC5)  [ ]    [ ] GPIO19  (MISO)
            GPIO25 (DAC1)  [ ]    [ ] GPIO18  (SCK)
            GPIO26 (DAC2)  [ ]    [ ] GPIO5   ⚠️ Strapping
            GPIO27        [ ]     [ ] GPIO17  (TX2)
            GPIO14        [ ]     [ ] GPIO16  (RX2)
            GPIO12 ⚠️     [ ]     [ ] GPIO4
            GND          [ ]      [ ] GPIO0   ⚠️ Boot
            GPIO13       [ ]      [ ] GPIO2   ⚠️ Boot LED
            GPIO9  (⚡ Flash) [ ]  [ ] GPIO15  ⚠️ Strapping
            GPIO10 (⚡ Flash) [ ]  [ ] GPIO8   (⚡ Flash)
            GPIO11 (⚡ Flash) [ ]  [ ] GPIO7   (⚡ Flash)
            VIN (5V)     [ ]      [ ] GPIO6   (⚡ Flash)
            GND          [ ]      [ ] 3V3
                    ┌──────────────┐
                    │   ▪▪▪▪▪▪▪▪   │
                    └──────────────┘
```

**Legend:**
- ⚠️ Strapping pin (use with caution)
- ⚡ Flash pins (DO NOT USE)
- ADCx = Analog input capable
- DACx = Analog output capable

---

## ESP32-S3 DevKit (44-pin)

```
                    ┌──────────────┐
                    │    USB-C     │
                    └──────────────┘
            3V3    [ ]              [ ] GND
            3V3    [ ]              [ ] GPIO43 (TX)
            RST    [ ]              [ ] GPIO44 (RX)
            GPIO4  [ ]              [ ] GPIO1
            GPIO5  [ ]              [ ] GPIO2
            GPIO6  [ ]              [ ] GPIO42
            GPIO7  [ ]              [ ] GPIO41
            GPIO15 [ ]              [ ] GPIO40
            GPIO16 [ ]              [ ] GPIO39
            GPIO17 [ ]              [ ] GPIO38  (RGB LED)
            GPIO18 [ ]              [ ] GPIO37
            GPIO8  (SDA) [ ]        [ ] GPIO36
            GPIO9  (SCL) [ ]        [ ] GPIO35
            GPIO10 [ ]              [ ] GPIO0   ⚠️ Boot
            GPIO11 [ ]              [ ] GPIO45  ⚠️ Strapping
            GPIO12 [ ]              [ ] GPIO46  ⚠️ Strapping
            GPIO13 [ ]              [ ] GPIO47
            GPIO14 [ ]              [ ] GPIO48
            5V     [ ]              [ ] GND
                    └──────────────┘
```

**S3 Special Features:**
- USB OTG on GPIO19/20
- Camera interface support
- Vector extensions for ML

---

## ESP32-C3 Mini (13-pin per side)

```
                    ┌────────┐
                    │ USB-C  │
                    └────────┘
            GPIO0  ⚠️ [ ]     [ ] GPIO10
            GPIO1     [ ]     [ ] GPIO9  (Boot)  ⚠️
            GPIO2     [ ]     [ ] GPIO8  (Strapping) ⚠️
            GPIO3     [ ]     [ ] GPIO7
            GPIO4  (SDA) [ ]  [ ] GPIO6  (SCL)
            GPIO5     [ ]     [ ] GPIO5
            5V        [ ]     [ ] 3V3
            GND       [ ]     [ ] GND
                    └────────┘
```

**C3 Features:**
- WiFi + BLE 5.0
- RISC-V core
- USB CDC (no separate UART chip)

---

## D1 Mini (ESP8266)

```
                    ┌────────┐
                    │ USB    │
                    └────────┘
            RST    [ ]        [ ] TX  (GPIO1)
            A0     [ ]        [ ] RX  (GPIO3)
            D0     [ ] GPIO16 [ ] D1  (GPIO5/SCL)
            D5     [ ] GPIO14 [ ] D2  (GPIO4/SDA)
            D6     [ ] GPIO12 [ ] D3  (GPIO0)  ⚠️ Boot
            D7     [ ] GPIO13 [ ] D4  (GPIO2)  ⚠️ Boot/LED
            D8     [ ] GPIO15 [ ] GND          ⚠️ Boot
            3V3    [ ]        [ ] 5V
                    └────────┘
```

**D1 Mini Pin Mapping:**
| Label | GPIO | Function |
|-------|------|----------|
| D0 | 16 | Wake from deep sleep |
| D1 | 5 | SCL (I2C) |
| D2 | 4 | SDA (I2C) |
| D3 | 0 | Boot mode ⚠️ |
| D4 | 2 | Boot/LED ⚠️ |
| D5 | 14 | SCK (SPI) |
| D6 | 12 | MISO (SPI) |
| D7 | 13 | MOSI (SPI) |
| D8 | 15 | Boot (must be LOW) ⚠️ |
| A0 | ADC | Analog input (0-1V) |

---

## ESP32-S2 (43 GPIO: 0-21, 26-46)

Dual-core Xtensa LX7 at 240 MHz. Adds native USB (CDC/HID) and significantly more touch channels vs classic ESP32. No BLE.

| GPIO | ADC | Touch | DAC | Special |
|------|-----|-------|-----|---------|
| 0 | - | - | - | Strapping (boot mode, must be HIGH) |
| 1 | ADC1_CH0 | T1 | - | |
| 2 | ADC1_CH1 | T2 | - | |
| 3 | ADC1_CH2 | T3 | - | |
| 4 | ADC1_CH3 | T4 | - | |
| 5 | ADC1_CH4 | T5 | - | |
| 6 | ADC1_CH5 | T6 | - | |
| 7 | ADC1_CH6 | T7 | - | |
| 8 | ADC1_CH7 | T8 | - | |
| 9 | ADC1_CH8 | T9 | - | |
| 10 | ADC1_CH9 | T10 | - | |
| 11 | ADC2_CH0 | T11 | - | |
| 12 | ADC2_CH1 | T12 | - | |
| 13 | ADC2_CH2 | T13 | - | |
| 14 | ADC2_CH3 | T14 | - | |
| 15 | ADC2_CH4 | - | - | |
| 16 | ADC2_CH5 | - | - | |
| 17 | ADC2_CH6 | - | DAC1 | |
| 18 | ADC2_CH7 | - | DAC2 | |
| 19 | ADC2_CH8 | - | - | USB D- (when USB enabled) |
| 20 | ADC2_CH9 | - | - | USB D+ (when USB enabled) |
| 21 | - | - | - | |
| 26-32 | - | - | - | Available GPIO |
| 33-37 | - | - | - | SPI flash/PSRAM - do NOT use |
| 38 | - | - | - | |
| 39-42 | - | - | - | |
| 43 | - | - | - | UART0 TX |
| 44 | - | - | - | UART0 RX |
| 45 | - | - | - | Strapping (VDD_SPI voltage) |
| 46 | - | - | - | Strapping (ROM log), INPUT ONLY |

**Safe GPIO for general use:** 1-18, 21, 26-32, 38-42

**Default buses:**
- I2C: SDA=GPIO8 SCL=GPIO9
- SPI: MOSI=GPIO35 MISO=GPIO37 CLK=GPIO36
- UART0: TX=GPIO43 RX=GPIO44

> **Key warnings:**
> - GPIO33-37 are connected to SPI flash/PSRAM - never use on WROOM/MINI modules
> - GPIO19/20 become USB D-/D+ when USB peripheral is enabled - avoid for general I/O if using USB
> - GPIO45 and GPIO46 are strapping pins - add pull-up/pull-down if used
> - ADC2 pins share with WiFi - use ADC1 (GPIO1-10) when WiFi is active

---

## ESP32-S3 (45 GPIO: 0-21, 26-48)

Dual-core Xtensa LX7 at 240 MHz. Adds native USB OTG, vector instructions for ML inference, and more touch channels than S2. The most capable variant for edge AI and camera applications.

| GPIO | ADC | Touch | Special |
|------|-----|-------|---------|
| 0 | - | - | Strapping (boot mode) |
| 1 | ADC1_CH0 | T1 | |
| 2 | ADC1_CH1 | T2 | |
| 3 | ADC1_CH2 | T3 | |
| 4 | ADC1_CH3 | T4 | |
| 5 | ADC1_CH4 | T5 | |
| 6 | ADC1_CH5 | T6 | |
| 7 | ADC1_CH6 | T7 | |
| 8 | ADC1_CH7 | T8 | |
| 9 | ADC1_CH8 | T9 | |
| 10 | ADC1_CH9 | T10 | |
| 11 | ADC2_CH0 | T11 | |
| 12 | ADC2_CH1 | T12 | |
| 13 | ADC2_CH2 | T13 | |
| 14 | ADC2_CH3 | T14 | |
| 15 | ADC2_CH4 | - | |
| 16 | ADC2_CH5 | - | |
| 17 | ADC2_CH6 | - | |
| 18 | ADC2_CH7 | - | USB D- (native USB) |
| 19 | ADC2_CH8 | - | USB D+ (native USB) |
| 20 | ADC2_CH9 | - | |
| 21 | - | - | |
| 26 | - | - | |
| 27 | - | - | |
| 28 | - | - | |
| 29 | - | - | |
| 30 | - | - | |
| 31 | - | - | |
| 32 | - | - | |
| 33 | - | - | |
| 34 | - | - | |
| 35 | - | - | PSRAM (Octal) on WROOM-2 - avoid |
| 36 | - | - | PSRAM (Octal) on WROOM-2 - avoid |
| 37 | - | - | PSRAM (Octal) on WROOM-2 - avoid |
| 38 | - | - | |
| 39 | - | - | JTAG TCK |
| 40 | - | - | JTAG TDI |
| 41 | - | - | JTAG TDO |
| 42 | - | - | JTAG TMS |
| 43 | - | - | UART0 TX |
| 44 | - | - | UART0 RX |
| 45 | - | - | Strapping (VDD_SPI) |
| 46 | - | - | Strapping (ROM log), INPUT ONLY |
| 47 | - | - | |
| 48 | - | - | RGB LED on some devkits |

**Safe GPIO for general use:** 1-17, 21, 26-34, 38, 47-48

**Default buses:**
- I2C: SDA=GPIO8 SCL=GPIO9
- SPI: MOSI=GPIO11 MISO=GPIO13 CLK=GPIO12 CS=GPIO10
- UART0: TX=GPIO43 RX=GPIO44

> **Key warnings:**
> - GPIO35-37 are used for Octal PSRAM on WROOM-2 modules - do NOT use
> - GPIO39-42 are JTAG pins - avoid if using JTAG debugger
> - GPIO18/19 are USB D-/D+ for native USB OTG - avoid for general I/O if using USB
> - GPIO46 is INPUT ONLY and a strapping pin
> - ADC2 pins share with WiFi - prefer ADC1 (GPIO1-10) when WiFi is active

---

## ESP32-C3 (22 GPIO: 0-21)

Single-core RISC-V at 160 MHz. WiFi + BLE 5.0. Compact and cost-effective. Native USB Serial/JTAG (no separate USB chip needed).

| GPIO | ADC | Special |
|------|-----|---------|
| 0 | ADC1_CH0 | |
| 1 | ADC1_CH1 | |
| 2 | ADC1_CH2 | Strapping (boot) |
| 3 | ADC1_CH3 | |
| 4 | ADC1_CH4 | |
| 5 | ADC2_CH0 | ADC unavailable with WiFi |
| 6 | - | |
| 7 | - | |
| 8 | - | Strapping (boot mode) |
| 9 | - | Strapping (must be HIGH at boot), boot button on devkits |
| 10 | - | |
| 11 | - | VDD_SPI - do NOT use on WROOM modules |
| 12 | - | SPI flash CLK - do NOT use on WROOM modules |
| 13 | - | SPI flash Q - do NOT use on WROOM modules |
| 14 | - | SPI flash WP - do NOT use on WROOM modules |
| 15 | - | SPI flash CSn - do NOT use on WROOM modules |
| 16 | - | SPI flash D - do NOT use on WROOM modules |
| 17 | - | SPI flash HD - do NOT use on WROOM modules |
| 18 | - | USB D- (Serial/JTAG) - avoid unless repurposing USB |
| 19 | - | USB D+ (Serial/JTAG) - avoid unless repurposing USB |
| 20 | - | UART0 RX |
| 21 | - | UART0 TX |

**Safe GPIO for general use:** 0, 1, 3, 4, 6, 7, 8, 10

**Default buses:**
- I2C: SDA=GPIO8 SCL=GPIO9
- SPI: MOSI=GPIO7 MISO=GPIO2 CLK=GPIO6 CS=GPIO10
- UART0: TX=GPIO21 RX=GPIO20

> **Key warnings:**
> - GPIO11-17 are connected to SPI flash on WROOM modules - never use
> - GPIO18/19 are USB Serial/JTAG pins - reprogramming via OTA required if reassigned
> - GPIO9 must be HIGH at boot - boot button pulls it LOW only during flash mode
> - ADC2 (GPIO5) is unusable while WiFi is active - use ADC1 (GPIO0-4) instead

---

## ESP32-C6 (31 GPIO: 0-30)

Single-core RISC-V at 160 MHz. WiFi 6 (802.11ax) + BLE 5.3 + 802.15.4 (Thread/Zigbee). Low-Power (LP) core with dedicated LP GPIO for deep-sleep wake sources.

| GPIO | ADC | LP GPIO | Special |
|------|-----|---------|---------|
| 0 | ADC1_CH0 | LP_GPIO0 | |
| 1 | ADC1_CH1 | LP_GPIO1 | |
| 2 | ADC1_CH2 | LP_GPIO2 | |
| 3 | ADC1_CH3 | LP_GPIO3 | |
| 4 | ADC1_CH4 | LP_GPIO4 | |
| 5 | ADC1_CH5 | LP_GPIO5 | |
| 6 | ADC1_CH6 | LP_GPIO6 | |
| 7 | - | LP_GPIO7 | |
| 8 | - | - | Strapping (boot mode) |
| 9 | - | - | Strapping (boot), boot button on devkits |
| 10 | - | - | |
| 11 | - | - | |
| 12 | - | - | USB D- (Serial/JTAG) |
| 13 | - | - | USB D+ (Serial/JTAG) |
| 14 | - | - | |
| 15 | - | - | Strapping (JTAG source select) |
| 16 | - | - | UART0 TX |
| 17 | - | - | UART0 RX |
| 18 | - | - | |
| 19 | - | - | |
| 20 | - | - | |
| 21 | - | - | |
| 22 | - | - | |
| 23 | - | - | |
| 24 | - | - | |
| 25 | - | - | SPI flash CLK - do NOT use on WROOM |
| 26 | - | - | SPI flash CSn - do NOT use on WROOM |
| 27 | - | - | SPI flash Q - do NOT use on WROOM |
| 28 | - | - | SPI flash D - do NOT use on WROOM |
| 29 | - | - | SPI flash WP - do NOT use on WROOM |
| 30 | - | - | SPI flash HD - do NOT use on WROOM |

**Safe GPIO for general use:** 0-6, 8-11, 14, 18-23

**Default buses:**
- I2C: SDA=GPIO6 SCL=GPIO7
- SPI: MOSI=GPIO19 MISO=GPIO20 CLK=GPIO18
- UART0: TX=GPIO16 RX=GPIO17

> **Key warnings:**
> - GPIO25-30 are SPI flash pins on WROOM modules - never use
> - GPIO12/13 are USB Serial/JTAG - avoid unless repurposing USB
> - GPIO15 selects JTAG source at boot - leave floating or pull appropriately
> - LP GPIO (GPIO0-7) can wake the device from deep sleep via the LP core
> - No ADC2 - all ADC is on ADC1 (GPIO0-6)

---

## ESP32-H2 (28 GPIO: 0-27)

Single-core RISC-V at 96 MHz. 802.15.4 (Thread/Zigbee) + BLE 5.3. No WiFi. Designed for low-power mesh networking. LP GPIO for deep-sleep wake.

| GPIO | ADC | LP GPIO | Special |
|------|-----|---------|---------|
| 0 | ADC1_CH0 | LP_GPIO0 | |
| 1 | ADC1_CH1 | LP_GPIO1 | |
| 2 | ADC1_CH2 | LP_GPIO2 | |
| 3 | ADC1_CH3 | LP_GPIO3 | |
| 4 | ADC1_CH4 | LP_GPIO4 | |
| 5 | - | LP_GPIO5 | |
| 6 | - | LP_GPIO6 | |
| 7 | - | LP_GPIO7 | |
| 8 | - | - | Strapping (boot mode) |
| 9 | - | - | Strapping (boot), boot button |
| 10 | - | - | |
| 11 | - | - | |
| 12 | - | - | SPI flash CLK - do NOT use |
| 13 | - | - | SPI flash CSn - do NOT use |
| 14 | - | - | SPI flash Q - do NOT use |
| 15 | - | - | SPI flash D - do NOT use |
| 16 | - | - | SPI flash WP - do NOT use |
| 17 | - | - | SPI flash HD - do NOT use |
| 18 | - | - | |
| 19 | - | - | |
| 20 | - | - | |
| 21 | - | - | |
| 22 | - | - | UART0 TX |
| 23 | - | - | UART0 RX |
| 24 | - | - | |
| 25 | - | - | |
| 26 | - | - | USB D- (Serial/JTAG) |
| 27 | - | - | USB D+ (Serial/JTAG) |

**Safe GPIO for general use:** 0-4, 10-11, 18-21, 24-25

**Default buses:**
- I2C: SDA=GPIO1 SCL=GPIO0
- SPI: MOSI=GPIO5 MISO=GPIO0 CLK=GPIO4
- UART0: TX=GPIO22 RX=GPIO23

> **Key warnings:**
> - NO WiFi. Wireless is 802.15.4 (Thread/Zigbee) + BLE only
> - GPIO12-17 are SPI flash pins - never use
> - GPIO26/27 are USB Serial/JTAG - avoid unless repurposing USB
> - LP GPIO (GPIO0-7) can wake from deep sleep via LP core
> - Running at 96 MHz (not 160/240 MHz) - factor into timing-sensitive code

---

## ESP32-P4 (55 GPIO: 0-54)

Dual-core Xtensa LX9 at 400 MHz + LP RISC-V core. High-performance application processor. No wireless - pair with ESP32-C6 for WiFi/BLE/Thread. Designed for camera, display, and AI inference workloads.

| GPIO Range | Notes |
|---|---|
| 0-7 | General purpose, LP capable (LP_GPIO0-7) |
| 8-15 | General purpose |
| 16-23 | General purpose |
| 24 | USB D- |
| 25 | USB D+ |
| 26-31 | MIPI DSI data lanes |
| 28 | Strapping (boot mode) |
| 29-30 | Strapping pins |
| 32-40 | General purpose, high-drive capability |
| 41-47 | General purpose |
| 48-54 | General purpose, some shared with MIPI CSI camera |

- ADC1: GPIO0-6
- ADC2: GPIO7-9 (no WiFi conflict - no WiFi on P4)
- Default I2C: SDA=GPIO7 SCL=GPIO8

**Safe GPIO for general use:** 0-23, 32-40, 41-47 (avoid 26-31 if using MIPI DSI, avoid 48-54 if using MIPI CSI)

> **Key warnings:**
> - No wireless - must pair with ESP32-C6 (or similar) for connectivity
> - GPIO26-31 are MIPI DSI lanes - only free if not using a display
> - GPIO48-54 overlap with MIPI CSI - only free if not using a camera
> - GPIO28-30 are strapping pins - handle carefully
> - LP GPIO (GPIO0-7) supports deep-sleep wake via LP core
> - Runs at 400 MHz - fastest ESP32 variant, check peripheral timing

---

## ESP32-C61

RISC-V core (same family as C3). Pin layout follows C3 family conventions. Safe GPIO rules from C3 apply - refer to the ESP32-C3 section for general guidance.

Key differences from C3:
- PSRAM uses dedicated pins not shared with user GPIO on standard modules (no PSRAM conflict on exposed pins)
- Strapping pins follow C3 family conventions (GPIO2, GPIO8, GPIO9)
- Default buses are identical to C3

> When in doubt, treat the C61 the same as the C3 for pin selection. Avoid GPIO11-17 (flash), GPIO18-19 (USB), and respect the same strapping pin rules.

---

## Strapping Pins Reference

### ESP32

| GPIO | Function | Boot Requirement |
|------|----------|------------------|
| 0 | Boot mode | HIGH = normal boot, LOW = download mode |
| 2 | Boot mode | Must be LOW or floating at boot |
| 5 | SDIO timing | Affects SDIO slave timing |
| 12 | MTDI | HIGH = 1.8V flash, LOW = 3.3V flash |
| 15 | MTDO | HIGH = debug output enabled |

**Safe to use after boot:** GPIO0, 2, 5, 15 (with pull-up/down)
**Avoid:** GPIO12 (can cause boot failure if wrong state)

### ESP32-S2

| GPIO | Function |
|------|----------|
| 0 | Boot mode (must be HIGH for normal boot) |
| 45 | VDD_SPI voltage select |
| 46 | Boot mode / ROM log, INPUT ONLY |

### ESP32-S3

| GPIO | Function |
|------|----------|
| 0 | Boot mode |
| 45 | VDD_SPI voltage |
| 46 | Boot mode / ROM log |

### ESP32-C3

| GPIO | Function |
|------|----------|
| 2 | Strapping |
| 8 | Strapping (ROM log) |
| 9 | Boot mode |

### ESP32-C6

| GPIO | Function |
|------|----------|
| 8 | Boot mode |
| 9 | Boot mode (boot button) |
| 15 | JTAG source select |

### ESP32-H2

| GPIO | Function |
|------|----------|
| 8 | Boot mode |
| 9 | Boot mode (boot button) |

### ESP32-P4

| GPIO | Function |
|------|----------|
| 28 | Boot mode |
| 29 | Strapping |
| 30 | Strapping |

### ESP8266

| GPIO | Boot Requirement |
|------|------------------|
| 0 | HIGH = normal, LOW = flash mode |
| 2 | Must be HIGH at boot |
| 15 | Must be LOW at boot |

---

## ADC Capable Pins

### ESP32
- ADC1: GPIO32-39 (can use with WiFi)
- ADC2: GPIO0, 2, 4, 12-15, 25-27 (NOT usable with WiFi!)

### ESP32-S2
- ADC1: GPIO1-10
- ADC2: GPIO11-20 (NOT usable with WiFi)

### ESP32-S3
- ADC1: GPIO1-10
- ADC2: GPIO11-20

### ESP32-C3
- ADC1: GPIO0-4
- ADC2: GPIO5 (limited when WiFi active)

### ESP32-C6
- ADC1: GPIO0-6 (all ADC on ADC1 - no ADC2)

### ESP32-H2
- ADC1: GPIO0-4 (all ADC on ADC1 - no ADC2)

### ESP32-P4
- ADC1: GPIO0-6
- ADC2: GPIO7-9 (no WiFi conflict)

### ESP8266
- A0 only (0-1V range, use voltage divider for 3.3V)

---

## PWM / LEDC Capable Pins

### ESP32
All GPIOs except input-only (34-39) support PWM via LEDC.

### ESP32-S2 / S3
All GPIOs support PWM.

### ESP32-C3 / C6 / H2
All GPIOs support PWM.

### ESP32-P4
All GPIOs support PWM.

### ESP8266
All GPIOs except GPIO16 support PWM (software PWM).

---

## Touch Capable Pins (ESP32 only)

| Touch Pad | GPIO |
|-----------|------|
| T0 | GPIO4 |
| T1 | GPIO0 |
| T2 | GPIO2 |
| T3 | GPIO15 |
| T4 | GPIO13 |
| T5 | GPIO12 |
| T6 | GPIO14 |
| T7 | GPIO27 |
| T8 | GPIO33 |
| T9 | GPIO32 |

ESP32-S2 and S3 also support capacitive touch on GPIO1-14 (T1-T14). See variant-specific tables above.

---

## Quick Reference Table

| Feature | ESP32 | ESP32-S2 | ESP32-S3 | ESP32-C3 | ESP32-C6 | ESP32-H2 | ESP32-P4 | ESP8266 |
|---------|-------|----------|----------|----------|----------|----------|----------|---------|
| GPIO Count | 34 | 43 | 45 | 22 | 31 | 28 | 55 | 17 |
| ADC Channels | 18 | 20 | 20 | 6 | 7 | 5 | 10 | 1 |
| DAC | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| Touch | 10 | 14 | 14 | 0 | 0 | 0 | 0 | 0 |
| WiFi | 802.11b/g/n | 802.11b/g/n | 802.11b/g/n | 802.11b/g/n | 802.11ax (WiFi 6) | No | No | 802.11b/g/n |
| BLE | BT 4.2 | No | BLE 5.0 | BLE 5.0 | BLE 5.3 | BLE 5.3 | No | No |
| 802.15.4 | No | No | No | No | Yes | Yes | No | No |
| I2C | 2 | 2 | 2 | 1 | 1 | 1 | 2 | 1 (SW) |
| SPI | 4 | 4 | 4 | 3 | 3 | 3 | 3 | 2 |
| UART | 3 | 2 | 3 | 2 | 3 | 2 | 3 | 2 |
| PWM | 16 ch | 8 ch | 8 ch | 6 ch | 6 ch | 6 ch | 8 ch | SW |
| CPU | Xtensa LX6 | Xtensa LX7 | Xtensa LX7 | RISC-V | RISC-V | RISC-V | Xtensa LX9 | Xtensa L106 |
| Max MHz | 240 | 240 | 240 | 160 | 160 | 96 | 400 | 160 |
| Flash Pins | GPIO6-11 | GPIO33-37 | GPIO35-37* | GPIO11-17 | GPIO25-30 | GPIO12-17 | Internal | GPIO6-11 |

*S3 WROOM-2 only (Octal PSRAM variant)
