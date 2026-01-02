# Troubleshooting Guide

Common issues and solutions across all Aurora Smart Home skills.

---

## Quick Diagnosis

| Symptom | Likely Cause | Skill | Solution |
|---------|--------------|-------|----------|
| ESPHome device won't connect | WiFi/board config | esphome | [WiFi Issues](#esphome-wifi-issues) |
| Entity not appearing in HA | Discovery/naming | esphome/ha-yaml | [Entity Discovery](#entity-not-appearing) |
| Automation not triggering | Trigger/condition | ha-yaml | [Automation Debug](#automation-not-triggering) |
| Integration won't load | Python error | ha-integration | [Integration Debug](#integration-wont-load) |
| Template error | Jinja2 syntax | ha-yaml | [Template Issues](#template-errors) |
| OTA update fails | Memory/network | esphome | [OTA Issues](#ota-update-fails) |

---

## ESPHome Issues

### WiFi Issues

**Symptom:** Device won't connect to WiFi or keeps disconnecting.

**Solutions:**

1. **Check credentials**
   ```yaml
   wifi:
     ssid: !secret wifi_ssid      # Verify in secrets.yaml
     password: !secret wifi_password
   ```

2. **Use static IP** (more reliable)
   ```yaml
   wifi:
     ssid: !secret wifi_ssid
     password: !secret wifi_password
     manual_ip:
       static_ip: 192.168.1.100
       gateway: 192.168.1.1
       subnet: 255.255.255.0
   ```

3. **Enable fast_connect** (saves 1-2 seconds)
   ```yaml
   wifi:
     ssid: !secret wifi_ssid
     password: !secret wifi_password
     fast_connect: true
   ```

4. **Check router settings**
   - Ensure 2.4GHz network (ESP8266/ESP32 don't support 5GHz)
   - Disable AP isolation
   - Check MAC filtering

### OTA Update Fails

**Symptom:** OTA updates timeout or fail.

**Solutions:**

1. **Check available memory**
   ```yaml
   esphome:
     name: my-device
     # Add if config is large
     platformio_options:
       board_build.partitions: min_spiffs.csv
   ```

2. **Enable safe mode**
   ```yaml
   ota:
     - platform: esphome
       password: !secret ota_password
       safe_mode: true
   ```

3. **Increase timeout** (for slow networks)
   ```yaml
   ota:
     - platform: esphome
       password: !secret ota_password
       num_attempts: 5
   ```

4. **Firewall ports**
   - ESPHome OTA uses port 3232 (ESP32) or 8266 (ESP8266)

### GPIO Issues

**Symptom:** Sensor/output not working on specific pin.

**Check strapping pins:**

| Chip | Avoid for Outputs |
|------|-------------------|
| ESP8266 | GPIO0, GPIO2, GPIO15 |
| ESP32 | GPIO0, GPIO2, GPIO12, GPIO15 |
| ESP32-S3 | GPIO0, GPIO45, GPIO46 |
| ESP32-C3 | GPIO2, GPIO8, GPIO9 |

**Input-only pins (ESP32):** GPIO34, GPIO35, GPIO36, GPIO39

**ADC2 + WiFi conflict (ESP32):** ADC2 pins cannot be used while WiFi is active.

### Board Not Recognized

**Symptom:** Compilation fails with board error.

**Solution:** Use exact board ID:
```yaml
esp32:
  board: esp32dev              # Generic ESP32
  # board: esp32-s3-devkitc-1  # ESP32-S3 DevKit
  # board: esp32-c3-devkitm-1  # ESP32-C3 DevKit
  # board: esp32-c6-devkitc-1  # ESP32-C6 DevKit
  # board: d1_mini             # ESP8266 D1 Mini
```

---

## Home Assistant Automation Issues

### Automation Not Triggering

**Symptom:** Automation exists but never runs.

**Debug steps:**

1. **Check trigger state**
   ```yaml
   trigger:
     - platform: state
       entity_id: binary_sensor.motion
       to: "on"           # Must be string with quotes!
       # NOT: to: on      # This is a boolean, not string
   ```

2. **Verify entity_id exists**
   - Developer Tools → States → Search for entity

3. **Check conditions**
   ```yaml
   condition:
     - condition: state
       entity_id: input_boolean.automation_enabled
       state: "on"
   ```

4. **Enable trace** and trigger manually:
   - Settings → Automations → Select automation → Traces

5. **Check for typos** in entity_id (most common issue)

### Entity Not Appearing

**Symptom:** ESPHome device connected but entities missing in HA.

**Solutions:**

1. **Check ESPHome integration**
   - Settings → Integrations → ESPHome → Configure → Re-add device

2. **Verify entity naming**
   ```yaml
   # ESPHome config
   sensor:
     - platform: dht
       temperature:
         name: "Living Room Temperature"  # This becomes sensor.living_room_temperature
   ```

3. **Check entity registry**
   - Entity may be disabled → Settings → Entities → Show disabled

4. **Restart HA** after adding new entities

### Template Errors

**Symptom:** Template renders as error or empty.

**Common fixes:**

1. **Missing default filter**
   ```yaml
   # Bad - fails if entity unavailable
   {{ states('sensor.temperature') | float * 1.8 + 32 }}

   # Good - handles unavailable
   {{ states('sensor.temperature') | float(0) * 1.8 + 32 }}
   ```

2. **Wrong state access**
   ```yaml
   # Bad - returns all states (slow)
   {{ states() | selectattr('domain', 'eq', 'light') | list }}

   # Good - filter by domain
   {{ states.light | selectattr('state', 'eq', 'on') | list | count }}
   ```

3. **Numeric comparisons**
   ```yaml
   # Bad - string comparison
   {{ states('sensor.temp') > 20 }}

   # Good - convert to number
   {{ states('sensor.temp') | float > 20 }}
   ```

4. **Test templates**
   - Developer Tools → Template → Paste and test

### Deprecated Syntax

**Symptom:** Automation works but shows warnings.

**Updates needed:**

```yaml
# Old (deprecated)
service_template: "{{ 'light.turn_on' if on else 'light.turn_off' }}"
data_template:
  entity_id: "{{ light_entity }}"

# New (correct)
service: "{{ 'light.turn_on' if on else 'light.turn_off' }}"
target:
  entity_id: "{{ light_entity }}"
data:
  brightness: "{{ brightness }}"
```

---

## Home Assistant Integration Issues

### Integration Won't Load

**Symptom:** Custom integration fails to load after restart.

**Debug steps:**

1. **Check logs**
   - Settings → System → Logs → Filter by integration name

2. **Verify file structure**
   ```
   custom_components/
   └── my_integration/
       ├── __init__.py
       ├── manifest.json
       ├── config_flow.py
       └── const.py
   ```

3. **Check manifest.json**
   ```json
   {
     "domain": "my_integration",  // Must match folder name
     "name": "My Integration",
     "version": "1.0.0",
     "config_flow": true,
     "requirements": []
   }
   ```

4. **Validate Python syntax**
   ```bash
   python -m py_compile custom_components/my_integration/__init__.py
   ```

### Timestamp Errors

**Symptom:** Timezone issues or "naive datetime" warnings.

**Fix:**
```python
# Bad
from datetime import datetime
now = datetime.now()

# Good
from homeassistant.util import dt as dt_util
now = dt_util.now()  # Timezone-aware
```

### Attribute Serialization Errors

**Symptom:** "Object of type X is not JSON serializable"

**Fix:**
```python
# Bad - dataclass in attributes
@property
def extra_state_attributes(self):
    return {"data": self._data_object}

# Good - convert to dict
@property
def extra_state_attributes(self):
    return {
        "value": self._data_object.value,
        "timestamp": self._data_object.timestamp.isoformat(),
    }
```

### Async/Blocking Errors

**Symptom:** Event loop blocked or "Detected blocking call"

**Fix:**
```python
# Bad - blocking HTTP
import requests
response = requests.get(url)

# Good - async HTTP
from homeassistant.helpers.aiohttp_client import async_get_clientsession

session = async_get_clientsession(hass)
async with session.get(url) as response:
    data = await response.json()
```

---

## Voice Assistant Issues

### Wake Word Not Detecting

**Symptom:** Voice satellite doesn't respond to wake word.

**Solutions:**

1. **Check microphone wiring**
   ```yaml
   microphone:
     - platform: i2s_audio
       i2s_din_pin: GPIO4   # Verify this matches your wiring
       adc_type: external
       pdm: false
   ```

2. **Enable debug logging**
   ```yaml
   logger:
     level: DEBUG
     logs:
       micro_wake_word: DEBUG
   ```

3. **Test microphone separately**
   - Record audio and verify it's capturing

4. **Check wake word model**
   ```yaml
   micro_wake_word:
     models:
       - model: okay_nabu  # Try different models
   ```

### No Audio Output

**Symptom:** TTS responses not playing.

**Solutions:**

1. **Verify speaker wiring**
   ```yaml
   speaker:
     - platform: i2s_audio
       i2s_dout_pin: GPIO8  # Verify this
       dac_type: external
   ```

2. **Check volume**
   ```yaml
   voice_assistant:
     volume_multiplier: 2.0  # Increase if too quiet
   ```

3. **Test speaker with simple tone**
   ```yaml
   # Add test button
   button:
     - platform: template
       name: "Test Speaker"
       on_press:
         - speaker.play: test_tone.wav
   ```

---

## Matter/Thread Issues

### Device Not Pairing

**Symptom:** QR code scan doesn't work.

**Solutions:**

1. **Same network required**
   - Phone and ESP must be on same WiFi network

2. **Check router multicast**
   - mDNS/multicast must not be blocked

3. **Factory reset and retry**
   ```yaml
   button:
     - platform: factory_reset
       name: "Factory Reset"
   ```

4. **Verify Matter config**
   ```yaml
   matter:
     device_type: dimmable_light  # Must match your device
   ```

### Thread Not Working

**Symptom:** Thread-only device can't connect.

**Requirements:**
- ESP32-C6 or ESP32-H2 (only chips with Thread)
- Thread Border Router (HomePod Mini, Nest Hub, etc.)

```yaml
esp32:
  board: esp32-c6-devkitc-1
  framework:
    type: esp-idf
    sdkconfig_options:
      CONFIG_OPENTHREAD_ENABLED: y
```

---

## General Debug Tips

### Enable Detailed Logging

**ESPHome:**
```yaml
logger:
  level: DEBUG
  logs:
    component: DEBUG
```

**Home Assistant:**
```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.my_integration: debug
    homeassistant.components.automation: debug
```

### Check System Resources

**ESPHome memory:**
```yaml
sensor:
  - platform: debug
    free:
      name: "Free Memory"
```

**Home Assistant:**
- Settings → System → Hardware → Check RAM/CPU

### Common Port Numbers

| Service | Port |
|---------|------|
| ESPHome Dashboard | 6052 |
| ESPHome OTA (ESP32) | 3232 |
| ESPHome OTA (ESP8266) | 8266 |
| Home Assistant | 8123 |
| Supervisor API | 4357 |
| mDNS | 5353 |

---

## Getting Help

If these solutions don't work:

1. **Check skill references** - Each skill has detailed troubleshooting docs
2. **Search GitHub Issues** - [aurora-smart-home issues](https://github.com/tonylofgren/aurora-smart-home/issues)
3. **Home Assistant Forums** - [community.home-assistant.io](https://community.home-assistant.io)
4. **ESPHome Discord** - [discord.gg/esphome](https://discord.gg/esphome)

---

*Generated with [aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
