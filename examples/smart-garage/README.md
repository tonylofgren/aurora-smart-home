# Smart Garage Example

Complete garage automation system with door control, car presence detection, and safety features.

## Features

- **Garage Door Control**: Open/close with position feedback
- **Car Presence Detection**: Know if car is home
- **Safety Features**: Obstruction detection, auto-close timer
- **Environmental Monitoring**: Temperature, humidity
- **Security**: Door state alerts, motion detection

## Hardware List

### ESP32 Controller
- ESP32 DevKit or ESP32-C3 Mini

### Sensors & Actuators
| Component | Purpose | Interface |
|-----------|---------|-----------|
| Reed switches (2x) | Door open/closed detection | GPIO |
| HC-SR04 Ultrasonic | Car presence detection | GPIO |
| DHT22 | Temperature & humidity | GPIO |
| PIR sensor | Motion detection | GPIO |
| Relay module | Door opener control | GPIO |
| IR break beam | Obstruction detection | GPIO |

### Optional Add-ons
- ESP32-CAM for visual monitoring
- LED strip for lighting
- Smoke/CO detector

## Wiring Diagram

```
ESP32 DevKit
├── GPIO4 ──── Reed Switch (Door Closed)
├── GPIO5 ──── Reed Switch (Door Open)
├── GPIO16 ─── Ultrasonic Trigger
├── GPIO17 ─── Ultrasonic Echo
├── GPIO18 ─── DHT22 Data
├── GPIO19 ─── PIR Sensor
├── GPIO21 ─── Relay (Door Opener)
├── GPIO22 ─── IR Break Beam
└── GND ────── Common ground
```

## File Structure

```
smart-garage/
├── README.md
├── garage-controller.yaml    # ESPHome configuration
├── automations.yaml          # Home Assistant automations
├── dashboard.yaml            # Lovelace dashboard
└── secrets.yaml.example      # Template for secrets
```

## Installation

1. **Flash ESPHome device**:
   ```bash
   esphome run garage-controller.yaml
   ```

2. **Wire the door opener**:
   - Connect relay NO (normally open) contacts in parallel with your existing wall button
   - This simulates pressing the wall button

3. **Mount sensors**:
   - Reed switches at door frame (closed + open positions)
   - Ultrasonic sensor pointing at car parking spot
   - PIR in corner for motion coverage

4. **Add automations to HA**:
   Copy `automations.yaml` content to Home Assistant.

## Configuration

### Car Detection Distance
Adjust `car_present_distance` substitution:
- Measure distance to floor when no car: e.g., 250 cm
- Measure distance to car roof: e.g., 120 cm
- Set threshold between: e.g., 180 cm

### Auto-Close Timer
Default: 10 minutes after door opens
Adjust in automations.yaml

## Home Assistant Integration

### Entities Created

**Cover**
- `cover.garage_door` - Main door control with open/close/stop

**Sensors**
- `sensor.garage_temperature`
- `sensor.garage_humidity`
- `sensor.garage_car_distance`

**Binary Sensors**
- `binary_sensor.garage_door_closed`
- `binary_sensor.garage_door_open`
- `binary_sensor.garage_car_present`
- `binary_sensor.garage_motion`
- `binary_sensor.garage_obstruction`

**Buttons**
- `button.garage_door_toggle`

## Safety Features

1. **Obstruction Detection**: IR break beam stops door if triggered
2. **Auto-Stop**: Door stops if neither limit switch triggered after 30s
3. **Remote Disable**: Can disable remote control for security
4. **Position Memory**: Remembers last known state

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Door doesn't move | Check relay wiring, verify wall button works |
| Wrong open/closed state | Swap reed switch positions or invert in config |
| Car detection unreliable | Adjust distance threshold, check sensor angle |
| False motion alerts | Adjust PIR sensitivity pot, add delay filter |

## Integration with Car

If your car supports geofencing (Tesla, BMW, etc.), you can:
1. Auto-open garage when approaching
2. Auto-close after car leaves

Example automation included in `automations.yaml`.

## Credits

Created for [Aurora Smart Home](https://github.com/tonylofgren/aurora-smart-home)
