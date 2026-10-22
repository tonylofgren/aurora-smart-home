"""Check the installable dashboard structure and responsive grid contract."""

import importlib.util
from pathlib import Path
import shutil

import yaml

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "ha-dashboard-design/assets/custom-editorial"


def test_editorial_layout_and_theme():
    dashboard = yaml.safe_load((ASSETS / "dashboard.yaml").read_text(encoding="utf-8"))
    themes = yaml.safe_load((ASSETS / "theme.yaml").read_text(encoding="utf-8"))
    templates = dashboard["button_card_templates"]
    for view in dashboard["views"]:
        assert view["theme"] in themes
        assert view["type"] == "panel" and len(view["cards"]) == 1
        grid = view["cards"][0]
        assigned = {card["view_layout"]["grid-area"] for card in grid["cards"]}
        layouts = [grid["layout"], *grid["layout"]["mediaquery"].values()]
        for layout in layouts:
            rows = [line.strip(' "').split() for line in layout["grid-template-areas"].splitlines()]
            assert len({len(row) for row in rows}) == 1
            assert {cell for row in rows for cell in row if cell != "."} == assigned
        for card in grid["cards"]:
            if "template" in card:
                assert card["template"] in templates
            if "entity" in card:
                assert card["entity"].endswith("_replace_me")
        for template in templates.values():
            if "template" in template:
                assert template["template"] in templates


def test_dashboard_theme_assets_pass_delivery_structure(tmp_path):
    path = ROOT / "aurora/scripts/check-delivery.py"
    spec = importlib.util.spec_from_file_location("delivery_custom_dashboard", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    (tmp_path / "dashboards").mkdir()
    (tmp_path / "themes").mkdir()
    (tmp_path / "www").mkdir()
    shutil.copy(ASSETS / "dashboard.yaml", tmp_path / "dashboards/editorial.yaml")
    shutil.copy(ASSETS / "theme.yaml", tmp_path / "themes/editorial.yaml")
    shutil.copy(ASSETS / "README.md", tmp_path / "README.md")
    assert all(result.passed for result in module.check_subdir_structure(tmp_path))
    (tmp_path / "unrelated").mkdir()
    assert any(not result.passed for result in module.check_subdir_structure(tmp_path))
