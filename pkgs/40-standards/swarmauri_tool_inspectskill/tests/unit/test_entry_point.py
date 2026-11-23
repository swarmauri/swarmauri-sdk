from importlib.metadata import entry_points

import pytest
from swarmauri_tool_inspectskill import InspectSkill


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(group="swarmauri.tools", name="InspectSkill")
    assert any(point.load() is InspectSkill for point in points)
