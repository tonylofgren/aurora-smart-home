"""Constants for Webhook Integration."""
from __future__ import annotations

from typing import Final

DOMAIN: Final = "my_webhook"

# Config entry data keys
WEBHOOK_ID_KEY: Final = "webhook_id"

# Sensor keys that will be created from webhook data
DEFAULT_SENSORS: Final = ["value", "status", "count"]
