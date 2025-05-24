import time
import pytest

from swarmauri_base.ComponentBase import ResourceTypes
from swarmauri_standard.cost_guard_rails.StaticCostGuardRail import StaticCostGuardRail
from swarmauri_standard.cost_guard_rails.WindowedCostGuardRail import WindowedCostGuardRail


@pytest.fixture
def static_guard():
    return StaticCostGuardRail(budget=10)


@pytest.fixture
def windowed_guard():
    return WindowedCostGuardRail(budget=5, reset_interval=0.5)


@pytest.mark.unit
def test_resource(static_guard):
    assert static_guard.resource == ResourceTypes.COST_GUARD_RAIL.value


@pytest.mark.unit
def test_types(static_guard, windowed_guard):
    assert static_guard.type == "StaticCostGuardRail"
    assert windowed_guard.type == "WindowedCostGuardRail"


@pytest.mark.unit
def test_allow(static_guard):
    assert static_guard.allow(3)
    assert not static_guard.allow(8)


@pytest.mark.unit
def test_window_reset(windowed_guard):
    assert windowed_guard.allow(5)
    assert not windowed_guard.allow(1)
    time.sleep(0.6)
    assert windowed_guard.allow(5)

