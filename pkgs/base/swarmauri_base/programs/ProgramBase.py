import json
import logging
import copy
from typing import Dict, Any, Optional, ClassVar

from swarmauri_core.programs.IProgram import IProgram, DiffType

logger = logging.getLogger(__name__)


class ProgramBase(IProgram):
    """
    Abstract base class for program representation with serialization, diffing, and validation.
    
    This class provides reusable logic for program representation, implementing
    the core functionality required by the IProgram interface including serialization,
    diffing, validation, and diff application workflows.
    
    Attributes:
        _program_type: Class variable to store the program type identifier
    """
    
    _program_type: ClassVar[str] = "base"
    
    def __init__(self):
        """Initialize a new program base instance."""
        super().__init__()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the program to a dictionary representation.
        
        Returns:
            A dictionary representing the program state
        """
        raise NotImplementedError("Subclasses must implement to_dict()")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IProgram':
        """
        Create a program instance from a dictionary representation.
        
        Args:
            data: Dictionary containing the program state
            
        Returns:
            A new program instance
            
        Raises:
            ValueError: If the dictionary cannot be parsed into a valid program
        """
        raise NotImplementedError("Subclasses must implement from_dict()")
    
    def clone(self) -> 'IProgram':
        """
        Create a deep copy of this program.
        
        Returns:
            A new program instance with the same state
        """
        return copy.deepcopy(self)
    
    def serialize(self) -> str:
        """
        Serialize the program to a JSON string.
        
        Returns:
            A JSON string representing the program
        """
        try:
            # Convert the program to a dictionary and then to JSON
            program_dict = self.to_dict()
            return json.dumps(program_dict, indent=2)
        except Exception as e:
            logger.error(f"Error serializing program: {e}")
            raise
    
    @classmethod
    def deserialize(cls, serialized: str) -> 'IProgram':
        """
        Deserialize a JSON string to a program instance.
        
        Args:
            serialized: JSON string representation of a program
            
        Returns:
            A program instance
            
        Raises:
            ValueError: If the JSON string cannot be parsed into a valid program
        """
        try:
            data = json.loads(serialized)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            logger.error(f"Error deserializing program: Invalid JSON format: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Error deserializing program: {e}")
            raise
    
    def diff(self, other: 'IProgram') -> DiffType:
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
        self_dict = self.to_dict()
        other_dict = other.to_dict()
        
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
    
    def apply_diff(self, diff: DiffType) -> 'IProgram':
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
        new_dict = new_program.to_dict()
        
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
                        raise ValueError(f"Missing 'value' for {action} operation on key {key}")
                    new_dict[key] = operation["value"]
                else:
                    raise ValueError(f"Unknown diff action '{action}' for key {key}")
            
            # Create a new program instance from the modified dictionary
            result = self.__class__.from_dict(new_dict)
            logger.debug(f"Diff applied successfully")
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