# Material You Style

Google Material Design 3 - dynamic color, generous rounded corners, tonal surfaces.
Familiar, polished, and accessible. Works great in both light and dark mode.

---

## 1. Theme YAML

Save as `config/themes/material-you.yaml`:

```yaml
Material You:
  primary-color: "#6750A4"
  accent-color: "#7965AF"
  primary-background-color: "#fffbfe"
  secondary-background-color: "#f3edf7"
  card-background-color: "#fffbfe"
  primary-text-color: "#1c1b1f"
  secondary-text-color: "#49454f"
  disabled-text-color: "#c4c0c9"
  divider-color: "#e6e0ec"

  sidebar-background-color: "#f3edf7"
  sidebar-selected-icon-color: "#6750A4"
  sidebar-icon-color: "#79747e"

  state-on-color: "#6750A4"
  state-off-color: "#e6e0ec"

  primary-font-family: "'Google Sans', 'Roboto', sans-serif"

  ha-card-border-radius: "28px"
  ha-card-box-shadow: "0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)"
  ha-card-border-color: "transparent"
```

---

## 2. card-mod Global Styles

```yaml
card_mod:
  style: |
    ha-card {
      background: #fffbfe !important;
      border: none !important;
      border-radius: 28px !important;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
      transition: box-shadow 0.2s, transform 0.2s !important;
    }
    ha-card:hover {
      box-shadow: 0 4px 8px rgba(103,80,164,0.15) !important;
      transform: translateY(-1px) !important;
    }
```

---

## 3. Card Templates

### Sensor Display

```yaml
type: custom:button-card
entity: sensor.YOUR_TEMPERATURE
name: Living Room
icon: mdi:thermometer
styles:
  card:
    - background: "#f3edf7"
    - border-radius: 28px
    - padding: 24px
    - box-shadow: none
  icon:
    - color: "#6750A4"
    - width: 28px
    - background: "rgba(103,80,164,0.1)"
    - border-radius: 50%
    - padding: 8px
  name:
    - color: "#49454f"
    - font-size: 12px
    - font-weight: 500
  state:
    - color: "#1c1b1f"
    - font-size: 36px
    - font-weight: 400
```

### Multi-Sensor Row

```yaml
type: horizontal-stack
cards:
  - type: custom:button-card
    entity: sensor.YOUR_TEMPERATURE
    name: Temp
    styles:
      card:
        - background: "#f3edf7"
        - border-radius: 24px
        - padding: 16px
        - box-shadow: none
      icon:
        - color: "#B3261E"
        - background: "rgba(179,38,30,0.1)"
        - border-radius: 50%
        - padding: 6px
        - width: 20px
      name:
        - color: "#49454f"
        - font-size: 11px
        - font-weight: 500
      state:
        - color: "#1c1b1f"
        - font-size: 22px
        - font-weight: 400
  - type: custom:button-card
    entity: sensor.YOUR_HUMIDITY
    name: Humidity
    styles:
      card:
        - background: "#e8f5e9"
        - border-radius: 24px
        - padding: 16px
        - box-shadow: none
      icon:
        - color: "#386A20"
        - background: "rgba(56,106,32,0.1)"
        - border-radius: 50%
        - padding: 6px
        - width: 20px
      name:
        - color: "#49454f"
        - font-size: 11px
        - font-weight: 500
      state:
        - color: "#1c1b1f"
        - font-size: 22px
        - font-weight: 400
```

### Media Player

```yaml
type: media-player
entity: media_player.YOUR_SPEAKER
card_mod:
  style: |
    ha-card {
      background: #f3edf7 !important;
      border-radius: 28px !important;
      box-shadow: none !important;
      border: none !important;
    }
    .title { color: #1c1b1f !important; font-weight: 500 !important; }
    .secondary { color: #49454f !important; }
    paper-progress { --paper-progress-active-color: #6750A4 !important; --paper-progress-container-color: #e8def8 !important; }
```

### Light Control

```yaml
type: light
entity: light.YOUR_LIGHT
name: Ceiling
card_mod:
  style: |
    ha-card {
      background: #fffde7 !important;
      border-radius: 28px !important;
      box-shadow: none !important;
    }
    .light-info .name { color: #1c1b1f !important; font-weight: 400 !important; }
    ha-slider { --slider-bar-color: #F6A800 !important; }
```

### Button Grid

```yaml
type: grid
columns: 3
square: true
cards:
  - type: custom:button-card
    entity: scene.YOUR_SCENE
    name: Relax
    icon: mdi:weather-sunset
    styles:
      card:
        - background: "#f3edf7"
        - border-radius: 24px
        - padding: 20px 12px
        - box-shadow: none
      icon:
        - color: "#6750A4"
        - background: "rgba(103,80,164,0.12)"
        - border-radius: 50%
        - padding: 8px
        - width: 24px
      name:
        - color: "#49454f"
        - font-size: 12px
        - font-weight: 500
    state:
      - value: "on"
        styles:
          card:
            - background: "#6750A4"
          icon:
            - color: white
            - background: "rgba(255,255,255,0.2)"
          name:
            - color: white
```

### Climate / Thermostat

```yaml
type: thermostat
entity: climate.YOUR_THERMOSTAT
card_mod:
  style: |
    ha-card {
      background: #f3edf7 !important;
      border-radius: 28px !important;
      box-shadow: none !important;
    }
    .main-value { color: #1c1b1f !important; }
    .current-mode { color: #49454f !important; }
```

### Security / Alarm

```yaml
type: alarm-panel
entity: alarm_control_panel.YOUR_ALARM
card_mod:
  style: |
    ha-card {
      background: #fce8e6 !important;
      border-radius: 28px !important;
      box-shadow: none !important;
    }
    .state-label { color: #B3261E !important; }
    mwc-button { --mdc-theme-primary: #B3261E !important; }
```

### Camera

```yaml
type: picture-glance
entity: camera.YOUR_CAMERA
title: Front Door
entities:
  - binary_sensor.YOUR_MOTION
  - lock.YOUR_DOOR_LOCK
card_mod:
  style: |
    ha-card {
      border-radius: 28px !important;
      overflow: hidden !important;
      box-shadow: 0 2px 8px rgba(0,0,0,0.12) !important;
    }
    .box { background: linear-gradient(transparent, rgba(28,27,31,0.85)) !important; }
    .title { color: white !important; font-weight: 500 !important; }
```

### Weather

```yaml
type: weather-forecast
entity: weather.YOUR_WEATHER
forecast_type: daily
card_mod:
  style: |
    ha-card {
      background: #e3f2fd !important;
      border-radius: 28px !important;
      box-shadow: none !important;
    }
    .city { color: #1c1b1f !important; font-weight: 500 !important; }
    .temp { color: #1c1b1f !important; font-weight: 300 !important; }
```

### Energy Monitor

```yaml
type: custom:button-card
entity: sensor.YOUR_POWER
name: Energy
icon: mdi:flash
styles:
  card:
    - background: "#fffde7"
    - border-radius: 28px
    - padding: 24px
    - box-shadow: none
  icon:
    - color: "#F6A800"
    - background: "rgba(246,168,0,0.12)"
    - border-radius: 50%
    - padding: 8px
    - width: 28px
  name:
    - color: "#49454f"
    - font-size: 12px
    - font-weight: 500
  state:
    - color: "#1c1b1f"
    - font-size: 32px
    - font-weight: 400
```

### Presence / Person

```yaml
type: entities
title: At Home
show_header_toggle: false
card_mod:
  style: |
    ha-card {
      background: #f3edf7 !important;
      border-radius: 28px !important;
      box-shadow: none !important;
    }
    .card-header { color: #1c1b1f !important; font-weight: 500 !important; }
    .state { color: #6750A4 !important; }
    .info { color: #49454f !important; }
entities:
  - entity: person.YOUR_PERSON
  - entity: person.YOUR_PERSON_2
```

### Statistics Graph

```yaml
type: statistics-graph
entities:
  - sensor.YOUR_TEMPERATURE
title: Temperature History
card_mod:
  style: |
    ha-card {
      background: #f3edf7 !important;
      border-radius: 28px !important;
      box-shadow: none !important;
    }
    .card-header { color: #1c1b1f !important; font-weight: 500 !important; }
    svg text { fill: #79747e !important; }
    svg .graph-line { stroke: #6750A4 !important; }
```

### Alert Banner

```yaml
type: conditional
conditions:
  - condition: state
    entity: binary_sensor.YOUR_ALERT
    state: "on"
card:
  type: custom:button-card
  name: Action needed
  icon: mdi:alert-circle-outline
  styles:
    card:
      - background: "#fce8e6"
      - border-radius: 28px
      - padding: 16px 20px
      - box-shadow: none
    icon:
      - color: "#B3261E"
      - background: "rgba(179,38,30,0.1)"
      - border-radius: 50%
      - padding: 6px
      - width: 18px
    name:
      - color: "#B3261E"
      - font-size: 13px
      - font-weight: 500
```

### Header / Navigation

```yaml
type: custom:button-card
name: Living Room
icon: mdi:sofa
styles:
  card:
    - background: "#6750A4"
    - border-radius: 50px
    - padding: 10px 20px
    - box-shadow: "0 2px 8px rgba(103,80,164,0.3)"
    - width: fit-content
  icon:
    - color: white
    - width: 18px
  name:
    - color: white
    - font-size: 13px
    - font-weight: 500
```

---

*Part of [aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
