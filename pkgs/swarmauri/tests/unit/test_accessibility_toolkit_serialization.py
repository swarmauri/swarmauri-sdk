from swarmauri.plugin_manager import discover_and_register_plugins
from swarmauri.toolkits.AccessibilityToolkit import AccessibilityToolkit
from swarmauri.tools.AutomatedReadabilityIndexTool import (
    AutomatedReadabilityIndexTool,
)
from swarmauri.tools.ColemanLiauIndexTool import ColemanLiauIndexTool
from swarmauri.tools.FleschKincaidTool import FleschKincaidTool
from swarmauri.tools.FleschReadingEaseTool import FleschReadingEaseTool
from swarmauri.tools.GunningFogTool import GunningFogTool


def test_accessibility_toolkit_serialization_roundtrip():
    discover_and_register_plugins()
    toolkit = AccessibilityToolkit()
    assert isinstance(
        toolkit.tools["AutomatedReadabilityIndexTool"], AutomatedReadabilityIndexTool
    )
    assert isinstance(toolkit.tools["ColemanLiauIndexTool"], ColemanLiauIndexTool)
    assert isinstance(toolkit.tools["FleschKincaidTool"], FleschKincaidTool)
    assert isinstance(toolkit.tools["FleschReadingEaseTool"], FleschReadingEaseTool)
    assert isinstance(toolkit.tools["GunningFogTool"], GunningFogTool)

    serialized = toolkit.model_dump_json()
    restored = AccessibilityToolkit.model_validate_json(serialized)
    assert isinstance(restored.tools["GunningFogTool"], GunningFogTool)
