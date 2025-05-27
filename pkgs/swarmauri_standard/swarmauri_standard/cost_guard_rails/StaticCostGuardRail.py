from __future__ import annotations

from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.cost_guard_rails.CostGuardRailBase import CostGuardRailBase


@ComponentBase.register_type(CostGuardRailBase, "StaticCostGuardRail")
class StaticCostGuardRail(CostGuardRailBase):
    """Cost guard rail with a static budget."""

    type: Literal["StaticCostGuardRail"] = "StaticCostGuardRail"
