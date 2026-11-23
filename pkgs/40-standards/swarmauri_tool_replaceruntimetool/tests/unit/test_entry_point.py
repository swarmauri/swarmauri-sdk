from importlib.metadata import entry_points

import pytest
from swarmauri_tool_replaceruntimetool import ReplaceRuntimeTool


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(group="swarmauri.tools", name="ReplaceRuntimeTool")
    assert any(point.load() is ReplaceRuntimeTool for point in points)
