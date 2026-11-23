"""Verify facade discovery uses the standalone subprocess component."""

from importlib.metadata import EntryPoint

import pytest
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


@pytest.mark.unit
def test_subprocess_is_first_class() -> None:
    point = EntryPoint(
        name="SubprocessTool",
        value="swarmauri_tool_subprocess:SubprocessTool",
        group="swarmauri.tools",
    )
    assert PluginCitizenshipRegistry.is_first_class(point)
    assert (
        PluginCitizenshipRegistry.get_external_module_path(
            "swarmauri.tools.SubprocessTool"
        )
        == "swarmauri_tool_subprocess.SubprocessTool"
    )
