# File: swarmauri_standard/evaluator_pools/AccessibilityEvaluatorPool.py
from __future__ import annotations

from typing import Any, Dict, List, Literal, Sequence

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.evaluator_pools.EvaluatorPoolBase import EvaluatorPoolBase
from swarmauri_core.evaluators.IEvaluate import IEvaluate
from swarmauri_standard.programs.Program import Program

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

    class _EvaluatorRegistry(dict):
        """Dict-like registry that iterates over values for legacy callers."""

        def __iter__(self):
            return iter(self.values())

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
        self.evaluators = self._EvaluatorRegistry()
        self._allow_add = True

        # The pool’s registry is a Dict[str, IEvaluate] coming from the base-class
        self.weights: Dict[str, float] = weights or {}

        # ------------------------------------------------------------------ #
        # 1) caller supplied evaluators           → honoured as-is
        # 2) no evaluators supplied (None / empty) → register built-ins
        # ------------------------------------------------------------------ #
        if evaluators is not None:
            for ev in evaluators:
                self._register_evaluator_internal(ev, ev.__class__.__name__)
        else:
            self._register_builtin_evaluators()

        # custom aggregation that flips “lower-is-better” metrics
        self.set_aggregation_function(self._accessibility_aggregation)
        self._allow_add = False

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
                self._register_evaluator_internal(inst, cls.__name__)
                # default weight = 1 unless already provided
                self.weights.setdefault(cls.__name__, 1.0)
            except Exception as exc:  # pragma: no cover
                if self.logger:
                    self.logger.error("Failed to instantiate %s: %s", cls.__name__, exc)

    def _register_evaluator_internal(self, evaluator: IEvaluate, name: str) -> None:
        super().add_evaluator(evaluator, name)

    def add_evaluator(self, evaluator: IEvaluate, name: Any = None) -> str:  # type: ignore[override]
        """Legacy behavior: disallow runtime add after initialization."""
        if not self._allow_add:
            raise RuntimeError(
                "AccessibilityEvaluatorPool manages evaluator registration internally"
            )
        if not isinstance(name, str) and name is not None:
            name = evaluator.__class__.__name__
        return super().add_evaluator(evaluator, name)

    def remove_evaluator(self, name: str) -> bool:
        removed = super().remove_evaluator(name)
        if removed:
            self.weights.pop(name, None)
        return removed

    def reset(self) -> None:
        for evaluator in self.evaluators.values():
            if hasattr(evaluator, "reset"):
                evaluator.reset()

    def configure(self, config: Dict[str, Any]) -> None:
        if "weights" in config and isinstance(config["weights"], dict):
            self.weights = dict(config["weights"])

    def _should_evaluate_file(self, file_path: str, content: Any) -> bool:
        if not content:
            return False
        ext = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
        return ext in {"py", "txt", "md", "html", "htm", "rst"}

    def _evaluate_file(self, file_path: str, file_content: Any) -> float:
        if not self._should_evaluate_file(file_path, file_content):
            return 0.0
        scores: list[float] = []
        for evaluator in self.evaluators.values():
            evaluate_file = getattr(evaluator, "evaluate_file", None)
            if not callable(evaluate_file):
                continue
            try:
                result = evaluate_file(file_path, file_content)
                if isinstance(result, dict):
                    scores.append(float(result.get("score", 0.0)))
                else:
                    scores.append(float(result))
            except Exception:
                scores.append(0.0)
        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        if not scores:
            return 0.0
        total, total_weight = 0.0, 0.0
        for name, score in scores.items():
            score_f = float(score)
            if name == "FleschReadingEaseEvaluator":
                norm = max(0.0, min(1.0, score_f / 100.0))
            else:
                norm = max(0.0, min(1.0, 1.0 - score_f))
            weight = float(self.weights.get(name, 1.0))
            total += norm * weight
            total_weight += weight
        return 0.0 if total_weight == 0.0 else total / total_weight

    def _legacy_evaluate(self, program: Program) -> Dict[str, Any]:
        source_files = (
            program.get_source_files() if hasattr(program, "get_source_files") else {}
        )
        file_scores = {
            path: self._evaluate_file(path, content)
            for path, content in source_files.items()
            if self._should_evaluate_file(path, content)
        }

        evaluator_scores: Dict[str, float] = {}
        for name, evaluator in self.evaluators.items():
            agg = getattr(evaluator, "aggregate_results", None)
            if callable(agg):
                try:
                    result = agg(file_scores)
                    evaluator_scores[name] = float(result.get("score", 0.0))
                except Exception:
                    evaluator_scores[name] = 0.0
            else:
                evaluator_scores[name] = 0.0

        overall = (
            sum(evaluator_scores.values()) / len(evaluator_scores)
            if evaluator_scores
            else 0.0
        )
        return {
            "overall_score": overall,
            "evaluator_scores": evaluator_scores,
            "file_scores": file_scores,
        }

    def evaluate(self, programs: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        # Backward-compatible single-program mode used in unit tests.
        if not isinstance(programs, Sequence) or isinstance(programs, (str, bytes)):
            return self._legacy_evaluate(programs)
        return super().evaluate(programs, **kwargs)

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
