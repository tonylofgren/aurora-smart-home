# Home Assistant Integration Development Cheat Sheet

Quick reference for custom integration development patterns.

## File Structure

```
custom_components/my_integration/
├── __init__.py           # Setup, async_setup_entry
├── manifest.json         # Metadata, dependencies
├── config_flow.py        # UI configuration
├── const.py              # Constants
├── coordinator.py        # DataUpdateCoordinator
├── entity.py             # Base entity class
├── sensor.py             # Sensor platform
├── switch.py             # Switch platform
├── strings.json          # UI strings
└── translations/
    └── en.json           # English translations
```

## manifest.json

```json
{
  "domain": "my_integration",
  "name": "My Integration",
  "version": "1.0.0",
  "codeowners": ["@username"],
  "config_flow": true,
  "documentation": "https://github.com/...",
  "iot_class": "local_polling",
  "requirements": ["my-library==1.0.0"],
  "dependencies": [],
  "integration_type": "hub"
}
```

## __init__.py

```python
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import MyCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from config entry."""
    coordinator = MyCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
```

## config_flow.py

```python
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD
import voluptuous as vol

from .const import DOMAIN

class MyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle user step."""
        errors = {}

        if user_input is not None:
            # Validate input
            try:
                await self._test_connection(user_input[CONF_HOST])
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_HOST],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PASSWORD): str,
            }),
            errors=errors,
        )
```

## DataUpdateCoordinator

```python
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

class MyCoordinator(DataUpdateCoordinator):
    """Coordinator for fetching data."""

    def __init__(self, hass, entry):
        """Initialize."""
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.entry = entry
        self.api = MyAPI(entry.data[CONF_HOST])

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            return await self.api.async_get_data()
        except APIError as err:
            raise UpdateFailed(f"Error: {err}") from err
```

## Entity Base Class

```python
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

class MyEntity(CoordinatorEntity):
    """Base entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, device_id):
        """Initialize."""
        super().__init__(coordinator)
        self._device_id = device_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=f"My Device {self._device_id}",
            manufacturer="My Company",
            model="Model X",
        )
```

## Sensor Platform

```python
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature

class MySensor(MyEntity, SensorEntity):
    """Sensor entity."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, device_id, key):
        """Initialize."""
        super().__init__(coordinator, device_id)
        self._key = key
        self._attr_unique_id = f"{device_id}_{key}"
        self._attr_translation_key = key

    @property
    def native_value(self):
        """Return sensor value."""
        return self.coordinator.data.get(self._key)
```

## Switch Platform

```python
from homeassistant.components.switch import SwitchEntity

class MySwitch(MyEntity, SwitchEntity):
    """Switch entity."""

    def __init__(self, coordinator, device_id):
        """Initialize."""
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_switch"
        self._attr_name = "Power"

    @property
    def is_on(self):
        """Return if switch is on."""
        return self.coordinator.data.get("power", False)

    async def async_turn_on(self, **kwargs):
        """Turn on."""
        await self.coordinator.api.async_set_power(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn off."""
        await self.coordinator.api.async_set_power(False)
        await self.coordinator.async_request_refresh()
```

## Common Device Classes

### Sensors
```python
SensorDeviceClass.TEMPERATURE      # °C, °F
SensorDeviceClass.HUMIDITY         # %
SensorDeviceClass.BATTERY          # %
SensorDeviceClass.POWER            # W, kW
SensorDeviceClass.ENERGY           # Wh, kWh
SensorDeviceClass.VOLTAGE          # V
SensorDeviceClass.CURRENT          # A
SensorDeviceClass.PRESSURE         # hPa, bar
SensorDeviceClass.ILLUMINANCE      # lx
SensorDeviceClass.CO2              # ppm
SensorDeviceClass.PM25             # µg/m³
```

### Binary Sensors
```python
BinarySensorDeviceClass.MOTION
BinarySensorDeviceClass.DOOR
BinarySensorDeviceClass.WINDOW
BinarySensorDeviceClass.MOISTURE
BinarySensorDeviceClass.SMOKE
BinarySensorDeviceClass.OCCUPANCY
BinarySensorDeviceClass.BATTERY
BinarySensorDeviceClass.CONNECTIVITY
```

## State Classes

```python
SensorStateClass.MEASUREMENT       # Temp, humidity (can go up/down)
SensorStateClass.TOTAL             # Total count (resets possible)
SensorStateClass.TOTAL_INCREASING  # Energy (only increases)
```

## Services

```python
# In __init__.py
async def async_setup_entry(hass, entry):
    ...
    hass.services.async_register(
        DOMAIN,
        "my_service",
        async_handle_service,
        schema=vol.Schema({
            vol.Required("target"): str,
        }),
    )

async def async_handle_service(call):
    """Handle service call."""
    target = call.data["target"]
    # Do something
```

## Events

```python
# Fire event
hass.bus.async_fire(
    f"{DOMAIN}_event",
    {"device_id": device_id, "action": "button_press"},
)

# Listen to event
async def async_setup_entry(hass, entry):
    hass.bus.async_listen(
        f"{DOMAIN}_event",
        async_handle_event,
    )
```

## Options Flow

```python
class MyOptionsFlow(config_entries.OptionsFlow):
    """Options flow."""

    def __init__(self, config_entry):
        """Initialize."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "scan_interval",
                    default=self.config_entry.options.get("scan_interval", 30),
                ): int,
            }),
        )

# In config_flow.py
class MyConfigFlow(config_entries.ConfigFlow):
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MyOptionsFlow(config_entry)
```

## translations/en.json

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Connect to Device",
        "data": {
          "host": "Host",
          "password": "Password"
        }
      }
    },
    "error": {
      "cannot_connect": "Failed to connect",
      "unknown": "Unknown error"
    }
  },
  "entity": {
    "sensor": {
      "temperature": {
        "name": "Temperature"
      }
    }
  }
}
```

## Testing

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_api():
    with patch("custom_components.my_integration.MyAPI") as mock:
        mock.return_value.async_get_data.return_value = {"temp": 22.5}
        yield mock

async def test_sensor_value(hass, mock_api):
    """Test sensor returns correct value."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_HOST: "test"})
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.my_device_temperature")
    assert state.state == "22.5"
```

## Quick Reference

| Task | Pattern |
|------|---------|
| Get coordinator | `hass.data[DOMAIN][entry.entry_id]` |
| Force refresh | `await coordinator.async_request_refresh()` |
| Check connected | `coordinator.last_update_success` |
| Unique ID | `f"{device_id}_{sensor_type}"` |
| Entry options | `entry.options.get("key", default)` |
| Fire event | `hass.bus.async_fire(event_type, data)` |
| Log | `_LOGGER.debug("msg %s", var)` |

## Common Imports

```python
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_PORT,
)
```
