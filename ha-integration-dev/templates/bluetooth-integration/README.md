# Bluetooth Integration Template

This template demonstrates how to create a Home Assistant integration for Bluetooth Low Energy (BLE) devices.

## Features

- **Bluetooth Discovery**: Auto-detect devices via advertisements
- **Passive Scanning**: Listen for broadcast data without connecting
- **Active Connections**: Read GATT characteristics when needed
- **Coordinator Pattern**: Centralized data updates

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Integration setup, Bluetooth device initialization |
| `config_flow.py` | Discovery and manual configuration |
| `coordinator.py` | Data fetching (passive + active) |
| `sensor.py` | Sensor entities with EntityDescription |
| `manifest.json` | Integration metadata with Bluetooth dependencies |
| `strings.json` | UI strings for config flow |

## Customization Steps

### 1. Update Device Identification

In `const.py`, update:
```python
MANUFACTURER_ID = 0x1234  # Your device's manufacturer ID
SERVICE_UUID = "..."       # Your device's service UUID
DEVICE_NAME_PREFIX = "..."  # Device name prefix
```

### 2. Update Discovery Matching

In `manifest.json`:
```json
{
  "bluetooth": [
    {"local_name": "YourDevice*"},
    {"manufacturer_id": 1234},
    {"service_uuid": "0000180f-0000-1000-8000-00805f9b34fb"}
  ]
}
```

### 3. Parse Advertisement Data

In `coordinator.py`, customize `_parse_advertisement()`:
```python
def _parse_advertisement(self, service_info):
    # Parse your device's manufacturer data format
    payload = service_info.manufacturer_data.get(MANUFACTURER_ID)
    return {
        "battery": payload[0],
        "temperature": int.from_bytes(payload[1:3], "little") / 10,
    }
```

### 4. Add Entity Descriptions

In `sensor.py`, update `SENSOR_DESCRIPTIONS` with your device's sensors.

## Bluetooth Patterns

### Passive Only (Advertisements)

Best for devices that broadcast all data:
- Xiaomi sensors
- iBeacons
- Most environmental sensors

```python
# In coordinator.py - just use advertisement callback
# No need for _async_read_device_data()
```

### Active Connection Required

For devices that need GATT reads:
- Heart rate monitors
- Smart locks
- Devices with security

```python
# In coordinator.py - implement _async_read_device_data()
async with BleakClient(ble_device) as client:
    data = await client.read_gatt_char(CHAR_UUID)
```

## Testing

```bash
# List Bluetooth devices
hcitool lescan

# Check device advertisement
bluetoothctl
> scan on
```

## Resources

- [Home Assistant Bluetooth Documentation](https://developers.home-assistant.io/docs/core/bluetooth)
- [Bleak Documentation](https://bleak.readthedocs.io/)
- [GATT Characteristics](https://www.bluetooth.com/specifications/gatt/characteristics/)

---

*Generated with [ha-integration@aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
