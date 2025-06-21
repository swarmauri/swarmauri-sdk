from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple, Literal

from peagen.plugin_manager import resolve_plugin_spec
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_core.ComponentBase import ComponentBase
from swarmauri_core.programs.IProgram import IProgram as Program


@ComponentBase.register_model()
class CompositeEvaluator(EvaluatorBase):
    """Combine multiple evaluators with optional weights."""

    type: Literal["CompositeEvaluator"] = "CompositeEvaluator"

    def __init__(
        self,
        evaluators: Sequence[Any],
        weights: Sequence[float] | None = None,
        **data: Any,
    ) -> None:
        super().__init__(**data)
        self.evaluator_refs = list(evaluators)
        self.weights = (
            list(weights) if weights is not None else [1.0] * len(self.evaluator_refs)
        )
        self.sub_evaluators: List[EvaluatorBase] = []
        for ev in self.evaluator_refs:
            if isinstance(ev, str):
                cls = resolve_plugin_spec("evaluators", ev)
                self.sub_evaluators.append(cls())
            elif isinstance(ev, type) and issubclass(ev, EvaluatorBase):
                self.sub_evaluators.append(ev())
            elif isinstance(ev, EvaluatorBase):
                self.sub_evaluators.append(ev)
            else:
                raise TypeError(f"Invalid evaluator reference: {ev!r}")
        if len(self.weights) < len(self.sub_evaluators):
            self.weights.extend([1.0] * (len(self.sub_evaluators) - len(self.weights)))

    def _compute_score(
        self, program: Program, **kwargs: Any
    ) -> Tuple[float, Dict[str, Any]]:
        scores: List[float] = []
        metadata: List[Dict[str, Any]] = []
        for ev in self.sub_evaluators:
            s, m = ev.evaluate(program, **kwargs)
            scores.append(s)
            metadata.append(m)
        total_w = sum(self.weights) or 1.0
        weighted = sum(s * w for s, w in zip(scores, self.weights)) / total_w
        meta = {"scores": scores, "weights": self.weights, "sub_metadata": metadata}
        return weighted, meta
