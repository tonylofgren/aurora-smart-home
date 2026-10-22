# ESPHome 2026.9.0 - Complete Release Reference (September 2026)

**Release date:** September 16, 2026 (2026.9.0), with a patch release 2026.9.1 on September 29, 2026
**Source:** https://esphome.io/changelog/2026.9.0/ and https://esphome.io/components/ota/esphome/

**Current-version note (2026-10-22):** This describes the September release. For current
generation also read [2026.10](release-2026-10.md), including the native ESP8266 default
and optional single-install OTA migration. The [component inventory](new-components-2026-9-10.md)
links reusable examples for every new public September/October component.

When the user is on this version, upgrading TO it, or asking "what's new", read this file BEFORE generating YAML. The OTA block every Aurora config carries changes shape this release: encrypted OTA replaces the OTA password as the recommended setup. Modbus controller gets another round of renames, and a real `climate: platform: template` finally exists.

---

## What landed in 2026.9.0 at a glance

Security of the update path is the headline. Ten themes worth knowing before you upgrade:

1. **Encrypted OTA.** The `esphome` OTA platform can encrypt the firmware image with the same Noise scheme (ChaCha20-Poly1305) the native API already uses. A bare `encryption:` block under the OTA platform reuses the `api:` key, so one key protects both the HA connection and updates. It replaces `password:`, which only authenticated the uploader and left the image (WiFi credentials and API key included) readable on the wire.
2. **Encryption got cheap.** The Noise and libsodium code was roughly halved. API encryption on an ESP8266 D1 mini now costs about 42 KB of flash (was about 81 KB) and 48 bytes of static RAM (was about 1.4 KB), and the handshake is about twice as fast. "ESP8266 is too small for API encryption" is no longer a valid reason to skip it.
3. **Modbus controller renames.** `custom_command` becomes `custom_pdu` (PDU only, no address byte), `register_count` and `force_new_range` merge into `reuse_previous_range`, per-sensor `skip_updates` is retired, and a new `continuous:` mode polls as fast as the bus allows.
4. **`climate: platform: template`.** A first-class template climate entity with per-property set actions and a `climate.template.publish` action. Replaces the old "abuse `thermostat` or write a custom component" workaround for UART and IR driven AC units.
5. **New sensors.** `d01` (PM2.5), `sfa40` (formaldehyde plus temperature and humidity), `ds1603l` (ultrasonic liquid level), `mk2pvrouter` (PV surplus diverter telemetry), plus a Tuya `water_heater` platform and Hörmann HCP vent and half-open buttons.
6. **Ethernet on a shared SPI bus.** SPI Ethernet chips (W5500, DM9051, ENC28J60, CH390) can now sit on an existing `spi:` bus via `spi_id:` instead of owning their own pins.
7. **Improv serial is network-agnostic.** `improv_serial` works on Ethernet-only boards, reports per-interface URLs, and can run on a dedicated UART with `uart_id:`.
8. **API actions describe themselves.** User-defined `api: actions:` accept a `description` and per-variable `description` and `example`, so Home Assistant renders a proper action form.
9. **Build speed.** Parallel PlatformIO package downloads, cached component discovery on native ESP-IDF builds, and no-op rebuilds that skip the package probe. Biggest gain on Raspberry Pi and HA app installs. No YAML impact.
10. **ESP8266 hardening.** Log strings moved to flash, heap-exhaustion paths fail the operation instead of rebooting, and Arduino core pins below 3.0.0 are rejected. A native (PlatformIO-free) ESP8266 toolchain is announced for 2026.10.0 but is not usable yet.

---

## Upgrade Checklist (run through this BEFORE flashing 2026.9.0)

- [ ] Device has `ota: - platform: esphome` with `password:`? -> keep the password for THIS update. Switch to `encryption:` only after the device runs 2026.9.x (see "Migrating an existing device" below). Validation will warn while both `password:` and an API key are set; that warning is expected during the transition.
- [ ] Device has `api:` but no `encryption: key:`? -> add one now if you plan to move OTA to encryption. If Home Assistant provisioned the key at adoption, copy that exact key into the YAML. Never generate a fresh key for an adopted device.
- [ ] Use `custom_command:` on a `modbus_controller` sensor? -> rename to `custom_pdu:` and drop the leading device-address byte. Frames whose first byte matches the controller `address:` are auto-migrated with a warning until 2027.3.0; anything else needs a manual fix.
- [ ] Use `force_new_range: true` or `register_count:` on Modbus items? -> use `reuse_previous_range: false` (or delete `register_count` when it matches the value type width). A `register_count` that disagrees with the value type now fails validation.
- [ ] Use per-sensor `skip_updates:` on Modbus? -> it no longer does anything. Put slow registers on a second `modbus_controller` with the same `address:` and a longer `update_interval:`.
- [ ] Modbus holding-register `switch` or `output` with a non-zero `offset:`? -> offsets are now byte-accurate (`address + offset/2`) and odd offsets are rejected. Re-check which register you actually write.
- [ ] Modbus switch `write_lambda` that relies on its return value to change the displayed state? -> the return value now only changes what goes on the wire. Publish the state explicitly or invert it in the read `lambda`.
- [ ] `modbus_controller` with `address: 0`? -> rejected unless you set `allow_broadcast_read: true` for a non-compliant device that answers broadcast.
- [ ] `homeassistant.event` with `variables:` written as lambda code but without a `!lambda` tag? -> add `!lambda`. Untagged strings that look like code warn now and become static text in 2027.3.0.
- [ ] ESP32 with a custom MAC burned into eFuse? -> it now applies to every interface (WiFi, Ethernet, BT, 802.15.4). Update DHCP reservations, MAC allowlists, BLE bonds, and re-commission Thread/Zigbee, or opt out with `esp32: advanced: ignore_efuse_custom_mac: true`.
- [ ] ESP8266 config pins `framework: version:` below 3.0.0? -> remove the pin or set 3.1.2. Older cores now fail validation, even for `logs` and `upload`.
- [ ] Use `esp32_hosted` with an ESP-IDF pin older than 5.3? -> remove the pin; 5.3 is the minimum.
- [ ] Use `mhz19`, `cm1106`, `daly_bms`, `pylontech`, `teleinfo`, `vbus`, `hydreon_rgxx`, `hrxl_maxsonar_wr`, `wl_134`, or `cse7761`? -> the required UART baud rate and parity are now checked at config time. Set them on the `uart:` bus if validation complains.
- [ ] Lambdas calling `set_timezone("...")` on the time component? -> removed. Use the YAML `timezone:` option or let Home Assistant (2026.3+) push the zone.

---

## Encrypted OTA

### Why it matters

Until now an OTA upload travelled in plaintext. The firmware image embeds the WiFi password and the API key, so anyone able to capture traffic on the LAN could pull both out of an update. An OTA `password:` did not help, because it only proved who was uploading. With `encryption:` the image is confidential in transit, and because the scheme uses a pre-shared key, the uploader is authenticated at the same time. No password is needed.

### Rules

- In 2026.9, `encryption:` and `password:` are mutually exclusive. In 2026.10 they may coexist only for the explicit `encryption.allow_plaintext_upload` migration path; remove the fallback and password afterward.
- A bare `encryption:` inherits the `api:` encryption key. This is the recommended form.
- Give the OTA block its own `key:` only when the config has no `api:` block at all (an MQTT-only device, for example). Next to a static API key, a different OTA key is rejected at validation.
- With `encryption:` present, the device refuses plaintext uploads and the CLI refuses to send them, so an attacker cannot downgrade the transfer.
- There is no key rotation over OTA yet. Changing the key means a serial flash or a web_server OTA upload.
- Plaintext OTA from pre-2026.9 firmware is scheduled for removal in 2027.3.0. Do at least step 1 of the migration before then.

### New device (flashed over USB first)

```yaml
api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    encryption:          # bare block: uses the api: key above
```

A device flashed by serial can carry `encryption:` from day one.

### Device without `api:` (MQTT only)

```yaml
mqtt:
  broker: !secret mqtt_broker

ota:
  - platform: esphome
    encryption:
      key: !secret ota_encryption_key   # base64 of 32 random bytes, same format as an API key
```

Generate a key with:

```bash
python -c "import base64, os; print(base64.b64encode(os.urandom(32)).decode())"
```

### Migrating an existing device (two updates)

An installed device that uses `password:` cannot jump straight to `encryption:`. The firmware currently on it still checks the password, and it does not know how to offer encryption yet.

**Step 1: update to 2026.9.x with the password still in place.** If `api:` has no key, add one in the same edit (copy the HA-provisioned key if there is one).

```yaml
api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password    # keep for this one update
```

After this flash the log shows encryption being offered with plaintext still accepted.

**Step 2: swap the password for encryption and update again.**

```yaml
ota:
  - platform: esphome
    encryption:
```

### The two error messages and what they mean

| Error | Cause | Fix |
|-------|-------|-----|
| `ESP requests password, but no password given!` | The password was removed before the device ran 2026.9.x | Put `password:` back, do step 1, then step 2 |
| `the device did not offer encryption; refusing to send the image in plaintext` | `encryption:` was added before the device ran 2026.9.x with a key it can offer | Remove `encryption:`, do step 1 with the password, then step 2 |

Locked out with a lost key: serial flash, or upload through the `web_server` OTA page if it is enabled.

### Aurora rule

Volt generates bare `encryption:` for every new device. When Volt edits an EXISTING device config, it first checks whether the current OTA block uses `password:`. If it does, the delivery includes the two-step migration above instead of a one-shot swap, and the README states which step the user is on. Full procedure and the HA-provisioned-key warning: `references/security-hardening.md`.

---

## Modbus Controller: Another Round of Renames

The 2026.7 rewrite continues. Every change below is aimed at making register ranges and custom frames predictable.

### `custom_command` becomes `custom_pdu`

`custom_command` took a raw frame that started with the device address. `custom_pdu` takes only the PDU (function code plus data). The address comes from the controller and the CRC is appended automatically.

```yaml
# Before (2026.8 and older)
sensor:
  - platform: modbus_controller
    modbus_controller_id: sdm120
    name: "Total active energy"
    custom_command: [0x2, 0x4, 0x1, 0x56, 0x00, 0x02]
    value_type: FP32

# After (2026.9): drop the leading 0x2, it comes from the controller address
sensor:
  - platform: modbus_controller
    modbus_controller_id: sdm120
    name: "Total active energy"
    custom_pdu: [0x4, 0x1, 0x56, 0x00, 0x02]
    value_type: FP32
    unit_of_measurement: kWh
    accuracy_decimals: 1
```

For `custom_pdu` polls the trigger `address` argument is `-1`, and the function code is reported with the 0x80 exception bit masked. Automations that filtered on the synthetic address need an update.

### `reuse_previous_range` replaces `register_count` and `force_new_range`

`reuse_previous_range` is tri-state:

| Value | Meaning |
|-------|---------|
| `auto` (default) | Join the previous range when addresses are adjacent and the item's position in the reply is exact |
| `true` | Always join, reading across address gaps and past non-standard `response_size` registers |
| `false` | Always start a new range at this item |

`force_new_range: true` maps to `reuse_previous_range: false`. The old keys still load with a deprecation warning until 2027.3.0. The vendor workaround `register_count: 1` with `response_size: 4` for FP32 no longer validates; describe the value with the right `value_type` instead.

### Slow registers: second controller instead of `skip_updates`

```yaml
modbus_controller:
  - id: inverter_fast
    address: 0x1
    modbus_id: modbus_bus
    update_interval: 5s       # power, current
  - id: inverter_slow
    address: 0x1              # same device, second controller
    modbus_id: modbus_bus
    update_interval: 5min     # energy totals, firmware version
```

`offline_skip_updates` is not affected by this change.

### Continuous polling

```yaml
modbus_controller:
  - id: meter
    address: 0x1
    modbus_id: modbus_bus
    continuous: true      # stream reads back to back to fill idle bus time
    update_interval: 30s  # still needed: retry cadence if the device stops answering
```

Continuous reads rank below every one-shot request, so writes still go out promptly. Use it for a device with a small register set that should be read with minimal latency. On a bus shared by several devices it keeps the line busy, so prefer normal polling there.

---

## Climate: a Real Template Platform

`climate: platform: template` exposes a full climate entity whose behaviour you supply. Each set action receives the requested value as `x`. With `optimistic: true` (the default) ESPHome applies the request immediately; with `optimistic: false` you report the real state yourself through `climate.template.publish`.

```yaml
climate:
  - platform: template
    id: heat_pump
    name: "Heat pump"
    optimistic: true
    sensor: room_temperature
    supported_modes:
      - "OFF"
      - HEAT
      - COOL
    visual:
      min_temperature: 16
      max_temperature: 30
      temperature_step: 0.5
    set_mode_action:
      - logger.log:
          format: "Mode requested: %d"
          args: ["(int) x"]
    set_target_temperature_action:
      - logger.log:
          format: "Target requested: %.1f"
          args: ["x"]
```

Other options: `humidity_sensor`, `supports_action`, `supported_fan_modes`, `custom_fan_modes`, `supported_swing_modes`, `supported_presets`, `custom_presets`, `set_target_temperature_low_action` plus `set_target_temperature_high_action` for two-point setpoints, `set_target_humidity_action`, and `on_control` (fires once per command with the full call as `x`).

When to pick which climate platform:

| Situation | Platform |
|-----------|----------|
| ESPHome itself decides heat/cool from a sensor and drives relays | `thermostat` |
| An external unit (UART AC, IR AC, heat pump controller) makes the decisions and ESPHome only relays commands and state | `template` (new) |
| A brand with an existing IR protocol component | `climate_ir_*` / `heatpumpir` |

---

## New Hardware

### `d01` PM2.5 sensor (UART)

Broadcasts a reading roughly every 1.4 seconds at 9600 baud.

```yaml
uart:
  rx_pin: GPIO4
  baud_rate: 9600

sensor:
  - platform: d01
    name: "PM2.5"
    filters:
      - lambda: return (x - 5.0) * 0.4;   # calibration knob: tune against a reference meter
```

### `sfa40` formaldehyde, temperature, humidity (Sensirion, I2C)

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

sensor:
  - platform: sfa40
    formaldehyde:
      name: "Formaldehyde"
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
```

Optional `address` and `update_interval`.

### `ds1603l` ultrasonic liquid level (UART)

Outputs distance in millimetres with `device_class: distance` and `state_class: measurement` by default.

```yaml
uart:
  - id: uart_level
    rx_pin: GPIO16
    tx_pin: GPIO17
    baud_rate: 9600

sensor:
  - platform: ds1603l
    uart_id: uart_level
    name: "Tank level distance"
    filters:
      - filter_out: nan
      - delta: 1.0
```

### `mk2pvrouter` PV surplus diverter telemetry (UART, TeleInfo style)

```yaml
uart:
  rx_pin: GPIO17
  baud_rate: 9600
  parity: EVEN
  data_bits: 7
  stop_bits: 1

mk2pvrouter:

sensor:
  - platform: mk2pvrouter
    tag: "P"
    name: "Grid power"
  - platform: mk2pvrouter
    tag: "D1"
    name: "Diversion rate load 1"
```

Route solar-diversion projects through Watt for the energy side.

### Tuya `water_heater` platform

Datapoint numbers are device specific. Read them from the Tuya MCU log before writing the config.

```yaml
water_heater:
  - platform: tuya
    name: "Water heater"
    switch_datapoint: 1
    target_temperature_datapoint: 2
    current_temperature_datapoint: 3
    mode_datapoint: 4
    eco_value: 0
    electric_value: 2
    supported_modes:
      - "OFF"
      - ECO
      - ELECTRIC
    visual:
      min_temperature: 30
      max_temperature: 75
      target_temperature_step: 1
```

### Hörmann HCP vent and half-open buttons

Adds to the `hoermann_hcp` cover from 2026.8.

```yaml
button:
  - platform: hoermann_hcp
    vent:
      name: "Garage vent"
    half_open:
      name: "Garage half open"
```

`hoermann_hcp_id` is only needed with more than one hub.

### `snapshot` display (host platform)

Renders a display to a BMP file on the build machine, useful for previewing LVGL or display layouts in docs and CI. The SDL display also gained `headless:`.

```yaml
host:

display:
  - platform: snapshot
    id: preview
    dimensions:
      width: 320
      height: 240
# trigger with:  - snapshot.take: { id: preview, filename: start_screen.bmp }
```

### Zigbee time on ESP32

`time: - platform: zigbee` (requires the `zigbee:` component) now works on ESP32 as well as nRF52. On ESP32 it re-requests time every `update_interval` (default 15 min).

---

## Networking

### Ethernet on a shared SPI bus

The bus must be a hardware SPI interface (`spi2` or `spi3`) with a `miso_pin`. With `spi_id:` set, the Ethernet block must not repeat `clk_pin`, `mosi_pin`, or `miso_pin`.

```yaml
spi:
  - id: spi_bus
    interface: spi2
    clk_pin: GPIO12
    mosi_pin: GPIO11
    miso_pin: GPIO13

ethernet:
  type: W5500
  spi_id: spi_bus
  cs_pin: GPIO10
  interrupt_pin: GPIO14
  reset_pin: GPIO9
```

### TCP send buffer (ESP32)

```yaml
network:
  tcp_send_buffer: 16kB   # 2880 to 65535 bytes; raise only when logs report the TCP buffer is full
```

A cheaper fix than `enable_high_performance` for a busy Bluetooth proxy.

### Improv serial on its own UART

```yaml
uart:
  - id: improv_uart
    tx_pin: GPIO17
    rx_pin: GPIO16
    baud_rate: 115200

improv_serial:
  uart_id: improv_uart
```

### Provisioning window closes completely

When the `provisioning:` window expires, the fallback WiFi AP and captive portal now shut down too. A config with an AP but no station credentials warns at validation. An unprovisioned device whose window timed out refuses new API clients until it is power cycled.

---

## API: Self-Describing Actions

`api: actions:` entries accept a `description`, and each variable can use a long form with `type`, `description`, and `example`. The short `name: type` form still works. Checked against the ESPHome source at tag 2026.9.1; the esphome.io API page had not been updated with these keys at the time of writing.

```yaml
api:
  actions:
    - action: set_brightness
      description: "Set the panel backlight"
      variables:
        level:
          type: float
          description: "Brightness from 0 to 1"
          example: "0.5"
      then:
        - light.turn_on:
            id: backlight
            brightness: !lambda 'return level;'
```

On ESP8266 the action name, variable names, descriptions, and examples must fit in 384 bytes per action.

`homeassistant.event` variables that look like lambda code are compiled as lambdas for now, with a warning. Tag them explicitly:

```yaml
- homeassistant.event:
    event: esphome.button_pressed
    data:
      value: !lambda 'return id(counter);'
```

`homeassistant.action` now also accepts plain static strings.

---

## Boards, Chips, Toolchains

| Target | Change |
|--------|--------|
| ESP8266 | Arduino core below 3.0.0 rejected; large RAM savings; native toolchain scaffolding (core 3.1.2, xtensa gcc 10.3) dormant until 2026.10.0 |
| ESP32 (all) | Custom eFuse MAC applied to all interfaces; ESP-IDF builds exclude more unused IDF components by default (WiFi and BT stacks too, when unused) |
| ESP32-P4 | `esp32_hosted` ESP-NOW passthrough (co-processor needs matching esp-hosted firmware); 2026.9.1 fixes P4 builds without WiFi/ESP-NOW/BLE |
| ESP32-S3 | Logger UART runs from the XTAL clock, which fixes garbled stack traces |
| ESP32-C2 | newlib nano printf disabled (2026.9.1) |
| ESP32-S31 | ADC, GPIO validation, `mipi_rgb` support; still a preview target |
| ESP32 Hosted | ESP-IDF 5.3 minimum |
| RP2040 / RP2350 | `rp2_ble_tracker` gains automation triggers and scan actions; faster X25519 for API encryption |
| LibreTiny | ISR-driven IR transmit with `non_blocking:` on BK7238 and RTL8720C; BK72xx deep sleep rejects `wakeup_pin_mode` |
| nRF52 | Watchdog timeout 30 s with the Adafruit bootloader (2026.9.1) |

Smaller additions without their own section: LVGL `list` and `table` widgets plus radial and conical gradients; `online_image` detects the format from Content-Type; `runtime_image` supports QOI; `epaper_spi` adds UC8179 panels (Waveshare 7.5" v2, Seeed reTerminal E1001); `sen6x` VOC/NOx algorithm tuning; `emontx` AP and F tags; `climate_ir_lg` `advanced_commands_support`; `mitsubishi_cn105` Fahrenheit; `sendspin` codec preference list; `audio_http` persistent ring buffer. Verify the keys against the component page before generating YAML for any of these.

---

## Package-Relative File Paths

A file option (font, image, certificate) whose path does not exist relative to the main config is now resolved relative to the YAML file that declares it. Packages can ship their own fonts and images next to the package file instead of forcing a fixed layout on the consumer.

---

## Home Assistant Side

- **Adopted devices and OTA keys.** If Home Assistant provisioned the API key at adoption, that key must be in the YAML before migrating OTA. Device Builder writes it automatically and shows it in the device menu. Generating a new key locks HA out of the device.
- **Action forms.** The new action `description`/`example` metadata gives HA a proper form in the action editor.
- **Timezone.** The on-device POSIX timezone parser is gone. HA 2026.3+ pushes a pre-parsed zone over the API; older HA falls back to the compile-time zone.
- **Media player.** The legacy `supports_pause` flag is no longer sent. Current HA uses feature flags and is unaffected.
- **MQTT light discovery** advertises `brightness: true` again, so HA sends brightness and colour separately.
- **Bluetooth proxy.** Congestion warnings fire once instead of flooding the log; a scan window above 600 ms alongside WiFi warns at config time; GATT clients re-register after `ble.disable`/`ble.enable`.

---

## Patch Release 2026.9.1 (September 29, 2026)

Bugfix only, no breaking changes.

- The OTA encryption key is kept even without `api:`, so safe-mode uploads work.
- The OTA plaintext warning no longer fires when web_server OTA is disabled.
- MIPI DSI lets ESP-IDF pick the DPHY PLL reference clock.
- ESP32 and RP2 print the previous crash report before the logger takes over.
- Windows console runs in UTF-8 during native `idf.py` builds (garbled output fixed).
- `web_server` masks the value, not only the state, of password `text` entities.
- `mipi_spi` DC/CS ordering regression for `spi_16` fixed.
- LVGL's `lv_conf.h` honours `esphome: build_flags`.
- SPI Ethernet receive frames moved to PSRAM.

---

## Breaking Changes Reference (compact)

| Area | Change | Migration |
|------|--------|-----------|
| OTA | `encryption:` added, cannot coexist with `password:`; password next to an API key warns | Two-step migration; new devices use bare `encryption:` |
| Modbus | `custom_command` -> `custom_pdu` (PDU only) | Drop the address byte |
| Modbus | `register_count`/`force_new_range` -> `reuse_previous_range` | `force_new_range: true` = `reuse_previous_range: false` |
| Modbus | `skip_updates` retired | Second controller with a slower `update_interval` |
| Modbus | Holding-register switch/output `offset` byte-accurate, odd offsets rejected | Re-verify target registers |
| Modbus | Switch `write_lambda` return no longer changes displayed state | Publish state explicitly |
| Modbus | `address: 0` rejected without `allow_broadcast_read` | Use the real unit address |
| API | Lambda-looking `homeassistant.event` strings | Tag with `!lambda` |
| ESP32 | Custom eFuse MAC applies to all interfaces | Update reservations or set `ignore_efuse_custom_mac: true` |
| ESP8266 | Arduino core below 3.0.0 rejected | Remove the pin or use 3.1.2 |
| ESP32 Hosted | ESP-IDF 5.3 minimum | Remove older IDF pins |
| UART | Required settings validated at config time for several components | Set baud/parity on the bus |
| Time | `set_timezone()` and the POSIX parser removed | YAML `timezone:` or HA push |

---

## Developer-Facing Changes (external components, lambdas)

If you only write YAML, skip this section.

- Removed: `EntityBase::get_device_class()`, `get_icon()`, `get_unit_of_measurement()` (use the `_to`/`_ref` variants); `gamma_correct()`/`gamma_uncorrect()` (use the `LightState` LUT helpers); `wifi_ssid()` (use `wifi_ssid_to()`); `get_eth_mac_address_pretty()`; `AsyncWebServerRequest::url()` (use `url_to()`); `ModbusDevice::waiting_for_response()` (use `ready_for_immediate_send()`); string overloads of `make_name_with_suffix()`.
- Deprecated until 2027.3.0: `UARTDevice::check_uart_settings()`, the `ModbusCommandItem` and `queue_command()` family, `IntervalSyncer::set_write_interval()` (it is now a `PollingComponent`; use `set_update_interval()`).
- ESP-IDF builds exclude more built-in IDF components by default (esp_wifi, bt, esp_phy, esp_driver_i2c, esp_driver_ledc, esp-tls, json, esp_http_server and others), and the mbedTLS certificate bundle is only built on request. External components call `esp32.include_builtin_idf_component("<name>")` or `esp32.require_certificate_bundle()` in `to_code`; users can add `esp32: framework: advanced: include_builtin_idf_components:`.
- `runtime_image` keeps its decoder allocated between decodes, a small persistent RAM cost on tight devices.

---

## Deprecation Timeline

| Version | What goes away |
|---------|----------------|
| 2026.10.0 | Native ESP8266 toolchain is now released and default; see the October reference |
| 2026.11.0 | Ethernet `clk_mode` |
| 2027.1.0 | Legacy `image:` keys from before the 2026.7 platform migration |
| 2027.2.0 | `esp32_ble_id` and `voc`/`nox` aliases from 2026.8 |
| 2027.3.0 | Plaintext OTA from pre-2026.9 firmware; Modbus `custom_command` auto-migration, `skip_updates`, `force_new_range`, `register_count` shims; untagged lambda-looking `homeassistant.event` strings; LED strip `rgb_order`/`is_rgbw`/`is_wrgb` |

---

## What Did NOT Change (reassurance)

- `api: encryption: key:` itself is unchanged; existing keys keep working.
- Devices that keep `password:` continue to update normally until 2027.3.0. The migration is recommended, not forced, in 2026.9.
- Check the UART validation checklist even for non-Modbus sensors. Light and display guidance here is September-specific; October has further changes.
- `web_server` OTA keeps working and is the recovery path when the key is lost.

---

## Recipes (complete worked examples)

### Recipe 1: New ESP32-C3 sensor with encrypted OTA from day one

```yaml
esphome:
  name: hallway-climate
  friendly_name: Hallway Climate

esp32:
  variant: esp32c3
  board: esp32-c3-devkitm-1
  framework:
    type: esp-idf

logger:

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    encryption:          # inherits the api: key; flash once over USB, then OTA is encrypted

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    password: !secret fallback_ap_password

captive_portal:

i2c:
  sda: GPIO6
  scl: GPIO7

sensor:
  - platform: sht4x
    temperature:
      name: "Temperature"
      filters:
        - offset: 0.0    # calibration knob
    humidity:
      name: "Humidity"
```

`secrets.yaml` needs `api_encryption_key`, `wifi_ssid`, `wifi_password`, `fallback_ap_password`. No OTA secret.

### Recipe 2: Migrating an adopted device from OTA password to encryption

1. Copy the API key Home Assistant uses for this device into `secrets.yaml` (Device Builder shows it in the device menu). Do not generate a new one.
2. Flash 2026.9.x with this OTA block (unchanged except for the ESPHome version):

```yaml
ota:
  - platform: esphome
    password: !secret ota_password
```

3. Confirm the device is online in HA, then change the block and flash again:

```yaml
ota:
  - platform: esphome
    encryption:
```

4. Remove `ota_password` from `secrets.yaml`.

### Recipe 3: Template climate driving a UART heat pump

```yaml
uart:
  id: hp_uart
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 9600

sensor:
  - platform: dallas_temp
    id: room_temperature
    name: "Room temperature"

climate:
  - platform: template
    id: heat_pump
    name: "Heat pump"
    optimistic: true
    sensor: room_temperature
    supported_modes:
      - "OFF"
      - HEAT
      - COOL
    visual:
      min_temperature: 16
      max_temperature: 30
      temperature_step: 1
    set_mode_action:
      - uart.write:
          id: hp_uart
          data: !lambda 'return {0xAA, 0x01, (uint8_t) x};'   # replace with your unit's frame format
    set_target_temperature_action:
      - uart.write:
          id: hp_uart
          data: !lambda 'return {0xAA, 0x02, (uint8_t) x};'
```

The frame bytes are placeholders for the unit's real protocol. When the unit reports its own state back over UART, parse it and call `climate.template.publish` with `optimistic: false` instead.

(Requires `one_wire:` configured for `dallas_temp`; omitted for brevity.)

### Recipe 4: SDM120 energy meter after the Modbus renames

```yaml
uart:
  id: mod_uart
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 9600
  stop_bits: 1

modbus:
  id: modbus_bus
  uart_id: mod_uart

modbus_controller:
  - id: sdm120
    address: 0x2
    modbus_id: modbus_bus
    update_interval: 10s
  - id: sdm120_slow
    address: 0x2
    modbus_id: modbus_bus
    update_interval: 5min

sensor:
  - platform: modbus_controller
    modbus_controller_id: sdm120
    name: "Voltage"
    register_type: read
    address: 0x0000
    value_type: FP32
    unit_of_measurement: V
    device_class: voltage
  - platform: modbus_controller
    modbus_controller_id: sdm120_slow
    name: "Total active energy"
    custom_pdu: [0x4, 0x1, 0x56, 0x00, 0x02]
    value_type: FP32
    unit_of_measurement: kWh
    device_class: energy
    state_class: total_increasing
    accuracy_decimals: 1
```

### Recipe 5: Tank level with the DS1603L

```yaml
uart:
  - id: uart_level
    rx_pin: GPIO16
    tx_pin: GPIO17
    baud_rate: 9600

sensor:
  - platform: ds1603l
    uart_id: uart_level
    id: tank_distance
    name: "Tank distance"
    filters:
      - filter_out: nan
      - delta: 1.0

  - platform: template
    name: "Tank level"
    unit_of_measurement: "%"
    accuracy_decimals: 0
    update_interval: 30s
    lambda: |-
      const float full_mm = 1200.0;   // calibration knob: tank height in mm
      if (isnan(id(tank_distance).state)) return NAN;
      return clamp((id(tank_distance).state / full_mm) * 100.0f, 0.0f, 100.0f);
```

The DS1603L is mounted under the tank and measures liquid height from below, so the distance equals the fill height. Measure the full height once and set `full_mm`.

### Recipe 6: W5500 Ethernet sharing the SPI bus with a display

```yaml
spi:
  - id: spi_bus
    interface: spi2
    clk_pin: GPIO12
    mosi_pin: GPIO11
    miso_pin: GPIO13

ethernet:
  type: W5500
  spi_id: spi_bus
  cs_pin: GPIO10
  interrupt_pin: GPIO14
  reset_pin: GPIO9

display:
  - platform: ili9xxx
    model: ILI9341
    spi_id: spi_bus
    cs_pin: GPIO15
    dc_pin: GPIO16
    lambda: |-
      it.print(0, 0, id(font_main), "Online");
```

Each device on the bus needs its own CS pin. Add a `font:` with id `font_main` for the display.

---

## Links

- Changelog: https://esphome.io/changelog/2026.9.0/
- OTA (encryption and migration): https://esphome.io/components/ota/esphome/
- Modbus controller: https://esphome.io/components/modbus_controller/
- Template climate: https://esphome.io/components/climate/template/
- Ethernet: https://esphome.io/components/ethernet/
