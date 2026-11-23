from importlib.metadata import entry_points

import pytest
from swarmauri_tool_cancelprocess import CancelProcessTool


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(group="swarmauri.tools", name="CancelProcessTool")
    assert any(point.load() is CancelProcessTool for point in points)
