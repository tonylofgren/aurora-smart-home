# Soft Pastel Style

Gentle pinks, lilacs, mint greens, and sky blues. Friendly, approachable, and cheerful.
Great for family homes - welcoming without being overwhelming.

---

## 1. Theme YAML

Save as `config/themes/soft-pastel.yaml`:

```yaml
Soft Pastel:
  primary-color: "#b388c8"
  accent-color: "#a0c8b0"
  primary-background-color: "#faf9ff"
  secondary-background-color: "#f2f0fa"
  card-background-color: "#ffffff"
  primary-text-color: "#3a2f4a"
  secondary-text-color: "#8878a0"
  disabled-text-color: "#c8c0d8"
  divider-color: "#ece8f4"

  sidebar-background-color: "#f2f0fa"
  sidebar-selected-icon-color: "#b388c8"
  sidebar-icon-color: "#b0a8c0"

  state-on-color: "#b388c8"
  state-off-color: "#ddd8ea"

  primary-font-family: "'Nunito', 'Quicksand', sans-serif"

  ha-card-border-radius: "22px"
  ha-card-box-shadow: "0 4px 16px rgba(100,80,140,0.08)"
  ha-card-border-color: "transparent"
```

---

## 2. card-mod Global Styles

```yaml
card_mod:
  style: |
    ha-card {
      background: #ffffff !important;
      border: none !important;
      border-radius: 22px !important;
      box-shadow: 0 4px 16px rgba(100,80,140,0.08) !important;
      transition: all 0.2s ease !important;
    }
    ha-card:hover {
      box-shadow: 0 6px 24px rgba(100,80,140,0.14) !important;
      transform: translateY(-2px) !important;
    }
```

---

## 3. Card Templates

### Sensor Display

```yaml
type: custom:button-card
entity: sensor.YOUR_TEMPERATURE
name: Bedroom
icon: mdi:thermometer
styles:
  card:
    - background: "linear-gradient(135deg, #fce4ec, #f8e6f8)"
    - border-radius: 22px
    - padding: 24px
    - box-shadow: 0 4px 16px rgba(180,120,160,0.15)
  icon:
    - color: "#c07898"
    - width: 28px
  name:
    - color: "#9878a8"
    - font-size: 12px
    - font-weight: 600
    - font-family: "'Nunito', sans-serif"
  state:
    - color: "#3a2f4a"
    - font-size: 36px
    - font-weight: 300
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
        - background: "linear-gradient(135deg, #fce4ec, #f8e6f8)"
        - border-radius: 20px
        - padding: 18px
        - box-shadow: none
      icon:
        - color: "#c07898"
        - width: 22px
      name:
        - color: "#9878a8"
        - font-size: 11px
        - font-weight: 600
      state:
        - color: "#3a2f4a"
        - font-size: 22px
        - font-weight: 400
  - type: custom:button-card
    entity: sensor.YOUR_HUMIDITY
    name: Humidity
    styles:
      card:
        - background: "linear-gradient(135deg, #e8f5e9, #e0f7ef)"
        - border-radius: 20px
        - padding: 18px
        - box-shadow: none
      icon:
        - color: "#5a9878"
        - width: 22px
      name:
        - color: "#5a9878"
        - font-size: 11px
        - font-weight: 600
      state:
        - color: "#3a2f4a"
        - font-size: 22px
        - font-weight: 400
  - type: custom:button-card
    entity: sensor.YOUR_CO2
    name: Air
    styles:
      card:
        - background: "linear-gradient(135deg, #e3f2fd, #e8eaf6)"
        - border-radius: 20px
        - padding: 18px
        - box-shadow: none
      icon:
        - color: "#5878b8"
        - width: 22px
      name:
        - color: "#5878b8"
        - font-size: 11px
        - font-weight: 600
      state:
        - color: "#3a2f4a"
        - font-size: 22px
        - font-weight: 400
```

### Button Grid

```yaml
type: grid
columns: 3
square: true
cards:
  - type: custom:button-card
    entity: scene.YOUR_SCENE
    name: Movie Night
    icon: mdi:popcorn
    styles:
      card:
        - background: "linear-gradient(135deg, #f3e5f5, #ede7f6)"
        - border-radius: 20px
        - padding: 20px 12px
        - box-shadow: none
      icon:
        - color: "#9c6fb8"
        - width: 28px
      name:
        - color: "#7858a0"
        - font-size: 11px
        - font-weight: 600
  - type: custom:button-card
    entity: scene.YOUR_SCENE_2
    name: Good Morning
    icon: mdi:weather-sunny
    styles:
      card:
        - background: "linear-gradient(135deg, #fffde7, #fff8e1)"
        - border-radius: 20px
        - padding: 20px 12px
        - box-shadow: none
      icon:
        - color: "#e8a030"
        - width: 28px
      name:
        - color: "#b07820"
        - font-size: 11px
        - font-weight: 600
  - type: custom:button-card
    entity: scene.YOUR_SCENE_3
    name: Story Time
    icon: mdi:book-open-variant
    styles:
      card:
        - background: "linear-gradient(135deg, #e8f5e9, #f1f8e9)"
        - border-radius: 20px
        - padding: 20px 12px
        - box-shadow: none
      icon:
        - color: "#4a9060"
        - width: 28px
      name:
        - color: "#3a7850"
        - font-size: 11px
        - font-weight: 600
```

### Weather

```yaml
type: weather-forecast
entity: weather.YOUR_WEATHER
forecast_type: daily
card_mod:
  style: |
    ha-card {
      background: linear-gradient(135deg, #e3f2fd, #e8eaf6) !important;
      border-radius: 22px !important;
      box-shadow: 0 4px 16px rgba(80,100,180,0.1) !important;
    }
    .city { color: #3a2f4a !important; font-weight: 600 !important; font-family: 'Nunito', sans-serif !important; }
    .temp { color: #3a2f4a !important; font-weight: 300 !important; }
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
  name: Heads up!
  icon: mdi:bell-ring
  styles:
    card:
      - background: "linear-gradient(135deg, #fce4ec, #ffeeff)"
      - border-radius: 22px
      - padding: 16px 20px
      - box-shadow: 0 4px 16px rgba(180,80,120,0.15)
    icon:
      - color: "#c0506a"
      - width: 22px
    name:
      - color: "#3a2f4a"
      - font-size: 13px
      - font-weight: 600
      - font-family: "'Nunito', sans-serif"
```

### Header / Navigation

```yaml
type: custom:button-card
name: Bedroom ✨
styles:
  card:
    - background: "linear-gradient(135deg, #f3e5f5, #ede7f6)"
    - border-radius: 50px
    - padding: 10px 22px
    - box-shadow: 0 4px 16px rgba(140,80,180,0.15)
    - width: fit-content
  name:
    - color: "#7858a0"
    - font-family: "'Nunito', sans-serif"
    - font-size: 14px
    - font-weight: 700
  icon:
    - display: none
```

---

*Part of [aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
