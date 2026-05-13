"""Shared pytest fixtures for aurora validation tests."""
import json
from pathlib import Path
import pytest

AURORA_ROOT = Path(__file__).resolve().parents[1]
REFERENCES_DIR = AURORA_ROOT / "references"
SCHEMAS_DIR = REFERENCES_DIR / "schemas"
BOARDS_DIR = REFERENCES_DIR / "boards"
COMPONENTS_DIR = REFERENCES_DIR / "components"
EXPANDERS_DIR = REFERENCES_DIR / "expanders"
VOLTAGE_SHIFTERS_DIR = REFERENCES_DIR / "voltage-shifters"


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


@pytest.fixture(scope="session")
def expander_schema():
    """Load the GPIO expander profile JSON Schema."""
    schema_path = SCHEMAS_DIR / "expander-profile.schema.json"
    with schema_path.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def voltage_shifter_schema():
    """Load the voltage level shifter profile JSON Schema."""
    schema_path = SCHEMAS_DIR / "voltage-shifter.schema.json"
    with schema_path.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def all_expander_profiles():
    """Load all GPIO expander profile JSON files."""
    profiles = []
    if EXPANDERS_DIR.exists():
        for path in find_json_files(EXPANDERS_DIR):
            with path.open(encoding="utf-8") as f:
                profiles.append((str(path.relative_to(AURORA_ROOT)), json.load(f)))
    return profiles


@pytest.fixture(scope="session")
def all_voltage_shifter_profiles():
    """Load all voltage level shifter profile JSON files."""
    profiles = []
    if VOLTAGE_SHIFTERS_DIR.exists():
        for path in find_json_files(VOLTAGE_SHIFTERS_DIR):
            with path.open(encoding="utf-8") as f:
                profiles.append((str(path.relative_to(AURORA_ROOT)), json.load(f)))
    return profiles
