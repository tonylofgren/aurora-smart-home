# Temperature + Humidity Room Monitor Template

The simplest useful ESPHome project: BME280 on I2C, three sensors (temp/humidity/pressure) reported every 30 seconds.

## When to use

- New ESPHome user looking for a first project
- Per-room climate data for HA dashboards
- Trigger for HVAC automations (humidifier, dehumidifier, fan)

## Recommended board

- **ESP32-C3 Super Mini**: cheapest, modern radio, tiny

## External hardware

- **BME280 I2C breakout** (~40 SEK; chip ID 0x60, not BMP280 chip ID 0x58!)

## Customization

- BME280 self-heats ~1C; adjust the `offset` filter
- Add an SSD1306 OLED on the same I2C bus for local display
- Swap BME280 for SCD40 (template `air-quality-monitor`) if you also need CO2
