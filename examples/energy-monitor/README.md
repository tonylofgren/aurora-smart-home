# Energy Monitor Example

Whole-house energy monitoring system using CT clamps for non-invasive current measurement.

## Features

- **Real-time Power Monitoring**: Instant watt readings
- **Energy Tracking**: Daily/monthly kWh consumption
- **Cost Calculation**: Electricity cost estimation
- **Circuit Monitoring**: Individual circuit tracking
- **Peak Detection**: High usage alerts

## Hardware List

### ESP32 Controller
- ESP32 DevKit (ADC required)
- ESP32-S3 (recommended, better ADC)

### Current Sensors
| Component | Specification | Use Case |
|-----------|---------------|----------|
| SCT-013-000 | 100A, 50mA output | Main feed (whole house) |
| SCT-013-030 | 30A, 1V output | Individual circuits |
| YHDC SCT-019 | 200A | Large installations |

### Supporting Components
| Component | Purpose |
|-----------|---------|
| Burden resistor | Convert current to voltage |
| Capacitor (10µF) | Filter noise |
| Voltage reference | Bias ADC input |
| Optocoupler (optional) | Galvanic isolation |

### Optional
- AC-AC adapter for voltage reference (more accurate)
- OLED display for local readout
- SD card for data logging

## Wiring Diagram

```
CT Clamp → Burden Resistor → Voltage Divider → ESP32 ADC

Detailed:
                    3.3V
                     │
                    [R1]  10kΩ
                     │
CT ──┬──[Burden]──┬──┼──── GPIO34 (ADC)
     │            │  │
    [C1]         [C2]│
    100nF        10µF│
     │            │  │
    GND ─────────────┴──── GND

Burden resistor values:
- SCT-013-000 (50mA): 33Ω for 1.65V peak
- SCT-013-030 (1V): No burden needed
```

## File Structure

```
energy-monitor/
├── README.md
├── energy-monitor.yaml           # ESPHome configuration
├── automations.yaml              # Home Assistant automations
├── dashboard.yaml                # Lovelace dashboard
└── secrets.yaml.example          # Template for secrets
```

## Installation

1. **Wire CT clamps**:
   - Clamp around LIVE wire only (not neutral)
   - Arrow on CT points toward load
   - Never open CT secondary when current flowing

2. **Flash ESPHome device**:
   ```bash
   esphome run energy-monitor.yaml
   ```

3. **Calibrate**:
   - Compare readings with known load (kettle, heater)
   - Adjust calibration values in config

4. **Add automations to HA**:
   Copy content from `automations.yaml`

## Calibration

### Step 1: Zero Calibration
With no load connected, note the ADC reading. This is your offset.

### Step 2: Reference Load
1. Use a known resistive load (e.g., 2000W kettle)
2. Note the ADC reading
3. Calculate: `calibration = known_watts / (reading - offset)`

### Step 3: Verify
Test with another known load to confirm accuracy.

## Configuration

### Electricity Cost
Update in `energy-monitor.yaml`:
```yaml
electricity_price: "0.15"  # Cost per kWh in your currency
```

### Multi-Circuit Setup
Add additional sensors for each circuit:
```yaml
sensor:
  - platform: ct_clamp
    sensor: ct_adc_kitchen
    name: "Kitchen Power"
```

## Home Assistant Integration

### Entities Created

**Sensors**
- `sensor.energy_power` - Current power (W)
- `sensor.energy_daily` - Today's usage (kWh)
- `sensor.energy_monthly` - This month's usage (kWh)
- `sensor.energy_cost_daily` - Today's cost
- `sensor.energy_voltage` - Mains voltage (if AC adapter used)

**Utility Meters (auto-created)**
- `sensor.energy_daily_peak` - Peak hour usage
- `sensor.energy_daily_offpeak` - Off-peak usage

## Energy Dashboard

Home Assistant's built-in Energy Dashboard works great:

1. Go to Settings → Dashboards → Energy
2. Add `sensor.energy_power` as Grid consumption
3. Set your electricity price

## Accuracy Considerations

| Factor | Impact | Solution |
|--------|--------|----------|
| No voltage reference | ±10% error | Use AC-AC adapter |
| Phase shift | Under-reading | Calibrate per circuit |
| Non-linear loads | Distortion | Use RMS calculation |
| Temperature drift | ADC variation | Periodic recalibration |

## Safety Warnings

⚠️ **Important Safety Notes**:

1. **Never work on live mains** - Turn off power first
2. **CT clamps are safe** - They don't touch mains wires
3. **Never open CT secondary** - Can generate dangerous voltage
4. **Keep ESP away from mains** - Use appropriate enclosure
5. **Consult electrician** - If unsure about installation

## Advanced: Three-Phase

For three-phase installations:
- Use 3 CT clamps (one per phase)
- Sum power readings
- Consider power factor correction

## Credits

Created for [Aurora Smart Home](https://github.com/tonylofgren/aurora-smart-home)

Based on OpenEnergyMonitor project methodology.
