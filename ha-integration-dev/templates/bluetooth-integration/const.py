"""Constants for the Bluetooth Device integration.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

DOMAIN = "my_bluetooth_device"

# Bluetooth identifiers
# Replace with your device's manufacturer data or service UUIDs
MANUFACTURER_ID = 0x1234  # Example manufacturer ID
SERVICE_UUID = "0000180f-0000-1000-8000-00805f9b34fb"  # Battery Service UUID

# Device identification
DEVICE_NAME_PREFIX = "MyDevice"

# Update intervals
DEFAULT_SCAN_INTERVAL = 60  # seconds

# Characteristic UUIDs (examples)
CHAR_BATTERY_LEVEL = "00002a19-0000-1000-8000-00805f9b34fb"
CHAR_TEMPERATURE = "00002a6e-0000-1000-8000-00805f9b34fb"
