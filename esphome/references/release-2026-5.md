# ESPHome 2026.5.0 - Complete Release Reference (May 2026)

**Release date:** May 2026 | **PRs:** 395
**Source:** https://esphome.io/changelog/2026.5.0/

When the user is on this version, upgrading TO it, or asking "what's new", read this file BEFORE generating YAML. New components and renamed keys invalidate older patterns.

---

## What landed in 2026.5.0 at a glance

The release is unusually broad. Ten themes worth knowing about before you upgrade:

1. **ESPHome Device Builder (Beta).** A separate web-app dashboard rewritten outside the in-tree dashboard. Available now via the "ESPHome (beta)" Home Assistant add-on. The classic dashboard is still default.
2. **Main loop + watchdog rework.** The runtime now actually runs `loop()` at the cadence you configured, and the watchdog feed throttling was finally retuned for ESP-IDF. Translates to lower idle CPU and lower battery draw on every platform.
3. **Sendspin** lands as the first-class multi-room synchronized audio stack. Hub + per-room players + group controller + metadata sensors.
4. **`radio_frequency`** debuts as a top-level entity type so RF transceivers can speak to Home Assistant without per-chip glue.
5. **Native ESP-IDF toolchain.** A new `toolchain: esp-idf` knob under `esp32:` lets ESPHome build with `idf.py` directly, alongside the existing PlatformIO path.
6. **The decoder pipeline now sits on four new streaming libraries** (microMP3, microWAV, microFLAC, microDecoder). Lower CPU per frame, and the previously-pathological Opus-on-vanilla-ESP32 case became a working configuration.
7. **Over-the-air firmware delivery picks up four genuinely new tricks:** partition-table rewrites can ride along with the app, bootloader images can ship over the wire, a second OTA platform exposes binary upload through `web_server`, and `safe_mode` learned to fall back to a factory partition after repeated boot failures so a bad rollout no longer means USB reflash.
8. **Zigbee enters core** for ESP32-C6 and ESP32-H2 (router and end-device roles, with the new `sensor: platform: zigbee` joining the existing binary_sensor platform).
9. **nRF52/Zephyr** continues filling out: deep sleep with Zigbee wakeup, OTA-safe watchdog feeding, native build prep.
10. **LVGL** picks up flexible grid layout shorthands, touch coordinates in event lambdas, an `on_update` trigger that distinguishes programmatic vs user value changes, and percentage-based line points.

---

## Upgrade Checklist (run through this BEFORE flashing 2026.5.0)

- [ ] Using `modbus_controller` server mode? → migrate to `modbus_server` component (renames below)
- [ ] Rely on more than 5 concurrent API connections on esp32/bk72xx/rtl87xx/ln882x? → set `api.max_connections` explicitly (default dropped 8 → 5)
- [ ] Play WAV from arbitrary URLs (not embedded, not preferred pipeline format)? → add `audio: codecs: wav:` so WAV stays compiled in
- [ ] Use `codec_support_enabled` on speaker media player? → drop it, use `format: NONE` (all codecs) or `format: WAV` (old `none`/`false` mode)
- [ ] Speaker media player has `files:` larger than 5 MB? → compress or pick efficient codec
- [ ] Multiple `ota: - platform: esphome` entries on different ports? → consolidate to one entry
- [ ] `throttle_average` with `time_period` > 24 h? → lower it (new schema cap is 24 h)
- [ ] Lambdas call `id(...).set_min_power(...)` etc. on FloatOutput? → add `min_power: 0%` to a single output entry to keep runtime setters compiled in
- [ ] External climate platform uses `set_supports_*`/`get_supports_*`? → switch to `add_feature_flags()`/`has_feature_flags()` (note `two_point_target_temperature` → `CLIMATE_REQUIRES_TWO_POINT_TARGET_TEMPERATURE`)
- [ ] External components calling `OneWireBus::skip()`? → handle the new `bool` return value (false = reset/presence pulse failed)
- [ ] External components using `PollingComponent()` with no argument? → pass interval explicitly; default constructor no longer polls
- [ ] External components using `esphome::RingBuffer`? → switch to `esphome::ring_buffer::RingBuffer` from `esphome/components/ring_buffer/ring_buffer.h` and add `AUTO_LOAD = ["ring_buffer"]`
- [ ] External components using `str_lower_case`, `format_hex`, `format_mac_address_pretty`, etc.? → include `esphome/core/alloc_helpers.h` directly (helpers.h re-export is temporary)
- [ ] `ektf2232` config still uses `rts_pin`? → rename to `reset_pin` (friendly migration error is gone)
- [ ] Long-lived BLE connections via `ble_client`? → may see lower WiFi throughput due to new coex behavior (this is expected; open issue if material)

---

## New Components

### Sendspin (Multi-Room Synchronized Audio)

A new component family that turns any ESPHome speaker into a synchronized member of a multi-room audio group. On a plain (non-PSRAM) ESP32 the stack can decode and play 2-channel Opus in real time, where previously you needed an S3 with PSRAM for that workload.

```yaml
# Hub device (connection + group state distribution)
sendspin:
  host: 192.168.1.50   # hub static IP
  port: 7474

# Group player - controls whole group, no local audio output
media_player:
  - platform: sendspin_group
    name: "All Rooms"

# Hub-side metadata sensors
sensor:
  - platform: sendspin
    track_progress:
      name: "Track Progress"

text_sensor:
  - platform: sendspin
    title:
      name: "Now Playing Title"
    artist:
      name: "Now Playing Artist"

# Per-speaker device
media_player:
  - platform: sendspin
    name: "Living Room"
    delay_compensation: 50ms   # tune per room for DAC/amp latency
```

The component shipped piece by piece across PR #15924 (hub), #15929 (controller role and switch action), #15948 (group media player), #15950 (media source platform with delay compensation), #15969 / #15971 (title/artist/album sensors and track-progress polling sensor), and #16178 (player buffer in internal SRAM plus a task-priority bump so stereo Opus stops stuttering on plain ESP32).

### radio_frequency Entity Type

A new top-level entity type for RF transceivers in Home Assistant. The `on_control` trigger fires regardless of which chip is wired underneath, so the same YAML works across vendors.

```yaml
radio_frequency:
  - id: my_rf
    name: "RF Transceiver"
    on_control:
      then:
        - remote_transmitter.transmit_raw:
            carrier_frequency: 433.92MHz
            code: [1000, -1000, 500, -500]
```

The `ir_rf_proxy` platform extends the existing IR proxy:

```yaml
radio_frequency:
  - platform: ir_rf_proxy
    name: "RF Proxy"
    frequency_min: 433.0MHz
    frequency_max: 434.0MHz
```

The entity has no knowledge of which RF chip is underneath, so any front-end works: CC1101, RFM69, SX127x, an HopeRF module, or a custom external component. Switching the chip between transmit and receive is delegated to whatever `remote_transmitter` already does through its `on_transmit` and `on_complete` triggers, so no new driver-specific glue is needed. PR #15556, #15744, #16368.

### modbus_server (Split from modbus_controller)

Server mode is now a dedicated component. ~60% flash savings (1.8 KB vs 4.5 KB).

```yaml
# OLD (2026.4.x and earlier):
modbus_controller:
  - id: my_inverter
    address: 0x01
    modbus_id: modbus0
    server_registers:
      - address: 0x0100
        value_type: U_WORD
        lambda: "return id(my_sensor).state;"
    server_courtesy_response: true

# NEW (2026.5.0):
modbus_server:
  - id: my_inverter
    address: 0x01
    modbus_id: modbus0
    registers:                            # renamed from server_registers
      - address: 0x0100
        value_type: U_WORD
        lambda: "return id(my_sensor).state;"
    courtesy_response: true               # renamed from server_courtesy_response

# Combined client + server in same device:
modbus_controller:                        # client side (reads from external slave)
  - id: my_client
    address: 0x02
    modbus_id: modbus0
    sensors: ...

modbus_server:                            # server side (answers external master)
  - id: my_server
    address: 0x01
    modbus_id: modbus0
    registers: ...
```

PR #15509.

### Audio HTTP Media Source

Streams MP3/WAV/FLAC from HTTP URLs.

```yaml
media_player:
  - platform: speaker
    name: "Speaker"
    media_sources:
      - platform: audio_http
        name: "HTTP Audio"
```

---

## Native ESP-IDF Toolchain

Build with native `idf.py` instead of PlatformIO.

```yaml
esp32:
  board: esp32dev
  toolchain: esp-idf      # NEW - selects build system, default still 'platformio'
  framework:
    type: esp-idf         # selects RUNTIME framework (separate from build system)
```

CLI override:
```bash
esphome --toolchain esp-idf compile my-device.yaml
```

Precedence: `--toolchain` (CLI) > `esp32.toolchain` (YAML) > `platformio` (default). PR #14678.

---

## Main Loop & Watchdog Overhaul

```yaml
esp32:
  board: esp32dev
  watchdog_timeout: 15s    # NEW: configurable 5-60 s (default 5 s, PR #15908)
```

Under the hood (no YAML change required):
- `loop()` now runs at configured cadence (~62 Hz default) instead of being pulled to ~128 Hz by unrelated scheduler activity
- Watchdog feed interval now per-platform: ESP32 = 1000 ms (1/5 of watchdog_timeout), ESP8266 = 100 ms, LibreTiny BK72xx = 2000 ms, others = 300 ms
- Old universal 3 ms throttle caused 26% CPU waste under raised `loop_interval_`
- Measured: 2.0 mA → 1.1 mA current drop on OpenThread proof-of-concept
- `App.set_loop_interval()` now actually enables power savings

If your YAML implicitly depended on `loop()` being pulled forward by other scheduled work, components will run less often. Use `HighFrequencyLoopRequester` for fast wakes. PRs #15792, #15846, #15908, #15984.

---

## Audio Stack Changes

### WAV decoding no longer always compiled in

Auto-included when you:
- Embed a WAV file
- Set `format: WAV` as preferred pipeline format
- Use speaker media player with `format: NONE`

If you only play WAV from arbitrary URLs via YAML actions:

```yaml
audio:
  codecs:
    wav:     # add this to keep WAV compiled in
```

### codec_support_enabled deprecated

```yaml
# OLD:
media_player:
  - platform: speaker
    codec_support_enabled: true   # deprecated/inert

# NEW:
media_player:
  - platform: speaker
    format: NONE      # all codecs (old 'all' mode)
    # format: WAV     # WAV only (old none/false mode)
```

PR #14771, #16244, #16266.

---

## LVGL Improvements

```text
display:
  - platform: ili9xxx
    ...
    lvgl:
      widgets:
        - obj:
            grid_rows: "3x"      # NEW: 3 rows, columns auto-derived
            # OR:
            grid_columns: "x4"   # 4 columns, rows from widget count

        - button:
            on_pressed:
              - lambda: |-
                  ESP_LOGI("touch", "x=%d y=%d", point.x, point.y);   # NEW: point param

        - slider:
            on_update:           # NEW: distinguishes programmatic vs user change
              trigger: PROGRAMMATIC
              then:
                - logger.log: "Value changed programmatically"

        - line:
            points:
              - [10%, 20%]       # NEW: percentage line points
              - [80%, 90%]
```

Also: checked-state binary sensors report toggle widget state directly (#16073). PRs #16041, #16073, #16209, #16272, #16312.

---

## Zigbee on ESP32-H2 and C6

```yaml
# esp32-c6 or esp32-h2 only - requires esp-idf framework
esp32:
  board: esp32-c6-devkitc-1
  framework:
    type: esp-idf

zigbee:
  power_source: BATTERY              # NEW: BATTERY or MAINS_SINGLE_PHASE
  on_join:                            # NEW: fires on join/rejoin
    then:
      - logger.log: "Joined Zigbee network"

# Binary sensor over Zigbee (was already there, still works)
binary_sensor:
  - platform: zigbee
    name: "Door Sensor"
    cluster: BINARY_INPUT

# Sensor over Zigbee - NEW in 2026.5.0 via analog data model
sensor:
  - platform: zigbee
    name: "Temperature"
```

Both Zigbee router and end-device roles are supported. ZHA and zigbee2mqtt auto-recognize the clusters - no quirks/converters needed. PRs #11553, #16026, #16060, #16062.

---

## OTA Enhancements

OTA is one of the largest surface-area changes in 2026.5.0. Four new capabilities, all of them either opt-in or auto-detected from the compiled binary:

### 1. Partition table updates over OTA

Previously, an OTA could only replace the application image. If you needed a different partition layout (larger app partition, new storage region, factory partition, etc.) you had to reflash via USB. In 2026.5.0 the OTA protocol can rewrite the partition table itself.

```yaml
ota:
  - platform: esphome
    password: !secret ota_password
    # Partition table updates are auto-detected from the compiled binary.
    # No new YAML key required.
```

The new partition table is staged in a reserved area, validated, and committed atomically on next reboot. If the validation fails, the device boots the previous app + partition table.

### 2. Bootloader updates over OTA

Same machinery, extended to the bootloader. ESPHome can now ship a new bootloader image over the wire alongside the app. Previously, bootloader upgrades meant a USB reflash. This unblocks deploying long-term ESP-IDF v6+ readiness, secure boot rotations, and chip-revision-specific bootloader fixes to already-deployed fleets.

```yaml
# No new key needed - bootloader updates are part of the extended OTA protocol
# when the compiled firmware includes a newer bootloader than what is on-device.
```

### 3. Web-server OTA platform

A second OTA platform exposed via the `web_server` component, so you can upload a `.bin` file through a browser without needing the ESPHome CLI or Home Assistant.

```yaml
web_server:
  port: 80
  # OTA tab appears automatically when web_server: is paired with ota:

ota:
  - platform: web_server
    # Manual binary upload via the device's web UI
```

Useful for one-off recovery, lab boards without HA, or air-gapped networks. Auth uses the existing `web_server: auth:` config.

### 4. Soft-brick recovery via safe_mode + factory partition

Most painful scenario before 2026.5.0: a bad OTA boots, fails to connect, and the device loops on watchdog reset with no way back except USB reflash.

```yaml
safe_mode:
  # Default behavior changed in 2026.5.0:
  # After N consecutive boot failures, the device falls back to the factory partition
  # which always boots a known-good "OTA recovery" image.

  num_attempts: 10       # default; tune for slow boot devices
  reboot_timeout: 5min   # if app does not call mark_boot_successful() within this, count as failed
```

The factory partition holds a minimal ESPHome image whose only job is to come up on WiFi + OTA so you can push a corrected firmware. The user-app image stays untouched until you push a new one.

To opt out (devices with no room for a factory partition):

```yaml
safe_mode:
  enable_factory_recovery: false
```

### 5. OTA consolidation rule (breaking)

```yaml
ota:
  - platform: esphome
    port: 3232
  - platform: esphome
    port: 3233        # REJECTED at config time in 2026.5.0
```

Multiple `platform: esphome` entries on different ports were silently ignored after the first one before; now the config fails fast. Pick one port.

### 6. nRF52 firmware updates

```yaml
ota:
  - platform: nrf52
    reset_pin_optional: true   # 2026.5.0+: DFU entry without nRESET pin broken out
```

For nRF52 boards where the nRESET pin isn't exposed, OTA via Nordic DFU now works (less reliable but feasible). For boards with nRESET broken out, the standard path remains preferred.

PRs across the 2026.5.0 OTA work touch ota_backend.cpp, safe_mode.cpp, and the partitions table generation in the build system.

---

## ESP32 Hardware Features

### BLE with PSRAM

```yaml
esp32_ble:
  use_psram: true    # NEW: directs Bluedroid to SPIRAM (~40 kB internal RAM freed)
```

PR #15644.

### SPDIF Speaker Output

```yaml
speaker:
  - platform: i2s_audio
    i2s_dout_pin: GPIO22
    mode: spdif      # NEW: digital audio via GPIO to optical receiver
```

PR #8065.

### ESP32-P4 USB High Speed

```yaml
usb_host:
  max_packet_size: 512   # NEW on ESP32-P4 (was 64-byte FS packets only)
```

PR #14584.

### WiFi phy_mode for ESP8266

```yaml
wifi:
  phy_mode: 11G    # NEW: pin to 11B, 11G, or 11N (workaround for problem routers)
```

PR #16055.

---

## nRF52 / Zephyr Improvements

```yaml
# Deep sleep with Zigbee wakeup (battery-powered nRF52)
deep_sleep:
  run_duration: 10s
  sleep_duration: 60s
  wakeup_pin: GPIO_ZIGBEE   # wakes on radio event

# Numeric comparison BLE pairing
zephyr_ble_server:
  on_numeric_comparison_request:
    then:
      - logger.log: "BLE pairing initiated"

# OTA with optional reset pin (boards without nRESET broken out)
ota:
  - platform: nrf52
    reset_pin_optional: true
```

Also: nRF52 Zigbee router support, OTA-safe watchdog feeding, crash logging on Zephyr, bootloader reserve area. PRs #13950, #16034, #16032, #11684, #14400, #16204, #16203, #16218.

---

## SX126x Cold Sleep

```yaml
# Reaches ~0.6 µA (1000x lower than warm sleep), for ESP32-deep-sleep-paired use
sx126x:
  on_idle:
    then:
      - sx126x.sleep:
          cold: true
```

PR #16144.

---

## BLE Reliability Fix (Bluetooth Proxy)

Long-standing `status=0x85` (133) GATT failures are fixed. The fix holds `ESP_COEX_PREFER_BT` for the full lifetime of active BLE connections. Yale/August lock owners were the most-affected group. PR #16036.

**Side effect:** configs with persistent `ble_client` connections may see lower WiFi throughput while connected. Expected - open an issue if it materially affects your workload.

---

## Other Notable Features

```yaml
# Round to significant digits - useful for light sensors spanning 6 orders of magnitude
sensor:
  - platform: bh1750
    name: "Light"
    filters:
      - round_to_significant_digits: 3   # NEW filter (#11157)

# Lock OPENING/OPEN states (#15120)
lock:
  - platform: template
    name: "Door Lock"
    # Now reports OPENING and OPEN states (in addition to LOCKED/UNLOCKED)

# AC dimmer zero-crossing interrupt type (#15862)
output:
  - platform: ac_dimmer
    gate_pin: GPIO5
    zero_cross_pin:
      number: GPIO4
      mode: INPUT
    zero_cross_interrupt_type: RISING   # NEW: configurable edge

# Voice assistant second audio channel (#16265)
voice_assistant:
  microphone: mic_main
  microphone_secondary: mic_noise    # NEW: separate noise-cancellation source

# Mitsubishi CN105 remote temperature (#15558)
climate:
  - platform: mitsubishi_cn105
    name: "AC"
    remote_temperature: my_room_sensor   # NEW: override internal sensor
```

CLI: `esphome config-hash my-device.yaml` returns a hash matching the mDNS TXT record - Device Builder uses it to skip re-flashing identical configs. PR #15548, #16145.

---

## Performance Numbers (Reference)

| Optimization | Measured |
|---|---|
| `millis()` on ESP8266 | 3348 ns → 1077 ns (2.7x faster) |
| BLE advertisement encode | 20-33% faster |
| i2s_audio software volume | 7.8% → 4.3% CPU at 48 kHz stereo |
| Watchdog feed CPU (ESP32+BT proxy, per 60 s) | 46.5 ms → 21.6 ms |
| Main loop active CPU (ESP8266, 10 components) | -41 ms/min reclaimed (~7%) |
| FloatOutput power scaling (5-ch H801) | -64 B RAM, -248 B flash |
| API clients_ vector → array | Net -4 B RAM at 1 client connected |
| `modbus_server` flash vs old wedged server | 1.8 KB vs 4.5 KB |
| Light/cover/climate action instances | 60-120 B → ≤20 B per instance |

---

## Recipes (complete worked examples)

These are full, copy-paste-ready configs that combine the new 2026.5.0 features into useful end devices. Each recipe lists the hardware, all required files, and the Home Assistant integration steps.

### Recipe 1: Three-room Sendspin music system

**Goal:** play the same audio in living room, kitchen, and bedroom from one Home Assistant media_player entity. Use any ESP32 with an I2S DAC.

**Hardware (per room):**
- ESP32-WROOM-32 or any ESP32 dev board
- MAX98357A I2S amplifier breakout (or any I2S DAC + amp)
- 4-8 ohm speaker

**Hub file (`audio-hub.yaml`):**

```yaml
esphome:
  name: audio-hub
  friendly_name: Audio Hub

esp32:
  board: esp32dev
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

sendspin:
  host: 192.168.1.50    # hub static IP, must be reachable from all speakers
  port: 7474

media_player:
  - platform: sendspin_group
    name: "All Rooms"   # single HA entity that controls every room together

sensor:
  - platform: sendspin
    track_progress:
      name: "Now Playing Progress"

text_sensor:
  - platform: sendspin
    title:
      name: "Now Playing Title"
    artist:
      name: "Now Playing Artist"
```

**Per-room speaker file (`speaker-livingroom.yaml`):**

```yaml
esphome:
  name: speaker-livingroom
  friendly_name: Living Room Speaker

esp32:
  board: esp32dev
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
  - id: i2s_out
    i2s_lrclk_pin: GPIO25
    i2s_bclk_pin: GPIO26

speaker:
  - platform: i2s_audio
    id: room_speaker
    dac_type: external
    i2s_dout_pin: GPIO22

media_player:
  - platform: sendspin
    name: "Living Room"
    delay_compensation: 50ms    # tune per room
```

Duplicate the per-room file for kitchen and bedroom, changing only `name:` and `friendly_name:`. Flash all three. In Home Assistant, you get four media_player entities: one per room plus the "All Rooms" group.

**Tuning:** start with `delay_compensation: 50ms` everywhere. If one room sounds noticeably ahead of the others, raise its compensation by 10 ms steps until they align. Each amp/DAC chain has different latency so values often differ per room.

### Recipe 2: Battery-powered Zigbee temperature sensor (ESP32-C6)

**Goal:** battery-powered Zigbee sensor with month-scale battery life, auto-paired to ZHA or zigbee2mqtt.

**Hardware:**
- Seeed Xiao ESP32-C6 (compact, ~$5)
- SHT4x temperature/humidity sensor (I2C)
- 2x AA holder or 3.7 V LiPo + boost converter

**File (`zigbee-temp-sensor.yaml`):**

```yaml
esphome:
  name: zigbee-temp-1
  friendly_name: Zigbee Temp 1

esp32:
  board: esp32-c6-devkitc-1
  variant: esp32c6
  framework:
    type: esp-idf

logger:
  level: WARN          # reduce log churn for battery life

i2c:
  sda: GPIO22
  scl: GPIO23

sensor:
  - platform: sht4x
    id: env_sensor
    update_interval: never    # we trigger it manually before sleep
    temperature:
      id: room_temp
      name: "Temperature"
    humidity:
      id: room_humidity
      name: "Humidity"

  - platform: zigbee
    name: "Zigbee Temperature"
    cluster: TEMPERATURE_MEASUREMENT
    lambda: "return id(room_temp).state;"

  - platform: zigbee
    name: "Zigbee Humidity"
    cluster: RELATIVE_HUMIDITY_MEASUREMENT
    lambda: "return id(room_humidity).state;"

zigbee:
  power_source: BATTERY
  on_join:
    then:
      - logger.log: "Joined Zigbee network, will sleep after first publish"

deep_sleep:
  id: ds
  run_duration: 10s
  sleep_duration: 15min

# Take one reading, publish, then sleep
interval:
  - interval: 9s
    then:
      - component.update: env_sensor
      - delay: 500ms
      - deep_sleep.enter: ds
```

**HA setup:** in ZHA or zigbee2mqtt, put the coordinator in pairing mode and reset the device. It joins as a standard Zigbee temperature + humidity sensor, no quirk file or custom converter needed. Battery life depends on `sleep_duration` and Zigbee wake interval - 15-minute reporting should give months on 2x AA.

### Recipe 3: Bluetooth Proxy optimized for Yale/August locks

**Goal:** dedicated BLE proxy that reliably proxies Yale/August lock unlocks even under heavy WiFi load. Take advantage of the 2026.5.0 coex fix and PSRAM allocation.

**Hardware:** ESP32-WROVER (has PSRAM) or ESP32-S3 with PSRAM. Avoid plain ESP32 (no PSRAM).

**File (`ble-proxy.yaml`):**

```yaml
esphome:
  name: ble-proxy-living
  friendly_name: BLE Proxy Living Room

esp32:
  board: esp-wrover-kit       # or esp32-s3-devkitc-1
  framework:
    type: esp-idf             # required for stable BLE proxy
  watchdog_timeout: 15s       # 2026.5.0+ knob, gives BLE proxy headroom

psram:
  mode: quad
  speed: 80MHz

esp32_ble:
  use_psram: true             # 2026.5.0+: free ~40 kB internal RAM

esp32_ble_tracker:
  scan_parameters:
    interval: 1100ms
    window: 1100ms
    active: true

bluetooth_proxy:
  active: true                # allow active connections (needed for locks)
  cache_services: true        # speed up reconnects

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  power_save_mode: NONE       # full WiFi performance, lock priority handled by coex fix

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:
  level: INFO
```

This config exercises three 2026.5.0 features simultaneously: the BLE/WiFi coex fix (no `status=133` failures), `use_psram` (more RAM for proxy buffers), and `watchdog_timeout` (longer headroom for the proxy task during active connections).

### Recipe 4: Low-power monitoring node with extended watchdog

**Goal:** battery-powered ESP32 that wakes briefly, reports sensors, sleeps for an hour. Use the 2026.5.0 watchdog knob to push idle power down further.

```yaml
esphome:
  name: outdoor-monitor
  friendly_name: Outdoor Monitor

esp32:
  board: esp32-c3-devkitm-1
  watchdog_timeout: 30s        # 2026.5.0+: long timeout, idle feed = 6 s
  framework:
    type: esp-idf

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  power_save_mode: LIGHT       # let WiFi sleep between packets

api:
  encryption:
    key: !secret api_key
  reboot_timeout: 0s           # don't reboot if HA disconnects

ota:
  - platform: esphome
    password: !secret ota_password

logger:
  level: WARN

i2c:
  sda: GPIO8
  scl: GPIO9

sensor:
  - platform: bme280_i2c
    temperature:
      name: "Outdoor Temperature"
    pressure:
      name: "Outdoor Pressure"
    humidity:
      name: "Outdoor Humidity"
    update_interval: never

  - platform: adc
    pin: GPIO4
    name: "Battery Voltage"
    attenuation: 11dB
    update_interval: never
    filters:
      - multiply: 2.0          # voltage divider

deep_sleep:
  id: ds
  sleep_duration: 1h

interval:
  - interval: 9s
    then:
      - component.update: bme280_i2c
      - delay: 200ms
      - deep_sleep.enter: ds
```

### Recipe 5: RF gateway with radio_frequency entity

**Goal:** ESP32 + CC1101 module that exposes a 433 MHz RF transceiver to HA via the new `radio_frequency` entity type, so HA can send arbitrary RF codes through it.

```yaml
esphome:
  name: rf-gateway
  friendly_name: RF Gateway

esp32:
  board: esp32dev
  framework:
    type: esp-idf

spi:
  clk_pin: GPIO18
  miso_pin: GPIO19
  mosi_pin: GPIO23

cc1101:
  cs_pin: GPIO5
  gdo0_pin: GPIO16
  bandwidth: 200kHz
  frequency: 433.92MHz

remote_transmitter:
  pin: GPIO16
  carrier_duty_percent: 100%

remote_receiver:
  pin: GPIO16
  dump: raw
  tolerance: 50%

radio_frequency:
  - platform: ir_rf_proxy
    name: "433 MHz Gateway"
    frequency_min: 433.0MHz
    frequency_max: 434.0MHz
    modulations:
      - OOK
      - FSK

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password
```

In Home Assistant, the device appears as a `radio_frequency` entity. Any RF-capable automation in HA (or Z-Wave-style integrations) can target it to send codes without needing custom ESPHome scripts on the device.

---

## Upgrade Playbook (2026.4.x → 2026.5.0)

Step-by-step migration order. Each step is independent so you can stop and roll back at any point.

### Pre-flight (before you touch anything)

1. **Snapshot.** `git commit` your YAML configs or back up the folder. The 2026.5.0 OTA recovery system is excellent but a config rollback is faster.
2. **Note your current ESPHome version.** `esphome version` or check the dashboard footer.
3. **Run `esphome config <device>.yaml`** on every config to catch any latent warnings before the upgrade compounds them.

### Step 1: Run through the upgrade checklist

Walk through the [Upgrade Checklist](#upgrade-checklist-run-through-this-before-flashing-20260) above. Fix everything that applies *before* upgrading ESPHome itself. This avoids compile errors on first build.

The most common gotchas in practice:

- **modbus_controller server mode users:** rename keys to `modbus_server:` block (see Modbus section).
- **Speaker media player users:** drop `codec_support_enabled`, set `format:` instead.
- **Multiple OTA entries:** consolidate to one.

### Step 2: Upgrade ESPHome itself

```bash
# pip install
pip install --upgrade esphome

# or Home Assistant add-on
# Update via Supervisor > Add-ons > ESPHome > Update
```

For the new Device Builder Beta (optional):

```bash
# Home Assistant: install the "ESPHome (beta)" add-on
# Stable and beta add-ons can run side by side.
```

### Step 3: Re-compile one device first

Pick your least-critical device. Compile, flash, verify it works.

```bash
esphome run my-test-device.yaml
```

If the compile fails, the error message will name the breaking change. Cross-reference with the Breaking Changes Reference below.

### Step 4: Fleet rollout

Once one device is verified, roll out to the rest. The new soft-brick recovery (safe_mode + factory partition) reduces the cost of a bad rollout - devices that fail to boot will return to a recovery image and accept new firmware.

### Common post-upgrade errors and fixes

| Error message | Cause | Fix |
|---------------|-------|-----|
| `'server_registers' is not a valid key for 'modbus_controller'` | Pre-2026.5.0 modbus server config | Move to `modbus_server:` block, rename `server_registers:` to `registers:` |
| `'codec_support_enabled' is not a valid option` | Deprecated speaker media player key | Remove the key, set `format: NONE` (all codecs) or `format: WAV` instead |
| `Multiple OTA platforms 'esphome' configured` | Multiple `ota: - platform: esphome` on different ports | Consolidate to a single entry |
| Compile-time `static_assert` mentioning FloatOutput power scaling | Lambda calls `set_min_power()` etc. on FloatOutput without YAML opt-in | Add `min_power: 0%` to any one output entry |
| `'rts_pin' is not a valid option for ektf2232` | Old migration shim removed | Rename to `reset_pin` |
| `throttle_average time_period must be ≤ 24h` | Filter time_period exceeded new cap | Lower to 24 h or below |
| Lock entity behaves oddly in HA | Lock platform reporting OPENING/OPEN states unexpectedly | If lock only opens the bolt (not the door), only return LOCKED/UNLOCKED from your lambda |

### Rollback

If something goes wrong: downgrade ESPHome (`pip install esphome==2026.4.5`), restore your YAML from git, re-flash. The 2026.5.0 OTA can downgrade (no signed-version checks in stock builds), or use USB reflash.

---

## Breaking Changes Reference (compact)

| Area | Change | Migration |
|------|---------|-----------|
| `modbus_controller` server mode | Split to new `modbus_server` component | Rename keys (see Modbus section above) |
| `api.max_connections` | Default 8 → 5 | Set explicitly if you need more |
| WAV decoding | Not always compiled in | Add `audio: codecs: wav:` if needed |
| `codec_support_enabled` | Inert/deprecated | Use `format: NONE` or `format: WAV` |
| OTA multiple ports | Multi-entry on different ports rejected | Single entry on one port |
| `throttle_average` filter | `time_period` capped at 24 h | Lower the value |
| `FloatOutput` runtime scaling | Gated behind build flag | Add `min_power: 0%` to one output entry |
| Files in speaker `files:` block | 5 MB per-file limit | Compress or use efficient codec |
| `ektf2232` `rts_pin` | Migration shim removed | Rename to `reset_pin` |
| Main loop cadence | Runs at configured rate (~62 Hz) | Add `HighFrequencyLoopRequester` if needed |
| `OneWireBus::skip()` (external components) | Now returns `bool` | Handle the return value |
| `PollingComponent()` default ctor | Now `SCHEDULER_DONT_RUN` | Pass interval explicitly |
| Climate `set_supports_*` accessors | Removed | Use `add_feature_flags()`/`has_feature_flags()` |
| `esphome::RingBuffer` location | Moved to `ring_buffer` component | Include from `esphome/components/ring_buffer/ring_buffer.h` |
| API `clients_` storage | `std::vector` → compile-time `std::array` | Use `MAX_API_CONNECTIONS` define |

---

## Developer-Facing Breaking Changes (external components, lambdas)

If you only write YAML, you can skip this section. The breaking changes below affect external components, custom platforms, and C++ lambdas that reach into ESPHome internals.

### `OneWireBus::skip()` returns `bool`

```cpp
// Before 2026.5.0:
bus->skip();   // void

// 2026.5.0+:
if (!bus->skip()) {
    return;   // reset/presence pulse failed; do not write to a dead bus
}
```

Also performs a bus reset before issuing the SKIP ROM command, fixing a long-standing 1-Wire protocol violation. PR #14669.

### `ComponentIterator::on_media_player` is pure virtual

External components implementing `ComponentIterator` must add a stub for media players, guarded by `USE_MEDIA_PLAYER`:

```cpp
#ifdef USE_MEDIA_PLAYER
bool on_media_player(media_player::MediaPlayer *obj) override { return true; }
#endif
```

PR #15618.

### Helpers moved to `alloc_helpers.h`

Heap-allocating helpers were extracted to `alloc_helpers.h` / `alloc_helpers.cpp`:

```cpp
// 2026.5.0+: include alloc_helpers.h directly
#include "esphome/core/alloc_helpers.h"
```

Affected helpers: `str_lower_case`, `str_snprintf`, `format_hex`, `format_hex_pretty`, `format_mac_address_pretty`, `value_accuracy_to_string`, `base64_encode`, `base64_decode (vector overload)`, `get_mac_address`, `get_mac_address_pretty`.

`helpers.h` re-exports `alloc_helpers.h` for backward compatibility until **2026.11.0**. Update your includes before then. PR #15623.

### `PollingComponent()` default constructor changed

```cpp
// Before 2026.5.0: default polled at 1 ms
class MyComp : public PollingComponent { ... };

// 2026.5.0+: default does not poll at all
class MyComp : public PollingComponent {
public:
    MyComp() : PollingComponent(5000) {}    // pass interval explicitly
    // OR:
    void setup() override {
        set_update_interval(5000);
    }
};
```

External components that bypass codegen, call `PollingComponent()` with no argument, and never call `set_update_interval()` will stop polling. PR #15832.

### `APIServer::clients_` storage changed

```cpp
// Before 2026.5.0:
std::vector<APIConnection *> clients_;    // grew via doubling

// 2026.5.0+:
std::array<APIConnection *, MAX_API_CONNECTIONS> clients_;   // compile-time size
```

The runtime `set_max_connections()` setter was removed. The cap is now the `MAX_API_CONNECTIONS` compile-time define, populated from YAML's `api: max_connections:`. PR #15889.

### `FloatOutput` power scaling gated

`min_power_`, `max_power_`, `zero_means_zero_` and corresponding setters are gated behind `USE_OUTPUT_FLOAT_POWER_SCALING`. Lambdas that call these setters require the YAML to opt in. A compile-time `static_assert` documents the fix at the call site. PR #15998.

### ESPNOW method visibility and naming

```cpp
// play() is now correctly protected (was public)
// broadcasted property renamed to broadcast
```

External components extending the ESPNOW classes need to update method names and visibility expectations. PR #16109.

### Climate `ClimateTraits` accessors removed

The 10 deprecated `get_supports_*` / `set_supports_*` accessors (current_temperature, current_humidity, two_point_target_temperature, target_humidity, action) are gone after their 6-month deprecation window:

```cpp
// Before:
traits.set_supports_current_temperature(true);
bool has = traits.get_supports_current_temperature();

// 2026.5.0+:
traits.add_feature_flags(CLIMATE_HAS_CURRENT_TEMPERATURE);
bool has = traits.has_feature_flags(CLIMATE_HAS_CURRENT_TEMPERATURE);
```

Special-case mapping: `two_point_target_temperature` maps to `CLIMATE_REQUIRES_TWO_POINT_TARGET_TEMPERATURE`. PR #16289.

### `EKTF2232` `rts_pin` migration shim removed

The schema-level `rts_pin` → `reset_pin` rename helper is gone. Configs still using `rts_pin` now get a generic schema rejection instead of the friendly renamed-to error.

### Core ring buffer moved

```cpp
// Before 2026.5.0:
#include "esphome/core/ring_buffer.h"
esphome::RingBuffer rb;

// 2026.5.0+:
#include "esphome/components/ring_buffer/ring_buffer.h"
esphome::ring_buffer::RingBuffer rb;
```

Add `AUTO_LOAD = ["ring_buffer"]` to your external component's `__init__.py`. The old `esphome/core/ring_buffer.h` location is deprecated with a 6-month removal window. PR #15623 (related).

The new ring buffer also gained a memory-preference parameter on `create()` so audio paths can target faster internal SRAM instead of PSRAM:

```cpp
auto rb = ring_buffer::RingBuffer::create(size, MemoryPreference::INTERNAL);
```

Useful when small buffers benefit from faster internal SRAM rather than the slow ESP32 PSRAM cache. PR #16187.

---

## What Did Not Change (reassurance)

If you're worried about an upgrade breaking things you depend on, these are explicitly stable in 2026.5.0:

- **All sensor/binary_sensor/switch/light platforms keep their existing YAML.** The big changes are additive (new platforms like `sendspin`, new triggers like `on_open` for locks, new options like `mode: spdif`).
- **`remote_transmitter` / `remote_receiver`** continue to work without modification. The new `radio_frequency` entity is opt-in.
- **`modbus_controller` client mode** is unchanged. Only server-mode keys moved to the new `modbus_server` component.
- **Zigbee binary_sensor** configs from earlier releases continue to work. `sensor: platform: zigbee` is new but the binary_sensor side is unchanged.
- **Existing `wifi:`, `api:`, `ota:` (single-entry), `logger:`, `web_server:` configs** keep working.
- **HA automations targeting existing entities** continue to work. New states (Lock OPENING/OPEN) are only added when your firmware explicitly returns them.
- **Legacy ESPHome dashboard** remains the default. The new Device Builder is opt-in.
- **PlatformIO build path** continues to be the default. The new `toolchain: esp-idf` is opt-in.

---

## New Device Builder Beta

Replaces the legacy dashboard. Lives in two new repos: `device-builder` (Python backend) and `device-builder-frontend` (web UI). Uses stable public ESPHome interfaces, not internal modules.

Available now via the **ESPHome (beta)** Home Assistant add-on (enabled by default in beta; stable-app users can opt in via the "Use new Device Builder Preview" toggle).

Capabilities over legacy:
- Visual component + automation builder alongside Monaco YAML
- Per-board pin info viewer (GPIO capability map)
- Firmware job queue with progress/history/cancel
- Remote builder - distribute compile/install to another instance over peer-paired link (mDNS, SHA-256 fingerprint, identity rotation)
- Labels (colored, searchable), areas as first-class field, friendly name editable
- Device cloning + multi-select bulk actions (update/delete/archive)
- Out-of-sync detection per device (version, config-hash, encryption-state)
- YAML diff view, cross-config YAML search with surrounding context
- Command palette (Cmd-K / Ctrl-K)
- Card + table views with configurable columns and faceted filters
- Real settings UI: theme, English/Français/Nederlands, editor layout, remote-builder controls
- First-run Wi-Fi onboarding + USB-plug detection

**The legacy dashboard remains the default in 2026.5.0.** (Update: ESPHome 2026.6.0 retired the legacy dashboard and made Device Builder 1.0 the default. See references/release-2026-6.md.) PRs #16206, #16290, #16300, #16346, #15548, #16145, #16267, #16276, #16296, #16357, #16214, #16378.

---

## Links

- Full changelog: https://esphome.io/changelog/2026.5.0/
- Device Builder: https://github.com/esphome/device-builder
- Device Builder frontend: https://github.com/esphome/device-builder-frontend
