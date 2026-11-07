from importlib.metadata import entry_points

import pytest
from swarmauri_tool_listruntimetools import ListRuntimeTools


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(group="swarmauri.tools", name="ListRuntimeTools")
    assert any(point.load() is ListRuntimeTools for point in points)
