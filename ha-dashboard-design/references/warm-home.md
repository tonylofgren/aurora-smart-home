# Warm Home Style

Amber, terracotta, and warm neutrals. Cozy, inviting feel - like candlelight on plaster walls.
Perfect for living rooms and evening use. Inspired by Scandinavian hygge and Mediterranean interiors.

---

## 1. Theme YAML

Save as `config/themes/warm-home.yaml`:

```yaml
Warm Home:
  primary-color: "#c47a3a"
  accent-color: "#d4874a"
  primary-background-color: "#faf7f2"
  secondary-background-color: "#f2ede4"
  card-background-color: "#fefcf8"
  primary-text-color: "#2d1f0e"
  secondary-text-color: "#8a7060"
  disabled-text-color: "#c8b8a8"
  divider-color: "#e8ddd0"

  sidebar-background-color: "#f2ede4"
  sidebar-selected-icon-color: "#c47a3a"
  sidebar-icon-color: "#a0887a"

  state-on-color: "#c47a3a"
  state-off-color: "#ddd0c0"

  primary-font-family: "'Lora', 'Georgia', serif"

  ha-card-border-radius: "18px"
  ha-card-box-shadow: "0 2px 16px rgba(100,60,20,0.08)"
  ha-card-border-color: "rgba(180,130,80,0.15)"
```

---

## 2. card-mod Global Styles

```yaml
card_mod:
  style: |
    ha-card {
      background: #fefcf8 !important;
      border: 1px solid rgba(180,130,80,0.12) !important;
      border-radius: 18px !important;
      box-shadow: 0 2px 16px rgba(100,60,20,0.08) !important;
      transition: box-shadow 0.2s ease !important;
    }
    ha-card:hover {
      box-shadow: 0 4px 24px rgba(100,60,20,0.12) !important;
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
    - background: "#fefcf8"
    - border: 1px solid rgba(180,130,80,0.12)
    - border-radius: 18px
    - padding: 24px
    - box-shadow: 0 2px 16px rgba(100,60,20,0.08)
  icon:
    - color: "#c47a3a"
    - width: 28px
  name:
    - color: "#8a7060"
    - font-size: 12px
    - font-weight: 400
  state:
    - color: "#2d1f0e"
    - font-size: 36px
    - font-weight: 400
    - font-family: "'Lora', serif"
```

### Light Control

```yaml
type: light
entity: light.YOUR_LIGHT
name: Fireplace Lamp
card_mod:
  style: |
    ha-card {
      background: linear-gradient(135deg, #fefcf8, #fdf5e6) !important;
      border: 1px solid rgba(196,122,58,0.2) !important;
      border-radius: 18px !important;
      box-shadow: 0 2px 16px rgba(100,60,20,0.08) !important;
    }
    .light-info .name { color: #2d1f0e !important; }
    ha-slider { --slider-bar-color: #c47a3a !important; }
```

### Button Grid

```yaml
type: grid
columns: 3
square: true
cards:
  - type: custom:button-card
    entity: scene.YOUR_SCENE
    name: Evening
    icon: mdi:candle
    styles:
      card:
        - background: "linear-gradient(135deg, #fdf5e6, #fae8c8)"
        - border: 1px solid rgba(196,122,58,0.2)
        - border-radius: 18px
        - padding: 20px 12px
      icon:
        - color: "#c47a3a"
        - width: 28px
      name:
        - color: "#8a7060"
        - font-size: 12px
  - type: custom:button-card
    entity: scene.YOUR_SCENE_2
    name: Dinner
    icon: mdi:food-turkey
    styles:
      card:
        - background: "linear-gradient(135deg, #fef5ee, #fde8d4)"
        - border: 1px solid rgba(200,100,60,0.2)
        - border-radius: 18px
        - padding: 20px 12px
      icon:
        - color: "#c46a3a"
        - width: 28px
      name:
        - color: "#8a7060"
        - font-size: 12px
  - type: custom:button-card
    entity: scene.YOUR_SCENE_3
    name: Morning
    icon: mdi:coffee
    styles:
      card:
        - background: "linear-gradient(135deg, #fdfaf5, #f8eedc)"
        - border: 1px solid rgba(160,100,40,0.2)
        - border-radius: 18px
        - padding: 20px 12px
      icon:
        - color: "#a46a2a"
        - width: 28px
      name:
        - color: "#8a7060"
        - font-size: 12px
```

### Weather

```yaml
type: weather-forecast
entity: weather.YOUR_WEATHER
forecast_type: daily
card_mod:
  style: |
    ha-card {
      background: linear-gradient(135deg, #fefcf8, #fdf5e6) !important;
      border: 1px solid rgba(180,130,80,0.12) !important;
      border-radius: 18px !important;
      box-shadow: 0 2px 16px rgba(100,60,20,0.08) !important;
    }
    .city { color: #2d1f0e !important; font-family: 'Lora', serif !important; }
    .temp { color: #2d1f0e !important; font-weight: 300 !important; }
```

### Climate / Thermostat

```yaml
type: thermostat
entity: climate.YOUR_THERMOSTAT
card_mod:
  style: |
    ha-card {
      background: linear-gradient(135deg, #fefcf8, #fdf5e6) !important;
      border: 1px solid rgba(180,130,80,0.15) !important;
      border-radius: 18px !important;
    }
    .main-value { color: #c47a3a !important; }
    .current-mode { color: #8a7060 !important; }
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
  name: Attention needed
  icon: mdi:bell-ring-outline
  styles:
    card:
      - background: "#fef5ee"
      - border: 1px solid rgba(196,80,40,0.3)
      - border-radius: 18px
      - padding: 16px 20px
    icon:
      - color: "#c44a2a"
      - width: 20px
    name:
      - color: "#2d1f0e"
      - font-size: 13px
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
    - color: "#c47a3a"
    - width: 20px
  name:
    - color: "#2d1f0e"
    - font-family: "'Lora', Georgia, serif"
    - font-size: 24px
    - font-weight: 400
    - letter-spacing: 0.3px
```

---

*Part of [aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
