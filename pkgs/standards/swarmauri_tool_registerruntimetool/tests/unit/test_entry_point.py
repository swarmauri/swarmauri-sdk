from importlib.metadata import entry_points

import pytest
from swarmauri_tool_registerruntimetool import RegisterRuntimeTool


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(group="swarmauri.tools", name="RegisterRuntimeTool")
    assert any(point.load() is RegisterRuntimeTool for point in points)
