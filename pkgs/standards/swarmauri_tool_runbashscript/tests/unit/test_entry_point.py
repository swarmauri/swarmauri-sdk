from importlib.metadata import entry_points

import pytest
from swarmauri_tool_runbashscript import RunBashScriptTool


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(group="swarmauri.tools", name="RunBashScriptTool")
    assert any(point.load() is RunBashScriptTool for point in points)
