# Aurora Validation Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the minimum viable validation pipeline for Volt: JSON schemas, one board profile (ESP32-S3), one component profile (BME280), pin and conflict validators, and Volt integration through Iron Law 6.

**Architecture:** A reference-data layer (`aurora/references/`) provides machine-readable JSON profiles for boards and components, validated by JSON Schema. Validator modules in markdown specify the rules Volt must follow. Python tests (`pytest`) verify both schema correctness and data integrity. Volt's SKILL.md is updated to reference the new structure and enforce a new Iron Law: validate before generating.

**Tech Stack:** Python 3.11+, pytest, jsonschema (Python library), pyyaml, JSON Schema Draft 2020-12, markdown.

**This plan delivers (Phase 1-3 MVP slice from spec):**
- JSON Schema for board profile and component profile
- ESP32-S3 DevKit C-1 board profile with full capability data
- BME280 component profile with variants and conflict data
- Pin validator and conflict validator (markdown instructions)
- Volt Iron Law 6: validate before generating
- Test suite that validates all JSON against schemas
- One end-to-end integration test demonstrating Volt's new workflow

---

## File Structure

**Will be created:**
```
aurora/references/schemas/
├── board-profile.schema.json          # JSON Schema for boards
└── component-profile.schema.json      # JSON Schema for components

aurora/references/boards/esp32/
└── esp32-s3-devkitc-1.json            # First board profile

aurora/references/components/temperature/
└── bme280.json                        # First component profile

aurora/references/validators/
├── pin-validator.md                   # Pin validation rules
└── conflict-validator.md              # Component conflict rules

aurora/tests/
├── conftest.py                        # pytest fixtures
├── test_board_schemas.py              # Validates all board JSON
├── test_component_schemas.py          # Validates all component JSON
├── test_esp32_s3_data_integrity.py    # Domain-specific data tests
├── test_bme280_data_integrity.py      # Domain-specific data tests
└── test_volt_iron_law_6.py            # Integration test

requirements-dev.txt                    # Python dev dependencies
```

**Will be modified:**
```
aurora/souls/volt.md                   # Add Iron Law 6
aurora/SKILL.md                        # Reference new directory structure
```

---

## Task 1: Setup test infrastructure

**Files:**
- Create: `requirements-dev.txt`
- Create: `aurora/tests/conftest.py`
- Create: `aurora/tests/__init__.py`

- [ ] **Step 1: Create requirements-dev.txt**

Create `requirements-dev.txt` with content:

```
pytest>=7.4.0
jsonschema>=4.20.0
pyyaml>=6.0
```

- [ ] **Step 2: Create empty __init__.py**

Create `aurora/tests/__init__.py` (empty file).

- [ ] **Step 3: Create conftest.py with shared fixtures**

Create `aurora/tests/conftest.py`:

```python
"""Shared pytest fixtures for aurora validation tests."""
import json
from pathlib import Path
import pytest

AURORA_ROOT = Path(__file__).resolve().parents[1]
REFERENCES_DIR = AURORA_ROOT / "references"
SCHEMAS_DIR = REFERENCES_DIR / "schemas"
BOARDS_DIR = REFERENCES_DIR / "boards"
COMPONENTS_DIR = REFERENCES_DIR / "components"


@pytest.fixture(scope="session")
def board_schema():
    """Load the board profile JSON Schema."""
    schema_path = SCHEMAS_DIR / "board-profile.schema.json"
    with schema_path.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def component_schema():
    """Load the component profile JSON Schema."""
    schema_path = SCHEMAS_DIR / "component-profile.schema.json"
    with schema_path.open(encoding="utf-8") as f:
        return json.load(f)


def find_json_files(root):
    """Recursively find all .json files under root, excluding schema files."""
    return [p for p in root.rglob("*.json") if not p.name.endswith(".schema.json")]


@pytest.fixture(scope="session")
def all_board_profiles():
    """Load all board profile JSON files."""
    profiles = []
    for path in find_json_files(BOARDS_DIR):
        with path.open(encoding="utf-8") as f:
            profiles.append((str(path.relative_to(AURORA_ROOT)), json.load(f)))
    return profiles


@pytest.fixture(scope="session")
def all_component_profiles():
    """Load all component profile JSON files."""
    profiles = []
    for path in find_json_files(COMPONENTS_DIR):
        with path.open(encoding="utf-8") as f:
            profiles.append((str(path.relative_to(AURORA_ROOT)), json.load(f)))
    return profiles
```

- [ ] **Step 4: Verify pytest can collect tests**

Run: `pip install -r requirements-dev.txt && python -m pytest aurora/tests/ --collect-only`
Expected: No errors, "no tests ran" (no test files yet).

- [ ] **Step 5: Commit**

```bash
git add requirements-dev.txt aurora/tests/conftest.py aurora/tests/__init__.py
git commit -m "chore: add pytest infrastructure for aurora validation tests"
```

---

## Task 2: Write board-profile JSON Schema

**Files:**
- Create: `aurora/references/schemas/board-profile.schema.json`
- Create: `aurora/tests/test_board_schemas.py`

- [ ] **Step 1: Write the failing test**

Create `aurora/tests/test_board_schemas.py`:

```python
"""Tests that all board profile JSON files conform to the board-profile schema."""
import jsonschema
import pytest


def test_board_schema_loads(board_schema):
    """The board profile schema itself must be valid JSON Schema."""
    jsonschema.Draft202012Validator.check_schema(board_schema)


def test_all_board_profiles_validate(all_board_profiles, board_schema):
    """Every board profile JSON must validate against the schema."""
    if not all_board_profiles:
        pytest.skip("No board profiles found yet")
    validator = jsonschema.Draft202012Validator(board_schema)
    for path, profile in all_board_profiles:
        errors = list(validator.iter_errors(profile))
        assert not errors, f"{path} failed validation: {[e.message for e in errors]}"
```

- [ ] **Step 2: Run test, verify it fails**

Run: `python -m pytest aurora/tests/test_board_schemas.py -v`
Expected: FAIL because `board-profile.schema.json` does not exist yet.

- [ ] **Step 3: Write the board profile schema**

Create `aurora/references/schemas/board-profile.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aurora-smart-home.dev/schemas/board-profile.schema.json",
  "title": "Aurora Board Profile",
  "type": "object",
  "required": [
    "schema_version", "board_id", "display_name", "chip", "manufacturer",
    "wireless", "power", "memory", "gpio", "smart_home_capabilities",
    "lifecycle", "esphome", "last_verified"
  ],
  "properties": {
    "schema_version": {"type": "string", "pattern": "^\\d+\\.\\d+(\\.\\d+)?$"},
    "board_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
    "display_name": {"type": "string", "minLength": 1},
    "chip": {"type": "string", "minLength": 1},
    "manufacturer": {"type": "string", "minLength": 1},
    "wireless": {
      "type": "object",
      "required": ["wifi", "bluetooth", "thread", "zigbee"],
      "properties": {
        "wifi": {"type": "array", "items": {"type": "string"}},
        "wifi_standard": {"type": ["string", "null"]},
        "bluetooth": {"type": ["string", "null"]},
        "bluetooth_classic": {"type": "boolean"},
        "thread": {"type": "boolean"},
        "zigbee": {"type": "boolean"},
        "lora": {"type": ["string", "null"]},
        "ethernet": {"type": ["string", "null"]}
      }
    },
    "power": {
      "type": "object",
      "required": ["usb_type", "operating_voltage", "deep_sleep_current_ua"],
      "properties": {
        "usb_type": {"type": ["string", "null"]},
        "operating_voltage": {"type": "number"},
        "input_voltage_range": {"type": "string"},
        "battery_connector": {"type": ["string", "null"]},
        "charging_ic": {"type": ["string", "null"]},
        "vbat_monitor_pin": {"type": ["integer", "null"]},
        "deep_sleep_current_ua": {"type": "number"},
        "light_sleep_current_ma": {"type": ["number", "null"]},
        "modem_sleep_current_ma": {"type": ["number", "null"]},
        "solar_input": {"type": "boolean"},
        "gpio_5v_tolerant": {"type": "boolean"}
      }
    },
    "memory": {
      "type": "object",
      "required": ["flash_mb", "psram_mb", "ram_kb"],
      "properties": {
        "flash_mb": {"type": "number"},
        "psram_mb": {"type": "number"},
        "psram_type": {"type": ["string", "null"]},
        "ram_kb": {"type": "number"}
      }
    },
    "gpio": {
      "type": "object",
      "required": ["valid_pins", "strapping_pins", "adc1_pins"],
      "properties": {
        "valid_pins": {"type": "array", "items": {"type": "integer"}, "uniqueItems": true},
        "strapping_pins": {"type": "array", "items": {"type": "integer"}, "uniqueItems": true},
        "reserved_for_usb": {"type": "array", "items": {"type": "integer"}},
        "reserved_for_flash": {"type": "array", "items": {"type": "integer"}},
        "input_only": {"type": "array", "items": {"type": "integer"}},
        "adc1_pins": {"type": "array", "items": {"type": "integer"}},
        "adc2_pins": {"type": "array", "items": {"type": "integer"}},
        "touch_pins": {"type": "array", "items": {"type": "integer"}},
        "dac_pins": {"type": "array", "items": {"type": "integer"}},
        "wake_source_pins": {"type": "array", "items": {"type": "integer"}},
        "i2c_default": {
          "type": "object",
          "properties": {"sda": {"type": "integer"}, "scl": {"type": "integer"}}
        },
        "spi_default": {
          "type": "object",
          "properties": {
            "mosi": {"type": "integer"}, "miso": {"type": "integer"},
            "sck": {"type": "integer"}, "cs": {"type": "integer"}
          }
        }
      }
    },
    "onboard_components": {
      "type": "object",
      "properties": {
        "led_gpio": {"type": ["integer", "null"]},
        "led_type": {"type": ["string", "null"]},
        "boot_button_gpio": {"type": ["integer", "null"]},
        "reset_button": {"type": ["string", "null"]},
        "display": {"type": ["string", "null"]},
        "imu": {"type": ["string", "null"]},
        "buzzer": {"type": ["string", "null"]}
      }
    },
    "smart_home_capabilities": {
      "type": "object",
      "required": ["bluetooth_proxy", "voice_assistant", "matter_controller"],
      "properties": {
        "bluetooth_proxy": {"type": "boolean"},
        "voice_assistant": {"type": "boolean"},
        "matter_controller": {"type": "boolean"},
        "matter_device": {"type": "boolean"},
        "zigbee_coordinator": {"type": "boolean"},
        "thread_border_router": {"type": "boolean"},
        "ble_tracker": {"type": "boolean"},
        "camera_support": {"type": "boolean"},
        "battery_powered": {"type": "boolean"},
        "ir_blaster": {"type": "boolean"},
        "rf_proxy_cc1101": {"type": "boolean"}
      }
    },
    "ota_safety": {
      "type": "object",
      "properties": {
        "factory_reset_pin": {"type": ["integer", "null"]},
        "external_programmer_needed": {"type": "boolean"},
        "usb_cdc_recovery": {"type": "boolean"},
        "min_required_features_for_unbricking": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "form_factor": {
      "type": "object",
      "properties": {
        "antenna": {"type": "string"},
        "ipex_connector": {"type": "boolean"},
        "dimensions_mm": {"type": "string"},
        "certifications": {"type": "array", "items": {"type": "string"}},
        "operating_temp_c": {"type": "string"}
      }
    },
    "limitations": {
      "type": "object",
      "properties": {
        "max_cpu_mhz": {"type": "integer"},
        "no_dac": {"type": "boolean"},
        "usb_blocks_gpio": {"type": "array", "items": {"type": "integer"}},
        "psram_blocks_gpio": {"type": "array", "items": {"type": "integer"}},
        "adc2_blocked_when_wifi_active": {"type": "boolean"},
        "strapping_conflict_warnings": {"type": "array", "items": {"type": "string"}}
      }
    },
    "lifecycle": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": {"enum": ["active", "legacy", "deprecated", "obsolete"]},
        "released": {"type": "string"},
        "deprecated_since": {"type": ["string", "null"]},
        "reason": {"type": ["string", "null"]},
        "successor": {"type": ["string", "null"]}
      }
    },
    "esphome": {
      "type": "object",
      "required": ["platform", "variant", "framework", "min_version"],
      "properties": {
        "platform": {"type": "string"},
        "variant": {"type": "string"},
        "framework": {"enum": ["arduino", "esp-idf"]},
        "min_version": {"type": "string"}
      }
    },
    "datasheet_url": {"type": "string", "format": "uri"},
    "last_verified": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
    "verified_source": {"type": "string"}
  }
}
```

- [ ] **Step 4: Run test, verify it passes**

Run: `python -m pytest aurora/tests/test_board_schemas.py -v`
Expected: 2 passed (`test_board_schema_loads` and `test_all_board_profiles_validate` which skips because no boards yet).

- [ ] **Step 5: Commit**

```bash
git add aurora/references/schemas/board-profile.schema.json aurora/tests/test_board_schemas.py
git commit -m "feat(aurora): add board profile JSON Schema with validation tests"
```

---

## Task 3: Write component-profile JSON Schema

**Files:**
- Create: `aurora/references/schemas/component-profile.schema.json`
- Create: `aurora/tests/test_component_schemas.py`

- [ ] **Step 1: Write the failing test**

Create `aurora/tests/test_component_schemas.py`:

```python
"""Tests that all component profile JSON files conform to the component-profile schema."""
import jsonschema
import pytest


def test_component_schema_loads(component_schema):
    """The component profile schema itself must be valid JSON Schema."""
    jsonschema.Draft202012Validator.check_schema(component_schema)


def test_all_component_profiles_validate(all_component_profiles, component_schema):
    """Every component profile JSON must validate against the schema."""
    if not all_component_profiles:
        pytest.skip("No component profiles found yet")
    validator = jsonschema.Draft202012Validator(component_schema)
    for path, profile in all_component_profiles:
        errors = list(validator.iter_errors(profile))
        assert not errors, f"{path} failed validation: {[e.message for e in errors]}"
```

- [ ] **Step 2: Run test, verify it fails**

Run: `python -m pytest aurora/tests/test_component_schemas.py -v`
Expected: FAIL because `component-profile.schema.json` does not exist yet.

- [ ] **Step 3: Write the component profile schema**

Create `aurora/references/schemas/component-profile.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aurora-smart-home.dev/schemas/component-profile.schema.json",
  "title": "Aurora Component Profile",
  "type": "object",
  "required": [
    "schema_version", "component_id", "display_name", "type", "category",
    "protocol", "pin_requirements", "power", "esphome"
  ],
  "properties": {
    "schema_version": {"type": "string", "pattern": "^\\d+\\.\\d+(\\.\\d+)?$"},
    "component_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
    "display_name": {"type": "string", "minLength": 1},
    "type": {"type": "string"},
    "category": {"type": "string"},
    "protocol": {
      "enum": ["i2c", "spi", "single_wire_digital", "uart", "onewire",
               "analog", "digital_io", "i2s", "pwm"]
    },
    "variants": {
      "type": "object",
      "properties": {
        "primary": {"type": "string"},
        "easily_confused_with": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["component_id", "difference"],
            "properties": {
              "component_id": {"type": "string"},
              "difference": {"type": "string"}
            }
          }
        },
        "knockoffs_known": {"type": "boolean"},
        "verification_method": {"type": "string"}
      }
    },
    "i2c": {
      "type": "object",
      "properties": {
        "default_addresses": {"type": "array", "items": {"type": "string"}},
        "address_strap_pin": {"type": ["string", "null"]},
        "max_speed_khz": {"type": "integer"}
      }
    },
    "pin_requirements": {
      "type": "object",
      "required": ["count", "type"],
      "properties": {
        "count": {"type": "integer", "minimum": 1},
        "type": {"type": "string"},
        "must_use_default_i2c_pins": {"type": "boolean"},
        "adc_required": {"type": "boolean"},
        "input_only_ok": {"type": "boolean"},
        "strapping_pin_ok": {"type": "boolean"},
        "5v_tolerant_required": {"type": "boolean"},
        "interrupt_capable_required": {"type": "boolean"}
      }
    },
    "external_components": {
      "type": "object",
      "properties": {
        "pullup_resistor": {"type": ["object", "null"]},
        "decoupling_cap": {"type": ["object", "null"]}
      }
    },
    "power": {
      "type": "object",
      "required": ["voltage_min", "voltage_max"],
      "properties": {
        "voltage_min": {"type": "number"},
        "voltage_max": {"type": "number"},
        "tolerates_5v": {"type": "boolean"},
        "level_shifter_required_on_5v_board": {"type": "boolean"},
        "current_ma_active": {"type": "number"},
        "current_sleep_ua": {"type": "number"}
      }
    },
    "limitations": {"type": "object"},
    "calibration": {
      "type": "object",
      "properties": {
        "required": {"type": "boolean"},
        "type": {"type": ["string", "null"]}
      }
    },
    "esphome": {
      "type": "object",
      "required": ["platform", "min_version"],
      "properties": {
        "platform": {"type": "string"},
        "min_version": {"type": "string"},
        "config_template": {"type": "string"}
      }
    },
    "datasheet_url": {"type": "string", "format": "uri"}
  }
}
```

- [ ] **Step 4: Run test, verify it passes**

Run: `python -m pytest aurora/tests/test_component_schemas.py -v`
Expected: 2 passed (schema loads, validation skips because no components yet).

- [ ] **Step 5: Commit**

```bash
git add aurora/references/schemas/component-profile.schema.json aurora/tests/test_component_schemas.py
git commit -m "feat(aurora): add component profile JSON Schema with validation tests"
```

---

## Task 4: Write ESP32-S3 board profile

**Files:**
- Create: `aurora/references/boards/esp32/esp32-s3-devkitc-1.json`
- Create: `aurora/tests/test_esp32_s3_data_integrity.py`

- [ ] **Step 1: Write the failing data integrity test**

Create `aurora/tests/test_esp32_s3_data_integrity.py`:

```python
"""Domain-specific data integrity tests for the ESP32-S3 board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "esp32" / "esp32-s3-devkitc-1.json"


@pytest.fixture(scope="module")
def s3_profile():
    """Load the ESP32-S3 DevKit C-1 profile."""
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_gpio_19_and_20_reserved_for_usb(s3_profile):
    """ESP32-S3 USB OTG uses GPIO 19 and 20. They must be marked reserved."""
    reserved = s3_profile["gpio"]["reserved_for_usb"]
    assert 19 in reserved
    assert 20 in reserved


def test_strapping_pins_include_0_3_45_46(s3_profile):
    """ESP32-S3 strapping pins are GPIO 0, 3, 45, 46 per Espressif datasheet."""
    strapping = set(s3_profile["gpio"]["strapping_pins"])
    assert {0, 3, 45, 46}.issubset(strapping)


def test_chip_has_ble_5(s3_profile):
    """ESP32-S3 has BLE 5.0 (no BT Classic)."""
    assert s3_profile["wireless"]["bluetooth"] == "BLE 5.0"
    assert s3_profile["wireless"]["bluetooth_classic"] is False


def test_chip_has_no_thread(s3_profile):
    """ESP32-S3 does not have 802.15.4, so no Thread or Zigbee."""
    assert s3_profile["wireless"]["thread"] is False
    assert s3_profile["wireless"]["zigbee"] is False


def test_smart_home_caps_consistent_with_chip(s3_profile):
    """ESP32-S3 supports bluetooth_proxy (has BLE) but not zigbee_coordinator (no 802.15.4)."""
    caps = s3_profile["smart_home_capabilities"]
    assert caps["bluetooth_proxy"] is True
    assert caps["zigbee_coordinator"] is False


def test_no_dac_on_s3(s3_profile):
    """ESP32-S3 has no DAC pins (removed compared to ESP32 classic)."""
    assert s3_profile["limitations"]["no_dac"] is True
    assert s3_profile["gpio"]["dac_pins"] == []


def test_valid_gpio_range_for_s3(s3_profile):
    """ESP32-S3 valid GPIO are 0-21 and 26-48 (22-25 are reserved for SPI flash)."""
    valid = set(s3_profile["gpio"]["valid_pins"])
    expected = set(range(0, 22)) | set(range(26, 49))
    assert valid == expected


def test_psram_blocks_gpio_26_to_32(s3_profile):
    """When PSRAM is active, GPIO 26-32 are unusable."""
    psram_blocks = set(s3_profile["limitations"]["psram_blocks_gpio"])
    assert {26, 27, 28, 29, 30, 31, 32}.issubset(psram_blocks)


def test_lifecycle_is_active(s3_profile):
    """ESP32-S3 DevKit C-1 is a current product, status must be active."""
    assert s3_profile["lifecycle"]["status"] == "active"
```

- [ ] **Step 2: Run test, verify it fails**

Run: `python -m pytest aurora/tests/test_esp32_s3_data_integrity.py -v`
Expected: FAIL because the profile JSON does not exist yet.

- [ ] **Step 3: Write the ESP32-S3 board profile**

Create `aurora/references/boards/esp32/esp32-s3-devkitc-1.json`:

```json
{
  "$schema": "../../schemas/board-profile.schema.json",
  "schema_version": "1.0",
  "board_id": "esp32-s3-devkitc-1",
  "display_name": "ESP32-S3 DevKit C-1",
  "chip": "ESP32-S3",
  "manufacturer": "Espressif",
  "wireless": {
    "wifi": ["2.4GHz"],
    "wifi_standard": "WiFi 4 (b/g/n)",
    "bluetooth": "BLE 5.0",
    "bluetooth_classic": false,
    "thread": false,
    "zigbee": false,
    "lora": null,
    "ethernet": null
  },
  "power": {
    "usb_type": "USB-C",
    "operating_voltage": 3.3,
    "input_voltage_range": "5V (USB) or 3.3V",
    "battery_connector": null,
    "charging_ic": null,
    "vbat_monitor_pin": null,
    "deep_sleep_current_ua": 7,
    "light_sleep_current_ma": 0.8,
    "modem_sleep_current_ma": 20,
    "solar_input": false,
    "gpio_5v_tolerant": false
  },
  "memory": {
    "flash_mb": 8,
    "psram_mb": 8,
    "psram_type": "OPI",
    "ram_kb": 512
  },
  "gpio": {
    "valid_pins": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48],
    "strapping_pins": [0,3,45,46],
    "reserved_for_usb": [19,20],
    "reserved_for_flash": [22,23,24,25],
    "input_only": [],
    "adc1_pins": [1,2,3,4,5,6,7,8,9,10],
    "adc2_pins": [11,12,13,14,15,16,17,18,19,20],
    "touch_pins": [1,2,3,4,5,6,7,8,9,10,11,12,13,14],
    "dac_pins": [],
    "wake_source_pins": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21],
    "i2c_default": {"sda": 8, "scl": 9},
    "spi_default": {"mosi": 11, "miso": 13, "sck": 12, "cs": 10}
  },
  "onboard_components": {
    "led_gpio": 38,
    "led_type": "RGB WS2812",
    "boot_button_gpio": 0,
    "reset_button": "EN pin",
    "display": null,
    "imu": null,
    "buzzer": null
  },
  "smart_home_capabilities": {
    "bluetooth_proxy": true,
    "voice_assistant": true,
    "matter_controller": true,
    "matter_device": true,
    "zigbee_coordinator": false,
    "thread_border_router": false,
    "ble_tracker": true,
    "camera_support": true,
    "battery_powered": false,
    "ir_blaster": true,
    "rf_proxy_cc1101": true
  },
  "ota_safety": {
    "factory_reset_pin": 0,
    "external_programmer_needed": false,
    "usb_cdc_recovery": true,
    "min_required_features_for_unbricking": ["wifi", "ota OR usb_cdc"]
  },
  "form_factor": {
    "antenna": "PCB",
    "ipex_connector": false,
    "dimensions_mm": "63 x 25.5",
    "certifications": ["FCC", "CE"],
    "operating_temp_c": "-40 to +85"
  },
  "limitations": {
    "max_cpu_mhz": 240,
    "no_dac": true,
    "usb_blocks_gpio": [19,20],
    "psram_blocks_gpio": [26,27,28,29,30,31,32],
    "adc2_blocked_when_wifi_active": true,
    "strapping_conflict_warnings": [
      "GPIO 0 must be HIGH at boot, pull-up if used as input",
      "GPIO 45 must be LOW at boot, affects flash voltage",
      "GPIO 46 must be LOW at boot, affects download mode"
    ]
  },
  "lifecycle": {
    "status": "active",
    "released": "2022-11",
    "deprecated_since": null,
    "reason": null,
    "successor": null
  },
  "esphome": {
    "platform": "esp32",
    "variant": "ESP32S3",
    "framework": "esp-idf",
    "min_version": "2023.6.0"
  },
  "datasheet_url": "https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf",
  "last_verified": "2026-05-13",
  "verified_source": "Espressif official + Arduino-ESP32 v3.0"
}
```

- [ ] **Step 4: Run all tests, verify they pass**

Run: `python -m pytest aurora/tests/test_esp32_s3_data_integrity.py aurora/tests/test_board_schemas.py -v`
Expected: All pass (data integrity 9 tests + schema validation 2 tests).

- [ ] **Step 5: Commit**

```bash
git add aurora/references/boards/esp32/esp32-s3-devkitc-1.json aurora/tests/test_esp32_s3_data_integrity.py
git commit -m "feat(aurora): add ESP32-S3 DevKit C-1 board profile"
```

---

## Task 5: Write BME280 component profile

**Files:**
- Create: `aurora/references/components/temperature/bme280.json`
- Create: `aurora/tests/test_bme280_data_integrity.py`

- [ ] **Step 1: Write the failing data integrity test**

Create `aurora/tests/test_bme280_data_integrity.py`:

```python
"""Domain-specific data integrity tests for the BME280 component profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "components" / "temperature" / "bme280.json"


@pytest.fixture(scope="module")
def bme280():
    """Load the BME280 profile."""
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_protocol_is_i2c(bme280):
    """BME280 uses I2C (or SPI, but we expose the I2C variant)."""
    assert bme280["protocol"] == "i2c"


def test_easily_confused_with_bmp280(bme280):
    """BME280 and BMP280 look identical but BMP280 lacks humidity."""
    confused = bme280["variants"]["easily_confused_with"]
    assert any(c["component_id"] == "bmp280" for c in confused)


def test_verification_method_includes_chip_id_check(bme280):
    """Detection must reference the chip ID register since the boards look identical."""
    method = bme280["variants"]["verification_method"].lower()
    assert "0x60" in method and "0x58" in method


def test_i2c_addresses_are_0x76_or_0x77(bme280):
    """BME280 ships as either 0x76 or 0x77 depending on SDO."""
    addresses = bme280["i2c"]["default_addresses"]
    assert "0x76" in addresses
    assert "0x77" in addresses


def test_does_not_tolerate_5v(bme280):
    """BME280 max voltage is 3.6V. On a 5V board it needs a level shifter."""
    assert bme280["power"]["tolerates_5v"] is False
    assert bme280["power"]["level_shifter_required_on_5v_board"] is True


def test_voltage_range(bme280):
    """BME280 operates between 1.8V and 3.6V."""
    assert bme280["power"]["voltage_min"] == 1.8
    assert bme280["power"]["voltage_max"] == 3.6


def test_pin_requirements_count_is_two(bme280):
    """I2C needs exactly SDA and SCL, so count = 2."""
    assert bme280["pin_requirements"]["count"] == 2
    assert bme280["pin_requirements"]["type"] == "i2c"


def test_no_calibration_required(bme280):
    """BME280 is factory calibrated, no user procedure needed."""
    assert bme280["calibration"]["required"] is False
```

- [ ] **Step 2: Run test, verify it fails**

Run: `python -m pytest aurora/tests/test_bme280_data_integrity.py -v`
Expected: FAIL because the BME280 profile does not exist yet.

- [ ] **Step 3: Write the BME280 component profile**

Create `aurora/references/components/temperature/bme280.json`:

```json
{
  "$schema": "../../schemas/component-profile.schema.json",
  "schema_version": "1.0",
  "component_id": "bme280",
  "display_name": "BME280 Temperature/Humidity/Pressure",
  "type": "environment_combined",
  "category": "environment",
  "protocol": "i2c",
  "variants": {
    "primary": "bme280",
    "easily_confused_with": [
      {
        "component_id": "bmp280",
        "difference": "BMP280 lacks humidity sensor, identical appearance"
      }
    ],
    "knockoffs_known": true,
    "verification_method": "Read chip ID register: 0x60 = BME280, 0x58 = BMP280"
  },
  "i2c": {
    "default_addresses": ["0x76", "0x77"],
    "address_strap_pin": "SDO (LOW=0x76, HIGH=0x77)",
    "max_speed_khz": 400
  },
  "pin_requirements": {
    "count": 2,
    "type": "i2c",
    "must_use_default_i2c_pins": false,
    "adc_required": false,
    "input_only_ok": false,
    "strapping_pin_ok": false,
    "5v_tolerant_required": false,
    "interrupt_capable_required": false
  },
  "external_components": {
    "pullup_resistor": {"value_ohm": 4700, "required": true, "note": "External pull-ups if board does not provide them"},
    "decoupling_cap": {"value_uf": 0.1, "required": true}
  },
  "power": {
    "voltage_min": 1.8,
    "voltage_max": 3.6,
    "tolerates_5v": false,
    "level_shifter_required_on_5v_board": true,
    "current_ma_active": 0.7,
    "current_sleep_ua": 0.1
  },
  "limitations": {
    "min_read_interval_s": 0.5,
    "operating_temp_c": "-40 to +85",
    "humidity_range": "0-100%",
    "pressure_range_hpa": "300-1100",
    "accuracy_temp_c": "+/- 0.5",
    "accuracy_humidity": "+/- 3%",
    "accuracy_pressure_hpa": "+/- 1"
  },
  "calibration": {
    "required": false,
    "type": null
  },
  "esphome": {
    "platform": "bme280_i2c",
    "min_version": "2022.1.0",
    "config_template": "templates/components/bme280.yaml"
  },
  "datasheet_url": "https://www.bosch-sensortec.com/products/environmental-sensors/humidity-sensors-bme280/"
}
```

- [ ] **Step 4: Run all tests, verify they pass**

Run: `python -m pytest aurora/tests/test_bme280_data_integrity.py aurora/tests/test_component_schemas.py -v`
Expected: All pass (8 data integrity tests + 2 schema tests).

- [ ] **Step 5: Commit**

```bash
git add aurora/references/components/temperature/bme280.json aurora/tests/test_bme280_data_integrity.py
git commit -m "feat(aurora): add BME280 component profile"
```

---

## Task 6: Write pin-validator instructions

**Files:**
- Create: `aurora/references/validators/pin-validator.md`

- [ ] **Step 1: Write the file existence test**

Append to `aurora/tests/test_volt_iron_law_6.py` (will be created in Task 10). For now, verify the file exists via:

Run: `test ! -f aurora/references/validators/pin-validator.md && echo MISSING || echo EXISTS`
Expected: MISSING

- [ ] **Step 2: Write the pin-validator markdown**

Create `aurora/references/validators/pin-validator.md`:

```markdown
# Pin Validator

Validates that every GPIO pin used in an ESPHome configuration exists on the selected board, is not reserved, and does not require special handling that the user has not provided.

## When to Run

Volt MUST run this validator after pin allocation (Step 7 of the validation workflow) and before generating YAML output. Other agents that touch GPIO (Echo, Nano, Watt) follow the same rule.

## Inputs

- `board_profile`: parsed JSON from `aurora/references/boards/<chip>/<board>.json`
- `pin_assignments`: object mapping component_id to a list of GPIO numbers, e.g. `{"bme280": [8, 9], "ld2410": [4, 5]}`
- `config_flags`: optional object describing project features that affect pin reservation, e.g. `{"usb_cdc_enabled": true, "psram_used": true, "wifi_enabled": true}`

## Checks

For every GPIO number in `pin_assignments`:

1. **Existence**: number must be in `board_profile.gpio.valid_pins`. If not, fail with: `GPIO <N> does not exist on <display_name>. Valid range: <list>.`

2. **USB reservation**: if `config_flags.usb_cdc_enabled` is true and number is in `board_profile.gpio.reserved_for_usb`, fail with: `GPIO <N> is used by USB CDC on <display_name>. Either move the pin or set usb_cdc: false (loses serial debug).`

3. **PSRAM reservation**: if `config_flags.psram_used` is true and number is in `board_profile.limitations.psram_blocks_gpio`, fail with: `GPIO <N> is reserved for PSRAM on <display_name>. Move the pin or build a board variant without PSRAM.`

4. **Flash reservation**: if number is in `board_profile.gpio.reserved_for_flash`, always fail with: `GPIO <N> is hardwired to the SPI flash chip. It cannot be used for anything else.`

5. **Strapping warning**: if number is in `board_profile.gpio.strapping_pins`, emit a warning (not a failure) with: `GPIO <N> is a strapping pin. Check the strapping_conflict_warnings entry: <text>. Add an external pull resistor matching the boot requirement.`

6. **Input-only check**: if `pin_assignments` requires output for this pin but number is in `board_profile.gpio.input_only`, fail with: `GPIO <N> is input only on <display_name>. Choose a different pin for outputs.`

7. **ADC2 with WiFi**: if number is in `board_profile.gpio.adc2_pins` and `config_flags.wifi_enabled` is true and `board_profile.limitations.adc2_blocked_when_wifi_active` is true, fail with: `GPIO <N> is on ADC2 which is unavailable while WiFi is active on <display_name>. Use an ADC1 pin instead: <adc1_pins>.`

## Output

- Pass: empty list
- Warnings: list of warning strings (Volt presents but does not block)
- Failures: list of failure strings (Volt MUST NOT generate YAML if non-empty)

## Example

Input:
- `board_profile`: ESP32-S3 DevKit C-1
- `pin_assignments`: `{"hc_sr04": [19, 20]}`
- `config_flags`: `{"usb_cdc_enabled": true}`

Output:
```
Failures:
- GPIO 19 is used by USB CDC on ESP32-S3 DevKit C-1. Either move the pin or set usb_cdc: false (loses serial debug).
- GPIO 20 is used by USB CDC on ESP32-S3 DevKit C-1. Either move the pin or set usb_cdc: false (loses serial debug).
```
```

- [ ] **Step 3: Verify the file is valid markdown with required sections**

Run: `grep -E "^## " aurora/references/validators/pin-validator.md`
Expected: Output lists "When to Run", "Inputs", "Checks", "Output", "Example".

- [ ] **Step 4: Verify all 7 checks are documented**

Run: `grep -E "^[0-9]+\. \*\*" aurora/references/validators/pin-validator.md | wc -l`
Expected: 7

- [ ] **Step 5: Commit**

```bash
git add aurora/references/validators/pin-validator.md
git commit -m "feat(aurora): add pin validator instructions for Volt"
```

---

## Task 7: Write conflict-validator instructions

**Files:**
- Create: `aurora/references/validators/conflict-validator.md`

- [ ] **Step 1: Check the file does not yet exist**

Run: `test ! -f aurora/references/validators/conflict-validator.md && echo MISSING || echo EXISTS`
Expected: MISSING

- [ ] **Step 2: Write the conflict-validator markdown**

Create `aurora/references/validators/conflict-validator.md`:

```markdown
# Conflict Validator

Detects pin and bus conflicts when two or more components share a board. Pin validation alone is not enough: two correctly assigned pins can still collide.

## When to Run

Volt runs this validator after pin allocation (Step 7) and after pin-validator passes. It runs once per project, not once per component.

## Inputs

- `board_profile`: parsed board JSON
- `component_assignments`: list of objects, each `{"component_id": "bme280", "component_profile": <loaded JSON>, "pins": [8, 9], "i2c_address": "0x76"}`
- `config_flags`: same as for pin-validator

## Checks

1. **Pin collision (non-bus)**: For each pin, count how many components claim it. If a pin is claimed by more than one component AND none of the colliding components use a shared bus protocol (i2c, onewire), fail with: `GPIO <N> is claimed by both <component_a> and <component_b>. Choose distinct pins for non-bus protocols.`

2. **I2C bus sharing**: Components with `protocol: i2c` may share SDA/SCL. Group them by the SDA/SCL pair. For each group, verify the `i2c_address` values are unique. If not, fail with: `<component_a> and <component_b> both use I2C address <addr>. Reassign one address via the strap pin or add a TCA9548A multiplexer.`

3. **OneWire bus sharing**: Multiple DS18B20 sensors may share a single GPIO. Permit collision when ALL colliding components use `protocol: onewire`.

4. **Voltage compatibility**: For each component, if `component_profile.power.tolerates_5v` is false and `board_profile.power.gpio_5v_tolerant` is false, no issue. If the component is on a 5V board and the component is not tolerant, fail with: `<component_id> max voltage is <voltage_max>V but the board operates at 5V. Add a level shifter (e.g. TXS0108E or BSS138 for I2C).`

5. **Strapping pin conflict**: For each component pin in `board_profile.gpio.strapping_pins`, check `component_profile.pin_requirements.strapping_pin_ok`. If false, fail with: `<component_id> cannot use strapping pin GPIO <N>. The boot requirement conflicts with the component's idle level.`

6. **ADC requirement**: For each component where `component_profile.pin_requirements.adc_required` is true, verify the assigned pin is in `board_profile.gpio.adc1_pins` or `board_profile.gpio.adc2_pins`. If not, fail with: `<component_id> needs an ADC-capable pin, but GPIO <N> on <display_name> is digital-only.`

7. **Interrupt capability**: For each component where `interrupt_capable_required` is true, verify the pin supports edge interrupts on the chip. On ESP32 family all GPIO support interrupts except `input_only` listed without `interrupt_capable`. If incompatible, fail with: `<component_id> needs interrupt support on GPIO <N>, but the board profile does not list it as interrupt-capable.`

## Output

Same structure as pin-validator: `{failures: [...], warnings: [...]}`.

Volt MUST NOT generate YAML if `failures` is non-empty.

## Example

Input:
- `board_profile`: ESP32-S3 DevKit C-1
- Components:
  - `bme280` at I2C addresses 0x76, pins 8/9
  - A second BME280 at I2C address 0x76, pins 8/9

Output:
```
Failures:
- bme280 and bme280 both use I2C address 0x76. Reassign one address via the strap pin or add a TCA9548A multiplexer.
```
```

- [ ] **Step 3: Verify the file is valid markdown with required sections**

Run: `grep -E "^## " aurora/references/validators/conflict-validator.md`
Expected: Output lists "When to Run", "Inputs", "Checks", "Output", "Example".

- [ ] **Step 4: Verify all 7 checks are documented**

Run: `grep -E "^[0-9]+\. \*\*" aurora/references/validators/conflict-validator.md | wc -l`
Expected: 7

- [ ] **Step 5: Commit**

```bash
git add aurora/references/validators/conflict-validator.md
git commit -m "feat(aurora): add conflict validator instructions for Volt"
```

---

## Task 8: Add Iron Law 6 to Volt's soul

**Files:**
- Modify: `aurora/souls/volt.md`

- [ ] **Step 1: Read current volt.md and locate the Iron Laws section**

Confirm `aurora/souls/volt.md` currently ends with Iron Law 5 at approximately line 89-93. The Voice section begins at approximately line 96.

- [ ] **Step 2: Insert Iron Law 6 between Iron Law 5 and Voice**

Modify `aurora/souls/volt.md`. Find the exact text:

```
**Iron Law 5 — Troubleshooting:**
Deliver a Troubleshooting section covering the 3 most likely failure points
for the actual components in this project. Not generic boilerplate — reference
the specific GPIOs, entity IDs, and voltage levels from the generated config.
Include multimeter measurement points for each actuator and ADC sensor.

## Voice
```

Replace with:

```
**Iron Law 5 — Troubleshooting:**
Deliver a Troubleshooting section covering the 3 most likely failure points
for the actual components in this project. Not generic boilerplate, reference
the specific GPIOs, entity IDs, and voltage levels from the generated config.
Include multimeter measurement points for each actuator and ADC sensor.

**Iron Law 6 — Validate Before Generating:**
Before producing any YAML, load the relevant board profile from
`aurora/references/boards/` and component profiles from
`aurora/references/components/`. Run the pin-validator and conflict-validator
described in `aurora/references/validators/`. If either reports failures,
do NOT generate YAML. Report the failures with concrete fix suggestions
and ask the user to choose. The reference data is the source of truth,
not your training memory.

## Voice
```

- [ ] **Step 3: Run a quick consistency test**

Create `aurora/tests/test_volt_iron_laws.py`:

```python
"""Tests that Volt's soul defines all expected Iron Laws."""
from pathlib import Path

VOLT_PATH = Path(__file__).resolve().parents[1] / "souls" / "volt.md"


def test_volt_has_six_iron_laws():
    content = VOLT_PATH.read_text(encoding="utf-8")
    for n in range(1, 7):
        marker = f"**Iron Law {n}"
        assert marker in content, f"Volt is missing {marker}"


def test_iron_law_6_references_validators():
    content = VOLT_PATH.read_text(encoding="utf-8")
    law_6_start = content.index("**Iron Law 6")
    law_6_end = content.index("## Voice", law_6_start)
    law_6 = content[law_6_start:law_6_end]
    assert "pin-validator" in law_6
    assert "conflict-validator" in law_6
    assert "aurora/references/boards" in law_6
```

Run: `python -m pytest aurora/tests/test_volt_iron_laws.py -v`
Expected: 2 passed.

- [ ] **Step 4: Verify the soul file still parses as readable markdown**

Run: `grep -c "^## " aurora/souls/volt.md`
Expected: At least 8 (sections: Character, Background, Technical Knowledge, Specialties, Emojis, Iron Laws, Voice).

- [ ] **Step 5: Commit**

```bash
git add aurora/souls/volt.md aurora/tests/test_volt_iron_laws.py
git commit -m "feat(aurora): add Iron Law 6 to Volt (validate before generating)"
```

---

## Task 9: Reference the new structure in aurora/SKILL.md

**Files:**
- Modify: `aurora/SKILL.md`

- [ ] **Step 1: Read SKILL.md and locate the Iron Laws Reference section**

Confirm `aurora/SKILL.md` has a section titled `## Iron Laws Reference` and a section titled `## Common Multi-Skill Workflows`. The new content goes between them.

- [ ] **Step 2: Add a Reference Data section before "Common Multi-Skill Workflows"**

Modify `aurora/SKILL.md`. Find the exact text:

```
- **Grid** (network): Never connect IoT devices to the main LAN without a VLAN plan — always establish segmentation before recommending device setup.

## Common Multi-Skill Workflows
```

Replace with:

```
- **Grid** (network): Never connect IoT devices to the main LAN without a VLAN plan, always establish segmentation before recommending device setup.

## Reference Data

Aurora ships machine-readable reference data so agents can validate against
authoritative specs instead of relying on training memory:

- `aurora/references/boards/`: board profiles per chip family. Volt and other
  hardware agents MUST load the matching profile before generating any GPIO
  configuration.
- `aurora/references/components/`: sensor and actuator profiles. Include
  variant disambiguation (e.g. BME280 vs BMP280), voltage levels, and pin
  requirements.
- `aurora/references/schemas/`: JSON Schema definitions for every JSON type.
  Tests in `aurora/tests/` validate that every reference file conforms.
- `aurora/references/validators/`: validator modules consumed by Volt and
  other agents. Current modules: `pin-validator.md`, `conflict-validator.md`.

When Volt produces output, it MUST follow Iron Law 6: load the relevant
profiles, run pin-validator and conflict-validator, and refuse to generate
YAML if either reports failures.

## Common Multi-Skill Workflows
```

- [ ] **Step 3: Bump skill version**

Find the line near the top of `aurora/SKILL.md`:

```
When activated, first output `v1.5.1` on its own line, then output the banner:
```

Change to:

```
When activated, first output `v1.6.0` on its own line, then output the banner:
```

- [ ] **Step 4: Write a structural test**

Create `aurora/tests/test_skill_md_structure.py`:

```python
"""Tests that aurora/SKILL.md references the new reference data structure."""
from pathlib import Path

SKILL_PATH = Path(__file__).resolve().parents[1] / "SKILL.md"


def test_skill_references_boards_directory():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "aurora/references/boards/" in content


def test_skill_references_components_directory():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "aurora/references/components/" in content


def test_skill_references_validators_directory():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "aurora/references/validators/" in content


def test_skill_mentions_iron_law_6():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "Iron Law 6" in content


def test_skill_version_bumped_to_1_6_0():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "v1.6.0" in content
```

Run: `python -m pytest aurora/tests/test_skill_md_structure.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add aurora/SKILL.md aurora/tests/test_skill_md_structure.py
git commit -m "feat(aurora): wire SKILL.md to new reference data structure, bump v1.6.0"
```

---

## Task 10: Integration test for Volt's new workflow

**Files:**
- Create: `aurora/tests/test_volt_iron_law_6.py`

This task verifies the data and rules are wired correctly by simulating Volt's validation flow against the ESP32-S3 + BME280 combination. The test does not invoke an LLM. It encodes the same logic Volt is required to follow.

- [ ] **Step 1: Write the integration test**

Create `aurora/tests/test_volt_iron_law_6.py`:

```python
"""Integration test for Volt's Iron Law 6 validation workflow.

This test does not invoke Claude. It encodes the same checks that Volt must
perform, using the same reference data, to ensure the data is consistent
with the rules.
"""
import json
from pathlib import Path
import pytest

REF_DIR = Path(__file__).resolve().parents[1] / "references"


@pytest.fixture(scope="module")
def s3():
    with (REF_DIR / "boards/esp32/esp32-s3-devkitc-1.json").open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def bme280():
    with (REF_DIR / "components/temperature/bme280.json").open(encoding="utf-8") as f:
        return json.load(f)


def run_pin_validator(board, pin_assignments, config_flags):
    """Simulates the pin-validator rules from pin-validator.md."""
    failures = []
    warnings = []
    valid = set(board["gpio"]["valid_pins"])
    reserved_usb = set(board["gpio"].get("reserved_for_usb", []))
    reserved_flash = set(board["gpio"].get("reserved_for_flash", []))
    strapping = set(board["gpio"].get("strapping_pins", []))
    psram_blocks = set(board.get("limitations", {}).get("psram_blocks_gpio", []))
    for component, pins in pin_assignments.items():
        for n in pins:
            if n not in valid:
                failures.append(f"GPIO {n} does not exist on {board['display_name']}.")
                continue
            if config_flags.get("usb_cdc_enabled") and n in reserved_usb:
                failures.append(f"GPIO {n} is used by USB CDC on {board['display_name']}.")
            if config_flags.get("psram_used") and n in psram_blocks:
                failures.append(f"GPIO {n} is reserved for PSRAM on {board['display_name']}.")
            if n in reserved_flash:
                failures.append(f"GPIO {n} is hardwired to SPI flash.")
            if n in strapping:
                warnings.append(f"GPIO {n} is a strapping pin on {board['display_name']}.")
    return {"failures": failures, "warnings": warnings}


def run_conflict_validator(board, component_assignments):
    """Simulates the conflict-validator rules from conflict-validator.md."""
    failures = []
    i2c_addr_seen = {}
    pin_owners = {}
    for entry in component_assignments:
        comp_id = entry["component_id"]
        profile = entry["component_profile"]
        for pin in entry["pins"]:
            if pin in pin_owners and profile["protocol"] not in {"i2c", "onewire"}:
                failures.append(
                    f"GPIO {pin} is claimed by both {pin_owners[pin]} and {comp_id}."
                )
            pin_owners.setdefault(pin, comp_id)
        if profile["protocol"] == "i2c" and entry.get("i2c_address"):
            addr = entry["i2c_address"]
            if addr in i2c_addr_seen:
                failures.append(
                    f"{i2c_addr_seen[addr]} and {comp_id} both use I2C address {addr}."
                )
            else:
                i2c_addr_seen[addr] = comp_id
        if not profile["power"]["tolerates_5v"] and board["power"]["operating_voltage"] >= 5:
            failures.append(
                f"{comp_id} max voltage is {profile['power']['voltage_max']}V but the board is 5V."
            )
    return {"failures": failures}


def test_happy_path_bme280_on_esp32_s3_passes(s3, bme280):
    """The canonical example: BME280 on ESP32-S3 DevKit C-1 with default I2C pins."""
    pin_result = run_pin_validator(
        s3,
        pin_assignments={"bme280": [s3["gpio"]["i2c_default"]["sda"], s3["gpio"]["i2c_default"]["scl"]]},
        config_flags={"usb_cdc_enabled": True, "psram_used": True, "wifi_enabled": True},
    )
    assert pin_result["failures"] == []

    conflict_result = run_conflict_validator(
        s3,
        component_assignments=[
            {"component_id": "bme280", "component_profile": bme280,
             "pins": [s3["gpio"]["i2c_default"]["sda"], s3["gpio"]["i2c_default"]["scl"]],
             "i2c_address": "0x76"}
        ],
    )
    assert conflict_result["failures"] == []


def test_gpio_19_with_usb_cdc_fails(s3):
    """Using a USB pin while USB CDC is enabled must fail."""
    result = run_pin_validator(
        s3,
        pin_assignments={"sensor": [19]},
        config_flags={"usb_cdc_enabled": True},
    )
    assert any("USB CDC" in msg for msg in result["failures"])


def test_gpio_outside_valid_range_fails(s3):
    """A GPIO number that does not exist on the board must fail."""
    result = run_pin_validator(
        s3,
        pin_assignments={"sensor": [99]},
        config_flags={},
    )
    assert any("does not exist" in msg for msg in result["failures"])


def test_strapping_pin_emits_warning_not_failure(s3):
    """Strapping pins are warnings, not failures."""
    result = run_pin_validator(
        s3,
        pin_assignments={"sensor": [0]},
        config_flags={},
    )
    assert result["failures"] == []
    assert any("strapping pin" in msg for msg in result["warnings"])


def test_two_bme280_same_address_fails(s3, bme280):
    """Two BME280 on the same I2C address must collide."""
    result = run_conflict_validator(
        s3,
        component_assignments=[
            {"component_id": "bme280_a", "component_profile": bme280,
             "pins": [8, 9], "i2c_address": "0x76"},
            {"component_id": "bme280_b", "component_profile": bme280,
             "pins": [8, 9], "i2c_address": "0x76"},
        ],
    )
    assert any("I2C address 0x76" in msg for msg in result["failures"])


def test_two_bme280_different_addresses_pass(s3, bme280):
    """Two BME280 on distinct I2C addresses must share the bus cleanly."""
    result = run_conflict_validator(
        s3,
        component_assignments=[
            {"component_id": "bme280_a", "component_profile": bme280,
             "pins": [8, 9], "i2c_address": "0x76"},
            {"component_id": "bme280_b", "component_profile": bme280,
             "pins": [8, 9], "i2c_address": "0x77"},
        ],
    )
    assert result["failures"] == []
```

- [ ] **Step 2: Run the test, verify it fails on missing fixtures**

If you ran the previous tasks, the JSON files exist and the test should pass. Run:

Run: `python -m pytest aurora/tests/test_volt_iron_law_6.py -v`
Expected: 6 passed.

- [ ] **Step 3: Run the full test suite**

Run: `python -m pytest aurora/tests/ -v`
Expected: All tests pass. Approximate count:
- Task 1: 0 tests (infrastructure only)
- Task 2: 2 tests (board schema)
- Task 3: 2 tests (component schema)
- Task 4: 9 tests (ESP32-S3 data integrity)
- Task 5: 8 tests (BME280 data integrity)
- Task 8: 2 tests (Volt Iron Laws)
- Task 9: 5 tests (SKILL.md structure)
- Task 10: 6 tests (Iron Law 6 integration)
- Total: 34 tests, all passing.

- [ ] **Step 4: Update CHANGELOG.md**

Modify `CHANGELOG.md`. Add a new entry at the top under the `[Unreleased]` section (or create one if missing):

```markdown
## [Unreleased]

### Added
- JSON Schema for board profile and component profile (aurora/references/schemas/)
- ESP32-S3 DevKit C-1 board profile with full capability data
- BME280 component profile with BMP280 disambiguation
- Pin validator and conflict validator (aurora/references/validators/)
- Volt Iron Law 6: validate before generating
- pytest test suite covering schemas, data integrity, and Volt workflow simulation
```

- [ ] **Step 5: Commit**

```bash
git add aurora/tests/test_volt_iron_law_6.py CHANGELOG.md
git commit -m "feat(aurora): add Iron Law 6 integration test suite"
```

---

## Self-Review

**Spec coverage check:**

| Spec section | Plan task |
|--------------|-----------|
| §3.1 schemas/ subdirectory | Tasks 2, 3 |
| §3.1 boards/ subdirectory | Task 4 |
| §3.1 components/ subdirectory | Task 5 |
| §3.1 validators/ subdirectory | Tasks 6, 7 |
| §3.2 Board profile JSON schema | Task 2 |
| §3.3 Component profile JSON schema | Task 3 |
| §3.7 Volt validation workflow (subset: STEP 5, 7, 8) | Tasks 6, 7, 10 |
| §3.15 Iron Law Test Suite (Volt subset) | Tasks 8, 10 |
| §4.2 JSON Schema validation | Tasks 2, 3 (pytest checks every JSON) |

**Out of scope for this plan (deferred to later plans):**
- Other 8 chip-family board profiles (Plan 2)
- Other 9+ sensor profiles, GPIO expanders, voltage shifters (Plan 2)
- Remaining 8 validator modules (Plan 2-3)
- Smart home boards (Plan 3)
- Templates library (Plan 4)
- Cross-agent hand-off (Plan 5)
- External components catalog (Plan 6)
- Retroactive YAML validation, tiered errors, snapshots (Plan 7)
- Schema versioning infra, CI/CD (Plan 8)

**Placeholder scan:** No TBDs, no "implement later", no "similar to Task N". Every step contains concrete code, exact commands, or exact text.

**Type consistency:** All test fixture names (`board_schema`, `component_schema`, `all_board_profiles`, `all_component_profiles`, `s3`, `bme280`) are defined in `conftest.py` (Task 1) or per-test fixtures and used consistently. JSON property names match between schemas (Tasks 2, 3) and data files (Tasks 4, 5).

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-13-aurora-validation-foundation.md`.**

Two execution options:

1. **Subagent-Driven (recommended)**: I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution**: Execute tasks in this session using executing-plans, batch execution with checkpoints.
