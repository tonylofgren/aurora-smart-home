# Smart Greenhouse Example

Complete automation system for a greenhouse or indoor garden with temperature control, automatic watering, and light management.

## Features

- **Climate Monitoring**: Temperature, humidity, soil moisture, light levels
- **Automatic Watering**: Scheduled or sensor-triggered irrigation
- **Ventilation Control**: Fan/window based on temperature
- **Grow Lights**: Schedule-based or light sensor controlled
- **Alerts**: High temp, low moisture, frost warnings

## Hardware List

### ESP32 Controller
- ESP32 DevKit or ESP32-S3

### Sensors
| Sensor | Purpose | Interface |
|--------|---------|-----------|
| DHT22 / SHT31 | Air temp & humidity | GPIO / I2C |
| Capacitive soil moisture | Soil moisture | ADC |
| BH1750 | Light level (lux) | I2C |
| DS18B20 | Soil/water temp | 1-Wire |

### Actuators
| Device | Purpose | Interface |
|--------|---------|-----------|
| Relay module (4ch) | Pumps, fans, lights | GPIO |
| Solenoid valve | Water control | Relay |
| Water pump | Irrigation | Relay |
| 12V fan | Ventilation | Relay/PWM |
| Grow light | Supplemental light | Relay |

## Wiring Diagram

```
ESP32 DevKit
├── GPIO4 ──── DHT22 Data (+ 4.7k pullup)
├── GPIO5 ──── DS18B20 (+ 4.7k pullup)
├── GPIO34 ─── Soil Moisture (ADC)
├── GPIO21 ─── SDA (BH1750)
├── GPIO22 ─── SCL (BH1750)
├── GPIO16 ─── Relay 1 (Water Pump)
├── GPIO17 ─── Relay 2 (Solenoid Valve)
├── GPIO18 ─── Relay 3 (Fan)
├── GPIO19 ─── Relay 4 (Grow Light)
└── GND ────── Common ground
```

## File Structure

```
smart-greenhouse/
├── README.md
├── greenhouse-controller.yaml    # ESPHome configuration
├── automations.yaml              # Home Assistant automations
├── dashboard.yaml                # Lovelace dashboard
└── secrets.yaml.example          # Template for secrets
```

## Installation

1. **Flash ESPHome device**:
   ```bash
   esphome run greenhouse-controller.yaml
   ```

2. **Add automations to HA**:
   Copy `automations.yaml` content to your Home Assistant automations.

3. **Import dashboard**:
   Import `dashboard.yaml` as a new Lovelace dashboard.

## Configuration

### Thresholds (adjust in ESPHome)
- Soil moisture low: < 30%
- Temperature high: > 30°C
- Temperature low (frost): < 5°C
- Light minimum: < 500 lux

### Watering Schedule
Default: 6:00 AM and 6:00 PM for 5 minutes each.
Adjust in Home Assistant automation.

## Home Assistant Integration

The ESPHome device creates these entities:

### Sensors
- `sensor.greenhouse_temperature`
- `sensor.greenhouse_humidity`
- `sensor.greenhouse_soil_moisture`
- `sensor.greenhouse_light`
- `sensor.greenhouse_soil_temperature`

### Switches
- `switch.greenhouse_water_pump`
- `switch.greenhouse_solenoid`
- `switch.greenhouse_fan`
- `switch.greenhouse_grow_light`

### Binary Sensors
- `binary_sensor.greenhouse_needs_water`
- `binary_sensor.greenhouse_too_hot`
- `binary_sensor.greenhouse_frost_warning`

## Customization

### Different Soil Sensor
Replace capacitive sensor with:
- Resistive soil moisture (less accurate)
- Xiaomi Flower Care (Bluetooth)

### Multiple Zones
Duplicate relay/sensor config for multiple grow beds.

### Water Level Monitoring
Add ultrasonic sensor (JSN-SR04T) to water tank.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Soil sensor always reads 100% | Check wiring, sensor may be submerged |
| Erratic readings | Add capacitor (100µF) to power supply |
| Relay clicking | Add flyback diode for inductive loads |
| WiFi disconnects | Move ESP away from water/metal |

## Credits

Created for [Aurora Smart Home](https://github.com/tonylofgren/aurora-smart-home)
