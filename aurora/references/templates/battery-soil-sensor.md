# Battery-Powered Soil Moisture Sensor

Sleep-most-of-the-time soil moisture monitor for indoor plants or garden beds. Designed for 12-18 month battery life on 2 AA cells via a boost converter, or 6+ months on a single 18650.

## When to use

- Monitor moisture for plants in pots
- Trigger HA notifications "Water the basil"
- Outdoor garden bed monitoring (with weatherproof enclosure)

## Recommended board

- **ESP32-C3 Super Mini**: deep sleep ~5uA, single ADC channel sufficient
- Alternative: ESP32-S3 if you want PSRAM logging (overkill for this use case)

## External hardware

- **Capacitive Soil Moisture v1.2** (~30 SEK; verify v1.2, NOT v1.0/1.1 which corrode)
- **Battery pack**: 2x AA + boost converter, or 18650 + TP4056 charger
- **Enclosure**: IP65 box if outdoors

## CRITICAL: calibration required

The `calibrate_linear` block has placeholder values. Replace them:

1. Hold sensor in dry air, note the raw ADC voltage in HA logs
2. Submerge sensor in water (up to but not above the line), note the voltage
3. Replace the two values in the YAML

Without calibration, the percentage is meaningless.

## Customization

- Adjust `sleep_duration` to balance freshness vs battery life
- Add a DS18B20 for soil temperature (OneWire on a separate GPIO)
- Set up an HA template sensor that estimates battery percentage from voltage

## Expected battery life

- 2x AA (3000mAh): ~12 months at 30-min interval
- 18650 (3000mAh, 3.7V): ~12 months at 30-min interval
