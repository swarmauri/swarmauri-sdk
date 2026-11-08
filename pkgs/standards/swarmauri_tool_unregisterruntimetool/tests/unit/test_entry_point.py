from importlib.metadata import entry_points

import pytest
from swarmauri_tool_unregisterruntimetool import UnregisterRuntimeTool


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(
        group="swarmauri.tools", name="UnregisterRuntimeTool"
    )
    assert any(point.load() is UnregisterRuntimeTool for point in points)
