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


# Type variable for the program type
P = TypeVar("P", bound=IProgram)


@ComponentBase.register_model()
class EvaluatorPoolBase(IEvaluatorPool, ComponentBase):
    """
    Abstract base class implementing thread-safe registry, dispatch, and result aggregation
    for evaluator pools.
    """

    resource: Optional[str] = ResourceTypes.EVALUATOR_POOL.value

    # Define private fields with exclude=True to keep them out of serialization
    evaluators: Dict[str, IEvaluate] = Field(default_factory=dict, exclude=True)
    lock: Any = Field(default=None, exclude=True)
    executor: Any = Field(default=None, exclude=True)
    aggregation_func: Any = Field(
        default=None,
        exclude=True,
    )

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def __init__(self, **kwargs: Any):
        """Initialize the pool evaluator base with empty evaluator registry and default settings."""
        super().__init__(**kwargs)
        # Initialize with the renamed fields (no leading underscore)
        self.evaluators = {}
        self.lock = threading.RLock()
        self.executor = None
        self.aggregation_func = (
            lambda scores: sum(scores) / len(scores) if scores else 0.0
        )

    def initialize(self) -> None:
        """
        Initialize the evaluator pool and its resources.

        Creates a thread pool executor for parallel evaluation tasks.

        Raises:
            RuntimeError: If initialization fails
        """
        try:
            self._executor = futures.ThreadPoolExecutor(max_workers=10)
            logger.info("Initialized PoolEvaluatorBase with thread pool executor")
        except Exception as e:
            logger.error(f"Failed to initialize PoolEvaluatorBase: {e}")
            raise RuntimeError(f"Failed to initialize evaluator pool: {e}")

    def shutdown(self) -> None:
        """
        Shut down the evaluator pool and release its resources.

        Shuts down the thread pool executor and clears evaluator registry.

        Raises:
            RuntimeError: If shutdown fails
        """
        try:
            if self._executor:
                self._executor.shutdown(wait=True)
                self._executor = None

            with self._lock:
                self._evaluators.clear()

            logger.info("Shut down PoolEvaluatorBase")
        except Exception as e:
            logger.error(f"Failed to shut down PoolEvaluatorBase: {e}")
            raise RuntimeError(f"Failed to shut down evaluator pool: {e}")

    def add_evaluator(self, evaluator: IEvaluate, name: Optional[str] = None) -> str:
        """
        Add an evaluator to the pool.

        Args:
            evaluator: The evaluator to add to the pool
            name: Optional name for the evaluator, if not provided a name will be generated

        Returns:
            The name assigned to the evaluator

        Raises:
            ValueError: If an evaluator with the same name already exists
            TypeError: If the evaluator doesn't implement IEvaluate
        """
        if not isinstance(evaluator, IEvaluate):
            logger.error(
                f"Attempted to add non-IEvaluate object to pool: {type(evaluator)}"
            )
            raise TypeError("Evaluator must implement IEvaluate interface")

        if name is None:
            name = f"evaluator_{len(self._evaluators) + 1}"

        with self._lock:
            if name in self._evaluators:
                logger.error(f"Evaluator with name '{name}' already exists in pool")
                raise ValueError(f"Evaluator with name '{name}' already exists")

            self._evaluators[name] = evaluator
            logger.info(f"Added evaluator '{name}' to pool")

        return name

    def remove_evaluator(self, name: str) -> bool:
        """
        Remove an evaluator from the pool by name.

        Args:
            name: The name of the evaluator to remove

        Returns:
            True if the evaluator was removed, False if it wasn't found
        """
        with self._lock:
            if name in self._evaluators:
                del self._evaluators[name]
                logger.info(f"Removed evaluator '{name}' from pool")
                return True

            logger.warning(f"Attempted to remove non-existent evaluator '{name}'")
            return False

    def evaluate(self, programs: Sequence[P], **kwargs) -> Sequence[IEvalResult]:
        """
        Evaluate all programs with all registered evaluators.

        This method runs each program through each evaluator and collects the results.

        Args:
            programs: The programs to evaluate
            **kwargs: Additional parameters to pass to evaluators

        Returns:
            A sequence of evaluation results, one for each program

        Raises:
            RuntimeError: If evaluation fails
        """
        try:
            # Pre-process programs
            processed_programs = self.pre_process(programs)

            # Dispatch evaluation tasks
            results = self._dispatch(processed_programs)

            # Post-process results
            final_results = self.post_process(results)

            return final_results
        except Exception as e:
            logger.error(f"Error in evaluate: {e}")
            raise RuntimeError(f"Failed to evaluate programs: {e}")

    async def evaluate_async(
        self, programs: Sequence[P], **kwargs
    ) -> Sequence[IEvalResult]:
        """
        Asynchronously evaluate all programs with all registered evaluators.

        This method runs each program through each evaluator concurrently and collects the results.

        Args:
            programs: The programs to evaluate
            **kwargs: Additional parameters to pass to evaluators

        Returns:
            A sequence of evaluation results, one for each program

        Raises:
            RuntimeError: If evaluation fails
        """
        try:
            # Create a function that runs evaluate in a separate thread
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._executor, partial(self.evaluate, programs, **kwargs)
            )
            return result
        except Exception as e:
            logger.error(f"Error in evaluate_async: {e}")
            raise RuntimeError(f"Failed to evaluate programs asynchronously: {e}")

    def aggregate(self, scores: Sequence[float]) -> float:
        """
        Aggregate multiple scores into a single score.

        This method combines multiple evaluation scores into a single scalar value
        according to the pool's aggregation strategy.

        Args:
            scores: The scores to aggregate

        Returns:
            The aggregated score

        Raises:
            ValueError: If scores is empty or contains invalid values
        """
        if not scores:
            logger.warning("Attempted to aggregate empty scores list")
            raise ValueError("Cannot aggregate empty scores list")

        try:
            return self._aggregation_func(scores)
        except Exception as e:
            logger.error(f"Error in score aggregation: {e}")
            raise ValueError(f"Failed to aggregate scores: {e}")

    def set_aggregation_function(
        self, func: Callable[[Sequence[float]], float]
    ) -> None:
        """
        Set the function used to aggregate scores.

        Args:
            func: A function that takes a sequence of scores and returns an aggregated score

        Raises:
            TypeError: If func is not callable or has an invalid signature
        """
        if not callable(func):
            logger.error("Attempted to set non-callable aggregation function")
            raise TypeError("Aggregation function must be callable")

        # Simple test to verify function signature
        try:
            test_result = func([0.5, 0.7])
            if not isinstance(test_result, (int, float)):
                raise TypeError("Aggregation function must return a numeric value")
        except Exception as e:
            logger.error(f"Invalid aggregation function: {e}")
            raise TypeError(f"Invalid aggregation function: {e}")

        self._aggregation_func = func
        logger.info("Set new aggregation function")

    def get_evaluator(self, name: str) -> Optional[IEvaluate]:
        """
        Get an evaluator by name.

        Args:
            name: The name of the evaluator to retrieve

        Returns:
            The evaluator if found, None otherwise
        """
        with self._lock:
            return self._evaluators.get(name)

    def get_evaluator_names(self) -> List[str]:
        """
        Get the names of all registered evaluators.

        Returns:
            A list of evaluator names
        """
        with self._lock:
            return list(self._evaluators.keys())

    def get_evaluator_count(self) -> int:
        """
        Get the number of registered evaluators.

        Returns:
            The count of evaluators in the pool
        """
        with self._lock:
            return len(self._evaluators)

    def _dispatch(self, programs: Sequence[P]) -> Sequence[IEvalResult]:
        """
        Dispatch programs to all evaluators and collect results.

        This internal method handles the actual execution of evaluators against programs.
        It's implemented to use the thread pool executor for parallel evaluation.

        Args:
            programs: The programs to evaluate

        Returns:
            A sequence of evaluation results

        Raises:
            RuntimeError: If dispatch fails
        """
        results = []

        with self._lock:
            evaluator_items = list(self._evaluators.items())

        if not evaluator_items:
            logger.warning("No evaluators registered, returning empty results")
            # Create empty results for each program
            return [self._create_eval_result(p, {}, {}) for p in programs]

        for program in programs:
            scores = {}
            metadata = {}

            # Create a list of futures for parallel execution
            future_to_evaluator = {}
            for name, evaluator in evaluator_items:
                future = self._executor.submit(evaluator.evaluate, program)
                future_to_evaluator[future] = name

            # Collect results as they complete
            for future in futures.as_completed(future_to_evaluator):
                name = future_to_evaluator[future]
                try:
                    result = future.result()
                    if isinstance(result, IEvalResult):
                        scores[name] = result.score
                        metadata[name] = result.metadata
                    else:
                        # Handle legacy evaluators that return dicts
                        scores[name] = result.get("score", 0.0)
                        metadata[name] = result.get("metadata", {})
                except Exception as e:
                    logger.error(f"Evaluator '{name}' failed: {e}")
                    scores[name] = 0.0
                    metadata[name] = {"error": str(e)}

            # Calculate aggregate score
            aggregate_score = self.aggregate(list(scores.values())) if scores else 0.0

            # Create and add the result
            aggregated_metadata = {
                "evaluator_results": metadata,
                "aggregate_score": aggregate_score,
            }
            result = self._create_eval_result(program, scores, aggregated_metadata)
            results.append(result)

        return results

    def _create_eval_result(
        self, program: IProgram, scores: Dict[str, float], metadata: Dict[str, Any]
    ) -> IEvalResult:
        """
        Create an evaluation result object.

        This method creates an IEvalResult implementation with the provided data.

        Args:
            program: The program that was evaluated
            scores: Dictionary mapping evaluator names to their scores
            metadata: Additional metadata about the evaluation

        Returns:
            An IEvalResult implementation
        """
        # Calculate aggregate score
        aggregate_score = self.aggregate(list(scores.values())) if scores else 0.0

        # Create a new result with the EvalResultBase implementation
        result = EvalResultBase(
            program=program,
            score=aggregate_score,
            metadata={
                "evaluator_scores": scores,
                "evaluator_metadata": metadata,
                "aggregate_score": aggregate_score,
            },
        )

        return result

    def pre_process(self, programs: Sequence[P]) -> Sequence[P]:
        """
        Pre-process programs before evaluation.

        This hook allows subclasses to transform or filter programs before they're evaluated.
        The default implementation returns the programs unchanged.

        Args:
            programs: The programs to pre-process

        Returns:
            The processed programs
        """
        return programs

    def post_process(self, results: Sequence[IEvalResult]) -> Sequence[IEvalResult]:
        """
        Post-process evaluation results.

        This hook allows subclasses to transform or filter results after evaluation.
        The default implementation returns the results unchanged.

        Args:
            results: The evaluation results to post-process

        Returns:
            The processed results
        """
        return results
