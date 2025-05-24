from __future__ import annotations

import time
from typing import Literal, Optional

from pydantic import Field, PrivateAttr, ConfigDict

from swarmauri_core.cost_guard_rails.ICostGuardRail import ICostGuardRail
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class CostGuardRailBase(ICostGuardRail, ComponentBase):
    """Base class implementing common cost guard rail logic."""

    budget: float = 0.0
    reset_interval: Optional[float] = None

    _spent: float = PrivateAttr(0.0)
    _last_reset: float = PrivateAttr(default_factory=time.time)

    resource: Optional[str] = Field(default=ResourceTypes.COST_GUARD_RAIL.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["CostGuardRailBase"] = "CostGuardRailBase"

    def _maybe_reset(self) -> None:
        if self.reset_interval is None:
            return
        now = time.time()
        if now - self._last_reset >= self.reset_interval:
            self._spent = 0.0
            self._last_reset = now

    def allow(self, cost: float) -> bool:
        """Return whether the given cost is permitted."""
        self._maybe_reset()
        if self._spent + cost <= self.budget:
            self._spent += cost
            return True
        return False

    def remaining_budget(self) -> float:
        """Return the remaining budget."""
        self._maybe_reset()
        return max(0.0, self.budget - self._spent)

    def add_budget(self, amount: float) -> None:
        """Increase the available budget."""
        self.budget += amount
