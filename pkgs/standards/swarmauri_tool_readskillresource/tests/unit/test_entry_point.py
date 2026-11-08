from importlib.metadata import entry_points

import pytest
from swarmauri_tool_readskillresource import ReadSkillResource


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(group="swarmauri.tools", name="ReadSkillResource")
    assert any(point.load() is ReadSkillResource for point in points)
