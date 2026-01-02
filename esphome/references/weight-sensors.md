# Weight Sensors Reference

Complete guide for weight measurement using load cells and ADC modules in ESPHome.

## Overview

Weight sensing uses **load cells** (strain gauge sensors) connected to **ADC modules** that convert the small voltage changes into digital readings.

## Hardware Options

### ADC Modules

| Module | Resolution | Channels | Speed | Best For |
|--------|------------|----------|-------|----------|
| **HX711** | 24-bit | 1 | 10-80 SPS | Most projects, kitchen scales |
| **NAU7802** | 24-bit | 1 | 10-320 SPS | High accuracy, I2C interface |
| **ADS1220** | 24-bit | 4 | Up to 2000 SPS | Multi-channel, professional |
| **ADS1115** | 16-bit | 4 | Up to 860 SPS | General purpose, lower accuracy |

### Load Cells

| Type | Capacity Range | Accuracy | Use Case |
|------|---------------|----------|----------|
| **Bar/Beam** | 1kg - 500kg | ±0.05% | Kitchen scales, platform scales |
| **Button** | 5kg - 200kg | ±0.1% | Compact designs, bed sensors |
| **S-Type** | 10kg - 5000kg | ±0.02% | Industrial, hanging scales |
| **Shear Beam** | 100kg - 10000kg | ±0.02% | Floor scales, vehicle weighing |

### Common Configurations

| Application | Load Cell | ADC | Notes |
|-------------|-----------|-----|-------|
| Kitchen scale | 4x 50kg bar cells | HX711 | Full bridge configuration |
| Bee hive | 4x 50kg bar cells | HX711 | Outdoor, weatherproof |
| Pet feeder | 1x 5kg button | HX711 | Monitor food level |
| Body scale | 4x 50kg bar cells | NAU7802 | Higher accuracy |
| Package scale | 1x 10kg S-type | HX711 | Hanging or platform |

## HX711 Wiring

```
Load Cell Wires (typical colors):
  Red    → E+ (Excitation+)
  Black  → E- (Excitation-)
  White  → A- (Signal-)
  Green  → A+ (Signal+)
  Shield → GND (if present)

HX711 to ESP32:
  VCC  → 3.3V or 5V
  GND  → GND
  DT   → GPIO (DOUT)
  SCK  → GPIO (CLK)
```

### Four Load Cells (Full Bridge)

```
For platform scales with 4 load cells:

        ┌────────┐
   Red──┤ Cell 1 ├──White─┐
        └────────┘        │
        ┌────────┐        │
   Red──┤ Cell 2 ├──White─┼──→ HX711 A+
        └────────┘        │
        ┌────────┐        │
   Red──┤ Cell 3 ├──Green─┤
        └────────┘        │
        ┌────────┐        │
   Red──┤ Cell 4 ├──Green─┴──→ HX711 A-
        └────────┘

All Black wires → HX711 E-
All other wires (usually unmarked) → HX711 E+
```

## ESPHome Configuration

### Basic HX711

```yaml
sensor:
  - platform: hx711
    name: "Weight"
    dout_pin: GPIO4
    clk_pin: GPIO5
    gain: 128
    update_interval: 1s
    filters:
      - sliding_window_moving_average:
          window_size: 5
          send_every: 1
      - calibrate_linear:
          - 0 -> 0          # Zero point (tare)
          - 847000 -> 1000  # Calibration: raw_value -> grams
    unit_of_measurement: "g"
    accuracy_decimals: 1
```

### With Tare Function

```yaml
globals:
  - id: tare_offset
    type: float
    restore_value: yes
    initial_value: '0.0'

  - id: calibration_factor
    type: float
    restore_value: yes
    initial_value: '2280'  # Adjust after calibration

sensor:
  - platform: hx711
    name: "Weight Raw"
    id: weight_raw
    dout_pin: GPIO4
    clk_pin: GPIO5
    gain: 128
    update_interval: 500ms
    internal: true
    filters:
      - sliding_window_moving_average:
          window_size: 5
          send_every: 1

  - platform: template
    name: "Weight"
    id: weight
    unit_of_measurement: "g"
    accuracy_decimals: 1
    device_class: weight
    lambda: |-
      float raw = id(weight_raw).state;
      float weight = (raw - id(tare_offset)) / id(calibration_factor);
      return max(0.0f, weight);
    update_interval: 500ms

button:
  - platform: template
    name: "Tare Scale"
    on_press:
      - lambda: |-
          id(tare_offset) = id(weight_raw).state;
          ESP_LOGI("scale", "Tare set to: %.2f", id(tare_offset));
```

### NAU7802 (I2C)

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

sensor:
  - platform: nau7802
    name: "Weight"
    update_interval: 1s
    gain: 128
    sps: 80  # Samples per second: 10, 20, 40, 80, 320
    filters:
      - sliding_window_moving_average:
          window_size: 5
          send_every: 1
```

## Calibration Procedure

### Step 1: Find Zero Point (Tare)
```
1. Power on scale with nothing on it
2. Note the raw reading from logs/sensor
3. This is your zero offset
```

### Step 2: Calculate Calibration Factor
```
1. Place known weight on scale (e.g., 1000g)
2. Note the raw reading
3. Calculate: factor = (raw_reading - zero_offset) / known_weight
4. Example: (847000 - 10000) / 1000 = 837
```

### Step 3: Verify
```
1. Update calibration_factor in config
2. Test with different known weights
3. Adjust if readings are off
```

### Calibration Tips
- Use certified calibration weights if available
- Temperature affects readings - calibrate at operating temp
- Wait for readings to stabilize before recording
- Calibrate with weight in center of platform

## Multiple Unit Support

```yaml
sensor:
  # Primary in grams
  - platform: template
    name: "Weight (g)"
    id: weight_grams
    unit_of_measurement: "g"
    lambda: return id(weight_raw_calibrated).state;

  # Kilograms
  - platform: template
    name: "Weight (kg)"
    unit_of_measurement: "kg"
    accuracy_decimals: 3
    lambda: return id(weight_grams).state / 1000.0;

  # Pounds
  - platform: template
    name: "Weight (lb)"
    unit_of_measurement: "lb"
    accuracy_decimals: 2
    lambda: return id(weight_grams).state / 453.592;

  # Ounces
  - platform: template
    name: "Weight (oz)"
    unit_of_measurement: "oz"
    accuracy_decimals: 1
    lambda: return id(weight_grams).state / 28.3495;
```

## Advanced Features

### Stability Detection

```yaml
globals:
  - id: stable_readings
    type: int
    initial_value: '0'

sensor:
  - platform: template
    name: "Weight Stable"
    id: stable_weight
    lambda: |-
      static float last_reading = 0;
      float current = id(weight).state;

      // Check if reading changed less than 1g
      if (abs(current - last_reading) < 1.0) {
        id(stable_readings)++;
      } else {
        id(stable_readings) = 0;
      }
      last_reading = current;

      // Return weight only when stable for 5 readings
      if (id(stable_readings) >= 5) {
        return current;
      }
      return {};
    update_interval: 200ms

binary_sensor:
  - platform: template
    name: "Weight Stable"
    lambda: return id(stable_readings) >= 5;
```

### Auto-Zero (Drift Compensation)

```yaml
interval:
  - interval: 1h
    then:
      - if:
          condition:
            # Only auto-zero when weight is very low (nothing on scale)
            lambda: return id(weight).state < 5.0;
          then:
            - lambda: |-
                id(tare_offset) = id(weight_raw).state;
                ESP_LOGI("scale", "Auto-zero applied");
```

### Overload Protection

```yaml
binary_sensor:
  - platform: template
    name: "Scale Overload"
    device_class: problem
    lambda: |-
      // HX711 saturates at ~0x7FFFFF (8388607)
      float raw = id(weight_raw).state;
      return raw > 8000000 || raw < -8000000;
```

## Temperature Compensation

Load cells are temperature sensitive. For high accuracy:

```yaml
sensor:
  - platform: dallas_temp
    id: scale_temp
    address: 0x1234567890ABCDEF

  - platform: template
    name: "Weight Compensated"
    lambda: |-
      float weight = id(weight).state;
      float temp = id(scale_temp).state;

      // Typical load cell drift: ~0.02% per °C
      float reference_temp = 20.0;
      float temp_coefficient = 0.0002;
      float compensation = 1.0 + (temp - reference_temp) * temp_coefficient;

      return weight / compensation;
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| No reading | Wiring error | Check connections, swap DT/SCK |
| Reading stuck at max | Overload or broken cell | Check load, replace cell |
| Drifting readings | Temperature change | Add temp compensation |
| Noisy readings | Electrical interference | Add capacitor, shielded cable |
| Non-linear response | Wrong calibration | Calibrate at multiple points |
| Slow response | Long filter window | Reduce window_size |

## Example Applications

### Kitchen Scale
- 4x 50kg bar cells in full bridge
- HX711 with 128 gain
- 0.1g accuracy
- Tare button
- Unit switching (g/kg/oz/lb)

### Bee Hive Monitor
- 4x 100kg shear beam cells
- NAU7802 for accuracy
- Weatherproof enclosure
- Daily weight change tracking
- Battery powered with deep sleep

### Pet Feeder Level
- 1x 5kg button cell under bowl
- HX711
- Food level percentage
- Low food alert

### Package Scale
- 1x S-type load cell
- Hanging or platform mount
- Shipping label printer integration

## Further Reading

- [HX711 Datasheet](https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf)
- [NAU7802 ESPHome Docs](https://esphome.io/components/sensor/nau7802.html)
- [Load Cell Application Note](https://www.hbm.com/en/0014/load-cells/)

## Related Templates

- [weight-scale.yaml](../assets/templates/weight-scale.yaml) - Complete kitchen scale template
