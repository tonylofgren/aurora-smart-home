"""Constants for LLM Conversation Agent.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

DOMAIN = "my_llm_assistant"

# Configuration keys
CONF_LLM_PROVIDER = "llm_provider"
CONF_API_KEY = "api_key"
CONF_API_URL = "api_url"
CONF_MODEL = "model"
CONF_TEMPERATURE = "temperature"
CONF_MAX_TOKENS = "max_tokens"
CONF_MAX_HISTORY = "max_history"

# LLM Providers
PROVIDER_OLLAMA = "ollama"
PROVIDER_OPENAI = "openai"
PROVIDER_ANTHROPIC = "anthropic"

# Defaults
DEFAULT_PROVIDER = PROVIDER_OLLAMA
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL_OLLAMA = "llama3.2"
DEFAULT_MODEL_OPENAI = "gpt-4o-mini"
DEFAULT_MODEL_ANTHROPIC = "claude-3-haiku-20240307"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 500
DEFAULT_MAX_HISTORY = 10

# Domains to include in context
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
]

# Maximum entities to include in context
MAX_ENTITIES_CONTEXT = 50
