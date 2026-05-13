# Bluetooth Proxy Template

Forwards Bluetooth Low Energy advertisements and active connections to Home Assistant. One of the highest-impact ESPHome projects: extends BLE coverage across your home without buying expensive proprietary hubs.

## When to use

- You have BLE devices (Xiaomi temp sensors, BTHome devices, smart locks, etc.) that are out of range of your HA host
- You want HA to connect to BLE devices (locks, switchbots) instead of just listening
- You need cheap "BLE coverage extenders" room by room

## Recommended boards

- **ESP32-C3 Super Mini** -- cheapest, BLE 5.0, ~30 SEK, tiny form factor
- **ESP32-S3 DevKit C-1** -- more headroom for future expansion (voice, screen)
- **ESP32 DevKit V1** -- works but legacy; pick C3 instead for new projects

Do NOT use: ESP32-S2 (no BLE), ESP8266 D1 Mini (no BLE), ESP32-P4 (no radio).

## Customization

- Set `active: false` if you only want passive scanning (lower power, no remote BLE connections from HA)
- Adjust `scan_parameters` for performance vs power tradeoffs
- Multiple proxies in different rooms create a "BLE mesh" coverage

## After deploy

1. Add the device to Home Assistant via auto-discovery
2. Check `Settings > Devices > Bluetooth` for paired peripherals
3. Move BLE devices around the home and watch coverage on the HA logbook
