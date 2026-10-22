"""Validate reusable release packages with ESPHome's actual configuration schema.

Optional dependency: esphome==2026.10.0. Secrets and full-node wrappers are created
only in pytest's temporary directory; no user's secrets or device is accessed.
"""

from importlib.metadata import PackageNotFoundError, version
import base64
from pathlib import Path
import subprocess
import secrets
import re
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "esphome/assets/templates/2026-10"
PACKAGES = sorted(p for p in TEMPLATES.glob("*.yaml") if p.stem != "snapshot-host")


def test_release_inventory_has_sources_and_examples():
    """Keep every upstream new-component entry discoverable, including internal ones."""
    catalog = ROOT / "esphome/references/new-components-2026-9-10.md"
    text = catalog.read_text(encoding="utf-8")
    september = {"noise", "sfa40", "mk2pvrouter", "d01", "ds1603l", "snapshot"}
    october = {
        "bridge", "uart_mux", "icnt86", "rx8025t", "tas2780", "tfluna",
        "pzem6l24", "systa_bus", "xiaomi_body_scale", "pn71xx", "counter",
        "tas58xx", "stcc4", "tcp_uart", "uart_tcp", "exponential_moving_average",
        "unicode", "espectre", "xiaomi_mccgq02hl",
    }
    for component in september | october:
        assert f"`{component}`" in text, f"Missing upstream component: {component}"
    assert "API IR/RF completion reply" in text  # Existing API tagged new-component upstream.
    readme = (TEMPLATES / "README.md").read_text(encoding="utf-8")
    for package in TEMPLATES.glob("*.yaml"):
        assert package.name in text
        assert package.name in readme
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if not target.startswith("https://"):
            assert (catalog.parent / target.split("#")[0]).exists(), target


@pytest.mark.parametrize("package", PACKAGES, ids=lambda p: p.stem)
def test_release_package_schema(package, tmp_path):
    try:
        installed = version("esphome")
    except PackageNotFoundError:
        pytest.skip("Install esphome==2026.10.0 to check upstream schemas")
    if installed != "2026.10.0":
        pytest.skip(f"Release fixtures target 2026.10.0, found {installed}")
    (tmp_path / "secrets.yaml").write_text(
        'wifi_ssid: "schema-test-only"\n'
        'wifi_password: "not-a-real-network-password"\n'
        f'api_encryption_key: "{base64.b64encode(secrets.token_bytes(32)).decode()}"\n'
        'scale_mac: "02:00:00:00:00:01"\n'
        'scale_bindkey: "00000000000000000000000000000000"\n'
        'door_mac: "02:00:00:00:00:02"\n'
        'door_bindkey: "00000000000000000000000000000000"\n',
        encoding="utf-8",
    )
    config = tmp_path / "node.yaml"
    config.write_text(
        "esphome:\n  name: schema-check\n"
        "esp32:\n  board: esp32-s3-devkitc-1\n"
        "  framework:\n    type: esp-idf\n"
        "logger:\n  baud_rate: 0\n  hardware_uart: UART0\n"
        "wifi:\n  ssid: !secret wifi_ssid\n  password: !secret wifi_password\n"
        "api:\n  encryption:\n    key: !secret api_encryption_key\n"
        "ota:\n  - platform: esphome\n    encryption:\n"
        f'packages:\n  example: !include "{package.as_posix()}"\n',
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "esphome", "config", str(config)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_snapshot_host_schema(tmp_path):
    if sys.platform == "win32":
        pytest.skip("ESPHome host target requires Linux/macOS; Windows is rejected upstream")
    try:
        if version("esphome") != "2026.10.0":
            pytest.skip("Requires ESPHome 2026.10.0")
    except PackageNotFoundError:
        pytest.skip("Requires ESPHome 2026.10.0")
    config = tmp_path / "snapshot.yaml"
    config.write_text((TEMPLATES / "snapshot-host.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "esphome", "config", str(config)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr
