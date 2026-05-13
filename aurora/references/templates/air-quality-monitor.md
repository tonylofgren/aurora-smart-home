# Air Quality Monitor Template

CO2 + temperature + humidity sensor for a single room, using the Sensirion SCD40 (NDIR true CO2 sensor, not eCO2).

## When to use

- Bedroom CO2 monitoring for sleep quality
- Home office air quality tracking
- Trigger ventilation automations based on CO2

## Recommended board

- **ESP32-C3 Super Mini**: cheap, BLE 5.0, small form factor
- Alternative: any ESP32 you already have

## External hardware

- **SCD40 breakout** (~150 SEK; 0x62 I2C address fixed)
- Pull-up resistors usually included on breakout boards

## Customization

- Replace SCD40 with SCD41 (variant with single-shot mode for battery operation)
- Add an SSD1306 OLED for local display
- Tighten `update_interval` to 10s if you want faster trending data

## Calibration

SCD40 auto-calibrates by assuming the lowest CO2 reading over 7 days is outdoor air (400ppm). For accuracy, ventilate the room daily for at least 1 hour to give the sensor a reference. You can also force-calibrate via the `force_recalibration` action in ESPHome.
