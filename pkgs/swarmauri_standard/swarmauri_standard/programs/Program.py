from typing import Dict, Any, Literal, Optional, ClassVar
import logging
import uuid
from datetime import datetime

from swarmauri_core.programs.IProgram import IProgram, DiffType
from swarmauri_base.programs.ProgramBase import ProgramBase

logger = logging.getLogger(__name__)


class Program(ProgramBase):
    """
    Concrete implementation of ProgramBase providing an immutable program object.
    
    This class implements the abstract methods defined in ProgramBase and provides
    functionality for serialization, diffing, and validation of program objects.
    
    Attributes:
        type: The literal type identifier for this program class
        id: Unique identifier for the program instance
        version: Version information for the program
        metadata: Additional metadata associated with the program
        content: The actual program content
    """
    
    _program_type: ClassVar[str] = "standard"
    type: Literal["Program"] = "Program"
    
    def __init__(
        self,
        id: Optional[str] = None,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new Program instance.
        
        Args:
            id: Unique identifier for the program, auto-generated if not provided
            version: Version information, defaults to "1.0.0" if not provided
            metadata: Additional metadata for the program
            content: The actual program content
        """
        super().__init__()
        self.id = id if id else str(uuid.uuid4())
        self.version = version if version else "1.0.0"
        self.metadata = metadata if metadata else {}
        self.content = content if content else {}
        
        # Ensure program ID and version are included in metadata
        if "program_id" not in self.metadata:
            self.metadata["program_id"] = self.id
        if "program_version" not in self.metadata:
            self.metadata["program_version"] = self.version
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the program to a dictionary representation.
        
        Returns:
            A dictionary representing the program state
        """
        return {
            "type": self.type,
            "id": self.id,
            "version": self.version,
            "metadata": self.metadata,
            "content": self.content
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Program':
        """
        Create a program instance from a dictionary representation.
        
        Args:
            data: Dictionary containing the program state
            
        Returns:
            A new program instance
            
        Raises:
            ValueError: If the dictionary cannot be parsed into a valid program
        """
        # Validate the required fields
        required_fields = ["id", "version", "metadata", "content"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field '{field}' in program data")
        
        # Validate type if present
        if "type" in data and data["type"] != "Program":
            raise ValueError(f"Expected program type 'Program', got '{data['type']}'")
        
        # Create and return a new Program instance
        return cls(
            id=data["id"],
            version=data["version"],
            metadata=data["metadata"],
            content=data["content"]
        )
    
    def diff(self, other: IProgram) -> DiffType:
        """
        Calculate the difference between this program and another.
        
        This implementation uses the default diff logic from ProgramBase.
        
        Args:
            other: Another program to compare against
            
        Returns:
            A structured representation of the differences between programs
            
        Raises:
            TypeError: If the other program is not compatible for diffing
        """
        return super().diff(other)
    
    def apply_diff(self, diff: DiffType) -> 'Program':
        """
        Apply a diff to this program to create a new modified program.
        
        This implementation uses the default apply_diff logic from ProgramBase.
        
        Args:
            diff: The diff structure to apply to this program
            
        Returns:
            A new program instance with the diff applied
            
        Raises:
            ValueError: If the diff cannot be applied to this program
            TypeError: If the diff is not in the expected format
        """
        result = super().apply_diff(diff)
        
        # Update the version number to indicate a change
        if isinstance(result, Program):
            # Simple version increment - in a production system, this would follow
            # semantic versioning rules based on the nature of the changes
            version_parts = result.version.split('.')
            if len(version_parts) >= 3:
                version_parts[-1] = str(int(version_parts[-1]) + 1)
                result.version = '.'.join(version_parts)
                result.metadata["program_version"] = result.version
                result.metadata["updated_at"] = datetime.utcnow().isoformat()
        
        return result
    
    def validate(self) -> bool:
        """
        Validate that this program is well-formed and executable.
        
        This implementation performs basic validation checks on the program structure.
        
        Returns:
            True if the program is valid, False otherwise
        """
        logger.info(f"Validating {self._program_type} program with ID {self.id}")
        
        # Check for required metadata
        if "program_id" not in self.metadata or self.metadata["program_id"] != self.id:
            logger.error("Program ID mismatch or missing in metadata")
            return False
        
        if "program_version" not in self.metadata or self.metadata["program_version"] != self.version:
            logger.error("Program version mismatch or missing in metadata")
            return False
        
        # Additional validation could be implemented here based on specific requirements
        # For example, validating the structure of the content, checking for required fields, etc.
        
        logger.info(f"Program {self.id} validation successful")
        return True