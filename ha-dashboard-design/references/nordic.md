# Nordic Style

Light, airy, Scandinavian design. Minimal color, generous whitespace, soft shadows.
Inspired by IKEA, Muuto, and Nordic interior design. Works beautifully in bright rooms.

---

## 1. Theme YAML

Save as `config/themes/nordic.yaml`:

```yaml
Nordic:
  primary-color: "#4a7c9e"
  accent-color: "#4a7c9e"
  primary-background-color: "#f5f5f0"
  secondary-background-color: "#eeeeea"
  card-background-color: "#ffffff"
  primary-text-color: "#1a1a1a"
  secondary-text-color: "#888888"
  disabled-text-color: "#cccccc"
  divider-color: "#e8e8e4"

  sidebar-background-color: "#f0f0eb"
  sidebar-selected-icon-color: "#4a7c9e"
  sidebar-icon-color: "#aaaaaa"
  sidebar-text-color: "#444444"

  state-on-color: "#4a7c9e"
  state-off-color: "#cccccc"

  primary-font-family: "'Inter', 'Helvetica Neue', sans-serif"

  ha-card-border-radius: "16px"
  ha-card-box-shadow: "0 2px 12px rgba(0,0,0,0.06)"
  ha-card-border-color: "rgba(0,0,0,0.06)"
```

---

## 2. card-mod Global Styles

```yaml
card_mod:
  style: |
    ha-card {
      background: #ffffff !important;
      border: 1px solid rgba(0,0,0,0.06) !important;
      border-radius: 16px !important;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
      transition: box-shadow 0.2s ease !important;
    }
    ha-card:hover {
      box-shadow: 0 4px 20px rgba(0,0,0,0.1) !important;
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
    - background: white
    - border: 1px solid rgba(0,0,0,0.06)
    - border-radius: 16px
    - padding: 24px
    - box-shadow: 0 2px 12px rgba(0,0,0,0.06)
  icon:
    - color: "#4a7c9e"
    - width: 28px
  name:
    - color: "#888888"
    - font-size: 12px
    - font-weight: 400
    - text-transform: none
  state:
    - color: "#1a1a1a"
    - font-size: 36px
    - font-weight: 300
```

### Multi-Sensor Row

```yaml
type: horizontal-stack
cards:
  - type: custom:button-card
    entity: sensor.YOUR_TEMPERATURE
    name: Temperature
    styles:
      card:
        - background: white
        - border: 1px solid rgba(0,0,0,0.06)
        - border-radius: 16px
        - padding: 20px
        - box-shadow: 0 2px 8px rgba(0,0,0,0.05)
      icon:
        - color: "#e8845a"
        - width: 24px
      name:
        - color: "#aaaaaa"
        - font-size: 11px
      state:
        - color: "#1a1a1a"
        - font-size: 24px
        - font-weight: 300
  - type: custom:button-card
    entity: sensor.YOUR_HUMIDITY
    name: Humidity
    styles:
      card:
        - background: white
        - border: 1px solid rgba(0,0,0,0.06)
        - border-radius: 16px
        - padding: 20px
        - box-shadow: 0 2px 8px rgba(0,0,0,0.05)
      icon:
        - color: "#4a7c9e"
        - width: 24px
      name:
        - color: "#aaaaaa"
        - font-size: 11px
      state:
        - color: "#1a1a1a"
        - font-size: 24px
        - font-weight: 300
```

### Media Player

```yaml
type: media-player
entity: media_player.YOUR_SPEAKER
card_mod:
  style: |
    ha-card {
      background: white !important;
      border: 1px solid rgba(0,0,0,0.06) !important;
      border-radius: 16px !important;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    }
    .title { color: #1a1a1a !important; font-weight: 400 !important; }
    .secondary { color: #888 !important; }
```

### Light Control

```yaml
type: light
entity: light.YOUR_LIGHT
name: Reading Light
card_mod:
  style: |
    ha-card {
      background: white !important;
      border: 1px solid rgba(0,0,0,0.06) !important;
      border-radius: 16px !important;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    }
    .light-info .name { color: #1a1a1a !important; font-weight: 400 !important; }
    ha-slider { --slider-bar-color: #4a7c9e !important; }
```

### Button Grid

```yaml
type: grid
columns: 4
square: false
cards:
  - type: custom:button-card
    entity: scene.YOUR_SCENE
    name: Morning
    icon: mdi:weather-sunny
    styles:
      card:
        - background: white
        - border: 1px solid rgba(0,0,0,0.06)
        - border-radius: 16px
        - padding: 16px 8px
        - box-shadow: 0 2px 8px rgba(0,0,0,0.05)
        - height: 80px
      icon:
        - color: "#e8a44a"
        - width: 24px
      name:
        - color: "#888"
        - font-size: 11px
  - type: custom:button-card
    entity: scene.YOUR_SCENE_2
    name: Dinner
    icon: mdi:silverware-fork-knife
    styles:
      card:
        - background: white
        - border: 1px solid rgba(0,0,0,0.06)
        - border-radius: 16px
        - padding: 16px 8px
        - box-shadow: 0 2px 8px rgba(0,0,0,0.05)
        - height: 80px
      icon:
        - color: "#e8845a"
        - width: 24px
      name:
        - color: "#888"
        - font-size: 11px
```

### Climate / Thermostat

```yaml
type: thermostat
entity: climate.YOUR_THERMOSTAT
card_mod:
  style: |
    ha-card {
      background: white !important;
      border: 1px solid rgba(0,0,0,0.06) !important;
      border-radius: 16px !important;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    }
    .main-value { color: #1a1a1a !important; font-weight: 200 !important; }
    .current-mode { color: #888 !important; }
```

### Security / Alarm

```yaml
type: alarm-panel
entity: alarm_control_panel.YOUR_ALARM
card_mod:
  style: |
    ha-card {
      background: white !important;
      border: 1px solid rgba(0,0,0,0.06) !important;
      border-radius: 16px !important;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    }
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
      border-radius: 16px !important;
      overflow: hidden !important;
      box-shadow: 0 2px 12px rgba(0,0,0,0.1) !important;
      border: none !important;
    }
    .box { background: linear-gradient(transparent, rgba(0,0,0,0.7)) !important; }
    .title { color: white !important; font-weight: 400 !important; }
```

### Weather

```yaml
type: weather-forecast
entity: weather.YOUR_WEATHER
forecast_type: daily
card_mod:
  style: |
    ha-card {
      background: white !important;
      border: 1px solid rgba(0,0,0,0.06) !important;
      border-radius: 16px !important;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    }
    .city { color: #1a1a1a !important; font-weight: 300 !important; }
    .temp { color: #1a1a1a !important; font-weight: 200 !important; }
    .templow { color: #aaa !important; }
```

### Energy Monitor

```yaml
type: custom:button-card
entity: sensor.YOUR_POWER
name: Power
icon: mdi:transmission-tower
styles:
  card:
    - background: white
    - border: 1px solid rgba(0,0,0,0.06)
    - border-radius: 16px
    - padding: 24px
    - box-shadow: 0 2px 12px rgba(0,0,0,0.06)
  icon:
    - color: "#4a7c9e"
    - width: 28px
  name:
    - color: "#888"
    - font-size: 12px
  state:
    - color: "#1a1a1a"
    - font-size: 32px
    - font-weight: 300
```

### Statistics Graph

```yaml
type: statistics-graph
entities:
  - sensor.YOUR_TEMPERATURE
title: Temperature
card_mod:
  style: |
    ha-card {
      background: white !important;
      border: 1px solid rgba(0,0,0,0.06) !important;
      border-radius: 16px !important;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    }
    .card-header { color: #1a1a1a !important; font-weight: 400 !important; font-size: 14px !important; }
    svg text { fill: #aaa !important; }
    svg .graph-line { stroke: #4a7c9e !important; }
```

### Presence / Person

```yaml
type: entities
title: Home
show_header_toggle: false
card_mod:
  style: |
    ha-card {
      background: white !important;
      border: 1px solid rgba(0,0,0,0.06) !important;
      border-radius: 16px !important;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    }
    .card-header { color: #1a1a1a !important; font-weight: 400 !important; }
    .info { color: #888 !important; }
    .state { color: #4a7c9e !important; }
entities:
  - entity: person.YOUR_PERSON
  - entity: person.YOUR_PERSON_2
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
  name: Alert - Check required
  icon: mdi:alert-circle-outline
  styles:
    card:
      - background: "#fff8f0"
      - border: 1px solid rgba(232, 132, 90, 0.4)
      - border-radius: 16px
      - padding: 16px 20px
    icon:
      - color: "#e8845a"
      - width: 20px
    name:
      - color: "#1a1a1a"
      - font-size: 13px
      - font-weight: 400
```

### Header / Navigation

```yaml
type: custom:button-card
name: Living Room
icon: mdi:sofa-outline
styles:
  card:
    - background: transparent
    - border: none
    - box-shadow: none
    - padding: 0
    - width: fit-content
  icon:
    - color: "#aaaaaa"
    - width: 18px
  name:
    - color: "#1a1a1a"
    - font-size: 22px
    - font-weight: 300
    - letter-spacing: -0.3px
```

---

*Part of [aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
