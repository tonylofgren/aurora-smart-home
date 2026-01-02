# Multi-Coordinator Patterns

Guide för att använda flera DataUpdateCoordinators i en Home Assistant-integration.

## Översikt

En integration kan behöva flera coordinators när:
- Olika data behöver olika uppdateringsintervall
- Olika API-endpoints har olika rate limits
- Vissa data är mer kritisk och behöver snabbare uppdatering
- Data kommer från olika källor (API + WebSocket)

## Arkitektur

```
┌─────────────────────────────────────────────────────────┐
│                    Integration                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐    ┌──────────────────┐           │
│  │ StatusCoordinator│    │ HistoryCoordinator│          │
│  │  interval: 30s   │    │  interval: 5min   │          │
│  │  /api/status     │    │  /api/history     │          │
│  └────────┬─────────┘    └────────┬─────────┘           │
│           │                       │                      │
│           └───────────┬───────────┘                      │
│                       │                                  │
│              ┌────────┴────────┐                        │
│              │   ConfigEntry   │                        │
│              │   runtime_data  │                        │
│              └────────┬────────┘                        │
│                       │                                  │
│         ┌─────────────┼─────────────┐                   │
│         │             │             │                    │
│    ┌────┴────┐  ┌─────┴─────┐  ┌────┴────┐             │
│    │ Sensor  │  │  Binary   │  │ Switch  │             │
│    │ Entity  │  │  Sensor   │  │ Entity  │             │
│    └─────────┘  └───────────┘  └─────────┘             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Grundläggande Multi-Coordinator

### Dataclass för Runtime Data

```python
"""Data classes for multi-coordinator integration.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

from dataclasses import dataclass
from homeassistant.config_entries import ConfigEntry

from .coordinator import StatusCoordinator, HistoryCoordinator


@dataclass
class MyIntegrationData:
    """Runtime data for the integration."""

    status_coordinator: StatusCoordinator
    history_coordinator: HistoryCoordinator


type MyConfigEntry = ConfigEntry[MyIntegrationData]
```

### Coordinators

```python
"""Coordinators for multi-coordinator integration.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN
from .api import MyApiClient

_LOGGER = logging.getLogger(__name__)


class StatusCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator for real-time status data.

    Fast updates for current state.
    """

    def __init__(self, hass: HomeAssistant, client: MyApiClient) -> None:
        """Initialize status coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_status",
            update_interval=timedelta(seconds=30),
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        """Fetch status data."""
        try:
            return await self.client.async_get_status()
        except Exception as err:
            raise UpdateFailed(f"Error fetching status: {err}") from err


class HistoryCoordinator(DataUpdateCoordinator[list]):
    """Coordinator for historical data.

    Slower updates for non-critical data.
    """

    def __init__(self, hass: HomeAssistant, client: MyApiClient) -> None:
        """Initialize history coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_history",
            update_interval=timedelta(minutes=5),
        )
        self.client = client

    async def _async_update_data(self) -> list:
        """Fetch history data."""
        try:
            return await self.client.async_get_history()
        except Exception as err:
            raise UpdateFailed(f"Error fetching history: {err}") from err
```

### Setup Entry

```python
"""Integration setup with multi-coordinator.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import MyApiClient
from .const import DOMAIN, PLATFORMS
from .coordinator import StatusCoordinator, HistoryCoordinator
from .data import MyIntegrationData, MyConfigEntry


async def async_setup_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Set up integration from a config entry."""
    # Create API client
    client = MyApiClient(
        host=entry.data["host"],
        api_key=entry.data["api_key"],
    )

    # Create coordinators
    status_coordinator = StatusCoordinator(hass, client)
    history_coordinator = HistoryCoordinator(hass, client)

    # Fetch initial data for both
    await status_coordinator.async_config_entry_first_refresh()
    await history_coordinator.async_config_entry_first_refresh()

    # Store in runtime_data
    entry.runtime_data = MyIntegrationData(
        status_coordinator=status_coordinator,
        history_coordinator=history_coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Unload config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

### Entity med flera Coordinators

```python
"""Sensor entities using multiple coordinators.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .data import MyConfigEntry
from .coordinator import StatusCoordinator, HistoryCoordinator


async def async_setup_entry(hass, entry: MyConfigEntry, async_add_entities):
    """Set up sensor entities."""
    status_coord = entry.runtime_data.status_coordinator
    history_coord = entry.runtime_data.history_coordinator

    entities = [
        # Entities using status coordinator (fast updates)
        CurrentPowerSensor(status_coord, entry),
        CurrentStateSensor(status_coord, entry),

        # Entities using history coordinator (slow updates)
        TotalEnergySensor(history_coord, entry),
        DailyStatsSensor(history_coord, entry),
    ]

    async_add_entities(entities)


class CurrentPowerSensor(CoordinatorEntity[StatusCoordinator], SensorEntity):
    """Sensor for current power - uses status coordinator."""

    _attr_has_entity_name = True
    _attr_name = "Current Power"
    _attr_native_unit_of_measurement = "W"

    def __init__(
        self,
        coordinator: StatusCoordinator,
        entry: MyConfigEntry,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_current_power"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
        }

    @property
    def native_value(self):
        """Return current power."""
        return self.coordinator.data.get("power")


class TotalEnergySensor(CoordinatorEntity[HistoryCoordinator], SensorEntity):
    """Sensor for total energy - uses history coordinator."""

    _attr_has_entity_name = True
    _attr_name = "Total Energy"
    _attr_native_unit_of_measurement = "kWh"
    _attr_device_class = "energy"
    _attr_state_class = "total_increasing"

    def __init__(
        self,
        coordinator: HistoryCoordinator,
        entry: MyConfigEntry,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_total_energy"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
        }

    @property
    def native_value(self):
        """Return total energy from history."""
        if not self.coordinator.data:
            return None
        # Sum all energy from history
        return sum(item.get("energy", 0) for item in self.coordinator.data)
```

## Entity som använder BÅDA Coordinators

När en entity behöver data från flera coordinators:

```python
"""Entity that combines data from multiple coordinators.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import StatusCoordinator, HistoryCoordinator


class CombinedSensor(CoordinatorEntity[StatusCoordinator], SensorEntity):
    """Sensor that uses both coordinators."""

    _attr_has_entity_name = True
    _attr_name = "Efficiency"

    def __init__(
        self,
        status_coordinator: StatusCoordinator,
        history_coordinator: HistoryCoordinator,
        entry,
    ) -> None:
        """Initialize sensor."""
        # Primary coordinator for updates
        super().__init__(status_coordinator)

        # Store reference to secondary coordinator
        self._history_coordinator = history_coordinator
        self._attr_unique_id = f"{entry.entry_id}_efficiency"

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        # Also listen to history coordinator
        self.async_on_remove(
            self._history_coordinator.async_add_listener(
                self._handle_history_update
            )
        )

    @callback
    def _handle_history_update(self) -> None:
        """Handle history coordinator update."""
        self.async_write_ha_state()

    @property
    def native_value(self):
        """Calculate efficiency from both coordinators."""
        current_power = self.coordinator.data.get("power", 0)

        if not self._history_coordinator.data:
            return None

        avg_power = sum(
            item.get("power", 0) for item in self._history_coordinator.data
        ) / len(self._history_coordinator.data)

        if avg_power == 0:
            return None

        return round((current_power / avg_power) * 100, 1)

    @property
    def extra_state_attributes(self):
        """Return extra attributes from both sources."""
        return {
            "current_power": self.coordinator.data.get("power"),
            "history_points": len(self._history_coordinator.data or []),
            "last_status_update": self.coordinator.last_update_success_time.isoformat()
            if self.coordinator.last_update_success_time
            else None,
        }
```

## Koordinerad Refresh

Trigga uppdatering av alla coordinators:

```python
"""Service to refresh all coordinators.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

import asyncio
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN
from .data import MyConfigEntry


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services."""

    async def async_refresh_all(call: ServiceCall) -> None:
        """Refresh all coordinators."""
        entry_id = call.data.get("entry_id")

        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry_id and entry.entry_id != entry_id:
                continue

            data = entry.runtime_data

            # Refresh in parallel
            await asyncio.gather(
                data.status_coordinator.async_refresh(),
                data.history_coordinator.async_refresh(),
            )

    hass.services.async_register(
        DOMAIN,
        "refresh_all",
        async_refresh_all,
    )
```

## Conditional Coordinator

Coordinator som bara körs under vissa förhållanden:

```python
"""Conditional coordinator that pauses when not needed.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


class ConditionalCoordinator(DataUpdateCoordinator):
    """Coordinator that can be paused."""

    def __init__(self, hass, logger, name, client):
        """Initialize coordinator."""
        super().__init__(
            hass,
            logger,
            name=name,
            update_interval=timedelta(seconds=30),
        )
        self.client = client
        self._paused = False

    def pause(self) -> None:
        """Pause coordinator updates."""
        self._paused = True
        self.update_interval = None

    def resume(self, interval: timedelta | None = None) -> None:
        """Resume coordinator updates."""
        self._paused = False
        self.update_interval = interval or timedelta(seconds=30)
        # Trigger immediate refresh
        self.hass.async_create_task(self.async_refresh())

    async def _async_update_data(self):
        """Fetch data if not paused."""
        if self._paused:
            return self.data  # Return cached data

        return await self.client.async_get_data()
```

## Prioriterad Coordinator

Coordinator som anpassar intervall baserat på aktivitet:

```python
"""Adaptive coordinator with dynamic update interval.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


class AdaptiveCoordinator(DataUpdateCoordinator):
    """Coordinator with adaptive update interval."""

    def __init__(self, hass, logger, name, client):
        """Initialize coordinator."""
        super().__init__(
            hass,
            logger,
            name=name,
            update_interval=timedelta(minutes=1),  # Default slow
        )
        self.client = client
        self._activity_detected = False

    async def _async_update_data(self):
        """Fetch data and adjust interval based on activity."""
        data = await self.client.async_get_data()

        # Check for activity
        is_active = data.get("power", 0) > 100

        if is_active and not self._activity_detected:
            # Activity started - increase update frequency
            self._activity_detected = True
            self.update_interval = timedelta(seconds=10)

        elif not is_active and self._activity_detected:
            # Activity stopped - decrease update frequency
            self._activity_detected = False
            self.update_interval = timedelta(minutes=1)

        return data
```

## Best Practices

### Namngivning

```python
# Använd prefix för tydlighet
name=f"{DOMAIN}_status"      # my_integration_status
name=f"{DOMAIN}_history"     # my_integration_history
name=f"{DOMAIN}_realtime"    # my_integration_realtime
```

### Felhantering

```python
async def _async_update_data(self):
    """Handle errors gracefully."""
    try:
        return await self.client.async_get_data()
    except AuthenticationError:
        # Trigger reauth flow
        raise ConfigEntryAuthFailed("Authentication failed")
    except RateLimitError:
        # Temporary increase interval
        self.update_interval = timedelta(minutes=5)
        raise UpdateFailed("Rate limited, backing off")
    except Exception as err:
        raise UpdateFailed(f"Error: {err}") from err
```

### Resurshantering

```python
async def async_unload_entry(hass, entry):
    """Clean up resources."""
    # Coordinators cleanup handled automatically by HA
    # But close any shared resources
    if entry.runtime_data.client:
        await entry.runtime_data.client.async_close()

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

## Exempelprompts

```
"Skapa en integration med separata coordinators för status och historik"

"Jag vill ha snabb uppdatering för realtidsdata och långsam för statistik"

"Hur gör jag en entity som lyssnar på två coordinators?"

"Implementera en coordinator som pausar när ingen är hemma"

"Skapa en adaptiv coordinator som ökar frekvensen vid aktivitet"
```

## Se även

- `references/coordinator.md` - Grundläggande DataUpdateCoordinator
- `references/architecture.md` - Integration-arkitektur
- `references/entities.md` - Entity-plattformar
