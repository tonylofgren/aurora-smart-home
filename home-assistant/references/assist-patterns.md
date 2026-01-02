# Assist Patterns

Guide för att konfigurera och använda Home Assistant Assist (röstassistent).

## Översikt

Home Assistant Assist är den inbyggda röstassistenten som:
- Förstår naturligt språk
- Styr enheter via röst eller text
- Kan köras helt lokalt utan molntjänster
- Stöder flera språk inklusive svenska

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

## Grundläggande Konfiguration

### Aktivera Assist

1. Settings → Voice assistants
2. Klicka på "Add assistant"
3. Konfigurera komponenterna

### Komponenter

| Komponent | Lokalt | Moln | Rekommendation |
|-----------|--------|------|----------------|
| **STT** | Whisper | Google | Whisper för privatliv |
| **TTS** | Piper | Google | Piper för svenska |
| **Wake Word** | openWakeWord | - | Endast lokalt |
| **Conversation** | HA built-in | OpenAI | Built-in för kontroll |

## Custom Sentences

Skapa egna röstkommandon i `config/custom_sentences/sv/`:

### Grundläggande Syntax

```yaml
# config/custom_sentences/sv/lights.yaml
language: sv

intents:
  HassLightSet:
    data:
      - sentences:
          - "[sätt|ställ] {name} [på|till] {brightness} [procent]"
          - "{name} [på|till] {brightness} [procent]"

lists:
  brightness:
    range:
      from: 0
      to: 100
```

### Rum och Områden

```yaml
# config/custom_sentences/sv/rooms.yaml
language: sv

intents:
  HassLightSet:
    data:
      - sentences:
          - "tänd [alla] [lampor|lamporna] [i|på] {area}"
          - "släck [alla] [lampor|lamporna] [i|på] {area}"

  HassTurnOn:
    data:
      - sentences:
          - "starta {name}"
          - "sätt på {name}"
          - "slå på {name}"

  HassTurnOff:
    data:
      - sentences:
          - "stäng av {name}"
          - "stoppa {name}"
```

### Avancerade Mönster

```yaml
# config/custom_sentences/sv/scenes.yaml
language: sv

intents:
  HassSceneTurnOn:
    data:
      - sentences:
          - "[aktivera|starta|sätt på] {scene_mode} [läge|mode] [i|på] {area}"
          - "[jag vill ha] {scene_mode} [i|på] {area}"

lists:
  scene_mode:
    values:
      - in: "film"
        out: "movie"
      - in: "middag"
        out: "dinner"
      - in: "romantik"
        out: "romantic"
      - in: "fest"
        out: "party"
```

### Wildcards och Slots

```yaml
# config/custom_sentences/sv/custom.yaml
language: sv

intents:
  SetTemperature:
    data:
      - sentences:
          - "sätt temperaturen [i|på] {area} [till|på] {temperature} grader"
          - "{temperature} grader [i|på] {area}"

lists:
  temperature:
    range:
      from: 15
      to: 30
```

## Intent Scripts

Koppla intents till automationer:

```yaml
# config/intent_script.yaml
intent_script:
  GetWeatherForecast:
    speech:
      text: >
        Vädret imorgon blir {{ states('weather.home') }}
        med {{ state_attr('weather.home', 'temperature') }} grader.

  GoodMorning:
    speech:
      text: "God morgon! Jag förbereder huset."
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
      text: "Ha en bra dag! Jag stänger av allt."
    action:
      - service: script.leave_home
```

Registrera i `configuration.yaml`:

```yaml
intent_script: !include intent_script.yaml
```

Och skapa sentences:

```yaml
# config/custom_sentences/sv/routines.yaml
language: sv

intents:
  GoodMorning:
    data:
      - sentences:
          - "god morgon"
          - "vakna huset"
          - "starta morgonrutin"

  LeaveHome:
    data:
      - sentences:
          - "jag går nu"
          - "hejdå"
          - "stäng av allt"
```

## Områdesbaserade Kommandon

```yaml
# config/custom_sentences/sv/area_commands.yaml
language: sv

intents:
  HassLightSet:
    data:
      - sentences:
          - "dämpa [belysningen|ljuset] [i|på] {area}"
        slots:
          brightness: 30

      - sentences:
          - "full belysning [i|på] {area}"
          - "max ljus [i|på] {area}"
        slots:
          brightness: 100

      - sentences:
          - "mysbelysning [i|på] {area}"
        slots:
          brightness: 20

  HassTurnOn:
    data:
      - sentences:
          - "starta [alla] {device_class} [i|på] {area}"

  HassTurnOff:
    data:
      - sentences:
          - "[stäng av|stoppa] [alla] {device_class} [i|på] {area}"

lists:
  device_class:
    values:
      - in: "lampor"
        out: "light"
      - in: "fläktar"
        out: "fan"
      - in: "tv"
        out: "media_player"
```

## Mediakontroll

```yaml
# config/custom_sentences/sv/media.yaml
language: sv

intents:
  HassMediaPause:
    data:
      - sentences:
          - "pausa [musiken|videon|media]"
          - "stopp [musiken|videon]"

  HassMediaUnpause:
    data:
      - sentences:
          - "fortsätt [spela]"
          - "play"

  HassMediaNext:
    data:
      - sentences:
          - "nästa [låt|spår|video]"
          - "hoppa över"

  HassSetVolume:
    data:
      - sentences:
          - "[sätt] volymen [till] {volume} [procent]"
          - "{volume} [procent] volym"

lists:
  volume:
    range:
      from: 0
      to: 100
```

## Timer och Påminnelser

```yaml
# config/custom_sentences/sv/timers.yaml
language: sv

intents:
  HassTimerStart:
    data:
      - sentences:
          - "sätt [en] timer [på] {minutes} minuter"
          - "påminn mig om {minutes} minuter"
          - "väck mig om {minutes} minuter"

  HassTimerCancel:
    data:
      - sentences:
          - "avbryt timer[n]"
          - "stoppa timer[n]"
          - "stäng av timer[n]"

lists:
  minutes:
    range:
      from: 1
      to: 120
```

## Konversationsflöden

Multi-turn conversations:

```yaml
# config/custom_sentences/sv/conversation.yaml
language: sv

intents:
  StartVacuum:
    data:
      - sentences:
          - "städa {area}"

  ConfirmVacuum:
    data:
      - sentences:
          - "ja [tack]"
          - "kör [på]"
          - "starta"

  CancelVacuum:
    data:
      - sentences:
          - "nej [tack]"
          - "avbryt"
```

```yaml
# intent_script.yaml
intent_script:
  StartVacuum:
    speech:
      text: "Ska jag starta dammsugaren i {{ area }}? Säg ja eller nej."
    # Store context for follow-up

  ConfirmVacuum:
    speech:
      text: "Dammsugaren startar nu."
    action:
      - service: vacuum.start
        target:
          entity_id: vacuum.roborock
```

## Felsökning

### Debug Sentences

Testa dina sentences i Developer Tools → Assist:

1. Skriv in ditt kommando
2. Se vilken intent som matchas
3. Kontrollera slots och values

### Vanliga Problem

| Problem | Lösning |
|---------|---------|
| "Jag förstår inte" | Kontrollera sentence syntax |
| Fel intent matchas | Gör sentences mer specifika |
| Entity hittas inte | Använd friendly_name eller alias |
| Timeout | Kontrollera STT/TTS tjänster |

### Logga Conversation

```yaml
logger:
  logs:
    homeassistant.components.conversation: debug
    homeassistant.components.intent: debug
```

## Alias för Enheter

Ge enheter alternativa namn:

```yaml
# Settings → Devices & Services → Entities → [Entity] → Edit
# Eller via customize.yaml:

homeassistant:
  customize:
    light.living_room_ceiling:
      aliases:
        - taklampan
        - stora lampan
        - vardagsrumslampan
```

## Expose Configuration

Begränsa vilka enheter som kan styras:

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
          - "dim {name} to {brightness}"
```

## Exempelprompts

```
"Skapa svenska röstkommandon för att styra lampor i olika rum"

"Jag vill kunna säga 'god morgon' och starta en rutin"

"Konfigurera Assist för att hantera timer och påminnelser"

"Skapa custom sentences för mediakontroll på svenska"

"Felsök varför mitt röstkommando inte fungerar"
```

## Best Practices

1. **Använd synonymer** - `[tänd|slå på|starta]`
2. **Gör sentences naturliga** - Tänk på hur du faktiskt pratar
3. **Testa i Developer Tools** - Verifiera innan produktion
4. **Använd areas** - `{area}` istället för rumsnamn i sentences
5. **Begränsa exposed entities** - Säkerhet och prestanda
6. **Alias för friendly names** - Enklare att säga

## Se även

- `references/jinja2-templates.md` - Jinja2 för dynamiska svar
- `references/automations.md` - Koppla till automationer
- `../esphome/references/voice-local.md` - ESPHome voice devices
- `../ha-integration-dev/references/conversation-agent.md` - Custom agents
