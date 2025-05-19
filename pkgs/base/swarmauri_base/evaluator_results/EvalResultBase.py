import logging
from typing import Any, ClassVar, Dict, Optional

from swarmauri_core.evaluator_results.IEvalResult import IEvalResult
from swarmauri_core.programs.IProgram import IProgram

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class EvalResultBase(IEvalResult, ComponentBase):
    """
    Abstract base class for evaluation results.

    This class provides reusable logic for packaging evaluation results including
    score storage, metadata handling, and serialization. It implements the IEvalResult
    interface with base functionality.

    Attributes
    ----------
    resource : Optional[str]
        Resource type identifier, defaults to EVALUATOR_RESULT
    _score : float
        Protected attribute storing the evaluation score
    _metadata : Dict[str, Any]
        Protected attribute storing evaluation metadata
    _program : IProgram
        Protected attribute storing the evaluated program
    _metadata_schema : ClassVar[Dict[str, Any]]
        Class variable defining the schema for valid metadata keys
    """

    resource: Optional[str] = ResourceTypes.EVALUATOR_RESULT.value

    # Class variable for metadata schema validation
    _metadata_schema: ClassVar[Dict[str, Any]] = {
        "type": "object",
        "properties": {
            # Define expected metadata properties here
            # This is a template and should be overridden by subclasses
        },
        "additionalProperties": True,  # Allow additional properties by default
    }

    def __init__(self, score: float, metadata: Dict[str, Any], program: IProgram):
        """
        Initialize a new evaluation result.

        Parameters
        ----------
        score : float
            The numerical evaluation score
        metadata : Dict[str, Any]
            Dictionary containing metadata about the evaluation
        program : IProgram
            The program that was evaluated
        """
        super().__init__()
        self._score = score
        self._program = program

        # Validate metadata against schema
        self._validate_metadata(metadata)
        self._metadata = metadata

        logger.debug(f"Created evaluation result with score: {score}")

    def _validate_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Validate metadata against the defined schema.

        Parameters
        ----------
        metadata : Dict[str, Any]
            The metadata to validate

        Raises
        ------
        ValueError
            If metadata doesn't conform to the schema
        """
        # This is a simple validation implementation
        # In a real implementation, consider using a library like jsonschema
        try:
            # Check if metadata is a dictionary
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary")

            # Additional validation logic would go here
            # This would typically involve checking against self._metadata_schema

            logger.debug("Metadata validation passed")
        except Exception as e:
            logger.error(f"Metadata validation failed: {str(e)}")
            raise ValueError(f"Invalid metadata format: {str(e)}")

    @property
    def score(self) -> float:
        """
        Get the evaluation score.

        Returns
        -------
        float
            The numerical score of the evaluation.
        """
        return self._score

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Get additional metadata about the evaluation.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing metadata about the evaluation.
        """
        return self._metadata

    @property
    def program(self) -> IProgram:
        """
        Get the program associated with this evaluation result.

        Returns
        -------
        IProgram
            The program that was evaluated.
        """
        return self._program
