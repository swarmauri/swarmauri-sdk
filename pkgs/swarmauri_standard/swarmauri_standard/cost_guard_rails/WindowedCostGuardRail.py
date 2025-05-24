from __future__ import annotations

from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.cost_guard_rails.CostGuardRailBase import CostGuardRailBase


@ComponentBase.register_type(CostGuardRailBase, "WindowedCostGuardRail")
class WindowedCostGuardRail(CostGuardRailBase):
    """Cost guard rail that resets after a time window."""

    type: Literal["WindowedCostGuardRail"] = "WindowedCostGuardRail"

    def __init__(self, *, reset_interval: float, **data):
        super().__init__(reset_interval=reset_interval, **data)
