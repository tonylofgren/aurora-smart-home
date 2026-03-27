# Retro Terminal Style

Green phosphor on black, monospace fonts, scanline effects.
Pure geek aesthetic - looks like a 1980s mainframe running your smart home.

---

## 1. Theme YAML

Save as `config/themes/retro-terminal.yaml`:

```yaml
Retro Terminal:
  primary-color: "#00cc44"
  accent-color: "#00ff55"
  primary-background-color: "#000800"
  secondary-background-color: "#010a02"
  card-background-color: "#020f04"
  primary-text-color: "#00cc44"
  secondary-text-color: "#006622"
  disabled-text-color: "#003311"
  divider-color: "#004418"

  sidebar-background-color: "#000800"
  sidebar-selected-icon-color: "#00ff55"
  sidebar-icon-color: "#004420"

  state-on-color: "#00ff55"
  state-off-color: "#003311"

  primary-font-family: "'Share Tech Mono', 'Courier New', monospace"

  ha-card-border-radius: "0px"
  ha-card-box-shadow: "0 0 0 1px #004420, 0 0 16px rgba(0,204,68,0.1)"
  ha-card-border-color: "#004420"
```

---

## 2. card-mod Global Styles

```yaml
card_mod:
  style: |
    ha-card {
      background: #020f04 !important;
      border: 1px solid #004420 !important;
      border-radius: 0 !important;
      box-shadow: 0 0 16px rgba(0,204,68,0.08) !important;
      font-family: 'Share Tech Mono', 'Courier New', monospace !important;
      position: relative !important;
      overflow: hidden !important;
    }
    ha-card::before {
      content: '' !important;
      position: absolute !important;
      top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important;
      background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0, 204, 68, 0.015) 2px,
        rgba(0, 204, 68, 0.015) 4px
      ) !important;
      pointer-events: none !important;
      z-index: 1 !important;
    }
```

---

## 3. Card Templates

### Sensor Display

```yaml
type: custom:button-card
entity: sensor.YOUR_TEMPERATURE
name: THERMAL SENSOR
icon: mdi:thermometer
styles:
  card:
    - background: "#020f04"
    - border: 1px solid #004420
    - border-radius: 0
    - padding: 24px
    - box-shadow: 0 0 16px rgba(0,204,68,0.08)
    - font-family: "'Share Tech Mono', monospace"
  icon:
    - color: "#00cc44"
    - width: 24px
    - filter: drop-shadow(0 0 4px #00cc44)
  name:
    - color: "#006622"
    - font-size: 9px
    - letter-spacing: 4px
    - font-family: "'Share Tech Mono', monospace"
  state:
    - color: "#00ff55"
    - font-size: 40px
    - font-weight: 400
    - font-family: "'Share Tech Mono', monospace"
    - text-shadow: 0 0 10px rgba(0,255,85,0.6)
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
        - background: "#020f04"
        - border: 1px solid #004420
        - border-radius: 0
        - padding: 16px
      icon:
        - display: none
      name:
        - color: "#004420"
        - font-size: 9px
        - letter-spacing: 3px
        - font-family: monospace
      state:
        - color: "#00cc44"
        - font-size: 22px
        - font-family: monospace
        - text-shadow: 0 0 8px rgba(0,204,68,0.5)
  - type: custom:button-card
    entity: sensor.YOUR_HUMIDITY
    name: HUM%
    styles:
      card:
        - background: "#020f04"
        - border: 1px solid #004420
        - border-radius: 0
        - padding: 16px
      icon:
        - display: none
      name:
        - color: "#004420"
        - font-size: 9px
        - letter-spacing: 3px
        - font-family: monospace
      state:
        - color: "#00cc44"
        - font-size: 22px
        - font-family: monospace
        - text-shadow: 0 0 8px rgba(0,204,68,0.5)
  - type: custom:button-card
    entity: sensor.YOUR_POWER
    name: WATT
    styles:
      card:
        - background: "#020f04"
        - border: 1px solid #004420
        - border-radius: 0
        - padding: 16px
      icon:
        - display: none
      name:
        - color: "#004420"
        - font-size: 9px
        - letter-spacing: 3px
        - font-family: monospace
      state:
        - color: "#00cc44"
        - font-size: 22px
        - font-family: monospace
        - text-shadow: 0 0 8px rgba(0,204,68,0.5)
```

### Button Grid

```yaml
type: grid
columns: 3
square: true
cards:
  - type: custom:button-card
    entity: switch.YOUR_SWITCH
    name: PWR_01
    icon: mdi:power
    styles:
      card:
        - background: "#020f04"
        - border: 1px solid #004420
        - border-radius: 0
        - padding: 20px 12px
      icon:
        - color: "#006622"
        - width: 24px
      name:
        - color: "#006622"
        - font-size: 9px
        - letter-spacing: 2px
        - font-family: monospace
    state:
      - value: "on"
        styles:
          card:
            - border-color: "#00cc44"
            - box-shadow: 0 0 12px rgba(0,204,68,0.2)
          icon:
            - color: "#00ff55"
            - filter: drop-shadow(0 0 4px #00ff55)
          name:
            - color: "#00cc44"
  - type: custom:button-card
    entity: switch.YOUR_SWITCH_2
    name: PWR_02
    icon: mdi:power
    styles:
      card:
        - background: "#020f04"
        - border: 1px solid #004420
        - border-radius: 0
        - padding: 20px 12px
      icon:
        - color: "#006622"
        - width: 24px
      name:
        - color: "#006622"
        - font-size: 9px
        - letter-spacing: 2px
        - font-family: monospace
    state:
      - value: "on"
        styles:
          card:
            - border-color: "#00cc44"
          icon:
            - color: "#00ff55"
          name:
            - color: "#00cc44"
```

### Weather

```yaml
type: weather-forecast
entity: weather.YOUR_WEATHER
forecast_type: daily
card_mod:
  style: |
    ha-card {
      background: #020f04 !important;
      border: 1px solid #004420 !important;
      border-radius: 0 !important;
    }
    .city { color: #00cc44 !important; font-family: monospace !important; font-size: 11px !important; letter-spacing: 4px !important; text-transform: uppercase !important; }
    .temp { color: #00ff55 !important; font-family: monospace !important; text-shadow: 0 0 10px rgba(0,255,85,0.5) !important; }
    .weather-condition { color: #006622 !important; }
```

### Alarm / Security

```yaml
type: alarm-panel
entity: alarm_control_panel.YOUR_ALARM
card_mod:
  style: |
    ha-card {
      background: #020f04 !important;
      border: 1px solid #cc2200 !important;
      border-radius: 0 !important;
      box-shadow: 0 0 20px rgba(204,34,0,0.1) !important;
    }
    .state-label { color: #ff3300 !important; font-family: monospace !important; text-shadow: 0 0 10px rgba(255,51,0,0.6) !important; }
```

### Statistics Graph

```yaml
type: statistics-graph
entities:
  - sensor.YOUR_TEMPERATURE
title: "> TELEMETRY_LOG"
card_mod:
  style: |
    ha-card {
      background: #020f04 !important;
      border: 1px solid #004420 !important;
      border-radius: 0 !important;
    }
    .card-header { color: #00cc44 !important; font-family: monospace !important; font-size: 11px !important; letter-spacing: 2px !important; }
    svg text { fill: #004420 !important; font-family: monospace !important; }
    svg .graph-line { stroke: #00cc44 !important; filter: drop-shadow(0 0 3px #00cc44) !important; }
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
  name: "!! SYSTEM ALERT - BREACH DETECTED !!"
  icon: mdi:alert
  styles:
    card:
      - background: "rgba(200, 30, 0, 0.1)"
      - border: 1px solid #cc2200
      - border-radius: 0
      - padding: 16px 20px
      - box-shadow: 0 0 20px rgba(200,30,0,0.2)
      - animation: terminal-blink 1s step-end infinite
    icon:
      - color: "#ff3300"
      - filter: drop-shadow(0 0 6px #ff3300)
      - width: 20px
    name:
      - color: "#ff3300"
      - font-family: monospace
      - font-size: 11px
      - letter-spacing: 2px
      - text-shadow: 0 0 8px rgba(255,51,0,0.8)
```

### Header / Navigation

```yaml
type: custom:button-card
name: "> SECTOR_01 / LIVING_ROOM"
styles:
  card:
    - background: transparent
    - border: none
    - border-bottom: 1px solid #004420
    - border-radius: 0
    - box-shadow: none
    - padding: 0 0 12px 0
    - width: fit-content
  name:
    - color: "#00cc44"
    - font-family: "'Share Tech Mono', monospace"
    - font-size: 13px
    - letter-spacing: 2px
    - text-shadow: 0 0 8px rgba(0,204,68,0.4)
  icon:
    - display: none
```

---

## 4. CSS Animations

Save as `/config/www/terminal-animations.css`:

```css
@keyframes terminal-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

@keyframes terminal-cursor {
  0%, 100% { border-right-color: #00cc44; }
  50% { border-right-color: transparent; }
}

/* Scanline overlay for the full page */
body::after {
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 30, 0, 0.08) 2px,
    rgba(0, 30, 0, 0.08) 4px
  );
  pointer-events: none;
  z-index: 9999;
}
```

Add to dashboard:
```yaml
resources:
  - url: /local/terminal-animations.css
    type: css
```

---

*Part of [aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
