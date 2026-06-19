# ESPHome 2026.6.0 - Complete Release Reference (June 2026)

**Release date:** June 2026 (2026.6.0 on June 3, patch 2026.6.1 on June 19)
**Source:** https://esphome.io/changelog/2026.6.0/

When the user is on this version, upgrading TO it, or asking "what's new", read this file BEFORE generating YAML. New components, a platform-wide WiFi default change, and several renamed/removed keys invalidate older patterns.

---

## What landed in 2026.6.0 at a glance

Nine themes worth knowing before you upgrade:

1. **The legacy dashboard is gone.** ESPHome Device Builder reached 1.0.0 and replaces the old in-tree dashboard, which is retired. As of 2026.6.0 the Device Builder is the dashboard bundled by default in the official Home Assistant ESPHome add-on. The 2026.5.0 "Use new Device Builder Preview" toggle no longer exists.
2. **ESP8266 WiFi security default flipped to WPA2.** `min_auth_mode` now defaults to `WPA2` on ESP8266, matching ESP32. Devices on legacy WPA-only (TKIP) routers must pin `min_auth_mode: WPA` or they stop associating. This is the broadest change in the release because roughly 40% of installs run on ESP8266.
3. **`enable_on_boot: false` finally frees its memory.** WiFi reclaims about 15-30 KB and ethernet about 3-8 KB of DMA-capable internal SRAM when disabled at boot, via a lazy-init path. Ethernet also gains enable/disable actions and connected/enabled conditions, matching the WiFi automation surface.
4. **A new `motion` IMU framework.** A generic hub component exposes acceleration, angular rate, and derived pitch/roll, plus auto-calibration actions, with two concrete drivers: Bosch BMI270 and STMicro LSM6DS.
5. **Audio stack modernization.** Zero-copy ring buffers across the critical audio paths, an any-bit-depth mixer (8/16/24/32), resampler bit-depth pass-through, a new `router` speaker for live output switching, and optional PSRAM task stacks.
6. **New hardware support.** PCM5122 stereo I2S DAC, XDB401 I2C pressure sensor, FTDI and Prolific USB-serial drivers, and a new Waveshare AMOLED display panel.
7. **Configuration and tooling.** YAML frontmatter for arbitrary file metadata, a top-level `build_flags` that finally works on native ESP-IDF, `esphome config --no-defaults`, Codeberg git URLs, and `github://` framework sources.
8. **ESP-IDF 6 groundwork.** Native RISC-V clang-tidy, float-to-double promotion fixes, and sdkconfig changes that set up upcoming ESP-IDF 6 support. No YAML change required.
9. **DLMS and DSMR smart-meter overhaul.** DLMS moves to the external `dlms_parser` library with dynamic OBIS codes and optional decryption keys; DSMR gains EON Hungary support and moves one entity from `sensor:` to `text_sensor:`.

---

## Upgrade Checklist (run through this BEFORE flashing 2026.6.0)

- [ ] ESP8266 on a legacy WPA-only (TKIP) router? -> add `min_auth_mode: WPA` under `wifi:` or the device stops associating
- [ ] Use the `dsmr` `electricity_switch_position` sensor? -> move it from `sensor:` to `text_sensor:`
- [ ] Use a `nextion` display with `dump_device_info: true`? -> remove that option (device info is always logged now)
- [ ] Still loading components from a `custom_components/` folder? -> migrate them to `external_components:`
- [ ] `time:` with `platform: homeassistant` and an explicit `timezone:`? -> Home Assistant no longer overrides your configured zone; drop the local `timezone:` if you relied on HA overriding a stale value
- [ ] Use the `dlms_meter` `provider:` option? -> it is now ignored with a deprecation warning and will be removed in 2026.11.0
- [ ] Run `neopixelbus` on an ESP32? -> it is deprecated on ESP32; prefer `esp32_rmt_led_strip` (see `lights.md`)
- [ ] External component calls `mark_failed("...")` / `status_set_error("...")`? -> wrap the string in `LOG_STR(...)`
- [ ] External component uses `cv.only_with_esp_idf` or `CORE.using_esp_idf`? -> use `cv.only_on_esp32` / `CORE.is_esp32`
- [ ] Lambda reads `text_sensor->raw_state`? -> use `text_sensor->get_raw_state()`
- [ ] Lambda references `mipi_dsi::MIPI_DSI`? -> rename to `mipi_dsi::MipiDsi`

---

## ESPHome Device Builder Replaces the Legacy Dashboard

The Device Builder shipped as an opt-in beta in 2026.5.0 and reached 1.0.0 in 2026.6.0. The legacy in-tree dashboard is retired, and the Device Builder is now the dashboard bundled by default in the Home Assistant ESPHome add-on. There is no YAML impact; this is a tooling change.

What it adds over the legacy text-only dashboard:

- Visual component and automation builder alongside a CodeMirror YAML editor, with a device navigator sidebar.
- Component catalog with dependency resolution and a per-board pin info viewer that maps GPIO capabilities.
- Firmware job queue with progress, history, and cancel for compile / install / clean.
- Remote builder: one instance can offload OTA builds to another over a peer-paired link.
- Labels, areas, editable friendly name, device cloning, and multi-select bulk actions.
- Out-of-sync detection (encryption-state badge, version and config-hash diagnostics).
- YAML diff view, cross-config search, and a command palette.
- First-run WiFi onboarding and an expanded install-method dialog (Web Serial, server-side USB, `web.esphome.io`, manual `.bin`).

The 2026.5.0 "Use new Device Builder Preview" toggle is gone. Device Builder lives in the `device-builder` (backend) and `device-builder-frontend` (UI) repositories. PR #16989 and the device-builder 1.0.x bumps.

---

## ESP8266 WiFi Security Raised to WPA2 (breaking)

ESP8266 now defaults to `min_auth_mode: WPA2`, matching the ESP32 default. A deprecation warning has been printed on every ESP8266 config without an explicit `min_auth_mode` since 2026.1.

Configs connecting to modern WPA2/WPA3 access points need no change. Devices on legacy WPA-only (TKIP) routers must pin the old behavior:

```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  min_auth_mode: WPA   # only needed for legacy WPA/TKIP routers
```

PR #16682.

---

## WiFi and Ethernet Free Their Memory When Disabled at Boot

`enable_on_boot: false` previously skipped only the `start()` call, leaving the full driver resident in DMA-capable internal SRAM. The heavy allocation work is now lazy: a dormant interface costs zero internal RAM until it is actually enabled.

> Important: WiFi and ethernet still cannot be enabled at the same time in one configuration. ESPHome rejects a config that defines both. Use one interface per device. The two snippets below are alternatives, not a combined config.

WiFi brought up on demand instead of at boot:

```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  enable_on_boot: false   # frees ~15-30 KB internal SRAM until wifi.enable runs
```

Ethernet, with the new lifecycle automation surface:

```yaml
ethernet:
  type: W5500
  clk_pin: GPIO18
  mosi_pin: GPIO23
  miso_pin: GPIO19
  cs_pin: GPIO5
  interrupt_pin: GPIO4
  enable_on_boot: false   # frees ~3-8 KB internal SRAM until ethernet.enable runs

button:
  - platform: template
    name: "Bring up Ethernet"
    on_press:
      - ethernet.enable
      # also: ethernet.disable; new conditions: ethernet.connected, ethernet.enabled
```

Field test on an ESP32-S3 with W5500 ethernet, I2S audio, and a bluetooth_proxy: free internal SRAM under peak load went from about 14 KB to about 32 KB. ESPHome describes this as groundwork toward eventually supporting both interfaces in one configuration, but that is not possible yet (see the exclusivity note above). The W5500 SPI driver additionally moved bulk transfers to an interrupt-driven DMA path, cutting ethernet-task CPU on a 48 kHz 24-bit FLAC stream from about 5% to about 3.8%. PRs #16606, #16607, #16596.

---

## New `motion` IMU Framework

The `motion` component is a hub: a driver platform talks to the chip, and a `sensor: platform: motion` exposes each value you want. Derived `pitch` and `roll` come from the framework, and there are actions for level and heading calibration.

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

# Driver platform - talks to the chip (BMI270 shown; lsm6ds is identical shape)
motion:
  - platform: bmi270
    id: my_imu
    address: 0x68            # BMI270 default; LSM6DS defaults to 0x6A (some boards 0x6B)
    accelerometer_range: 4G
    gyroscope_range: 2000DPS

# Exposed values - one sensor per measurement
sensor:
  - platform: motion
    type: acceleration_x
    name: "Accel X"
  - platform: motion
    type: gyroscope_x
    name: "Gyro X"
  - platform: motion
    type: pitch
    name: "Pitch"
  - platform: motion
    type: roll
    name: "Roll"
```

`type:` accepts the per-axis acceleration and gyroscope values plus the derived `pitch` / `roll`. The hub supports `axis_map` and a 3x3 `transform_matrix` to remap or invert physical axes, plus `update_interval`.

Calibration actions remap the axes so a mounted board reads level / true heading:

```yaml
button:
  - platform: template
    name: "Calibrate Level"
    on_press:
      - motion.calibrate_level:
          id: my_imu
          save: true            # persist the matrix to NVS flash
          on_success:
            - logger.log: "Level calibration succeeded"
          on_error:
            - logger.log: "Level calibration failed"
# Also: motion.calibrate_heading, motion.clear_calibration
```

Drivers: **BMI270** (used in M5Stack Tab5 and Espressif EchoEar, PR #16202) and **STMicro LSM6DS3TR-C** (used in the Seeed ReTerminal D1001, PR #16232). Hub PR #16226.

---

## Audio Stack Modernization

### Any-bit-depth mixer and the new `router` speaker

The mixer speaker now accepts 8, 16, 24, or 32 bits per sample, lifting the last 16-bit-only restriction. The new `router` speaker switches between output speakers at runtime, for example live SPDIF and analog I2S switching from a `select` entity.

```yaml
speaker:
  # Two physical outputs
  - platform: i2s_audio
    id: analog_speaker_id
    i2s_audio_id: i2s_analog
    i2s_dout_pin: GPIO22
    dac_type: external
  - platform: i2s_audio
    id: spdif_speaker_id
    i2s_audio_id: i2s_spdif
    i2s_dout_pin: GPIO25
    dac_type: external
    # mode: spdif    # (2026.5.0 feature) for optical output

  # Router presents a single virtual speaker and routes to one output at a time
  - platform: router
    id: router_id
    output_speakers:
      - spdif_speaker_id
      - analog_speaker_id
    bits_per_sample: 16      # 8-32
    num_channels: 2          # 1 or 2
    sample_rate: 48000       # 8000-... Hz

select:
  - platform: template
    name: "Audio Output"
    optimistic: true
    options: ["SPDIF", "Analog"]
    on_value:
      - router.speaker.switch_output:
          id: router_id
          target_speaker: !lambda |-
            return x == "SPDIF" ? id(spdif_speaker_id) : id(analog_speaker_id);
```

### Zero-copy ring buffers and PSRAM task stacks

Internally, the allocate-and-copy `AudioSourceTransferBuffer` was replaced with a zero-copy `RingBufferAudioSource` across the resampler, the speaker media-player decoder, `micro_wake_word`, and `voice_assistant`, removing one allocation and one copy per audio chunk. No YAML change. The resampler also now passes the input bit depth through unchanged by default, letting the faster mixer do any conversion.

Audio task stacks can move to PSRAM to save internal SRAM on the ESP32-S3:

```yaml
micro_wake_word:
  task_stack_in_psram: true   # saves ~3 KB internal SRAM, no measurable perf cost
```

`task_stack_in_psram` is now consistent across `audio_file`, `audio_http`, `mixer`, `resampler`, `sendspin`, and the speaker media player. Backed by esp-audio-libs v3.2.x. PRs #16524, #16592, #16560, #16564, #16595, #16597, #16632, #16628, #16892.

---

## New Hardware Support

### PCM5122 audio DAC

Texas Instruments stereo I2S DAC popular on Raspberry Pi HATs, with mute, digital volume, and four configurable GPIO pins (numbers 3-6) exposed through the standard pin schema.

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

i2s_audio:
  - id: i2s_output
    i2s_lrclk_pin: GPIO25
    i2s_bclk_pin: GPIO26

audio_dac:
  - platform: pcm5122
    id: pcm5122_dac
    address: 0x4D            # default
    bits_per_sample: 16bit   # 16bit / 24bit / 32bit

speaker:
  - platform: i2s_audio
    i2s_audio_id: i2s_output
    id: speaker_id
    i2s_dout_pin: GPIO22
    dac_type: external
    audio_dac: pcm5122_dac

# A DAC GPIO can drive, for example, an external amplifier enable pin
switch:
  - platform: gpio
    name: "Amplifier Enable"
    pin:
      pcm5122: pcm5122_dac
      number: 4              # must be 3-6
      mode:
        output: true
    restore_mode: RESTORE_DEFAULT_ON
```

PR #15709.

### XDB401 pressure sensor

I2C pressure and temperature from the XIDIBEI XDB401. Pressure is reported in Pascal; scale it with a filter.

```yaml
sensor:
  - platform: xdb401
    update_interval: 1s
    address: 0x7F             # default
    pressure_range_bar: 10    # your sensor model's range (1, 2, 10, ...)
    temperature:
      name: "Temperature"
      accuracy_decimals: 2
    pressure:
      name: "Pressure"
      unit_of_measurement: "bar"
      accuracy_decimals: 2
      filters:
        - multiply: 0.00001   # Pa -> bar
```

PR #15108.

### USB-serial drivers (FTDI and Prolific)

The `usb_uart` component gained FTDI FT23XX-family and Prolific PL2303-family drivers. A configured channel acts as a `uart` anywhere a UART is required. Chip type is auto-detected from the USB descriptor; multi-channel chips appear as separate channels.

```yaml
usb_uart:
  - type: ft23xx            # also: pl2303, pl2303gc/gb/gt/gl/ge/gs, cp210x, ch34x, ...
    channels:
      - id: usb_serial_1
        baud_rate: 9600
        buffer_size: 1024
        # data_bits / stop_bits / parity available

# Use the channel like any UART
text_sensor:
  - platform: ...
    uart_id: usb_serial_1
```

PRs #14587 (FTDI), #16885 (Prolific). New display: Waveshare ESP32-S3-Touch-AMOLED-2.16 on `mipi_spi` (PR #16887).

---

## Configuration and Tooling

### YAML frontmatter

A leading `---`-separated YAML document is now treated as opaque metadata, stripped before validation, and captured per file. Tooling (including the Device Builder) can consume arbitrary fields like author, version, and labels.

```yaml
author: Jane Doe
version: 1.0.0
labels: [office, climate]
---
esphome:
  name: my-node
```

PR #16552.

### Top-level `build_flags` on native IDF

`esphome.build_flags` applies compiler flags on both PlatformIO and native ESP-IDF. The older `platformio_options.build_flags` was PlatformIO-only, so users on native IDF targets (ESP32-P4, ESP32-H2) needed this.

```yaml
esphome:
  name: my-node
  build_flags:
    - "-DMY_CUSTOM_DEFINE=1"
```

PR #16629.

### Other tooling

- `esphome config --no-defaults` prints only the user-supplied config after substitutions and packages resolve, with no injected schema defaults. Useful for diffing and minimal bug reports. PR #16718.
- `codeberg://owner/repo/path/file.yaml` is now a supported source for `dashboard_import` and short-form `packages`, alongside `github://` and `gitlab://`. PR #16501.
- `esp32.framework.source` accepts `github://owner/repo@ref` (and `.git@ref`), doing a shallow clone with submodules so pre-release ESP-IDF can be tested. PR #16639.
- WiFi SSIDs are now redacted in `esphome config` output alongside passwords, driven by `cv.sensitive()`. Pass `--show-secrets` to bypass. PR #16690.
- The `logs` command gained `--states` / `--no-states` to control whether state changes appear in the stream. PR #16746.

---

## Other Notable Features

```yaml
# Cycle light effects without hardcoding their names (#16491)
button:
  - platform: template
    name: "Next Effect"
    on_press:
      - light.effect.next:
          id: my_light
          include_none: true   # let the cycle pass through "no effect"
# Also: light.effect.previous. The light must have at least one effect.

# RP2040 / RP2350 variant selection (#16602)
rp2040:
  board: rpipicow
  variant: rp2350           # auto-derived from the board if omitted

# ESP32 flash mode and frequency (#16920)
esp32:
  board: esp32dev
  flash_mode: dio
  flash_frequency: 80MHz

# esp_hosted transport buffers in PSRAM, fixes boot asserts on tight P4 + LVGL (#16627)
esp32_hosted:
  use_psram: true

# Mitsubishi CN105 swing modes (#15653)
climate:
  - platform: mitsubishi_cn105
    name: "AC"
    # vertical / horizontal / both swing now supported

# LVGL meter arcs can be rounded (#16669)
# lvgl: ... arc: ... rounded: true
```

Lambda light effects now receive the light as `it`, matching addressable effects (#16815). LVGL config validation is up to 4.5x faster after a schema hot-path rework (#16567, #16569, #16614, #16615, #16633), which makes every save in the Device Builder snappier. Zephyr IPv6 networking landed on nRF52 as the first step toward OpenThread there (#16336).

---

## DLMS and DSMR Smart Meters

The `dlms_meter` component was rebuilt on the external `dlms_parser` library:

- Define custom sensors, text sensors, or binary sensors by OBIS code (for example `"1-0:99.99.9"`) instead of a fixed property list.
- Binary sensor support is new.
- The decryption key is now optional; plaintext meters work directly.
- The 2400-baud requirement is gone; configure the UART to whatever your meter speaks.
- New options: `auth_key`, `custom_patterns`, `skip_crc`, `receive_timeout`.

The legacy schema still validates. The `provider:` key is ignored with a deprecation warning and will be removed in 2026.11.0. PR #15458.

DSMR added EON Hungary meter support, custom auth keys, and automatic hex-string detection in equipment-ID fields. Note the breaking move: `electricity_switch_position` is now a `text_sensor:` (Hungarian meters emit it as a string like `ON`). PR #16561.

---

## Breaking Changes Reference (compact)

| Area | Change | Migration |
|------|--------|-----------|
| WiFi (ESP8266) | `min_auth_mode` default `WPA` -> `WPA2` | Pin `min_auth_mode: WPA` only for legacy WPA/TKIP routers |
| DSMR | `electricity_switch_position` moved platforms | Declare it under `text_sensor:` |
| DLMS meter | Rebuilt on `dlms_parser`; `provider:` ignored | Remove `provider:` (removal in 2026.11.0); legacy schema still works |
| Nextion | `dump_device_info` removed | Delete the key; device info is always logged |
| HA time | Explicit `timezone:` no longer overridden by HA | Remove local `timezone:` if you relied on HA overriding it |
| Core | `custom_components/` auto-loader removed | Use `external_components:` |
| ESP32 | `neopixelbus` deprecated on ESP32 | Prefer `esp32_rmt_led_strip` |
| Core (config dump) | WiFi SSID now redacted | Pass `--show-secrets` to see it |

---

## Developer-Facing Breaking Changes (external components, lambdas)

If you only write YAML, skip this section.

- **`Component::mark_failed` / `status_set_error` `const char *` overloads removed.** Use the `const LogString *` overloads via `LOG_STR("...")`. PR #16680.
- **`cv.only_with_esp_idf` and `CORE.using_esp_idf` removed.** Use `cv.only_on_esp32` / `CORE.is_esp32`; use `CORE.using_toolchain_esp_idf` for the rare actual toolchain check. PR #16681.
- **`text_sensor::TextSensor::raw_state` public member removed.** Use `get_raw_state()`. PR #16683.
- **`mipi_dsi::MIPI_DSI` renamed to `mipi_dsi::MipiDsi`.** Runtime behavior unchanged. PR #16837.

  ```cpp
  // Before
  auto *display = static_cast<mipi_dsi::MIPI_DSI *>(...);
  // After
  auto *display = static_cast<mipi_dsi::MipiDsi *>(...);
  ```

- **`nfc::format_uid(span)` / `nfc::format_bytes(span)` heap helpers removed.** Use the stack-buffer variants `nfc::format_uid_to(buf, span)` / `nfc::format_bytes_to(buf, span)` with `FORMAT_UID_BUFFER_SIZE` / `FORMAT_BYTES_BUFFER_SIZE`. PR #16684.
- **`seq<>` and `gens<>` tuple-unpack templates removed** from `core/automation.h`. Use `std::index_sequence` / `std::index_sequence_for`. PR #16685.
- **`audio::scale_audio_samples` deprecated.** Switch to `esp_audio_libs::gain::apply` (Q31 scale factor, byte buffers, explicit `bytes_per_sample`). Removal in 2026.12.0. PR #16831.
- **`cv.sensitive()` schema marker.** External component schemas should wrap sensitive fields with `cv.sensitive(...)` for redaction. The regex fallback stays as a bridge through 2026.12.0. PR #16690.

ESP-IDF 6 groundwork landed across the codebase (native RISC-V clang-tidy, float-to-double promotion fixes, sdkconfig pinned to newlib). This is preparation only; ESP-IDF 6 is not yet the default framework. PRs #16809, #16812, #16823, #16850.

---

## What Did Not Change (reassurance)

- **All sensor/binary_sensor/switch/light platforms keep their existing YAML.** The big changes are additive (new `motion`, `router`, `pcm5122`, `xdb401`, `usb_uart` platforms) or default flips with a documented escape hatch.
- **ESP32 WiFi configs are unaffected** by the WPA2 default; only ESP8266 changed, and only on legacy WPA/TKIP routers.
- **`wifi:` / `ethernet:` configs without `enable_on_boot`** behave as before. The RAM reclaim only applies when you explicitly set `enable_on_boot: false`.
- **The mixer, resampler, and existing speakers** keep their YAML. Any-bit-depth and zero-copy buffers are internal.
- **Existing `dlms_meter` and `dsmr` configs** still validate (DSMR's `electricity_switch_position` is the one entity that must move).
- **PlatformIO remains the default build path.** ESP-IDF 6 work is groundwork, not a default change.

---

## Recipes (complete worked examples)

### Recipe 1: Tilt and orientation sensor (motion + BMI270)

**Goal:** report pitch, roll, and live acceleration from a BMI270 to Home Assistant, with a button to calibrate "level" for however the board is mounted.

```yaml
esphome:
  name: tilt-sensor
  friendly_name: Tilt Sensor

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:

i2c:
  sda: GPIO8
  scl: GPIO9

motion:
  - platform: bmi270
    id: imu
    accelerometer_range: 4G
    gyroscope_range: 2000DPS

sensor:
  - platform: motion
    type: pitch
    name: "Pitch"
  - platform: motion
    type: roll
    name: "Roll"
  - platform: motion
    type: acceleration_z
    name: "Accel Z"

button:
  - platform: template
    name: "Calibrate Level"
    on_press:
      - motion.calibrate_level:
          id: imu
          save: true
          on_success:
            - logger.log: "Mounted orientation saved as level"
```

### Recipe 2: HiFi media player with PCM5122 DAC

**Goal:** a clean line-out media player using the TI PCM5122, with one DAC GPIO switching an external amplifier on and off with playback.

```yaml
esphome:
  name: hifi-player
  friendly_name: HiFi Player

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf

psram:
  mode: octal
  speed: 80MHz

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:

i2c:
  sda: GPIO8
  scl: GPIO9

i2s_audio:
  - id: i2s_out
    i2s_lrclk_pin: GPIO13
    i2s_bclk_pin: GPIO12

audio_dac:
  - platform: pcm5122
    id: dac
    bits_per_sample: 24bit

speaker:
  - platform: i2s_audio
    id: line_out
    i2s_audio_id: i2s_out
    i2s_dout_pin: GPIO14
    dac_type: external
    audio_dac: dac
  # Mixer combines the media and announcement streams into the single DAC output
  - platform: mixer
    id: mixer_out
    output_speaker: line_out
    source_speakers:
      - id: media_input
      - id: announce_input
  - platform: resampler
    id: media_resampler
    output_speaker: media_input
  - platform: resampler
    id: announce_resampler
    output_speaker: announce_input

switch:
  - platform: gpio
    id: amp_enable
    pin:
      pcm5122: dac
      number: 4
      mode:
        output: true

media_player:
  - platform: speaker
    name: "HiFi Player"
    task_stack_in_psram: true   # 2026.6.0: task stack in PSRAM
    media_pipeline:
      speaker: media_resampler
      num_channels: 2
    announcement_pipeline:
      speaker: announce_resampler
      num_channels: 1
```

### Recipe 3: Live SPDIF / analog output switcher (router speaker)

**Goal:** one media player whose audio can be routed live between an optical SPDIF output and an analog I2S DAC, selectable from a Home Assistant dropdown.

```yaml
esphome:
  name: audio-router
  friendly_name: Audio Router

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:

i2s_audio:
  - id: i2s_analog
    i2s_lrclk_pin: GPIO25
    i2s_bclk_pin: GPIO26
  - id: i2s_spdif
    i2s_lrclk_pin: GPIO27
    i2s_bclk_pin: GPIO14

speaker:
  - platform: i2s_audio
    id: analog_out
    i2s_audio_id: i2s_analog
    i2s_dout_pin: GPIO22
    dac_type: external
  - platform: i2s_audio
    id: spdif_out
    i2s_audio_id: i2s_spdif
    i2s_dout_pin: GPIO21
    dac_type: external
    mode: spdif

  - platform: router
    id: out_router
    output_speakers:
      - analog_out
      - spdif_out
    bits_per_sample: 16
    num_channels: 2
    sample_rate: 48000

  # Media player pipelines feed the router, which then routes to one output
  - platform: mixer
    id: mixer_out
    output_speaker: out_router
    source_speakers:
      - id: media_input
      - id: announce_input
  - platform: resampler
    id: media_resampler
    output_speaker: media_input
  - platform: resampler
    id: announce_resampler
    output_speaker: announce_input

select:
  - platform: template
    name: "Audio Output"
    optimistic: true
    restore_value: true
    options: ["Analog", "SPDIF"]
    initial_option: "Analog"
    on_value:
      - router.speaker.switch_output:
          id: out_router
          target_speaker: !lambda |-
            return x == "SPDIF" ? id(spdif_out) : id(analog_out);

media_player:
  - platform: speaker
    name: "Routed Player"
    media_pipeline:
      speaker: media_resampler
      num_channels: 2
    announcement_pipeline:
      speaker: announce_resampler
      num_channels: 1
```

### Recipe 4: Low-RAM node that keeps WiFi off until needed

**Goal:** keep WiFi compiled in but disabled at boot so the device reclaims 15 to 30 KB of internal SRAM for other work (large LVGL UI, audio buffers, BLE), then bring the radio up on demand. Uses YAML frontmatter to tag the file for the Device Builder.

(WiFi and ethernet cannot coexist in one config, so this is a single-interface WiFi example. For a wired device, use `ethernet:` with its own `enable_on_boot` and the `ethernet.enable` / `ethernet.disable` actions instead.)

```yaml
author: Ops Team
version: 1.0.0
labels: [low-ram]
---
esphome:
  name: lowram-node
  friendly_name: Low RAM Node

esp32:
  board: esp32-c3-devkitm-1
  framework:
    type: esp-idf

# WiFi stays compiled in but costs no internal RAM until enabled
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  enable_on_boot: false

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:

# Bring WiFi up (or down) on demand: a button here, but a schedule or a
# sensor threshold works the same way
button:
  - platform: template
    name: "Connect WiFi"
    on_press:
      - wifi.enable
  - platform: template
    name: "Disconnect WiFi"
    on_press:
      - wifi.disable
```

---

## Links

- Full changelog: https://esphome.io/changelog/2026.6.0/
- Motion / IMU: https://esphome.io/components/motion/
- Router speaker: https://esphome.io/components/speaker/router/
- PCM5122 DAC: https://esphome.io/components/audio_dac/pcm5122/
- USB UART: https://esphome.io/components/usb_uart/
