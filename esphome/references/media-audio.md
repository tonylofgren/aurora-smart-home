# ESPHome: Media Player, Microphone, Speaker & Audio DAC

Reference documentation for ESPHome's audio stack, including the redesigned media player architecture (2026.3+).
Source: https://esphome.io/components/

---

## Architecture Overview (2026.3+)

The media player stack was completely redesigned in ESPHome 2026.3. The old monolithic I2S Media Player has been replaced by a modular architecture:

```
┌─────────────────────────┐
│   Media Player Entity   │  ← Home Assistant sees this
├─────────────────────────┤
│  Speaker Media Player   │  ← Manages playback, pipelines
├─────────────────────────┤
│  Resampler / Mixer      │  ← Optional audio processing
├─────────────────────────┤
│  Speaker / Audio DAC    │  ← Audio output hardware
├─────────────────────────┤
│     I2S Audio Bus       │  ← Shared audio transport
└─────────────────────────┘
```

**Key change:** Instead of one `i2s_audio` media player that bundles everything, you now configure the I2S bus, speaker, optional DAC, and media player as separate components. This enables pluggable sources, dual pipelines (media + announcements), playlists, and Ogg Opus support.

---

## 1. I2S Audio (Shared Bus)

The I2S Audio component configures the I2S peripheral. Multiple components (speaker, microphone, media player) share this bus.

```yaml
i2s_audio:
  - id: i2s_out
    i2s_lrclk_pin: GPIO26   # WS / Word Select
    i2s_bclk_pin: GPIO25    # BCK / Bit Clock
  - id: i2s_in
    i2s_lrclk_pin: GPIO22
    i2s_bclk_pin: GPIO23
```

| Variable | Type | Description |
|----------|------|-------------|
| `i2s_lrclk_pin` | pin | **Required.** Word Select (WS/LRCLK) pin |
| `i2s_bclk_pin` | pin | **Required.** Bit Clock (BCK/BCLK) pin |
| `i2s_mclk_pin` | pin | Master Clock pin (some DACs require this) |

> **Note:** ESP32-S3 supports two I2S peripherals - you can have separate buses for input (mic) and output (speaker) simultaneously.

---

## 2. Speaker Platforms

### I2S Audio Speaker

```yaml
speaker:
  - platform: i2s_audio
    id: my_speaker
    i2s_audio_id: i2s_out
    dac_type: external        # external DAC (e.g., MAX98357A, PCM5102A)
    i2s_dout_pin: GPIO27      # Data out to DAC
    channel: mono             # left, right, mono, stereo
    sample_rate: 16000
    bits_per_sample: 16
    buffer_duration: 500ms
    i2s_comm_fmt: msb         # msb (AC101, PCM5102A) or lsb (PT8211)
```

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `dac_type` | enum | **Required** | `external` (I2S DAC) or `internal` (ESP32 built-in DAC) |
| `i2s_dout_pin` | pin | **Required** | I2S data output pin |
| `channel` | enum | | `left`, `right`, `mono`, `stereo` |
| `sample_rate` | int | `16000` | I2S sample rate in Hz |
| `bits_per_sample` | enum | | `16bit`, `24bit`, `32bit` |
| `buffer_duration` | time | `500ms` | Internal ring buffer. Larger = less stuttering, more RAM |
| `i2s_comm_fmt` | enum | `msb` | `msb` (AC101, PCM5102A) or `lsb` (PT8211) |

> **Note:** Internal DAC is low quality (8-bit). Only on original ESP32, not S2/S3/C3/C6.

### Mixer Speaker

Mixes audio from multiple source speakers into one output speaker.

```yaml
speaker:
  - platform: mixer
    id: mixer_speaker
    output: i2s_speaker       # Output speaker ID
    num_channels: 2           # 1 (mono) or 2 (stereo)
    queue_mode: false         # Play successively instead of mixing
```

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `output` | ID | **Required** | Output speaker component ID |
| `num_channels` | int | output channels | 1 (mono) or 2 (stereo) |
| `queue_mode` | bool | `false` | Play audio successively from each source instead of mixing |

> **Note:** When mixing, all streams must have the same sample rate. Use a resampler if rates differ.

### Resampler Speaker

Converts sample rate of an audio stream. Passes through directly if no resampling needed.

```yaml
speaker:
  - platform: resampler
    id: resampler_speaker
    output: mixer_speaker     # Output speaker ID
    buffer_duration: 500ms
    bits_per_sample: 16
    num_channels: 1
```

### UDP Speaker

Sends audio over the network via UDP.

```yaml
speaker:
  - platform: udp
    id: udp_speaker
    broadcast_port: 18511
    addresses:                # Optional, defaults to broadcast
      - 192.168.1.100
```

### Speaker Actions

```yaml
- speaker.play:
    id: my_speaker
    data: !lambda return {0x00, 0x01, ...};
- speaker.stop: my_speaker
- speaker.finish: my_speaker        # Stop accepting data, play remaining buffer
- speaker.volume_set:
    id: my_speaker
    volume: 0.5
- speaker.mute_on: my_speaker
- speaker.mute_off: my_speaker
```

### Speaker Conditions

```yaml
- speaker.is_playing:
    id: my_speaker
- speaker.is_stopped:
    id: my_speaker
```

---

## 3. Microphone Platforms

### I2S Audio Microphone

```yaml
microphone:
  - platform: i2s_audio
    id: my_mic
    i2s_audio_id: i2s_in
    adc_type: external        # External mic (INMP441, SPH0645) or internal (ESP32 ADC)
    i2s_din_pin: GPIO23       # Data in from mic
    pdm: false                # Set true for PDM microphones
    bits_per_sample: 32
    channel: left             # left, right, or stereo
    use_apll: false           # Use APLL for accurate clock
    correct_dc_offset: false  # Correct DC offset for mics with non-zero average
```

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `adc_type` | enum | **Required** | `external` (I2S mic) or `internal` (ESP32 ADC) |
| `i2s_din_pin` | pin | **Required** | I2S data input pin |
| `pdm` | bool | `false` | Enable for PDM microphones |
| `channel` | enum | `right` | `left`, `right`, or `stereo` |
| `bits_per_sample` | enum | | `16bit`, `24bit`, `32bit` |
| `bits_per_channel` | enum | `32bit` | Bit depth actually read |
| `use_apll` | bool | `false` | Use APLL for accurate clock |
| `correct_dc_offset` | bool | `false` | Correct DC offset |

### Common Microphone Wiring (INMP441)

| INMP441 Pin | ESP32 Pin | Notes |
|------------|-----------|-------|
| VDD | 3.3V | |
| GND | GND | |
| WS | GPIOx | Word Select (→ i2s_lrclk_pin) |
| SCK | GPIOx | Bit Clock (→ i2s_bclk_pin) |
| SD | GPIOx | Data Out → ESP i2s_din_pin |
| L/R | GND | Left channel (or 3.3V for right) |

### UDP Microphone

```yaml
microphone:
  - platform: udp
    id: udp_mic
    listen_port: 18511
```

### Microphone Actions

```yaml
- microphone.start_capture: my_mic
- microphone.stop_capture: my_mic
- microphone.mute: my_mic
- microphone.unmute: my_mic
```

### Microphone Triggers

```yaml
microphone:
  - platform: i2s_audio
    id: my_mic
    on_data:
      then:
        - lambda: |-
            // x is std::vector<int16_t>
            ESP_LOGD("mic", "Received %d samples", x.size());
```

---

## 4. Audio DAC

External audio codec chips for higher quality output.

### ES8311 (Mono Codec)

Single-channel codec - speaker output OR microphone input via I2S Audio.

```yaml
i2c:
  sda: GPIO18
  scl: GPIO23

audio_dac:
  - platform: es8311
    id: es8311_dac
    bits_per_sample: 16bit
    sample_rate: 16000
    use_mclk: true
    use_microphone: true      # Use PDM mic input
    mic_gain: 24DB            # 0DB to 42DB in 6dB steps
    address: 0x18
```

### ES8388 (Stereo Codec)

Dual-channel codec - supports BOTH speaker output AND microphone input simultaneously (full-duplex).

```yaml
audio_dac:
  - platform: es8388
    id: es8388_dac
    address: 0x10

# ES8388 provides select entities for routing
select:
  - platform: es8388
    dac_output:
      name: "DAC Output"
    adc_input_mic:
      name: "ADC Input Mic"
```

> **Note:** ES8388 is found on many ESP32-S3 audio dev boards (ESP32-S3-BOX, AI Thinker Audio Kit).

---

## 5. Media Player

### Speaker Media Player (Primary - 2026.3+)

The new primary media player platform with dual pipeline support.

```yaml
media_player:
  - platform: speaker
    name: "Room Speaker"
    id: room_speaker

    media_pipeline:
      speaker: media_resampler
      sources:
        - audio_file_source
        - http_source
      format: FLAC              # FLAC/MP3/OPUS/WAV/NONE
      sample_rate: 48000

    announcement_pipeline:
      speaker: announce_resampler
      sources:
        - tts_source
      format: FLAC
      sample_rate: 16000
```

At least one of `media_pipeline` or `announcement_pipeline` is required. Each pipeline needs a `speaker` ID and at least one source.

**Pipeline Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `speaker` | ID | **Required** | Speaker component ID |
| `sources` | list | **Required** | List of media source component IDs (min 1) |
| `format` | enum | `FLAC` | Transcode format: FLAC, MP3, OPUS, WAV, NONE |
| `sample_rate` | int | speaker rate | Audio sample rate |
| `num_channels` | int | | 1 (mono) or 2 (stereo) |

### Speaker Source Media Player (2026.3+)

Adds pluggable source support:

```yaml
media_player:
  - platform: speaker_source
    name: "Multi-Source Player"
    speaker: my_speaker
    sources:
      - id: ha_source
        type: home_assistant
      - id: file_source
        type: audio_file
```

### I2S Audio Media Player (Legacy)

Still supported but no longer recommended. Use Speaker Media Player for new projects.

```yaml
# LEGACY - prefer speaker media player
media_player:
  - platform: i2s_audio
    name: "Speaker"
    dac_type: external
    i2s_dout_pin: GPIO27
    mode: mono
    i2s_comm_fmt: msb         # msb (AC101, PCM5102A) or lsb (PT8211)
```

### Media Player Actions

```yaml
# Play media
- media_player.play_media:
    id: room_speaker
    media_url: "http://example.com/audio.mp3"

# Transport controls
- media_player.play: room_speaker
- media_player.pause: room_speaker
- media_player.stop: room_speaker
- media_player.toggle: room_speaker

# Volume
- media_player.volume_set:
    id: room_speaker
    volume: 50%
- media_player.volume_up: room_speaker
- media_player.volume_down: room_speaker
- media_player.mute: room_speaker
- media_player.unmute: room_speaker

# Power
- media_player.turn_on: room_speaker
- media_player.turn_off: room_speaker

# Track controls
- media_player.next: room_speaker
- media_player.previous: room_speaker

# Repeat
- media_player.repeat_off: room_speaker
- media_player.repeat_one: room_speaker
- media_player.repeat_all: room_speaker
```

### Media Player Triggers

```yaml
media_player:
  - platform: speaker
    on_play:
      - logger.log: "Playback started"
    on_pause:
      - logger.log: "Paused"
    on_idle:
      - logger.log: "Idle"
    on_announcement:
      - logger.log: "Announcement playing"
    on_turn_on:
      - logger.log: "Turned on"
    on_turn_off:
      - logger.log: "Turned off"
```

### Media Player Conditions

```yaml
- media_player.is_idle: room_speaker
- media_player.is_playing: room_speaker
```

---

## 6. Audio File (2026.3+)

Embed audio files directly into firmware for offline playback (boot sounds, alerts, chimes).

```yaml
audio_file:
  - id: boot_sound
    file: "sounds/boot.wav"
  - id: alert_sound
    file: "sounds/alert.wav"
```

> **Note:** Audio files are stored in flash. Keep them small. Consider Ogg Opus for compression.

---

## 7. Complete Examples

### Voice Assistant with Dual Pipelines (ESP32-S3 + ES8311)

```yaml
esphome:
  name: voice-speaker

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf

psram:
  mode: octal
  speed: 80MHz

i2c:
  sda: GPIO18
  scl: GPIO23

i2s_audio:
  - id: i2s_bus
    i2s_lrclk_pin: GPIO6
    i2s_bclk_pin: GPIO7
    i2s_mclk_pin: GPIO9

audio_dac:
  - platform: es8311
    id: dac_chip
    bits_per_sample: 16bit
    sample_rate: 16000
    use_mclk: true
    use_microphone: true
    mic_gain: 24DB

microphone:
  - platform: i2s_audio
    id: board_mic
    i2s_audio_id: i2s_bus
    i2s_din_pin: GPIO10
    channel: left
    bits_per_sample: 32

speaker:
  - platform: i2s_audio
    id: board_speaker
    i2s_audio_id: i2s_bus
    i2s_dout_pin: GPIO8
    dac_type: external
    channel: mono
    sample_rate: 16000

  - platform: mixer
    id: speaker_mixer
    output: board_speaker

  - platform: resampler
    id: announce_resampler
    output: speaker_mixer

  - platform: resampler
    id: media_resampler
    output: speaker_mixer

media_player:
  - platform: speaker
    name: "Voice Speaker"
    announcement_pipeline:
      speaker: announce_resampler
      format: FLAC
      num_channels: 1
    media_pipeline:
      speaker: media_resampler
      format: FLAC
      num_channels: 1

voice_assistant:
  microphone: board_mic
  speaker: announce_resampler
```

### Simple Music Player (MAX98357A)

```yaml
esphome:
  name: music-player

esp32:
  board: esp32dev

i2s_audio:
  i2s_lrclk_pin: GPIO26
  i2s_bclk_pin: GPIO25

speaker:
  - platform: i2s_audio
    id: amp_speaker
    dac_type: external
    i2s_dout_pin: GPIO27
    channel: mono

media_player:
  - platform: speaker
    name: "Kitchen Speaker"
    media_pipeline:
      speaker: amp_speaker
```

---

## Migration: I2S Media Player → Speaker Media Player

**Before (legacy):**
```yaml
media_player:
  - platform: i2s_audio
    name: "Speaker"
    dac_type: external
    i2s_dout_pin: GPIO27
    mode: mono
```

**After (2026.3+):**
```yaml
i2s_audio:
  i2s_lrclk_pin: GPIO26
  i2s_bclk_pin: GPIO25

speaker:
  - platform: i2s_audio
    id: my_speaker
    dac_type: external
    i2s_dout_pin: GPIO27
    channel: mono

media_player:
  - platform: speaker
    name: "Speaker"
    media_pipeline:
      speaker: my_speaker
```

**Key differences:**
1. I2S bus is now configured separately
2. Speaker is its own component
3. Media player references the speaker by ID
4. More flexibility - same speaker can be used by voice_assistant and media_player
5. Dual pipelines possible (media + announcements)

---

## Quick Reference

| Component | Platforms | Key Use Case |
|-----------|----------|-------------|
| `i2s_audio` | (base) | Configure I2S bus pins |
| `speaker` | i2s_audio, mixer, resampler, udp | Audio output hardware |
| `microphone` | i2s_audio, udp | Audio input hardware |
| `audio_dac` | es8311, es8388 | External audio codec |
| `media_player` | speaker, speaker_source, i2s_audio (legacy) | HA media player entity |
| `audio_file` | (base) | Embed audio in firmware |

## See Also

- `references/voice-local.md` - Voice assistant setup with wake words, STT, TTS
- `references/displays.md` - Add display for now-playing UI
- `references/bluetooth.md` - Bluetooth audio
