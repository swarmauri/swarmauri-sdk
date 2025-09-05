import logging
from typing import Any, ClassVar, Dict, Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.evaluator_results.EvalResultBase import EvalResultBase
from swarmauri_core.programs.IProgram import IProgram

logger = logging.getLogger(__name__)


@ComponentBase.register_type(EvalResultBase, "EvalResult")
class EvalResult(EvalResultBase):
    """
    Concrete implementation of EvalResultBase.

    This class holds a program reference, scalar score, and metadata.
    It provides a fully implemented evaluation result object.

    Attributes
    ----------
    type : Literal["EvalResult"]
        Type identifier for this component
    _score : float
        The numerical evaluation score
    _metadata : Dict[str, Any]
        Dictionary containing metadata about the evaluation
    _program : IProgram
        The program that was evaluated
    _metadata_schema : ClassVar[Dict[str, Any]]
        Schema for validating metadata structure
    """

    type: Literal["EvalResult"] = "EvalResult"

    # Extended metadata schema with specific validation requirements
    _metadata_schema: ClassVar[Dict[str, Any]] = {
        "type": "object",
        "properties": {
            # Define specific metadata properties here if needed
        },
        "additionalProperties": True,
    }

    def __init__(self, score: float, metadata: Dict[str, Any], program: IProgram):
        """
        Initialize a new evaluation result with score, metadata, and program.

        Parameters
        ----------
        score : float
            The numerical evaluation score
        metadata : Dict[str, Any]
            Dictionary containing metadata about the evaluation
        program : IProgram
            The program that was evaluated

        Raises
        ------
        TypeError
            If score is not a float or if metadata keys are not strings
        ValueError
            If program is None
        """
        # Validate score is a real number
        if not isinstance(score, (int, float)):
            logger.error(f"Score must be a number, got {type(score)}")
            raise TypeError(f"Score must be a number, got {type(score)}")

        # Validate program is not None
        if program is None:
            logger.error("Program cannot be None")
            raise ValueError("Program cannot be None")

        # Validate metadata keys are strings
        if not all(isinstance(key, str) for key in metadata.keys()):
            logger.error("All metadata keys must be strings")
            raise TypeError("All metadata keys must be strings")

        super().__init__(score, metadata, program)
        logger.debug(f"Created EvalResult with score {score} for program {program}")

    def _validate_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Validate metadata against the defined schema with additional checks.

        Parameters
        ----------
        metadata : Dict[str, Any]
            The metadata to validate

        Raises
        ------
        ValueError
            If metadata doesn't conform to the schema
        TypeError
            If metadata keys are not strings
        """
        # First perform basic validation from parent class
        # Check if metadata is a dictionary
        if not isinstance(metadata, dict):
            logger.error("Metadata validation failed: Metadata must be a dictionary")
            raise ValueError("Metadata must be a dictionary")

        # Ensure all keys are strings
        non_string_keys = [key for key in metadata.keys() if not isinstance(key, str)]
        if non_string_keys:
            logger.error(
                f"Metadata validation failed: All metadata keys must be strings. Found non-string keys: {non_string_keys}"
            )
            raise TypeError(
                f"All metadata keys must be strings. Found non-string keys: {non_string_keys}"
            )

        # Additional validation logic would go here
        logger.debug("Metadata validation passed")

    def update_metadata(self, new_metadata: Dict[str, Any]) -> None:
        """
        Update the evaluation result metadata with new values.

        Parameters
        ----------
        new_metadata : Dict[str, Any]
            New metadata to add or update

        Raises
        ------
        TypeError
            If new metadata keys are not strings
        """
        # Validate new metadata keys
        if not all(isinstance(key, str) for key in new_metadata.keys()):
            logger.error("All metadata keys must be strings")
            raise TypeError("All metadata keys must be strings")

        # Update metadata
        self._metadata.update(new_metadata)
        logger.debug(f"Updated metadata with {len(new_metadata)} new entries")

    def compare_to(self, other: "EvalResult") -> int:
        """
        Compare this evaluation result to another based on score.

        Parameters
        ----------
        other : EvalResult
            Another evaluation result to compare with

        Returns
        -------
        int
            1 if this result is better, -1 if other is better, 0 if equal

        Raises
        ------
        TypeError
            If other is not an EvalResult
        """
        if not isinstance(other, EvalResult):
            logger.error(f"Cannot compare EvalResult with {type(other)}")
            raise TypeError(f"Cannot compare EvalResult with {type(other)}")

        # Higher scores are better
        if self.score > other.score:
            return 1
        elif self.score < other.score:
            return -1
        else:
            return 0
