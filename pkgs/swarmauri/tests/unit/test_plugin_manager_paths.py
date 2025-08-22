import time
from importlib.metadata import EntryPoint

import pytest

from swarmauri.plugin_manager import PluginLoadError, process_plugin


def test_process_plugin_happy_path():
    """Processing a real plugin succeeds."""
    valid_ep = EntryPoint(
        name="CalculatorTool",
        value="swarmauri_standard.tools.calculator_tool:CalculatorTool",
        group="swarmauri.tools",
    )
    assert process_plugin(valid_ep)


def test_process_plugin_worst_case_path_performance():
    """Failing plugins raise errors quickly (<100ms)."""
    bad_ep = EntryPoint(
        name="missing", value="nonexistent.module:obj", group="swarmauri.agents"
    )
    start = time.perf_counter()
    with pytest.raises(PluginLoadError):
        process_plugin(bad_ep)
    duration = time.perf_counter() - start
    assert duration < 0.1
