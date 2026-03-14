# Glassmorphism Style

Frosted glass cards with depth, blur, and transparency. Looks stunning over dark wallpaper backgrounds.

**Best background:** Dark gradient or blurred photo. Set via `background:` in dashboard config.

---

## 1. Theme YAML

Save as `config/themes/glassmorphism.yaml`:

```yaml
Glassmorphism:
  # Base colors
  primary-color: "#7c6bff"
  accent-color: "#a89bff"
  primary-background-color: "rgba(10, 10, 20, 0.95)"
  secondary-background-color: "rgba(255, 255, 255, 0.05)"
  card-background-color: "rgba(255, 255, 255, 0.08)"
  primary-text-color: "#ffffff"
  secondary-text-color: "rgba(255, 255, 255, 0.6)"
  disabled-text-color: "rgba(255, 255, 255, 0.3)"
  divider-color: "rgba(255, 255, 255, 0.1)"

  # Sidebar
  sidebar-background-color: "rgba(255, 255, 255, 0.03)"
  sidebar-selected-icon-color: "#7c6bff"
  sidebar-icon-color: "rgba(255, 255, 255, 0.5)"

  # States
  state-on-color: "#7c6bff"
  state-off-color: "rgba(255, 255, 255, 0.2)"

  # Typography
  primary-font-family: "'Inter', 'Segoe UI', sans-serif"
  paper-font-body1_-_font-size: "14px"

  # Card radius
  ha-card-border-radius: "20px"
  ha-card-box-shadow: "0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.1)"
  ha-card-border-color: "rgba(255, 255, 255, 0.15)"
```

---

## 2. card-mod Global Styles

Add to dashboard YAML under `card_mod:`:

```yaml
card_mod:
  style: |
    ha-card {
      background: rgba(255, 255, 255, 0.08) !important;
      backdrop-filter: blur(20px) saturate(180%) !important;
      -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
      border: 1px solid rgba(255, 255, 255, 0.15) !important;
      border-radius: 20px !important;
      box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
      transition: all 0.3s ease !important;
    }
    ha-card:hover {
      background: rgba(255, 255, 255, 0.12) !important;
      transform: translateY(-2px) !important;
      box-shadow:
        0 16px 48px rgba(0, 0, 0, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
    }
```

---

## 3. Dashboard Background

```yaml
# In your dashboard YAML (views section)
background: "center / cover no-repeat url('/local/backgrounds/dark-blur.jpg') fixed"
```

Or pure CSS gradient (no image needed):
```yaml
background: "linear-gradient(135deg, #0a0a14 0%, #1a0a2e 50%, #0a1a2e 100%) fixed"
```

---

## 4. Card Templates

### Sensor Display

```yaml
type: custom:button-card
entity: sensor.YOUR_TEMPERATURE
name: Living Room
icon: mdi:thermometer
styles:
  card:
    - background: rgba(255, 255, 255, 0.08)
    - backdrop-filter: blur(20px)
    - -webkit-backdrop-filter: blur(20px)
    - border: 1px solid rgba(255, 255, 255, 0.15)
    - border-radius: 20px
    - padding: 20px
    - box-shadow: 0 8px 32px rgba(0,0,0,0.4)
  icon:
    - color: "#7c6bff"
    - width: 36px
  name:
    - color: rgba(255,255,255,0.6)
    - font-size: 12px
    - text-transform: uppercase
    - letter-spacing: 1px
  state:
    - color: "#ffffff"
    - font-size: 32px
    - font-weight: 600
```

### Multi-Sensor Row

```yaml
type: horizontal-stack
cards:
  - type: custom:button-card
    entity: sensor.YOUR_TEMPERATURE
    name: Temp
    icon: mdi:thermometer
    styles:
      card:
        - background: rgba(255,255,255,0.08)
        - backdrop-filter: blur(20px)
        - border: 1px solid rgba(255,255,255,0.15)
        - border-radius: 20px
        - padding: 16px 12px
      icon:
        - color: "#ff6b6b"
        - width: 28px
      name:
        - color: rgba(255,255,255,0.5)
        - font-size: 11px
      state:
        - color: white
        - font-size: 22px
        - font-weight: 600
  - type: custom:button-card
    entity: sensor.YOUR_HUMIDITY
    name: Humidity
    icon: mdi:water-percent
    styles:
      card:
        - background: rgba(255,255,255,0.08)
        - backdrop-filter: blur(20px)
        - border: 1px solid rgba(255,255,255,0.15)
        - border-radius: 20px
        - padding: 16px 12px
      icon:
        - color: "#6bb5ff"
        - width: 28px
      name:
        - color: rgba(255,255,255,0.5)
        - font-size: 11px
      state:
        - color: white
        - font-size: 22px
        - font-weight: 600
```

### Media Player

```yaml
type: media-player
entity: media_player.YOUR_SPEAKER
card_mod:
  style: |
    ha-card {
      background: rgba(255, 255, 255, 0.08) !important;
      backdrop-filter: blur(20px) !important;
      border: 1px solid rgba(255, 255, 255, 0.15) !important;
      border-radius: 20px !important;
      overflow: hidden !important;
    }
    .title { color: white !important; font-weight: 600 !important; }
    .secondary { color: rgba(255,255,255,0.6) !important; }
```

### Light Control

```yaml
type: light
entity: light.YOUR_LIGHT
name: Living Room
card_mod:
  style: |
    ha-card {
      background: rgba(255, 200, 100, 0.08) !important;
      backdrop-filter: blur(20px) !important;
      border: 1px solid rgba(255, 200, 100, 0.2) !important;
      border-radius: 20px !important;
    }
    .light-info .name { color: white !important; }
```

### Button Grid (Scenes / Shortcuts)

```yaml
type: grid
columns: 3
square: true
cards:
  - type: custom:button-card
    entity: scene.YOUR_SCENE
    name: Movie
    icon: mdi:movie-open
    tap_action:
      action: call-service
      service: scene.turn_on
      target:
        entity_id: scene.YOUR_SCENE
    styles:
      card:
        - background: rgba(124, 107, 255, 0.15)
        - backdrop-filter: blur(20px)
        - border: 1px solid rgba(124, 107, 255, 0.3)
        - border-radius: 16px
        - padding: 20px 12px
        - transition: all 0.2s ease
      icon:
        - color: "#7c6bff"
        - width: 32px
      name:
        - color: rgba(255,255,255,0.8)
        - font-size: 12px
  - type: custom:button-card
    entity: scene.YOUR_SCENE_2
    name: Relax
    icon: mdi:candle
    styles:
      card:
        - background: rgba(255, 150, 80, 0.15)
        - backdrop-filter: blur(20px)
        - border: 1px solid rgba(255, 150, 80, 0.3)
        - border-radius: 16px
        - padding: 20px 12px
      icon:
        - color: "#ff9650"
        - width: 32px
      name:
        - color: rgba(255,255,255,0.8)
        - font-size: 12px
  - type: custom:button-card
    entity: scene.YOUR_SCENE_3
    name: Work
    icon: mdi:laptop
    styles:
      card:
        - background: rgba(100, 200, 150, 0.15)
        - backdrop-filter: blur(20px)
        - border: 1px solid rgba(100, 200, 150, 0.3)
        - border-radius: 16px
        - padding: 20px 12px
      icon:
        - color: "#64c896"
        - width: 32px
      name:
        - color: rgba(255,255,255,0.8)
        - font-size: 12px
```

### Climate / Thermostat

```yaml
type: thermostat
entity: climate.YOUR_THERMOSTAT
card_mod:
  style: |
    ha-card {
      background: rgba(255, 255, 255, 0.08) !important;
      backdrop-filter: blur(20px) !important;
      border: 1px solid rgba(255, 255, 255, 0.15) !important;
      border-radius: 24px !important;
    }
    #root .main {
      color: white !important;
    }
```

### Security / Alarm

```yaml
type: alarm-panel
entity: alarm_control_panel.YOUR_ALARM
states:
  - arm_home
  - arm_away
  - arm_night
card_mod:
  style: |
    ha-card {
      background: rgba(255, 50, 50, 0.08) !important;
      backdrop-filter: blur(20px) !important;
      border: 1px solid rgba(255, 50, 50, 0.2) !important;
      border-radius: 20px !important;
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
      border-radius: 20px !important;
      overflow: hidden !important;
      border: 1px solid rgba(255,255,255,0.15) !important;
      box-shadow: 0 8px 32px rgba(0,0,0,0.5) !important;
    }
```

### Weather

```yaml
type: weather-forecast
entity: weather.YOUR_WEATHER
forecast_type: daily
card_mod:
  style: |
    ha-card {
      background: rgba(100, 150, 255, 0.08) !important;
      backdrop-filter: blur(20px) !important;
      border: 1px solid rgba(100, 150, 255, 0.2) !important;
      border-radius: 20px !important;
    }
    .city { color: white !important; font-size: 20px !important; }
    .temp { color: white !important; font-size: 48px !important; font-weight: 300 !important; }
```

### Energy Monitor

```yaml
type: custom:button-card
entity: sensor.YOUR_POWER_SENSOR
name: Power Usage
icon: mdi:lightning-bolt
styles:
  card:
    - background: rgba(255, 220, 50, 0.08)
    - backdrop-filter: blur(20px)
    - border: 1px solid rgba(255, 220, 50, 0.2)
    - border-radius: 20px
    - padding: 24px
  icon:
    - color: "#ffdc32"
    - width: 40px
  name:
    - color: rgba(255,255,255,0.6)
    - font-size: 12px
    - text-transform: uppercase
    - letter-spacing: 1px
  state:
    - color: white
    - font-size: 36px
    - font-weight: 300
```

### Presence / Person

```yaml
type: entities
title: Home
card_mod:
  style: |
    ha-card {
      background: rgba(255,255,255,0.08) !important;
      backdrop-filter: blur(20px) !important;
      border: 1px solid rgba(255,255,255,0.15) !important;
      border-radius: 20px !important;
    }
    .card-header { color: white !important; }
entities:
  - type: custom:button-card
    entity: person.YOUR_PERSON
    name: You
    show_state: true
    styles:
      card:
        - background: transparent
        - border: none
        - box-shadow: none
        - padding: 8px 0
      name:
        - color: white
        - font-size: 14px
      state:
        - color: rgba(255,255,255,0.6)
        - font-size: 12px
      icon:
        - border-radius: 50%
        - width: 40px
        - height: 40px
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
      background: rgba(255,255,255,0.08) !important;
      backdrop-filter: blur(20px) !important;
      border: 1px solid rgba(255,255,255,0.15) !important;
      border-radius: 20px !important;
    }
    .card-header { color: white !important; }
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
  name: "⚠️ Alert Active"
  icon: mdi:alert
  styles:
    card:
      - background: rgba(255, 80, 80, 0.2)
      - backdrop-filter: blur(20px)
      - border: 1px solid rgba(255, 80, 80, 0.4)
      - border-radius: 16px
      - padding: 16px
      - animation: pulse 2s infinite
    icon:
      - color: "#ff5050"
    name:
      - color: white
      - font-weight: 600
```

### Header / Room Navigation

```yaml
type: custom:button-card
name: Living Room
icon: mdi:sofa
styles:
  card:
    - background: rgba(124, 107, 255, 0.2)
    - backdrop-filter: blur(20px)
    - border: 1px solid rgba(124, 107, 255, 0.4)
    - border-radius: 50px
    - padding: 12px 24px
    - width: fit-content
  icon:
    - color: "#7c6bff"
    - width: 20px
  name:
    - color: white
    - font-size: 14px
    - font-weight: 500
```

---

## 5. Sections Dashboard Example

```yaml
type: masonry  # Change to "sections" if using HA 2024.6+
max_columns: 3
sections:
  - type: grid
    title: Climate
    cards:
      - type: weather-forecast
        entity: weather.YOUR_WEATHER
        # ... card-mod styles above
      - type: thermostat
        entity: climate.YOUR_THERMOSTAT
        # ... card-mod styles above

  - type: grid
    title: Lights
    cards:
      - type: light
        entity: light.YOUR_LIGHT
        # ... card-mod styles above

  - type: grid
    title: Security
    cards:
      - type: alarm-panel
        entity: alarm_control_panel.YOUR_ALARM
        # ... card-mod styles above
      - type: picture-glance
        entity: camera.YOUR_CAMERA
        # ... card-mod styles above
```

---

*Part of [aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
