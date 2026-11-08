from importlib.metadata import entry_points

import pytest
from swarmauri_tool_activateskill import ActivateSkill


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(group="swarmauri.tools", name="ActivateSkill")
    assert any(point.load() is ActivateSkill for point in points)
