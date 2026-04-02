# Common Multi-Skill Workflows

## New Sensor Device
1. **Volt** (`esphome`) — firmware config for the ESP board + sensor
2. **Sage** (`ha-yaml`) — automation using the new sensor entities
3. **Iris** (`ha-dashboard-design`) *(optional)* — dashboard card for the sensor

## Cloud Service Integration
1. **Atlas** (`api-catalog`) — understand the API pattern and auth method
2. **Ada** (`ha-integration`) — build the custom_components Python integration
3. **Sage** (`ha-yaml`) — automations and dashboard for the new entities

## Voice Assistant
- Local hardware path: **Volt** (`esphome`, ESP32-S3 + microphone) → **Sage** (`ha-yaml`, custom sentences)
- Cloud/LLM path: **Ada** (`ha-integration`, ConversationEntity) → **Sage** (`ha-yaml`, intent scripts)

## Full Room Automation
1. **Volt** (`esphome`) — sensors and switches for the room
2. **Sage** (`ha-yaml`) — room automation logic
3. **Iris** (`ha-dashboard-design`) — room control card
