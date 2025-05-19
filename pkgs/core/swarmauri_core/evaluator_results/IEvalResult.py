from abc import ABC, abstractmethod
from typing import Any, Dict

from swarmauri_core.programs.IProgram import IProgram


class IEvalResult(ABC):
    """
    Interface for evaluation results.

    This interface defines the contract for evaluation results, requiring
    accessors for score, metadata, and linkage to a program.
    """

    @property
    @abstractmethod
    def score(self) -> float:
        """
        Get the evaluation score.

        Returns
        -------
        float
            The numerical score of the evaluation.
        """
        pass

    @property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """
        Get additional metadata about the evaluation.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing metadata about the evaluation.
        """
        pass

    @property
    @abstractmethod
    def program(self) -> IProgram:
        """
        Get the program associated with this evaluation result.

        Returns
        -------
        IProgram
            The program that was evaluated.
        """
        pass
