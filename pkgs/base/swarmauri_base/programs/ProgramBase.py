import copy
import logging
from typing import ClassVar, Optional

from swarmauri_core.programs.IProgram import DiffType, IProgram

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class ProgramBase(IProgram, ComponentBase):
    """
    Abstract base class for program representation with serialization, diffing, and validation.

    This class provides reusable logic for program representation, implementing
    the core functionality required by the IProgram interface including serialization,
    diffing, validation, and diff application workflows.

    Attributes:
        _program_type: Class variable to store the program type identifier
    """

    _program_type: ClassVar[str] = "base"
    resource: Optional[str] = ResourceTypes.PROGRAM.value

    def clone(self) -> "IProgram":
        """
        Create a deep copy of this program.

        Returns:
            A new program instance with the same state
        """
        return copy.deepcopy(self)

    def diff(self, other: "IProgram") -> DiffType:
        """
        Calculate the difference between this program and another.

        Args:
            other: Another program to compare against

        Returns:
            A structured representation of the differences between programs

        Raises:
            TypeError: If the other program is not compatible for diffing
        """
        if not isinstance(other, IProgram):
            raise TypeError(f"Expected IProgram instance, got {type(other)}")

        # Log the diff operation for auditability
        logger.info(f"Computing diff between {self._program_type} programs")

        # This is a base implementation that should be overridden by subclasses
        # for more specific diff logic
        self_dict = self.model_dump()
        other_dict = other.model_dump()

        diff = {}

        # Identify removed keys
        for key in self_dict:
            if key not in other_dict:
                diff[key] = {"action": "remove"}

        # Identify added or modified keys
        for key, value in other_dict.items():
            if key not in self_dict:
                diff[key] = {"action": "add", "value": value}
            elif self_dict[key] != value:
                diff[key] = {"action": "modify", "value": value}

        logger.debug(f"Diff result: {diff}")
        return diff

    def apply_diff(self, diff: DiffType) -> "IProgram":
        """
        Apply a diff to this program to create a new modified program.

        Args:
            diff: The diff structure to apply to this program

        Returns:
            A new program instance with the diff applied

        Raises:
            ValueError: If the diff cannot be applied to this program
            TypeError: If the diff is not in the expected format
        """
        if not isinstance(diff, dict):
            raise TypeError(f"Expected dict for diff, got {type(diff)}")

        logger.info(f"Applying diff to {self._program_type} program")

        # Create a new program by cloning the current one
        new_program = self.clone()
        new_dict = new_program.model_dump()

        try:
            # Apply each diff operation
            for key, operation in diff.items():
                if not isinstance(operation, dict) or "action" not in operation:
                    raise ValueError(f"Invalid diff operation for key {key}")

                action = operation["action"]

                if action == "remove":
                    if key in new_dict:
                        del new_dict[key]
                elif action == "add" or action == "modify":
                    if "value" not in operation:
                        raise ValueError(
                            f"Missing 'value' for {action} operation on key {key}"
                        )
                    new_dict[key] = operation["value"]
                else:
                    raise ValueError(f"Unknown diff action '{action}' for key {key}")

            # Create a new program instance from the modified dictionary
            result = self.__class__.from_dict(new_dict)
            logger.debug("Diff applied successfully")
            return result

        except Exception as e:
            logger.error(f"Error applying diff: {e}")
            raise

    def validate(self) -> bool:
        """
        Validate that this program is well-formed and executable.

        This base implementation always returns True. Subclasses should override
        this method to implement specific validation logic.

        Returns:
            True if the program is valid, False otherwise
        """
        logger.info(f"Validating {self._program_type} program")
        # Base implementation doesn't implement specific validation
        # Subclasses should override this with actual validation logic
        return True
