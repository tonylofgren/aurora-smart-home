# Common Multi-Skill Workflows

## New Sensor Device
1. **Volt** (`esphome`) — firmware config for the ESP board + sensor
2. **Sage** (`ha-yaml`) — automation using the new sensor entities
3. **Iris** (`ha-dashboard-design`) *(optional)* — dashboard card for the sensor

*Note: if the project uses battery, actuators, outdoor mounting, or voltages > 5V —
run **Vera** (Hardware Safety Review) before Volt, and **Watt** (power budget) before
finalising the BOM. See Battery/Outdoor IoT Project workflow below.*

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

## Battery / Outdoor IoT Project
1. **Vera** (Hardware Safety Review) — battery protection, voltage safety, outdoor IP rating, mains isolation
2. **Watt** (`esphome`) — power budget table: µA/mA per state × daily duty cycle → battery days + solar panel sizing
3. **Volt** (`esphome`) — firmware YAML + wiring diagram (every GPIO) + calibration procedure (if needed) + troubleshooting section
4. **Sage** (`ha-yaml`) — automations using the new entities
5. **Manual** (`esphome`) — INSTALL.md and TROUBLESHOOTING.md with actual entity IDs and file paths
6. **Vera** (WAF Review) — household usability + manual override + graceful degradation
