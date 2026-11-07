from importlib.metadata import entry_points

import pytest
from swarmauri_toolkit_skillset import SkillsetToolkit


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(group="swarmauri.toolkits", name="SkillsetToolkit")
    assert any(point.load() is SkillsetToolkit for point in points)
