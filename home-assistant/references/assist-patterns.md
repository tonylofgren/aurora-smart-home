# Assist Patterns

Guide for configuring and using Home Assistant Assist (voice assistant).

## Overview

Home Assistant Assist is the built-in voice assistant that:
- Understands natural language
- Controls devices via voice or text
- Can run entirely locally without cloud services
- Supports multiple languages including English

## Assist Pipeline

```
┌────────────────────────────────────────────────────┐
│                  Assist Pipeline                    │
├────────────────────────────────────────────────────┤
│  Wake Word → Speech-to-Text → Conversation Agent   │
│                                   ↓                 │
│                            Intent Matching          │
│                                   ↓                 │
│                            Action Execution         │
│                                   ↓                 │
│                            Text-to-Speech → Output  │
└────────────────────────────────────────────────────┘
```

## Basic Configuration

### Enable Assist

1. Settings → Voice assistants
2. Click "Add assistant"
3. Configure the components

### Components

| Component | Local | Cloud | Recommendation |
|-----------|-------|-------|----------------|
| **STT** | Whisper | Google | Whisper for privacy |
| **TTS** | Piper | Google | Piper for local TTS |
| **Wake Word** | openWakeWord | - | Local only |
| **Conversation** | HA built-in | OpenAI | Built-in for control |

## Custom Sentences

Create your own voice commands in `config/custom_sentences/en/`:

### Basic Syntax

```yaml
# config/custom_sentences/en/lights.yaml
language: en

intents:
  HassLightSet:
    data:
      - sentences:
          - "[set] {name} [to] {brightness} [percent]"
          - "{name} [to] {brightness} [percent]"

lists:
  brightness:
    range:
      from: 0
      to: 100
```

### Rooms and Areas

```yaml
# config/custom_sentences/en/rooms.yaml
language: en

intents:
  HassLightSet:
    data:
      - sentences:
          - "turn on [all] [light|lights] [in|at] {area}"
          - "turn off [all] [light|lights] [in|at] {area}"

  HassTurnOn:
    data:
      - sentences:
          - "start {name}"
          - "turn on {name}"
          - "switch on {name}"

  HassTurnOff:
    data:
      - sentences:
          - "turn off {name}"
          - "stop {name}"
```

### Advanced Patterns

```yaml
# config/custom_sentences/en/scenes.yaml
language: en

intents:
  HassSceneTurnOn:
    data:
      - sentences:
          - "[activate|start|set] {scene_mode} [mode] [in|at] {area}"
          - "[I want] {scene_mode} [in|at] {area}"

lists:
  scene_mode:
    values:
      - in: "movie"
        out: "movie"
      - in: "dinner"
        out: "dinner"
      - in: "romantic"
        out: "romantic"
      - in: "party"
        out: "party"
```

### Wildcards and Slots

```yaml
# config/custom_sentences/en/custom.yaml
language: en

intents:
  SetTemperature:
    data:
      - sentences:
          - "set the temperature [in|at] {area} [to] {temperature} degrees"
          - "{temperature} degrees [in|at] {area}"

lists:
  temperature:
    range:
      from: 15
      to: 30
```

## Intent Scripts

Connect intents to automations:

```yaml
# config/intent_script.yaml
intent_script:
  GetWeatherForecast:
    speech:
      text: >
        Tomorrow's weather will be {{ states('weather.home') }}
        with {{ state_attr('weather.home', 'temperature') }} degrees.

  GoodMorning:
    speech:
      text: "Good morning! I am preparing the house."
    action:
      - service: scene.turn_on
        target:
          entity_id: scene.morning
      - service: media_player.play_media
        target:
          entity_id: media_player.kitchen
        data:
          media_content_id: "https://example.com/morning_news.mp3"
          media_content_type: "music"

  LeaveHome:
    speech:
      text: "Have a great day! I am turning everything off."
    action:
      - service: script.leave_home
```

Register in `configuration.yaml`:

```yaml
intent_script: !include intent_script.yaml
```

And create sentences:

```yaml
# config/custom_sentences/en/routines.yaml
language: en

intents:
  GoodMorning:
    data:
      - sentences:
          - "good morning"
          - "wake up house"
          - "start morning routine"

  LeaveHome:
    data:
      - sentences:
          - "I am leaving now"
          - "goodbye"
          - "turn everything off"
```

## Area-based Commands

```yaml
# config/custom_sentences/en/area_commands.yaml
language: en

intents:
  HassLightSet:
    data:
      - sentences:
          - "dim [the] [light|lights] [in|at] {area}"
        slots:
          brightness: 30

      - sentences:
          - "full brightness [in|at] {area}"
          - "max light [in|at] {area}"
        slots:
          brightness: 100

      - sentences:
          - "cozy lighting [in|at] {area}"
        slots:
          brightness: 20

  HassTurnOn:
    data:
      - sentences:
          - "start [all] {device_class} [in|at] {area}"

  HassTurnOff:
    data:
      - sentences:
          - "[turn off|stop] [all] {device_class} [in|at] {area}"

lists:
  device_class:
    values:
      - in: "lights"
        out: "light"
      - in: "fans"
        out: "fan"
      - in: "tv"
        out: "media_player"
```

## Media Control

```yaml
# config/custom_sentences/en/media.yaml
language: en

intents:
  HassMediaPause:
    data:
      - sentences:
          - "pause [the] [music|video|media]"
          - "stop [the] [music|video]"

  HassMediaUnpause:
    data:
      - sentences:
          - "continue [playing]"
          - "play"

  HassMediaNext:
    data:
      - sentences:
          - "next [song|track|video]"
          - "skip"

  HassSetVolume:
    data:
      - sentences:
          - "[set] [the] volume [to] {volume} [percent]"
          - "{volume} [percent] volume"

lists:
  volume:
    range:
      from: 0
      to: 100
```

## Timers and Reminders

```yaml
# config/custom_sentences/en/timers.yaml
language: en

intents:
  HassTimerStart:
    data:
      - sentences:
          - "set [a] timer [for] {minutes} minutes"
          - "remind me in {minutes} minutes"
          - "wake me in {minutes} minutes"

  HassTimerCancel:
    data:
      - sentences:
          - "cancel [the] timer"
          - "stop [the] timer"
          - "turn off [the] timer"

lists:
  minutes:
    range:
      from: 1
      to: 120
```

## Conversation Flows

Multi-turn conversations:

```yaml
# config/custom_sentences/en/conversation.yaml
language: en

intents:
  StartVacuum:
    data:
      - sentences:
          - "clean {area}"
          - "vacuum {area}"

  ConfirmVacuum:
    data:
      - sentences:
          - "yes [please]"
          - "go [ahead]"
          - "start"

  CancelVacuum:
    data:
      - sentences:
          - "no [thanks]"
          - "cancel"
```

```yaml
# intent_script.yaml
intent_script:
  StartVacuum:
    speech:
      text: "Should I start the vacuum in {{ area }}? Say yes or no."
    # Store context for follow-up

  ConfirmVacuum:
    speech:
      text: "The vacuum is starting now."
    action:
      - service: vacuum.start
        target:
          entity_id: vacuum.roborock
```

## Troubleshooting

### Debug Sentences

Test your sentences in Developer Tools → Assist:

1. Type your command
2. See which intent is matched
3. Check slots and values

### Common Issues

| Problem | Solution |
|---------|---------|
| "I don't understand" | Check sentence syntax |
| Wrong intent matched | Make sentences more specific |
| Entity not found | Use friendly_name or alias |
| Timeout | Check STT/TTS services |

### Log Conversation

```yaml
logger:
  logs:
    homeassistant.components.conversation: debug
    homeassistant.components.intent: debug
```

## Aliases for Entities

Give entities alternative names:

```yaml
# Settings → Devices & Services → Entities → [Entity] → Edit
# Or via customize.yaml:

homeassistant:
  customize:
    light.living_room_ceiling:
      aliases:
        - ceiling light
        - big light
        - living room lamp
```

## Expose Configuration

Limit which entities can be controlled:

```yaml
# Settings → Voice assistants → Expose
# Eller via automation:

conversation:
  intents:
    HassLightSet:
      - exposed_domains:
          - light
      - exposed_entities:
          - switch.coffee_maker
```

## Multi-Language Support

```yaml
# config/custom_sentences/en/lights.yaml
language: en

intents:
  HassLightSet:
    data:
      - sentences:
          - "set {name} to {brightness} percent"
          - "dim {name} to {brightness} percent"
```

## Example Prompts

```
"Create voice commands to control lights in different rooms"

"I want to be able to say 'good morning' and start a routine"

"Configure Assist to handle timers and reminders"

"Create custom sentences for media control"

"Debug why my voice command is not working"
```

## Best Practices

1. **Use synonyms** - `[turn on|switch on|start]`
2. **Make sentences natural** - Think about how you actually speak
3. **Test in Developer Tools** - Verify before production
4. **Use areas** - `{area}` instead of room names in sentences
5. **Limit exposed entities** - Security and performance
6. **Aliases for friendly names** - Easier to say

## See Also

- `references/jinja2-templates.md` - Jinja2 for dynamic responses
- `references/automations.md` - Connect to automations
- `../esphome/references/voice-local.md` - ESPHome voice devices
- `../ha-integration-dev/references/conversation-agent.md` - Custom agents
