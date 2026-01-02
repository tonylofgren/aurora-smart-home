"""LLM Conversation Agent implementation.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home

Supports:
- Ollama (local LLM)
- OpenAI (GPT-4, GPT-4o, etc.)
- Anthropic (Claude)

Features:
- Conversation history
- Home Assistant context injection
- Service call execution via LLM
"""
from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING, Any

import aiohttp

from homeassistant.components.conversation import (
    AbstractConversationAgent,
    ConversationInput,
    ConversationResult,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import ulid

from .const import (
    CONF_API_KEY,
    CONF_API_URL,
    CONF_LLM_PROVIDER,
    CONF_MAX_HISTORY,
    CONF_MODEL,
    CONF_TEMPERATURE,
    CONTROLLABLE_DOMAINS,
    DEFAULT_MAX_HISTORY,
    DEFAULT_TEMPERATURE,
    MAX_ENTITIES_CONTEXT,
    PROVIDER_ANTHROPIC,
    PROVIDER_OLLAMA,
    PROVIDER_OPENAI,
)

if TYPE_CHECKING:
    from . import MyConfigEntry

_LOGGER = logging.getLogger(__name__)


class LLMConversationAgent(AbstractConversationAgent):
    """LLM-powered conversation agent for Home Assistant."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: MyConfigEntry,
    ) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.config_entry = config_entry
        self._history: dict[str, list[dict[str, str]]] = {}

    @property
    def supported_languages(self) -> list[str]:
        """Return supported languages (all via LLM)."""
        return ["*"]

    @property
    def _provider(self) -> str:
        """Get LLM provider."""
        return self.config_entry.data[CONF_LLM_PROVIDER]

    @property
    def _model(self) -> str:
        """Get model name."""
        return self.config_entry.data[CONF_MODEL]

    @property
    def _temperature(self) -> float:
        """Get temperature setting."""
        return self.config_entry.options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)

    @property
    def _max_history(self) -> int:
        """Get max history length."""
        return self.config_entry.options.get(CONF_MAX_HISTORY, DEFAULT_MAX_HISTORY)

    async def async_process(
        self, user_input: ConversationInput
    ) -> ConversationResult:
        """Process user input and return response."""
        conversation_id = user_input.conversation_id or ulid.ulid_now()

        # Get or initialize conversation history
        if conversation_id not in self._history:
            self._history[conversation_id] = []

        # Build messages with history
        messages = self._history[conversation_id].copy()
        messages.append({"role": "user", "content": user_input.text})

        # Get Home Assistant context
        entities_context = await self._get_entities_context()
        system_prompt = self._build_system_prompt(entities_context, user_input.language)

        try:
            # Call LLM
            response = await self._call_llm(system_prompt, messages)

            # Parse and execute any actions from response
            action_result = await self._parse_and_execute_actions(response)

            # Update conversation history
            self._history[conversation_id].append(
                {"role": "user", "content": user_input.text}
            )
            self._history[conversation_id].append(
                {"role": "assistant", "content": response}
            )

            # Trim history if needed
            if len(self._history[conversation_id]) > self._max_history * 2:
                self._history[conversation_id] = self._history[conversation_id][
                    -self._max_history * 2 :
                ]

            # Build response
            speech = action_result if action_result else response
            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_speech(speech)

            return ConversationResult(
                response=intent_response,
                conversation_id=conversation_id,
            )

        except Exception as e:
            _LOGGER.error("Error processing conversation: %s", e)
            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                f"Error: {e}",
            )
            return ConversationResult(
                response=intent_response,
                conversation_id=conversation_id,
            )

    def _build_system_prompt(self, entities: list[dict], language: str) -> str:
        """Build system prompt with Home Assistant context."""
        entities_json = json.dumps(entities, ensure_ascii=False, indent=2)

        return f"""You are a smart home assistant for Home Assistant.
Your task is to help the user control their smart home and answer questions about device states.

AVAILABLE DEVICES:
{entities_json}

CAPABILITIES:
You can execute actions by including a JSON block in your response:
```json
{{"action": "call_service", "domain": "light", "service": "turn_on", "target": {{"entity_id": "light.living_room"}}, "data": {{"brightness_pct": 80}}}}
```

ACTION TYPES:
- turn_on: Turn on lights, switches, etc.
- turn_off: Turn off devices
- toggle: Toggle device state
- set_temperature: Set climate temperature (data: {{"temperature": 22}})
- set_hvac_mode: Set climate mode (data: {{"hvac_mode": "heat"}})
- open_cover/close_cover: Control blinds/covers
- play_media/pause: Control media players

RULES:
1. Always respond in the same language as the user
2. Be concise and helpful
3. If you execute an action, confirm what you did
4. If you can't do something, explain why
5. For status questions, summarize the relevant device states
6. Only include JSON action blocks when actually performing an action

Current language: {language}
"""

    async def _get_entities_context(self) -> list[dict]:
        """Get entities for LLM context."""
        entities = []

        for state in self.hass.states.async_all():
            if state.domain not in CONTROLLABLE_DOMAINS:
                continue

            entity_info = {
                "entity_id": state.entity_id,
                "state": state.state,
                "name": state.attributes.get("friendly_name", state.entity_id),
            }

            # Add relevant attributes based on domain
            if state.domain == "light":
                if brightness := state.attributes.get("brightness"):
                    entity_info["brightness"] = round(brightness / 255 * 100)
            elif state.domain == "climate":
                entity_info["current_temp"] = state.attributes.get("current_temperature")
                entity_info["target_temp"] = state.attributes.get("temperature")
            elif state.domain == "cover":
                entity_info["position"] = state.attributes.get("current_position")

            entities.append(entity_info)

            if len(entities) >= MAX_ENTITIES_CONTEXT:
                break

        return entities

    async def _call_llm(self, system_prompt: str, messages: list[dict]) -> str:
        """Call the configured LLM provider."""
        if self._provider == PROVIDER_OLLAMA:
            return await self._call_ollama(system_prompt, messages)
        elif self._provider == PROVIDER_OPENAI:
            return await self._call_openai(system_prompt, messages)
        elif self._provider == PROVIDER_ANTHROPIC:
            return await self._call_anthropic(system_prompt, messages)
        else:
            raise ValueError(f"Unknown provider: {self._provider}")

    async def _call_ollama(self, system_prompt: str, messages: list[dict]) -> str:
        """Call Ollama API."""
        url = self.config_entry.data[CONF_API_URL]
        session = async_get_clientsession(self.hass)

        ollama_messages = [{"role": "system", "content": system_prompt}] + messages

        async with session.post(
            f"{url}/api/chat",
            json={
                "model": self._model,
                "messages": ollama_messages,
                "stream": False,
                "options": {"temperature": self._temperature},
            },
            timeout=aiohttp.ClientTimeout(total=60),
        ) as resp:
            if resp.status != 200:
                raise Exception(f"Ollama error: {resp.status}")
            data = await resp.json()
            return data["message"]["content"]

    async def _call_openai(self, system_prompt: str, messages: list[dict]) -> str:
        """Call OpenAI API."""
        api_key = self.config_entry.data[CONF_API_KEY]
        session = async_get_clientsession(self.hass)

        openai_messages = [{"role": "system", "content": system_prompt}] + messages

        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": self._model,
                "messages": openai_messages,
                "temperature": self._temperature,
            },
            timeout=aiohttp.ClientTimeout(total=60),
        ) as resp:
            if resp.status != 200:
                error = await resp.text()
                raise Exception(f"OpenAI error: {error}")
            data = await resp.json()
            return data["choices"][0]["message"]["content"]

    async def _call_anthropic(self, system_prompt: str, messages: list[dict]) -> str:
        """Call Anthropic API."""
        api_key = self.config_entry.data[CONF_API_KEY]
        session = async_get_clientsession(self.hass)

        async with session.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self._model,
                "max_tokens": 1024,
                "system": system_prompt,
                "messages": messages,
            },
            timeout=aiohttp.ClientTimeout(total=60),
        ) as resp:
            if resp.status != 200:
                error = await resp.text()
                raise Exception(f"Anthropic error: {error}")
            data = await resp.json()
            return data["content"][0]["text"]

    async def _parse_and_execute_actions(self, response: str) -> str | None:
        """Parse LLM response for actions and execute them."""
        # Look for JSON action blocks
        json_pattern = r"```json\s*(\{[^`]+\})\s*```"
        matches = re.findall(json_pattern, response, re.DOTALL)

        if not matches:
            # Try finding inline JSON
            inline_pattern = r'\{"action":\s*"call_service"[^}]+\}'
            matches = re.findall(inline_pattern, response)

        results = []
        for match in matches:
            try:
                action = json.loads(match)
                if action.get("action") == "call_service":
                    await self._execute_service_call(action)
                    results.append(
                        f"Executed: {action['domain']}.{action['service']}"
                    )
            except (json.JSONDecodeError, KeyError) as e:
                _LOGGER.debug("Failed to parse action: %s", e)

        if results:
            # Return action confirmation, but also include the natural language response
            # by stripping out the JSON blocks
            clean_response = re.sub(json_pattern, "", response).strip()
            if clean_response:
                return clean_response
            return " | ".join(results)

        return None

    async def _execute_service_call(self, action: dict[str, Any]) -> None:
        """Execute a service call from LLM action."""
        domain = action["domain"]
        service = action["service"]
        target = action.get("target", {})
        data = action.get("data", {})

        # Merge target into service data
        service_data = {**data}
        if "entity_id" in target:
            service_data["entity_id"] = target["entity_id"]

        _LOGGER.info(
            "Executing service call: %s.%s with data %s",
            domain,
            service,
            service_data,
        )

        await self.hass.services.async_call(
            domain,
            service,
            service_data,
            blocking=True,
        )
