# Conversation Agent

Guide för att utveckla conversation agents (röstassistenter) för Home Assistant Assist.

## Översikt

En conversation agent tolkar användarens intentioner och utför åtgärder. Home Assistant använder conversation agents i Assist pipeline för röst- och textkommandon.

## Arkitektur

```
┌──────────────────────────────────────────────────┐
│                 Assist Pipeline                   │
├──────────────────────────────────────────────────┤
│  Wake Word → STT → Conversation Agent → TTS      │
│                          ↓                        │
│                   Intent Handler                  │
│                          ↓                        │
│                   Service Calls                   │
└──────────────────────────────────────────────────┘
```

## Conversation Agent Types

| Typ | Beskrivning | Användning |
|-----|-------------|------------|
| `ConversationEntity` | Custom intent parsing | Full kontroll |
| `AbstractConversationAgent` | LLM-baserad | AI/OpenAI |
| Built-in | Home Assistants egna | Standard |

## Minimal Conversation Agent

```python
"""Custom Conversation Agent.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

from homeassistant.components import conversation
from homeassistant.components.conversation import ConversationEntity, ConversationResult
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import ulid

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up conversation agent."""
    async_add_entities([MyConversationAgent(config_entry)])


class MyConversationAgent(ConversationEntity):
    """Custom conversation agent."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self._config_entry = config_entry
        self._attr_unique_id = config_entry.entry_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "My Conversation Agent",
            "manufacturer": "My Company",
        }

    @property
    def supported_languages(self) -> list[str]:
        """Return supported languages."""
        return ["sv", "en"]

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> ConversationResult:
        """Process user input and return response."""
        text = user_input.text.lower()

        # Simple intent matching
        if "status" in text:
            response = await self._get_home_status()
        elif "tänd" in text or "turn on" in text:
            response = await self._handle_turn_on(text)
        elif "släck" in text or "turn off" in text:
            response = await self._handle_turn_off(text)
        else:
            response = "Jag förstod inte. Försök igen."

        intent_response = conversation.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(response)

        return ConversationResult(
            response=intent_response,
            conversation_id=user_input.conversation_id or ulid.ulid_now(),
        )

    async def _get_home_status(self) -> str:
        """Get home status."""
        hass = self.hass
        lights_on = sum(
            1
            for state in hass.states.async_all("light")
            if state.state == "on"
        )
        return f"Du har {lights_on} lampor tända."

    async def _handle_turn_on(self, text: str) -> str:
        """Handle turn on command."""
        # Extract entity from text and call service
        await self.hass.services.async_call(
            "light", "turn_on", {"entity_id": "light.living_room"}
        )
        return "Lampan är tänd."

    async def _handle_turn_off(self, text: str) -> str:
        """Handle turn off command."""
        await self.hass.services.async_call(
            "light", "turn_off", {"entity_id": "light.living_room"}
        )
        return "Lampan är släckt."
```

## LLM-baserad Conversation Agent

Med OpenAI, Anthropic, eller lokal LLM:

```python
"""LLM Conversation Agent.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

import json
import logging
from typing import Any

from homeassistant.components import conversation
from homeassistant.components.conversation import (
    AbstractConversationAgent,
    ConversationInput,
    ConversationResult,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
from homeassistant.util import ulid

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class LLMConversationAgent(AbstractConversationAgent):
    """LLM-powered conversation agent."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize agent."""
        self.hass = hass
        self.config_entry = config_entry
        self.history: dict[str, list[dict[str, str]]] = {}

    @property
    def supported_languages(self) -> list[str]:
        """Return supported languages."""
        return ["*"]  # All languages via LLM

    async def async_process(
        self, user_input: ConversationInput
    ) -> ConversationResult:
        """Process user input using LLM."""
        conversation_id = user_input.conversation_id or ulid.ulid_now()

        # Get or create conversation history
        if conversation_id not in self.history:
            self.history[conversation_id] = []

        messages = self.history[conversation_id].copy()
        messages.append({"role": "user", "content": user_input.text})

        # Get available entities for context
        entities = await self._get_entities_context()

        # System prompt with Home Assistant context
        system_prompt = self._build_system_prompt(entities)

        try:
            # Call LLM API
            response = await self._call_llm(system_prompt, messages)

            # Parse and execute any actions
            action_result = await self._parse_and_execute(response)

            # Update history
            self.history[conversation_id].append(
                {"role": "user", "content": user_input.text}
            )
            self.history[conversation_id].append(
                {"role": "assistant", "content": response}
            )

            # Build response
            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_speech(action_result or response)

            return ConversationResult(
                response=intent_response,
                conversation_id=conversation_id,
            )

        except Exception as e:
            _LOGGER.error("LLM error: %s", e)
            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                f"Error processing request: {e}",
            )
            return ConversationResult(
                response=intent_response,
                conversation_id=conversation_id,
            )

    def _build_system_prompt(self, entities: list[dict]) -> str:
        """Build system prompt with HA context."""
        return f"""Du är en smart hemassistent för Home Assistant.

Tillgängliga enheter:
{json.dumps(entities, ensure_ascii=False, indent=2)}

Du kan utföra följande åtgärder genom att svara med JSON:
{{"action": "call_service", "domain": "light", "service": "turn_on", "entity_id": "light.living_room"}}
{{"action": "call_service", "domain": "climate", "service": "set_temperature", "entity_id": "climate.bedroom", "data": {{"temperature": 22}}}}

Om ingen åtgärd behövs, svara bara med text.
Svara alltid på samma språk som användaren."""

    async def _get_entities_context(self) -> list[dict]:
        """Get entities for LLM context."""
        entities = []
        for state in self.hass.states.async_all():
            if state.domain in ("light", "switch", "climate", "cover", "media_player"):
                entities.append({
                    "entity_id": state.entity_id,
                    "state": state.state,
                    "friendly_name": state.attributes.get("friendly_name", state.entity_id),
                })
        return entities[:50]  # Limit context size

    async def _call_llm(self, system: str, messages: list[dict]) -> str:
        """Call LLM API."""
        # Implementation depends on your LLM provider
        # Example for local Ollama:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "llama3",
                    "messages": [{"role": "system", "content": system}] + messages,
                    "stream": False,
                },
            ) as resp:
                data = await resp.json()
                return data["message"]["content"]

    async def _parse_and_execute(self, response: str) -> str | None:
        """Parse LLM response and execute actions."""
        try:
            # Try to find JSON action in response
            import re
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                action = json.loads(json_match.group())
                if action.get("action") == "call_service":
                    await self.hass.services.async_call(
                        action["domain"],
                        action["service"],
                        {"entity_id": action["entity_id"], **action.get("data", {})},
                    )
                    return f"Utfört: {action['service']} på {action['entity_id']}"
        except json.JSONDecodeError:
            pass
        return None
```

## Registrera Conversation Agent

I `__init__.py`:

```python
"""My integration with conversation agent.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .conversation_agent import LLMConversationAgent

PLATFORMS = ["conversation"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration."""
    hass.data.setdefault(DOMAIN, {})

    # Register conversation agent
    agent = LLMConversationAgent(hass, entry)
    conversation.async_set_agent(hass, entry, agent)
    hass.data[DOMAIN][entry.entry_id] = agent

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload integration."""
    conversation.async_unset_agent(hass, entry)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

## manifest.json

```json
{
  "domain": "my_llm_assistant",
  "name": "My LLM Assistant",
  "version": "1.0.0",
  "config_flow": true,
  "dependencies": ["conversation"],
  "requirements": ["aiohttp"],
  "iot_class": "local_push"
}
```

## Intent Handlers

Registrera custom intents:

```python
"""Custom intents.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

DOMAIN = "my_integration"


async def async_setup_intents(hass: HomeAssistant) -> None:
    """Register custom intents."""
    intent.async_register(hass, GetWeatherIntent())
    intent.async_register(hass, SetRoomModeIntent())


class GetWeatherIntent(intent.IntentHandler):
    """Handle weather intent."""

    intent_type = "GetWeather"
    slot_schema = {
        "location": intent.cv.string,
    }

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle the intent."""
        location = intent_obj.slots.get("location", {}).get("value", "home")

        # Get weather data
        weather = intent_obj.hass.states.get(f"weather.{location}")
        if weather:
            temp = weather.attributes.get("temperature")
            response = f"Temperaturen i {location} är {temp} grader."
        else:
            response = f"Kunde inte hitta väder för {location}."

        response_obj = intent_obj.create_response()
        response_obj.async_set_speech(response)
        return response_obj


class SetRoomModeIntent(intent.IntentHandler):
    """Handle room mode intent."""

    intent_type = "SetRoomMode"
    slot_schema = {
        "room": intent.cv.string,
        "mode": intent.cv.string,
    }

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle the intent."""
        room = intent_obj.slots["room"]["value"]
        mode = intent_obj.slots["mode"]["value"]

        # Execute room scene
        await intent_obj.hass.services.async_call(
            "scene", "turn_on", {"entity_id": f"scene.{room}_{mode}"}
        )

        response_obj = intent_obj.create_response()
        response_obj.async_set_speech(f"{room.title()} är nu i {mode}-läge.")
        return response_obj
```

## Custom Sentences

Lägg till `custom_sentences/sv/sentences.yaml`:

```yaml
language: sv
intents:
  GetWeather:
    data:
      - sentences:
          - "vad är vädret i {location}"
          - "hur är vädret i {location}"
          - "temperatur i {location}"
        slots:
          location:
            - vardagsrummet
            - köket
            - ute
  SetRoomMode:
    data:
      - sentences:
          - "sätt {room} i {mode} läge"
          - "aktivera {mode} i {room}"
        slots:
          room:
            - vardagsrummet
            - sovrummet
            - köket
          mode:
            - film
            - middag
            - natt
```

## Conversation History

Hantera konversationshistorik:

```python
class ConversationHistory:
    """Manage conversation history."""

    def __init__(self, max_history: int = 10) -> None:
        """Initialize history."""
        self._history: dict[str, list[dict]] = {}
        self._max_history = max_history

    def add(self, conversation_id: str, role: str, content: str) -> None:
        """Add message to history."""
        if conversation_id not in self._history:
            self._history[conversation_id] = []

        self._history[conversation_id].append({
            "role": role,
            "content": content,
        })

        # Trim history
        if len(self._history[conversation_id]) > self._max_history:
            self._history[conversation_id] = self._history[conversation_id][-self._max_history:]

    def get(self, conversation_id: str) -> list[dict]:
        """Get conversation history."""
        return self._history.get(conversation_id, [])

    def clear(self, conversation_id: str) -> None:
        """Clear conversation history."""
        self._history.pop(conversation_id, None)
```

## Error Handling

```python
from homeassistant.helpers.intent import IntentResponseErrorCode

async def async_process(self, user_input: ConversationInput) -> ConversationResult:
    """Process with proper error handling."""
    try:
        # Process input
        response = await self._process_input(user_input)

    except AuthenticationError:
        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_error(
            IntentResponseErrorCode.FAILED_TO_HANDLE,
            "Authentication failed. Please reconfigure the integration.",
        )

    except RateLimitError:
        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_error(
            IntentResponseErrorCode.FAILED_TO_HANDLE,
            "Rate limit reached. Please try again later.",
        )

    except Exception as e:
        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_error(
            IntentResponseErrorCode.UNKNOWN,
            f"An unexpected error occurred: {e}",
        )

    return ConversationResult(
        response=intent_response,
        conversation_id=user_input.conversation_id,
    )
```

## Testing

```python
"""Tests for conversation agent.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

import pytest
from homeassistant.components import conversation
from homeassistant.core import HomeAssistant

from custom_components.my_integration.conversation_agent import MyConversationAgent


async def test_turn_on_light(hass: HomeAssistant) -> None:
    """Test turning on light via conversation."""
    agent = MyConversationAgent(hass, mock_config_entry)

    user_input = conversation.ConversationInput(
        text="tänd lampan i vardagsrummet",
        language="sv",
        conversation_id="test",
    )

    result = await agent.async_process(user_input)

    assert result.response.speech["plain"]["speech"] == "Lampan är tänd."


async def test_get_status(hass: HomeAssistant) -> None:
    """Test getting home status."""
    # Set up some lights
    hass.states.async_set("light.living_room", "on")
    hass.states.async_set("light.bedroom", "off")

    agent = MyConversationAgent(hass, mock_config_entry)

    user_input = conversation.ConversationInput(
        text="vad är status hemma",
        language="sv",
        conversation_id="test",
    )

    result = await agent.async_process(user_input)

    assert "1 lampor tända" in result.response.speech["plain"]["speech"]
```

## Se även

- `references/services-events.md` - Anropa tjänster
- `references/entities.md` - Hantera entiteter
- `../home-assistant/references/assist-patterns.md` - Assist pipeline patterns
- `../esphome/references/voice-local.md` - ESPHome voice assistant
