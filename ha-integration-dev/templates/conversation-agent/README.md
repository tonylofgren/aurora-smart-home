# LLM Conversation Agent Template

A Home Assistant conversation agent powered by LLMs (Ollama, OpenAI, Anthropic).

## Features

- **Multi-provider support**: Ollama (local), OpenAI, Anthropic
- **Conversation history**: Maintains context across messages
- **Home Assistant context**: Injects device states into LLM prompts
- **Action execution**: LLM can control devices via JSON actions
- **Multilingual**: Responds in user's language

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Integration setup, agent registration |
| `config_flow.py` | Provider selection and configuration |
| `conversation_agent.py` | Main LLM logic and HA integration |
| `conversation.py` | ConversationEntity for Assist |
| `const.py` | Configuration constants |
| `manifest.json` | Integration metadata |
| `strings.json` | UI strings |

## Supported Providers

### Ollama (Local - Free)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2

# Start server (usually auto-starts)
ollama serve
```

Recommended models:
- `llama3.2` - Fast, good for home automation
- `mistral` - Good balance of speed/quality
- `gemma2` - Lightweight option

### OpenAI

Requires API key from https://platform.openai.com/api-keys

Recommended models:
- `gpt-4o-mini` - Fast and affordable
- `gpt-4o` - Best quality
- `gpt-4-turbo` - Good balance

### Anthropic

Requires API key from https://console.anthropic.com/

Recommended models:
- `claude-3-haiku-20240307` - Fast and affordable
- `claude-3-5-sonnet-20241022` - Best quality

## How It Works

```
User: "Turn on the living room lights to 50%"
       ↓
[Conversation Agent receives input]
       ↓
[Build system prompt with device context]
       ↓
[Call LLM API (Ollama/OpenAI/Anthropic)]
       ↓
[LLM returns response with optional action JSON]
       ↓
[Parse and execute actions]
       ↓
[Return speech response to Assist pipeline]
       ↓
User hears: "I've turned on the living room lights to 50%"
```

## Action Format

The LLM can include action blocks in its response:

```json
{
  "action": "call_service",
  "domain": "light",
  "service": "turn_on",
  "target": {"entity_id": "light.living_room"},
  "data": {"brightness_pct": 50}
}
```

## Customization

### Add More Domains

In `const.py`, update `CONTROLLABLE_DOMAINS`:

```python
CONTROLLABLE_DOMAINS = [
    "light",
    "switch",
    "climate",
    "cover",
    "fan",
    "media_player",
    "lock",
    "vacuum",
    "scene",
    "script",  # Add more domains
]
```

### Customize System Prompt

In `conversation_agent.py`, modify `_build_system_prompt()`:

```python
def _build_system_prompt(self, entities, language):
    return f"""You are a smart home assistant.

    Custom instructions here...

    Available devices:
    {entities}
    """
```

### Add Custom Actions

In `_parse_and_execute_actions()`, add handlers for custom action types.

## Installation

1. Copy `conversation-agent/` to `custom_components/my_llm_assistant/`
2. Restart Home Assistant
3. Go to Settings → Integrations → Add Integration
4. Search for "LLM Conversation Agent"
5. Select your provider and configure

## Usage with Assist

1. Go to Settings → Voice assistants
2. Create or edit a pipeline
3. Set "Conversation agent" to your LLM agent
4. Use with voice satellite or text input

## Example Conversations

**Control lights:**
- "Turn on the kitchen lights"
- "Set bedroom to 30%"
- "Turn off all lights"

**Climate:**
- "Set the temperature to 22 degrees"
- "What's the current temperature?"

**Status:**
- "Which lights are on?"
- "What's the status of the living room?"

**Scenes:**
- "Activate movie mode"
- "Set the house to night mode"

---

*Generated with [ha-integration@aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
