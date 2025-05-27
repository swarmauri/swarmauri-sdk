import asyncio
import logging
import threading
from concurrent import futures
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Sequence, TypeVar

from pydantic import Field
from swarmauri_core.evaluator_pools.IEvaluatorPool import IEvaluatorPool
from swarmauri_core.evaluator_results.IEvalResult import IEvalResult
from swarmauri_core.evaluators.IEvaluate import IEvaluate
from swarmauri_core.programs.IProgram import IProgram

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.evaluator_results.EvalResultBase import EvalResultBase

logger = logging.getLogger(__name__)
P = TypeVar("P", bound=IProgram)


@ComponentBase.register_model()
class EvaluatorPoolBase(IEvaluatorPool, ComponentBase):
    """
    Thread-safe evaluator-pool base class with registry, dispatch and aggregation.
    """

    resource: Optional[str] = ResourceTypes.EVALUATOR_POOL.value

    # ── runtime-only attributes (excluded from pydantic serialisation) ──────────
    evaluators: Dict[str, IEvaluate] = Field(default_factory=dict)
    lock: Any = Field(default=None, exclude=True)
    executor: Any = Field(default=None, exclude=True)
    aggregation_func: Any = Field(default=None, exclude=True)

    model_config = {"arbitrary_types_allowed": True}

    # ────────────────────────────────────────────────────────────────────────────
    # life-cycle
    # ────────────────────────────────────────────────────────────────────────────
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.evaluators = {}
        self.lock = threading.RLock()
        self.executor = None
        self.aggregation_func = (
            lambda scores: sum(scores) / len(scores) if scores else 0.0
        )

    def initialize(self) -> None:
        try:
            self.executor = futures.ThreadPoolExecutor(max_workers=10)
            logger.info("EvaluatorPool initialised with thread-pool executor")
        except Exception as e:
            logger.exception("Initialisation failed")
            raise RuntimeError(f"Failed to initialise evaluator pool: {e}") from e

    def shutdown(self) -> None:
        try:
            if self.executor:
                self.executor.shutdown(wait=True)
                self.executor = None
            with self.lock:
                self.evaluators.clear()
            logger.info("EvaluatorPool shut down")
        except Exception as e:
            logger.exception("Shutdown failed")
            raise RuntimeError(f"Failed to shut down evaluator pool: {e}") from e

    # ────────────────────────────────────────────────────────────────────────────
    # registry ops
    # ────────────────────────────────────────────────────────────────────────────
    def add_evaluator(self, evaluator: IEvaluate, name: Optional[str] = None) -> str:
        if not isinstance(evaluator, IEvaluate):
            raise TypeError("Evaluator must implement IEvaluate")

        name = name or f"evaluator_{len(self.evaluators) + 1}"
        with self.lock:
            if name in self.evaluators:
                raise ValueError(f"Evaluator '{name}' already exists")
            self.evaluators[name] = evaluator
        logger.debug("Added evaluator '%s'", name)
        return name

    def remove_evaluator(self, name: str) -> bool:
        with self.lock:
            removed = self.evaluators.pop(name, None) is not None
        if removed:
            logger.debug("Removed evaluator '%s'", name)
        return removed

    def get_evaluator(self, name: str) -> Optional[IEvaluate]:
        with self.lock:
            return self.evaluators.get(name)

    def get_evaluator_names(self) -> List[str]:
        with self.lock:
            return list(self.evaluators.keys())

    def get_evaluator_count(self) -> int:
        with self.lock:
            return len(self.evaluators)

    # ────────────────────────────────────────────────────────────────────────────
    # evaluation API
    # ────────────────────────────────────────────────────────────────────────────
    def evaluate(self, programs: Sequence[P], **kwargs) -> Sequence[IEvalResult]:
        try:
            processed = self.pre_process(programs)
            results = self._dispatch(processed)
            return self.post_process(results)
        except Exception as e:
            logger.exception("evaluate() failed")
            raise RuntimeError(f"Failed to evaluate programs: {e}") from e

    async def evaluate_async(
        self, programs: Sequence[P], **kwargs
    ) -> Sequence[IEvalResult]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, partial(self.evaluate, programs, **kwargs)
        )

    def _dispatch(self, programs: Sequence[P]) -> Sequence[IEvalResult]:
        if not self.evaluators:
            return [self._create_eval_result(p, {}, {}) for p in programs]

        results: List[IEvalResult] = []
        for program in programs:
            scores: Dict[str, float] = {}
            metadata: Dict[str, Any] = {}

            futures_map = {
                self.executor.submit(evaluator.evaluate, program): name
                for name, evaluator in self.evaluators.items()
            }

            for future in futures.as_completed(futures_map):
                name = futures_map[future]
                try:
                    res = future.result()
                    if isinstance(res, IEvalResult):
                        scores[name] = res.score
                        metadata[name] = res.metadata
                    else:  # legacy dict result
                        scores[name] = res.get("score", 0.0)
                        metadata[name] = res.get("metadata", {})
                except Exception as e:
                    logger.error("Evaluator '%s' failed: %s", name, e)
                    scores[name] = 0.0
                    metadata[name] = {"error": str(e)}

            agg_score = self.aggregate(scores.values()) if scores else 0.0
            results.append(
                self._create_eval_result(
                    program,
                    scores,
                    {"evaluator_metadata": metadata, "aggregate_score": agg_score},
                )
            )
        return results

    # ────────────────────────────────────────────────────────────────────────────
    # aggregation
    # ────────────────────────────────────────────────────────────────────────────
    def aggregate(self, scores: Sequence[float]) -> float:
        if not scores:
            raise ValueError("Cannot aggregate an empty score list")
        return self.aggregation_func(list(scores))

    def set_aggregation_function(
        self, func: Callable[[Sequence[float]], float]
    ) -> None:
        if not callable(func):
            raise TypeError("Aggregation function must be callable")
        # sanity-check signature
        result = func([0.5, 0.5])
        if not isinstance(result, (int, float)):
            raise TypeError("Aggregation function must return a numeric value")
        self.aggregation_func = func

    # ────────────────────────────────────────────────────────────────────────────
    # result helpers / hooks
    # ────────────────────────────────────────────────────────────────────────────
    def _create_eval_result(
        self, program: IProgram, scores: Dict[str, float], metadata: Dict[str, Any]
    ) -> IEvalResult:
        agg_score = self.aggregate(scores.values()) if scores else 0.0
        return EvalResultBase(
            program=program,
            score=agg_score,
            metadata={"evaluator_scores": scores, **metadata},
        )

    def pre_process(self, programs: Sequence[P]) -> Sequence[P]:
        return programs

    def post_process(self, results: Sequence[IEvalResult]) -> Sequence[IEvalResult]:
        return results
