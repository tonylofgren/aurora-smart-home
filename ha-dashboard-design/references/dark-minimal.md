# Dark Minimal Style

Pure black background, razor-thin borders, clean typography. No decorations - only information.
Inspired by Linear, Vercel, and high-end developer tools.

---

## 1. Theme YAML

Save as `config/themes/dark-minimal.yaml`:

```yaml
Dark Minimal:
  primary-color: "#ffffff"
  accent-color: "#ffffff"
  primary-background-color: "#000000"
  secondary-background-color: "#0a0a0a"
  card-background-color: "#0f0f0f"
  primary-text-color: "#ffffff"
  secondary-text-color: "#666666"
  disabled-text-color: "#333333"
  divider-color: "#1a1a1a"

  sidebar-background-color: "#050505"
  sidebar-selected-icon-color: "#ffffff"
  sidebar-icon-color: "#444444"
  sidebar-text-color: "#888888"

  state-on-color: "#ffffff"
  state-off-color: "#333333"

  primary-font-family: "'Inter', 'SF Pro Display', -apple-system, sans-serif"

  ha-card-border-radius: "12px"
  ha-card-box-shadow: "none"
  ha-card-border-color: "#1a1a1a"
```

---

## 2. card-mod Global Styles

```yaml
card_mod:
  style: |
    ha-card {
      background: #0f0f0f !important;
      border: 1px solid #1a1a1a !important;
      border-radius: 12px !important;
      box-shadow: none !important;
      transition: border-color 0.2s ease !important;
    }
    ha-card:hover {
      border-color: #333333 !important;
    }
```

---

## 3. Card Templates

### Sensor Display

```yaml
type: custom:button-card
entity: sensor.YOUR_TEMPERATURE
name: Temperature
icon: mdi:thermometer
styles:
  card:
    - background: "#0f0f0f"
    - border: 1px solid #1a1a1a
    - border-radius: 12px
    - padding: 24px
  icon:
    - color: "#ffffff"
    - width: 20px
    - opacity: "0.4"
  name:
    - color: "#666666"
    - font-size: 11px
    - text-transform: uppercase
    - letter-spacing: 1.5px
    - font-weight: 500
  state:
    - color: "#ffffff"
    - font-size: 40px
    - font-weight: 300
    - letter-spacing: -1px
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
        - background: "#0f0f0f"
        - border: 1px solid #1a1a1a
        - border-radius: 12px
        - padding: 20px
      name:
        - color: "#444444"
        - font-size: 10px
        - text-transform: uppercase
        - letter-spacing: 1.5px
      state:
        - color: white
        - font-size: 28px
        - font-weight: 300
      icon:
        - display: none
  - type: custom:button-card
    entity: sensor.YOUR_HUMIDITY
    name: Humidity
    styles:
      card:
        - background: "#0f0f0f"
        - border: 1px solid #1a1a1a
        - border-radius: 12px
        - padding: 20px
      name:
        - color: "#444444"
        - font-size: 10px
        - text-transform: uppercase
        - letter-spacing: 1.5px
      state:
        - color: white
        - font-size: 28px
        - font-weight: 300
      icon:
        - display: none
  - type: custom:button-card
    entity: sensor.YOUR_CO2
    name: CO₂
    styles:
      card:
        - background: "#0f0f0f"
        - border: 1px solid #1a1a1a
        - border-radius: 12px
        - padding: 20px
      name:
        - color: "#444444"
        - font-size: 10px
        - text-transform: uppercase
        - letter-spacing: 1.5px
      state:
        - color: white
        - font-size: 28px
        - font-weight: 300
      icon:
        - display: none
```

### Media Player

```yaml
type: media-player
entity: media_player.YOUR_SPEAKER
card_mod:
  style: |
    ha-card {
      background: #0f0f0f !important;
      border: 1px solid #1a1a1a !important;
      border-radius: 12px !important;
      box-shadow: none !important;
    }
    .title, .artist { color: white !important; }
    .secondary { color: #666 !important; }
    paper-progress { --paper-progress-active-color: white !important; }
```

### Light Control

```yaml
type: light
entity: light.YOUR_LIGHT
name: Light
card_mod:
  style: |
    ha-card {
      background: #0f0f0f !important;
      border: 1px solid #1a1a1a !important;
      border-radius: 12px !important;
    }
    .light-info .name { color: white !important; font-weight: 400 !important; }
    ha-slider { --slider-bar-color: white !important; }
```

### Button Grid

```yaml
type: grid
columns: 4
square: false
cards:
  - type: custom:button-card
    entity: switch.YOUR_SWITCH
    name: Kitchen
    icon: mdi:chef-hat
    state_display: " "
    styles:
      card:
        - background: "#0f0f0f"
        - border: 1px solid #1a1a1a
        - border-radius: 12px
        - padding: 16px 8px
        - height: 80px
      icon:
        - color: white
        - width: 22px
        - opacity: "0.8"
      name:
        - color: "#666"
        - font-size: 10px
        - text-transform: uppercase
        - letter-spacing: 1px
    state:
      - value: "on"
        styles:
          card:
            - border-color: "#333333"
            - background: "#161616"
          icon:
            - opacity: "1"
          name:
            - color: "#aaaaaa"
```

### Climate / Thermostat

```yaml
type: thermostat
entity: climate.YOUR_THERMOSTAT
card_mod:
  style: |
    ha-card {
      background: #0f0f0f !important;
      border: 1px solid #1a1a1a !important;
      border-radius: 12px !important;
    }
    .main-value { color: white !important; font-weight: 200 !important; font-size: 64px !important; }
    .current-mode { color: #666 !important; }
```

### Security / Alarm

```yaml
type: alarm-panel
entity: alarm_control_panel.YOUR_ALARM
card_mod:
  style: |
    ha-card {
      background: #0f0f0f !important;
      border: 1px solid #1a1a1a !important;
      border-radius: 12px !important;
    }
    .disarmed .state-label { color: #666 !important; }
    .armed .state-label { color: white !important; }
    mwc-button { --mdc-theme-primary: white !important; }
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
      border: 1px solid #1a1a1a !important;
      border-radius: 12px !important;
      overflow: hidden !important;
    }
    .box { background: linear-gradient(transparent, rgba(0,0,0,0.9)) !important; }
    .title { color: white !important; font-size: 13px !important; }
```

### Weather

```yaml
type: weather-forecast
entity: weather.YOUR_WEATHER
forecast_type: daily
card_mod:
  style: |
    ha-card {
      background: #0f0f0f !important;
      border: 1px solid #1a1a1a !important;
      border-radius: 12px !important;
    }
    .city { color: white !important; font-size: 16px !important; font-weight: 300 !important; }
    .temp { color: white !important; font-size: 56px !important; font-weight: 200 !important; }
    .templow, .temphigh { color: #666 !important; }
```

### Energy Monitor

```yaml
type: energy-distribution
card_mod:
  style: |
    ha-card {
      background: #0f0f0f !important;
      border: 1px solid #1a1a1a !important;
      border-radius: 12px !important;
    }
    .cell { color: white !important; }
    .value { font-weight: 300 !important; }
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
      background: #0f0f0f !important;
      border: 1px solid #1a1a1a !important;
      border-radius: 12px !important;
    }
    .card-header { color: white !important; font-weight: 400 !important; font-size: 14px !important; }
    svg text { fill: #666 !important; }
    svg .graph-line { stroke: white !important; }
```

### Presence / Person

```yaml
type: entities
title: Home
show_header_toggle: false
card_mod:
  style: |
    ha-card {
      background: #0f0f0f !important;
      border: 1px solid #1a1a1a !important;
      border-radius: 12px !important;
    }
    .card-header { color: white !important; font-weight: 400 !important; font-size: 13px !important; letter-spacing: 0.5px; }
    state-badge { border-radius: 50% !important; }
    .info { color: #666 !important; }
    .state { color: white !important; font-size: 12px !important; }
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
  name: Alert
  icon: mdi:alert-circle-outline
  styles:
    card:
      - background: "#0f0f0f"
      - border: 1px solid #ff4444
      - border-radius: 12px
      - padding: 16px 20px
    icon:
      - color: "#ff4444"
      - width: 18px
    name:
      - color: white
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
    - color: "#666"
    - width: 16px
  name:
    - color: white
    - font-size: 24px
    - font-weight: 300
    - letter-spacing: -0.5px
```

---

## 4. Sections Dashboard Example

```yaml
type: masonry  # Change to "sections" if using HA 2024.6+
max_columns: 4
background: "#000000"
sections:
  - type: grid
    title: ""
    cards:
      - type: custom:button-card
        name: Home
        icon: mdi:home-outline
        styles:
          card:
            - background: transparent
            - border: none
            - box-shadow: none
          name:
            - color: white
            - font-size: 28px
            - font-weight: 200
          icon:
            - display: none

  - type: grid
    title: Climate
    cards:
      - type: custom:button-card
        entity: sensor.YOUR_TEMPERATURE
        # ... sensor styles above

  - type: grid
    title: Lights
    cards:
      - type: light
        entity: light.YOUR_LIGHT
        # ... light styles above
```

---

*Part of [aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
