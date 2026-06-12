"""Tests for aurora/scripts/lint_ha_syntax.py.

Verifies that the legacy-syntax linter detects the deprecated Home
Assistant patterns the 2026-06 modernization removed, that it respects
the documented exceptions, and that the repo itself stays clean.
"""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import lint_ha_syntax as lint  # noqa: E402


def findings(snippet: str):
    return lint.lint_yaml_lines(snippet.split("\n"), "test.yaml")


class TestDetectsLegacyPatterns:
    def test_service_step_key(self):
        result = findings(
            "actions:\n"
            "  - service: light.turn_on\n"
            "    target:\n"
            "      entity_id: light.x\n"
        )
        assert len(result) == 1 and "action:" in result[0]

    def test_platform_in_trigger_list(self):
        result = findings(
            "triggers:\n"
            "  - platform: state\n"
            "    entity_id: binary_sensor.x\n"
        )
        assert len(result) == 1 and "trigger:" in result[0]

    def test_platform_in_wait_for_trigger(self):
        result = findings(
            "wait_for_trigger:\n"
            "  - platform: state\n"
        )
        assert len(result) == 1

    def test_singular_block_keys(self):
        result = findings(
            "trigger:\n"
            "  - trigger: state\n"
            "condition: []\n"
            "action:\n"
            "  - action: light.turn_on\n"
        )
        assert len(result) == 2  # bare trigger: and action: (condition: has value)

    def test_call_service(self):
        result = findings(
            "tap_action:\n"
            "  action: call-service\n"
        )
        assert len(result) == 1 and "perform-action" in result[0]

    def test_service_template(self):
        result = findings("service_template: \"{{ x }}\"\n")
        assert len(result) == 1


class TestRespectsExceptions:
    def test_blueprint_selector_keys_stay_singular(self):
        assert findings(
            "input:\n"
            "  custom_action:\n"
            "    selector:\n"
            "      action:\n"
        ) == []

    def test_sensor_platform_is_not_a_trigger(self):
        assert findings(
            "binary_sensor:\n"
            "  - platform: bayesian\n"
            "    observations:\n"
            "      - platform: state\n"
        ) == []

    def test_browser_mod_block(self):
        assert findings(
            "tap_action:\n"
            "  action: fire-dom-event\n"
            "  browser_mod:\n"
            "    service: browser_mod.popup\n"
        ) == []

    def test_old_marker_suppresses_until_new_marker(self):
        result = findings(
            "# Old (deprecated)\n"
            "action:\n"
            "  - service: light.turn_on\n"
            "# New (correct)\n"
            "actions:\n"
            "  - service: light.turn_on\n"
        )
        assert len(result) == 1  # only the one after the New marker

    def test_fields_in_services_yaml(self):
        assert findings(
            "my_service:\n"
            "  fields:\n"
            "    action:\n"
            "      name: Action\n"
        ) == []


class TestFenceParsing:
    def test_valid_fence_passes(self):
        assert lint.check_fence_parses(["a: 1", "b: !secret x"], "f.md", 0) == []

    def test_invalid_fence_fails(self):
        result = lint.check_fence_parses(["{{ jinja }}", "key: value"], "f.md", 0)
        assert len(result) == 1


def test_repo_is_clean(capsys):
    """The whole repo must stay free of legacy HA syntax and broken fences."""
    exit_code = lint.main([])
    output = capsys.readouterr().out
    assert exit_code == 0, f"lint_ha_syntax found regressions:\n{output}"
