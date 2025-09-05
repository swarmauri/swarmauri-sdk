import time

from swarmauri.plugin_manager import discover_and_register_plugins


def test_plugin_import_time_under_one_second():
    discover_and_register_plugins()
    start = time.perf_counter()
    from swarmauri.toolkits.AccessibilityToolkit import AccessibilityToolkit  # noqa: F401
    from swarmauri.tools.AutomatedReadabilityIndexTool import (
        AutomatedReadabilityIndexTool,  # noqa: F401
    )
    from swarmauri.tools.GunningFogTool import GunningFogTool  # noqa: F401

    duration = time.perf_counter() - start
    assert duration < 1.0
