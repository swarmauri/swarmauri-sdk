from importlib.metadata import entry_points

import pytest
from swarmauri_tool_listskills import ListSkills


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(group="swarmauri.tools", name="ListSkills")
    assert any(point.load() is ListSkills for point in points)
