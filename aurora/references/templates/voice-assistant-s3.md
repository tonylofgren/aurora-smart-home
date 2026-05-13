# Voice Assistant Template (ESP32-S3 satellite)

A local-first voice assistant satellite that runs the wake word on-device (no cloud), then streams audio to your Home Assistant Voice Pipeline for STT/intent/TTS.

## When to use

- You want a wake-word-triggered voice control in a specific room
- You want a private, no-cloud voice setup (paired with a local Whisper/Piper/LLM pipeline in HA)
- You already have HA Voice Assist configured with a pipeline

## Recommended board

- **ESP32-S3 DevKit C-1**: REQUIRED. Wake word needs the S3's AI acceleration and PSRAM.

Do NOT use: ESP32 classic, ESP32-S2, ESP32-C3 (no PSRAM, single core, insufficient).

## External hardware

- **INMP441 I2S microphone** (~30 SEK on AliExpress)
- **MAX98357A I2S amplifier + 4-ohm 3W speaker** (optional, for TTS responses)
- Both connect to the recommended pins in the YAML

## Customization

- Change `micro_wake_word.models` to other wake words (alexa, jarvis, hey_mycroft)
- Lower `noise_suppression_level` if speech is clipped
- Set `use_wake_word: true` after first deploy to enable on-board wake (default starts with HA-side wake)

## After deploy

1. In HA, go to Settings > Voice Assistants
2. Pair the device, assign it to a pipeline
3. Test by saying "Okay Nabu, turn on the kitchen light"
