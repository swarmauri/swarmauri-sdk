from importlib.metadata import entry_points

import pytest
from swarmauri_tool_inspectruntimetool import InspectRuntimeTool


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(group="swarmauri.tools", name="InspectRuntimeTool")
    assert any(point.load() is InspectRuntimeTool for point in points)
