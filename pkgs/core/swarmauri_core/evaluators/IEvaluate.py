from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from swarmauri_core.programs.IProgram import IProgram


class EvaluationError(Exception):
    """
    Exception raised when an evaluator encounters an error during evaluation.

    This exception should be raised when an evaluator fails to properly evaluate
    a program due to issues such as invalid program structure, execution errors,
    or other exceptional conditions.
    """

    pass


class IEvaluate(ABC):
    """
    Interface for program evaluation functions.

    This abstract class defines the contract that all evaluators must implement,
    providing methods to assess program fitness according to specific criteria.
    Evaluators must be stateless to allow for parallel execution.
    """

    @abstractmethod
    def evaluate(self, program: IProgram, **kwargs) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate a program and return a fitness score with metadata.

        This method assesses the fitness of a program according to specific criteria
        and returns both a scalar score and detailed metadata about the evaluation.

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
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Reset the evaluator to its initial state.

        This method should clear any internal state or cached data to ensure
        that the evaluator is ready for a new evaluation cycle.
        """
        pass
