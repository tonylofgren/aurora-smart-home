# Neon / Cyberpunk Style

Dark background with vivid neon accents, glow effects, and pulse animations.
Maximum visual impact — perfect for dedicated wall-mounted displays and night mode.

---

## 1. Theme YAML

Save as `config/themes/neon-cyberpunk.yaml`:

```yaml
Neon Cyberpunk:
  primary-color: "#00f5ff"
  accent-color: "#ff00ff"
  primary-background-color: "#050508"
  secondary-background-color: "#0a0a10"
  card-background-color: "#0d0d18"
  primary-text-color: "#e0e0ff"
  secondary-text-color: "#6060a0"
  disabled-text-color: "#303050"
  divider-color: "#1a1a30"

  sidebar-background-color: "#050508"
  sidebar-selected-icon-color: "#00f5ff"
  sidebar-icon-color: "#404060"

  state-on-color: "#00f5ff"
  state-off-color: "#202035"

  primary-font-family: "'Orbitron', 'Share Tech Mono', monospace"

  ha-card-border-radius: "8px"
  ha-card-box-shadow: "0 0 20px rgba(0, 245, 255, 0.1), inset 0 0 20px rgba(0,0,0,0.5)"
  ha-card-border-color: "rgba(0, 245, 255, 0.2)"
```

---

## 2. card-mod Global Styles

```yaml
card_mod:
  style: |
    ha-card {
      background: #0d0d18 !important;
      border: 1px solid rgba(0, 245, 255, 0.2) !important;
      border-radius: 8px !important;
      box-shadow: 0 0 20px rgba(0, 245, 255, 0.05) !important;
      position: relative !important;
      overflow: hidden !important;
      transition: all 0.3s ease !important;
    }
    ha-card::before {
      content: '' !important;
      position: absolute !important;
      top: 0 !important; left: 0 !important; right: 0 !important;
      height: 1px !important;
      background: linear-gradient(90deg, transparent, rgba(0,245,255,0.8), transparent) !important;
    }
    ha-card:hover {
      border-color: rgba(0, 245, 255, 0.5) !important;
      box-shadow: 0 0 30px rgba(0, 245, 255, 0.15) !important;
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
    - background: "#0d0d18"
    - border: 1px solid rgba(0, 245, 255, 0.2)
    - border-radius: 8px
    - padding: 24px
    - box-shadow: 0 0 20px rgba(0,245,255,0.05)
    - position: relative
    - overflow: hidden
  icon:
    - color: "#00f5ff"
    - width: 32px
    - filter: drop-shadow(0 0 6px #00f5ff)
  name:
    - color: "#6060a0"
    - font-size: 10px
    - text-transform: uppercase
    - letter-spacing: 3px
    - font-family: "'Orbitron', monospace"
  state:
    - color: "#00f5ff"
    - font-size: 36px
    - font-weight: 700
    - font-family: "'Orbitron', monospace"
    - text-shadow: 0 0 20px rgba(0,245,255,0.8)
```

### Multi-Sensor Row

```yaml
type: horizontal-stack
cards:
  - type: custom:button-card
    entity: sensor.YOUR_TEMPERATURE
    name: TEMP
    styles:
      card:
        - background: "#0d0d18"
        - border: 1px solid rgba(0,245,255,0.2)
        - border-radius: 8px
        - padding: 16px
      icon:
        - display: none
      name:
        - color: "#404060"
        - font-size: 9px
        - letter-spacing: 3px
        - font-family: monospace
      state:
        - color: "#00f5ff"
        - font-size: 24px
        - font-weight: 700
        - text-shadow: 0 0 10px rgba(0,245,255,0.6)
  - type: custom:button-card
    entity: sensor.YOUR_HUMIDITY
    name: HUM
    styles:
      card:
        - background: "#0d0d18"
        - border: 1px solid rgba(255,0,255,0.2)
        - border-radius: 8px
        - padding: 16px
      icon:
        - display: none
      name:
        - color: "#604060"
        - font-size: 9px
        - letter-spacing: 3px
        - font-family: monospace
      state:
        - color: "#ff00ff"
        - font-size: 24px
        - font-weight: 700
        - text-shadow: 0 0 10px rgba(255,0,255,0.6)
  - type: custom:button-card
    entity: sensor.YOUR_POWER
    name: PWR
    styles:
      card:
        - background: "#0d0d18"
        - border: 1px solid rgba(255,220,0,0.2)
        - border-radius: 8px
        - padding: 16px
      icon:
        - display: none
      name:
        - color: "#606000"
        - font-size: 9px
        - letter-spacing: 3px
        - font-family: monospace
      state:
        - color: "#ffdc00"
        - font-size: 24px
        - font-weight: 700
        - text-shadow: 0 0 10px rgba(255,220,0,0.6)
```

### Media Player

```yaml
type: media-player
entity: media_player.YOUR_SPEAKER
card_mod:
  style: |
    ha-card {
      background: #0d0d18 !important;
      border: 1px solid rgba(0,245,255,0.2) !important;
      border-radius: 8px !important;
      box-shadow: 0 0 20px rgba(0,245,255,0.05) !important;
    }
    .title { color: #00f5ff !important; text-shadow: 0 0 10px rgba(0,245,255,0.5) !important; }
    .secondary { color: #6060a0 !important; }
    paper-progress { --paper-progress-active-color: #00f5ff !important; }
```

### Light Control

```yaml
type: light
entity: light.YOUR_LIGHT
name: Neural Grid
card_mod:
  style: |
    ha-card {
      background: #0d0d18 !important;
      border: 1px solid rgba(255,0,255,0.2) !important;
      border-radius: 8px !important;
      box-shadow: 0 0 20px rgba(255,0,255,0.05) !important;
    }
    .light-info .name { color: #ff00ff !important; text-shadow: 0 0 10px rgba(255,0,255,0.5) !important; }
    ha-slider { --slider-bar-color: #ff00ff !important; }
```

### Button Grid

```yaml
type: grid
columns: 3
square: true
cards:
  - type: custom:button-card
    entity: scene.YOUR_SCENE
    name: ENGAGE
    icon: mdi:lightning-bolt
    styles:
      card:
        - background: "rgba(0, 245, 255, 0.05)"
        - border: 1px solid rgba(0, 245, 255, 0.3)
        - border-radius: 8px
        - padding: 20px 12px
        - box-shadow: 0 0 15px rgba(0,245,255,0.1)
      icon:
        - color: "#00f5ff"
        - width: 28px
        - filter: drop-shadow(0 0 4px #00f5ff)
      name:
        - color: "#00f5ff"
        - font-size: 9px
        - letter-spacing: 3px
        - font-family: monospace
  - type: custom:button-card
    entity: scene.YOUR_SCENE_2
    name: STEALTH
    icon: mdi:eye-off
    styles:
      card:
        - background: "rgba(255, 0, 255, 0.05)"
        - border: 1px solid rgba(255, 0, 255, 0.3)
        - border-radius: 8px
        - padding: 20px 12px
        - box-shadow: 0 0 15px rgba(255,0,255,0.1)
      icon:
        - color: "#ff00ff"
        - width: 28px
        - filter: drop-shadow(0 0 4px #ff00ff)
      name:
        - color: "#ff00ff"
        - font-size: 9px
        - letter-spacing: 3px
        - font-family: monospace
  - type: custom:button-card
    entity: scene.YOUR_SCENE_3
    name: REBOOT
    icon: mdi:restart
    styles:
      card:
        - background: "rgba(255, 220, 0, 0.05)"
        - border: 1px solid rgba(255, 220, 0, 0.3)
        - border-radius: 8px
        - padding: 20px 12px
        - box-shadow: 0 0 15px rgba(255,220,0,0.1)
      icon:
        - color: "#ffdc00"
        - width: 28px
        - filter: drop-shadow(0 0 4px #ffdc00)
      name:
        - color: "#ffdc00"
        - font-size: 9px
        - letter-spacing: 3px
        - font-family: monospace
```

### Climate / Thermostat

```yaml
type: thermostat
entity: climate.YOUR_THERMOSTAT
card_mod:
  style: |
    ha-card {
      background: #0d0d18 !important;
      border: 1px solid rgba(0,245,255,0.2) !important;
      border-radius: 8px !important;
    }
    .main-value {
      color: #00f5ff !important;
      text-shadow: 0 0 20px rgba(0,245,255,0.8) !important;
      font-size: 56px !important;
    }
```

### Security / Alarm

```yaml
type: alarm-panel
entity: alarm_control_panel.YOUR_ALARM
card_mod:
  style: |
    ha-card {
      background: #0d0d18 !important;
      border: 1px solid rgba(255, 50, 50, 0.4) !important;
      border-radius: 8px !important;
      box-shadow: 0 0 30px rgba(255,50,50,0.1) !important;
    }
    .state-label { color: #ff3232 !important; text-shadow: 0 0 10px rgba(255,50,50,0.8) !important; }
```

### Camera

```yaml
type: picture-glance
entity: camera.YOUR_CAMERA
title: SURVEILLANCE
entities:
  - binary_sensor.YOUR_MOTION
  - lock.YOUR_DOOR_LOCK
card_mod:
  style: |
    ha-card {
      border: 1px solid rgba(0,245,255,0.3) !important;
      border-radius: 8px !important;
      overflow: hidden !important;
      box-shadow: 0 0 20px rgba(0,245,255,0.1) !important;
    }
    .box { background: linear-gradient(transparent, rgba(5,5,8,0.95)) !important; }
    .title { color: #00f5ff !important; font-family: monospace !important; font-size: 11px !important; letter-spacing: 2px !important; }
```

### Weather

```yaml
type: weather-forecast
entity: weather.YOUR_WEATHER
forecast_type: daily
card_mod:
  style: |
    ha-card {
      background: #0d0d18 !important;
      border: 1px solid rgba(0,245,255,0.2) !important;
      border-radius: 8px !important;
    }
    .city { color: #00f5ff !important; font-family: monospace !important; letter-spacing: 2px !important; font-size: 12px !important; }
    .temp { color: #00f5ff !important; text-shadow: 0 0 20px rgba(0,245,255,0.6) !important; font-size: 52px !important; }
```

### Energy Monitor

```yaml
type: custom:button-card
entity: sensor.YOUR_POWER
name: POWER GRID
icon: mdi:lightning-bolt-circle
styles:
  card:
    - background: "#0d0d18"
    - border: 1px solid rgba(255,220,0,0.3)
    - border-radius: 8px
    - padding: 24px
    - box-shadow: 0 0 20px rgba(255,220,0,0.08)
  icon:
    - color: "#ffdc00"
    - width: 36px
    - filter: drop-shadow(0 0 8px #ffdc00)
  name:
    - color: "#606000"
    - font-size: 9px
    - letter-spacing: 3px
    - font-family: monospace
  state:
    - color: "#ffdc00"
    - font-size: 36px
    - font-weight: 700
    - font-family: monospace
    - text-shadow: 0 0 15px rgba(255,220,0,0.8)
```

### Presence / Person

```yaml
type: entities
title: OPERATORS ONLINE
show_header_toggle: false
card_mod:
  style: |
    ha-card {
      background: #0d0d18 !important;
      border: 1px solid rgba(0,245,255,0.2) !important;
      border-radius: 8px !important;
    }
    .card-header { color: #00f5ff !important; font-family: monospace !important; font-size: 10px !important; letter-spacing: 3px !important; }
    .state { color: #00f5ff !important; font-size: 10px !important; letter-spacing: 1px !important; }
    .info { color: #6060a0 !important; }
entities:
  - entity: person.YOUR_PERSON
  - entity: person.YOUR_PERSON_2
```

### Statistics Graph

```yaml
type: statistics-graph
entities:
  - sensor.YOUR_TEMPERATURE
title: TELEMETRY
card_mod:
  style: |
    ha-card {
      background: #0d0d18 !important;
      border: 1px solid rgba(0,245,255,0.2) !important;
      border-radius: 8px !important;
    }
    .card-header { color: #00f5ff !important; font-family: monospace !important; font-size: 10px !important; letter-spacing: 3px !important; }
    svg .graph-line { stroke: #00f5ff !important; filter: drop-shadow(0 0 4px #00f5ff) !important; }
    svg text { fill: #404060 !important; font-family: monospace !important; }
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
  name: SYSTEM ALERT — INTRUSION DETECTED
  icon: mdi:shield-alert
  styles:
    card:
      - background: "rgba(255, 0, 0, 0.1)"
      - border: 1px solid rgba(255, 0, 0, 0.6)
      - border-radius: 8px
      - padding: 16px 20px
      - box-shadow: 0 0 30px rgba(255,0,0,0.2)
      - animation: neon-pulse 1s infinite
    icon:
      - color: "#ff3232"
      - filter: drop-shadow(0 0 8px #ff3232)
      - width: 20px
    name:
      - color: "#ff3232"
      - font-family: monospace
      - font-size: 11px
      - letter-spacing: 2px
      - text-shadow: 0 0 10px rgba(255,50,50,0.8)
```

### Header / Navigation

```yaml
type: custom:button-card
name: SECTOR 01 — LIVING ROOM
icon: mdi:map-marker
styles:
  card:
    - background: transparent
    - border: none
    - box-shadow: none
    - padding: 0
    - width: fit-content
  icon:
    - color: "#00f5ff"
    - filter: drop-shadow(0 0 4px #00f5ff)
    - width: 14px
  name:
    - color: "#00f5ff"
    - font-family: "'Orbitron', monospace"
    - font-size: 11px
    - letter-spacing: 4px
    - text-shadow: 0 0 10px rgba(0,245,255,0.5)
```

---

## 4. CSS Animation (add to lovelace resources)

Save as `/config/www/neon-animations.css`:

```css
@keyframes neon-pulse {
  0%, 100% { box-shadow: 0 0 20px rgba(255,0,0,0.2); border-color: rgba(255,0,0,0.4); }
  50% { box-shadow: 0 0 40px rgba(255,0,0,0.4); border-color: rgba(255,0,0,0.8); }
}

@keyframes scan-line {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100vh); }
}
```

Add to dashboard:
```yaml
resources:
  - url: /local/neon-animations.css
    type: css
```

---

*Part of [aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
