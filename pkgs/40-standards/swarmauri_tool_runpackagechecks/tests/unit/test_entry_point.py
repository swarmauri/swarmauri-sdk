from importlib.metadata import entry_points

import pytest
from swarmauri_tool_runpackagechecks import RunPackageChecks


@pytest.mark.unit
def test_installed_entry_point():
    points = entry_points(group="swarmauri.tools", name="RunPackageChecks")
    assert any(point.load() is RunPackageChecks for point in points)
