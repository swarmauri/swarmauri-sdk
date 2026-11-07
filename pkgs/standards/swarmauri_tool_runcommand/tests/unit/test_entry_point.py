from importlib.metadata import entry_points

import pytest
from swarmauri_tool_runcommand import RunCommandTool


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(group="swarmauri.tools", name="RunCommandTool")
    assert any(point.load() is RunCommandTool for point in points)
