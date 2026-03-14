# Luxury Gold Style

Deep navy and charcoal backgrounds with gold accents and warm ambient lighting.
Opulent, sophisticated, and dramatic. Ideal for premium smart home displays.

---

## 1. Theme YAML

Save as `config/themes/luxury-gold.yaml`:

```yaml
Luxury Gold:
  primary-color: "#c9a84c"
  accent-color: "#d4b060"
  primary-background-color: "#0d0f18"
  secondary-background-color: "#131520"
  card-background-color: "#161a28"
  primary-text-color: "#f0e8d0"
  secondary-text-color: "#8a7a60"
  disabled-text-color: "#3a3020"
  divider-color: "#2a2416"

  sidebar-background-color: "#0d0f18"
  sidebar-selected-icon-color: "#c9a84c"
  sidebar-icon-color: "#5a5040"

  state-on-color: "#c9a84c"
  state-off-color: "#2a2416"

  primary-font-family: "'Cormorant Garamond', 'Playfair Display', Georgia, serif"

  ha-card-border-radius: "4px"
  ha-card-box-shadow: "0 4px 32px rgba(0,0,0,0.6), inset 0 1px 0 rgba(201,168,76,0.1)"
  ha-card-border-color: "rgba(201,168,76,0.15)"
```

---

## 2. card-mod Global Styles

```yaml
card_mod:
  style: |
    ha-card {
      background: #161a28 !important;
      border: 1px solid rgba(201,168,76,0.15) !important;
      border-radius: 4px !important;
      box-shadow: 0 4px 32px rgba(0,0,0,0.6), inset 0 1px 0 rgba(201,168,76,0.1) !important;
      position: relative !important;
      overflow: hidden !important;
    }
    ha-card::after {
      content: '' !important;
      position: absolute !important;
      bottom: 0 !important; left: 0 !important; right: 0 !important;
      height: 1px !important;
      background: linear-gradient(90deg, transparent, rgba(201,168,76,0.4), transparent) !important;
    }
```

---

## 3. Card Templates

### Sensor Display

```yaml
type: custom:button-card
entity: sensor.YOUR_TEMPERATURE
name: Grand Salon
icon: mdi:thermometer
styles:
  card:
    - background: "#161a28"
    - border: 1px solid rgba(201,168,76,0.15)
    - border-radius: 4px
    - padding: 28px
    - box-shadow: "0 4px 32px rgba(0,0,0,0.6)"
  icon:
    - color: "#c9a84c"
    - width: 24px
    - opacity: "0.7"
  name:
    - color: "#5a5040"
    - font-size: 10px
    - text-transform: uppercase
    - letter-spacing: 4px
    - font-family: "'Cormorant Garamond', serif"
    - font-weight: 400
  state:
    - color: "#c9a84c"
    - font-size: 44px
    - font-weight: 300
    - font-family: "'Cormorant Garamond', serif"
    - letter-spacing: -1px
```

### Multi-Sensor Row

```yaml
type: horizontal-stack
cards:
  - type: custom:button-card
    entity: sensor.YOUR_TEMPERATURE
    name: Salon
    styles:
      card:
        - background: "#161a28"
        - border: 1px solid rgba(201,168,76,0.1)
        - border-radius: 4px
        - padding: 20px
      icon:
        - display: none
      name:
        - color: "#5a5040"
        - font-size: 9px
        - text-transform: uppercase
        - letter-spacing: 3px
        - font-family: "'Cormorant Garamond', serif"
      state:
        - color: "#c9a84c"
        - font-size: 28px
        - font-weight: 300
        - font-family: "'Cormorant Garamond', serif"
  - type: custom:button-card
    entity: sensor.YOUR_HUMIDITY
    name: Humidity
    styles:
      card:
        - background: "#161a28"
        - border: 1px solid rgba(201,168,76,0.1)
        - border-radius: 4px
        - padding: 20px
      icon:
        - display: none
      name:
        - color: "#5a5040"
        - font-size: 9px
        - text-transform: uppercase
        - letter-spacing: 3px
        - font-family: "'Cormorant Garamond', serif"
      state:
        - color: "#c9a84c"
        - font-size: 28px
        - font-weight: 300
        - font-family: "'Cormorant Garamond', serif"
```

### Button Grid

```yaml
type: grid
columns: 3
square: true
cards:
  - type: custom:button-card
    entity: scene.YOUR_SCENE
    name: Soirée
    icon: mdi:glass-cocktail
    styles:
      card:
        - background: "rgba(201,168,76,0.05)"
        - border: 1px solid rgba(201,168,76,0.2)
        - border-radius: 4px
        - padding: 24px 12px
      icon:
        - color: "#c9a84c"
        - width: 28px
      name:
        - color: "#8a7a60"
        - font-size: 10px
        - letter-spacing: 3px
        - text-transform: uppercase
        - font-family: "'Cormorant Garamond', serif"
    state:
      - value: "on"
        styles:
          card:
            - background: "rgba(201,168,76,0.12)"
            - border: 1px solid rgba(201,168,76,0.4)
  - type: custom:button-card
    entity: scene.YOUR_SCENE_2
    name: Repose
    icon: mdi:candle
    styles:
      card:
        - background: "rgba(201,168,76,0.05)"
        - border: 1px solid rgba(201,168,76,0.2)
        - border-radius: 4px
        - padding: 24px 12px
      icon:
        - color: "#c9a84c"
        - width: 28px
      name:
        - color: "#8a7a60"
        - font-size: 10px
        - letter-spacing: 3px
        - text-transform: uppercase
        - font-family: "'Cormorant Garamond', serif"
```

### Climate / Thermostat

```yaml
type: thermostat
entity: climate.YOUR_THERMOSTAT
card_mod:
  style: |
    ha-card {
      background: #161a28 !important;
      border: 1px solid rgba(201,168,76,0.15) !important;
      border-radius: 4px !important;
    }
    .main-value {
      color: #c9a84c !important;
      font-family: 'Cormorant Garamond', serif !important;
      font-size: 64px !important;
      font-weight: 300 !important;
    }
    .current-mode { color: #5a5040 !important; font-size: 11px !important; letter-spacing: 2px !important; }
```

### Weather

```yaml
type: weather-forecast
entity: weather.YOUR_WEATHER
forecast_type: daily
card_mod:
  style: |
    ha-card {
      background: #161a28 !important;
      border: 1px solid rgba(201,168,76,0.15) !important;
      border-radius: 4px !important;
    }
    .city { color: #c9a84c !important; font-family: 'Cormorant Garamond', serif !important; font-size: 14px !important; letter-spacing: 3px !important; text-transform: uppercase !important; }
    .temp { color: #c9a84c !important; font-family: 'Cormorant Garamond', serif !important; font-size: 56px !important; font-weight: 300 !important; }
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
  name: Attention Required
  icon: mdi:shield-alert-outline
  styles:
    card:
      - background: "rgba(180,60,40,0.1)"
      - border: 1px solid rgba(180,60,40,0.4)
      - border-radius: 4px
      - padding: 16px 24px
    icon:
      - color: "#c04030"
      - width: 20px
    name:
      - color: "#f0e8d0"
      - font-family: "'Cormorant Garamond', serif"
      - font-size: 14px
      - letter-spacing: 2px
      - text-transform: uppercase
```

### Header / Navigation

```yaml
type: custom:button-card
name: Grand Salon
styles:
  card:
    - background: transparent
    - border: none
    - border-bottom: 1px solid rgba(201,168,76,0.2)
    - border-radius: 0
    - box-shadow: none
    - padding: 0 0 16px 0
    - width: fit-content
  name:
    - color: "#c9a84c"
    - font-family: "'Cormorant Garamond', serif"
    - font-size: 28px
    - font-weight: 400
    - letter-spacing: 4px
    - text-transform: uppercase
  icon:
    - display: none
```

---

*Part of [aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
