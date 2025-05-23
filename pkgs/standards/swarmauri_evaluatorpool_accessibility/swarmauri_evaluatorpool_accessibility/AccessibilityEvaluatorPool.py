import logging
import importlib
import inspect
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.evaluator_pools.EvaluatorPoolBase import EvaluatorPoolBase
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase

from swarmauri_standard.programs.Program import Program

logger = logging.getLogger(__name__)


@ComponentBase.register_type(EvaluatorPoolBase, "AccessibilityEvaluatorPool")
class AccessibilityEvaluatorPool(EvaluatorPoolBase):
    """
    Evaluator pool that runs a suite of accessibility and readability evaluators
    across a Program.

    This pool iterates through all files in a Program and invokes each of the
    Accessibility & Readability evaluators, then aggregates a combined score.
    """

    type: Literal["AccessibilityEvaluatorPool"] = "AccessibilityEvaluatorPool"

    def __init__(
        self,
        evaluators: Optional[List[EvaluatorBase]] = None,
        weights: Optional[Dict[str, float]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the AccessibilityEvaluatorPool.

        Parameters
        ----------
        evaluators : Optional[List[EvaluatorBase]]
            List of accessibility and readability evaluators to use
        weights : Optional[Dict[str, float]]
            Dictionary mapping evaluator names to their weights for score aggregation
        **kwargs : Any
            Additional keyword arguments
        """
        super().__init__(**kwargs)
        self.evaluators = evaluators if evaluators is not None else []
        self.weights = weights or {}

        if evaluators is None and not self.evaluators:
            self._auto_register_evaluators()

        # Validate that all evaluators are properly initialized
        for evaluator in self.evaluators:
            if not isinstance(evaluator, EvaluatorBase):
                raise TypeError(
                    f"Expected EvaluatorBase instance, got {type(evaluator)}"
                )

        logger.info(
            f"Initialized AccessibilityEvaluatorPool with {len(self.evaluators)} evaluators"
        )

    def _auto_register_evaluators(self) -> None:
        """Instantiate and register all evaluators defined in this package."""
        try:
            package = importlib.import_module(__package__)
            for name in getattr(package, "__all__", []):
                if name == "AccessibilityEvaluatorPool":
                    continue
                obj = getattr(package, name, None)
                if inspect.isclass(obj) and issubclass(obj, EvaluatorBase):
                    try:
                        evaluator = obj()
                        self.evaluators.append(evaluator)
                        self.weights.setdefault(obj.__name__, 1.0)
                    except Exception as e:  # pragma: no cover - best effort
                        logger.warning(f"Failed to instantiate evaluator {name}: {e}")
        except Exception as e:  # pragma: no cover - best effort
            logger.warning(f"Failed automatic evaluator registration: {e}")

    def evaluate(self, program: Program) -> Dict[str, Any]:
        """
        Evaluate accessibility and readability across all files in a program.

        Parameters
        ----------
        program : Program
            The program to evaluate

        Returns
        -------
        Dict[str, Any]
            Evaluation results containing:
            - overall_score: float between 0 and 1
            - evaluator_scores: Dict mapping evaluator names to their individual scores
            - file_scores: Dict mapping file paths to their individual scores
        """
        logger.info("Starting accessibility evaluation on program")

        if not self.evaluators:
            logger.warning("No evaluators configured, returning empty result")
            return {"overall_score": 0.0, "evaluator_scores": {}, "file_scores": {}}

        # Track scores by evaluator and by file
        evaluator_scores: Dict[str, float] = {}
        file_scores: Dict[str, float] = {}

        # Get all source files from the program
        source_files = program.get_source_files()

        # Process each file in the program
        for file_path, file_content in source_files.items():
            file_score = self._evaluate_file(file_path, file_content)
            file_scores[str(file_path)] = file_score

        # Calculate scores for each evaluator across all files
        for evaluator in self.evaluators:
            evaluator_name = evaluator.__class__.__name__
            evaluator_result = evaluator.aggregate_results()
            evaluator_scores[evaluator_name] = evaluator_result.get("score", 0.0)

        # Calculate overall weighted score
        overall_score = self._calculate_overall_score(evaluator_scores)

        result = {
            "overall_score": overall_score,
            "evaluator_scores": evaluator_scores,
            "file_scores": file_scores,
        }

        logger.info(
            f"Completed accessibility evaluation with overall score: {overall_score:.2f}"
        )
        return result

    def _evaluate_file(self, file_path: str, file_content: str) -> float:
        """
        Evaluate a single file using all configured evaluators.

        Parameters
        ----------
        file_path : str
            Path to the file to evaluate
        file_content : str
            Content of the file to evaluate

        Returns
        -------
        float
            The average score for this file across all evaluators
        """
        logger.debug(f"Evaluating accessibility for file: {file_path}")

        # Skip files that shouldn't be evaluated for accessibility
        if not self._should_evaluate_file(file_path, file_content):
            logger.debug(
                f"Skipping file {file_path} as it's not suitable for accessibility evaluation"
            )
            return 0.0

        file_scores = []

        # Run each evaluator on this file
        for evaluator in self.evaluators:
            try:
                # Update evaluate_file call to use file_path and file_content
                result = evaluator.evaluate_file(file_path, file_content)
                score = result.get("score", 0.0)
                file_scores.append(score)
                logger.debug(
                    f"Evaluator {evaluator.__class__.__name__} gave score {score:.2f} for {file_path}"
                )
            except Exception as e:
                logger.error(
                    f"Error evaluating {file_path} with {evaluator.__class__.__name__}: {str(e)}"
                )
                file_scores.append(0.0)

        # Calculate average score for this file
        if file_scores:
            avg_score = sum(file_scores) / len(file_scores)
            logger.debug(
                f"Average accessibility score for {file_path}: {avg_score:.2f}"
            )
            return avg_score
        return 0.0

    def _should_evaluate_file(self, file_path: str, file_content: str) -> bool:
        """
        Determine if a file should be evaluated for accessibility.

        Parameters
        ----------
        file_path : str
            Path to the file to check
        file_content : str
            Content of the file to check

        Returns
        -------
        bool
            True if the file should be evaluated, False otherwise
        """
        # Skip empty files
        if not file_content:
            return False

        # Skip files that are too large (might cause performance issues)
        if len(file_content) > 1_000_000:  # 1MB limit
            logger.warning(
                f"File {file_path} exceeds size limit for accessibility evaluation"
            )
            return False

        # Skip file types that don't make sense for accessibility evaluation
        excluded_extensions = {
            ".bin",
            ".pyc",
            ".pyo",
            ".so",
            ".dll",
            ".exe",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".ico",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".zip",
            ".tar",
            ".gz",
            ".rar",
        }

        file_ext = Path(file_path).suffix.lower()
        if file_ext in excluded_extensions:
            return False

        return True

    def _calculate_overall_score(self, evaluator_scores: Dict[str, float]) -> float:
        """
        Calculate the overall weighted score based on individual evaluator scores.

        Parameters
        ----------
        evaluator_scores : Dict[str, float]
            Dictionary mapping evaluator names to their scores

        Returns
        -------
        float
            The overall weighted score between 0 and 1
        """
        if not evaluator_scores:
            return 0.0

        total_weight = 0.0
        weighted_sum = 0.0

        for evaluator_name, score in evaluator_scores.items():
            # Get weight for this evaluator, default to 1.0 if not specified
            weight = self.weights.get(evaluator_name, 1.0)
            weighted_sum += score * weight
            total_weight += weight

        # Avoid division by zero
        if total_weight == 0.0:
            return 0.0

        # Ensure the result is between 0 and 1
        overall_score = min(1.0, max(0.0, weighted_sum / total_weight))
        return overall_score

    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the evaluator pool with the provided configuration.

        Parameters
        ----------
        config : Dict[str, Any]
            Configuration dictionary which may include:
            - evaluators: List of evaluator configurations
            - weights: Dictionary mapping evaluator names to their weights
        """
        logger.info("Configuring AccessibilityEvaluatorPool")

        if "weights" in config:
            self.weights = config["weights"]
            logger.debug(f"Updated evaluator weights: {self.weights}")

        # Other configuration options can be added here

    def add_evaluator(self, evaluator: EvaluatorBase, weight: float = 1.0) -> None:
        """
        Add an evaluator to the pool with an optional weight.

        Parameters
        ----------
        evaluator : EvaluatorBase
            The evaluator to add
        weight : float, default=1.0
            The weight to assign to this evaluator
        """
        if not isinstance(evaluator, EvaluatorBase):
            raise TypeError(f"Expected EvaluatorBase instance, got {type(evaluator)}")

        self.evaluators.append(evaluator)
        evaluator_name = evaluator.__class__.__name__
        self.weights[evaluator_name] = weight
        logger.info(f"Added evaluator {evaluator_name} with weight {weight}")

    def remove_evaluator(self, evaluator_name: str) -> bool:
        """
        Remove an evaluator from the pool by name.

        Parameters
        ----------
        evaluator_name : str
            The name of the evaluator class to remove

        Returns
        -------
        bool
            True if an evaluator was removed, False otherwise
        """
        for i, evaluator in enumerate(self.evaluators):
            if evaluator.__class__.__name__ == evaluator_name:
                self.evaluators.pop(i)
                self.weights.pop(evaluator_name, None)
                logger.info(f"Removed evaluator {evaluator_name}")
                return True

        logger.warning(f"No evaluator found with name {evaluator_name}")
        return False

    def reset(self) -> None:
        """
        Reset the evaluator pool, clearing any cached results.
        """
        logger.info("Resetting AccessibilityEvaluatorPool")

        # Reset each evaluator
        for evaluator in self.evaluators:
            evaluator.reset()
