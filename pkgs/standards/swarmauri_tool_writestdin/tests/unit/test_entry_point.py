from importlib.metadata import entry_points

import pytest
from swarmauri_tool_writestdin import WriteStdinTool


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(group="swarmauri.tools", name="WriteStdinTool")
    assert any(point.load() is WriteStdinTool for point in points)
