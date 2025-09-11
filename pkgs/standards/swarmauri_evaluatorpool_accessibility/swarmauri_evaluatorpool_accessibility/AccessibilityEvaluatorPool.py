# File: swarmauri_standard/evaluator_pools/AccessibilityEvaluatorPool.py
from __future__ import annotations

from typing import Any, Dict, List, Literal, Sequence

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.evaluator_pools.EvaluatorPoolBase import EvaluatorPoolBase
from swarmauri_core.evaluators.IEvaluate import IEvaluate

# ─────────────────────────────────────────────────────────────────────────────
# bring the default evaluators into scope
# adjust the import paths if your project lays them out differently
# ─────────────────────────────────────────────────────────────────────────────
from . import (  # noqa: E402
    AutomatedReadabilityIndexEvaluator,
    ColemanLiauIndexEvaluator,
    FleschKincaidGradeEvaluator,
    FleschReadingEaseEvaluator,
    GunningFogEvaluator,
)


@ComponentBase.register_type(EvaluatorPoolBase, "AccessibilityEvaluatorPool")
class AccessibilityEvaluatorPool(EvaluatorPoolBase):
    """
    Pool that aggregates classic readability / accessibility metrics.

    Every contained evaluator **must** satisfy the `IEvaluate` interface:
        • evaluate(program: IProgram, **kw) -> tuple[float, dict]
        • reset() -> None

    The pool itself follows the contracts defined by `EvaluatorPoolBase`
    (thread-safe registry, concurrent dispatch, aggregation hook, etc.).
    """

    type: Literal["AccessibilityEvaluatorPool"] = "AccessibilityEvaluatorPool"

    # ------------------------------------------------------------------ #
    # construction
    # ------------------------------------------------------------------ #
    def __init__(
        self,
        evaluators: Sequence[IEvaluate] | None = None,
        weights: Dict[str, float] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        # The pool’s registry is a Dict[str, IEvaluate] coming from the base-class
        self.weights: Dict[str, float] = weights or {}

        # ------------------------------------------------------------------ #
        # 1) caller supplied evaluators           → honoured as-is
        # 2) no evaluators supplied (None / empty) → register built-ins
        # ------------------------------------------------------------------ #
        if evaluators:
            for ev in evaluators:
                self.add_evaluator(ev, ev.__class__.__name__)
        else:
            self._register_builtin_evaluators()

        # custom aggregation that flips “lower-is-better” metrics
        self.set_aggregation_function(self._accessibility_aggregation)

        if self.logger:
            self.logger.info(
                "AccessibilityEvaluatorPool initialised with %d evaluators",
                self.get_evaluator_count(),
            )

    # ------------------------------------------------------------------ #
    # built-in evaluator registration
    # ------------------------------------------------------------------ #
    _BUILTINS: List[type[IEvaluate]] = [
        AutomatedReadabilityIndexEvaluator,
        ColemanLiauIndexEvaluator,
        FleschKincaidGradeEvaluator,
        FleschReadingEaseEvaluator,
        GunningFogEvaluator,
    ]

    def _register_builtin_evaluators(self) -> None:
        for cls in self._BUILTINS:
            try:
                inst = cls()
                self.add_evaluator(inst, cls.__name__)
                # default weight = 1 unless already provided
                self.weights.setdefault(cls.__name__, 1.0)
            except Exception as exc:  # pragma: no cover
                if self.logger:
                    self.logger.error("Failed to instantiate %s: %s", cls.__name__, exc)

    # ------------------------------------------------------------------ #
    # evaluation – we just rely on the base-class dispatcher
    # ------------------------------------------------------------------ #
    # Nothing to override here; EvaluatorPoolBase will:
    #   • spin up a ThreadPoolExecutor
    #   • fan-out evaluate() calls
    #   • gather (score, metadata) tuples
    #   • call self.aggregate() on the individual scores
    #   • wrap the result in an `EvalResultBase` instance

    # ------------------------------------------------------------------ #
    # aggregation helper – unify score direction, apply weights
    # ------------------------------------------------------------------ #
    def _accessibility_aggregation(self, raw_scores: Sequence[float]) -> float:
        """
        Convert individual evaluator scores to a 0–1 scale where “higher is
        better” and return a weighted mean.

        * FleschReadingEase already gives “higher == easier” → scale to 0-1.
        * All other metrics are “grade-level” indices (lower == easier) → invert.
        """
        names = self.get_evaluator_names()
        if not names:
            return 0.0

        total, total_weight = 0.0, 0.0
        for name, score in zip(names, raw_scores):
            # normalise & clamp
            if name == "FleschReadingEaseEvaluator":
                norm = max(0.0, min(1.0, score / 100.0))
            else:
                norm = max(0.0, min(1.0, 1.0 - (score / 20.0)))  # 0-20 -> 1-0
            w = self.weights.get(name, 1.0)
            total += norm * w
            total_weight += w

        return 0.0 if total_weight == 0 else total / total_weight
