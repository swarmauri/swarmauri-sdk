import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Literal

from pydantic import Field
from swarmauri_core.evaluators.IEvaluate import EvaluationError, IEvaluate
from swarmauri_core.programs.IProgram import IProgram as Program

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class EvaluatorBase(IEvaluate, ComponentBase):
    """
    Abstract base class implementing reusable logic for evaluation functions.

    This class provides template methods, logging, and a partial evaluation workflow
    that can be extended by concrete evaluator implementations. It handles common
    concerns like execution time tracking, exception handling, and score aggregation.
    """

    resource: Optional[str] = Field(default=ResourceTypes.EVALUATOR.value)
    type: Literal["EvaluatorBase"] = "EvaluatorBase"

    def evaluate(self, program: Program, **kwargs) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate a program and return a fitness score with metadata.

        This method wraps the concrete _compute_score implementation, capturing
        execution time and handling exceptions.

        Args:
            program: The program to evaluate
            **kwargs: Additional parameters for the evaluation process

        Returns:
            A tuple containing:
                - float: A scalar fitness score (higher is better)
                - Dict[str, Any]: Metadata about the evaluation, including feature dimensions

        Raises:
            EvaluationError: If the evaluation process fails
            TypeError: If the program is not of the expected type
        """
        if not isinstance(program, Program):
            raise TypeError(f"Expected Program type, got {type(program)}")

        start_time = time.time()

        try:
            # Call the concrete implementation to compute the score
            score, metadata = self._compute_score(program, **kwargs)

            # Add execution time to metadata
            execution_time = time.time() - start_time
            metadata["execution_time"] = execution_time

            logger.debug(
                f"Evaluation completed in {execution_time:.4f}s with score {score:.4f}"
            )
            return score, metadata

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Evaluation failed after {execution_time:.4f}s: {str(e)}")
            raise EvaluationError(f"Evaluation failed: {str(e)}") from e

    def _compute_score(
        self, program: Program, **kwargs
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Compute the evaluation score for a program.

        This is the main method to be implemented by concrete evaluator classes.

        Args:
            program: The program to evaluate
            **kwargs: Additional parameters for the evaluation process

        Returns:
            A tuple containing:
                - float: A scalar fitness score (higher is better)
                - Dict[str, Any]: Metadata about the evaluation

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("_compute_score must be implemented by subclasses")

    def aggregate_scores(
        self, scores: List[float], metadata_list: List[Dict[str, Any]]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Aggregate multiple evaluation scores and their metadata.

        This method provides a default implementation for aggregating scores from
        multiple evaluations, typically by averaging them.

        Args:
            scores: List of individual scores to aggregate
            metadata_list: List of metadata dictionaries corresponding to each score

        Returns:
            A tuple containing:
                - float: The aggregated score
                - Dict[str, Any]: Aggregated metadata
        """
        if not scores:
            return 0.0, {"error": "No scores to aggregate"}

        # Default aggregation is to average the scores
        aggregated_score = sum(scores) / len(scores)

        # Combine metadata
        aggregated_metadata = {
            "individual_scores": scores,
            "aggregation_method": "average",
            "score_count": len(scores),
        }

        # If all metadata dictionaries have the same keys, aggregate those values too
        if metadata_list:
            common_keys = set.intersection(
                *[set(meta.keys()) for meta in metadata_list]
            )
            for key in common_keys:
                # Skip keys that are not numeric or are already handled
                if key == "execution_time":
                    aggregated_metadata[key] = sum(meta[key] for meta in metadata_list)
                elif all(isinstance(meta[key], (int, float)) for meta in metadata_list):
                    aggregated_metadata[key] = sum(
                        meta[key] for meta in metadata_list
                    ) / len(metadata_list)

        return aggregated_score, aggregated_metadata

    def reset(self) -> None:
        """
        Reset the evaluator to its initial state.

        This method is called to clear any internal state or cached data
        before a new evaluation cycle begins.
        """
        # Reset logic can be implemented in subclasses if needed
        logger.debug("Resetting evaluator state")
        pass
