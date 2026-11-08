from importlib.metadata import entry_points

import pytest
from swarmauri_tool_readprocessoutput import ReadProcessOutputTool


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(
        group="swarmauri.tools", name="ReadProcessOutputTool"
    )
    assert any(point.load() is ReadProcessOutputTool for point in points)
