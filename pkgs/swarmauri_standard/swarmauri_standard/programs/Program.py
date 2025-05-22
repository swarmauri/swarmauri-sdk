import copy
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, Dict, Literal, Optional

from swarmauri_base.programs.ProgramBase import ProgramBase
from swarmauri_core.programs.IProgram import DiffType, IProgram

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
    model_config = {}

    def __init__(
        self,
        id: Optional[str] = None,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content: Optional[Dict[str, Any]] = None,
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

    def diff(self, other: IProgram) -> DiffType:
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

        logger.info(f"Computing diff between {self._program_type} programs")

        diff = {}

        # Compare content fields
        if hasattr(self, "content") and hasattr(other, "content"):
            content_diff = {}
            other_content = getattr(other, "content", {})

            # Find modified and removed keys
            for key, value in self.content.items():
                if key not in other_content:
                    content_diff[key] = {"old": value, "new": None}
                elif other_content[key] != value:
                    content_diff[key] = {"old": value, "new": other_content[key]}

            # Find added keys
            for key, value in other_content.items():
                if key not in self.content:
                    content_diff[key] = {"old": None, "new": value}

            if content_diff:
                diff["content"] = content_diff

        return diff

    def apply_diff(self, diff: DiffType) -> "Program":
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
        new_program = Program(
            id=self.id,
            version=self.version,
            metadata=copy.deepcopy(self.metadata),
            content=copy.deepcopy(self.content),
        )

        # Apply changes to content
        if "content" in diff and hasattr(new_program, "content"):
            content_diff = diff["content"]
            new_content = dict(new_program.content)

            for key, change in content_diff.items():
                if not isinstance(change, dict) or "new" not in change:
                    raise ValueError(f"Invalid diff format for key {key}")

                # Add or modify
                if change.get("new") is not None:
                    new_content[key] = change["new"]
                # Remove
                elif key in new_content:
                    del new_content[key]

            new_program.content = new_content

        # Update the version number to indicate a change
        version_parts = new_program.version.split(".")
        if len(version_parts) >= 3:
            version_parts[-1] = str(int(version_parts[-1]) + 1)
            new_program.version = ".".join(version_parts)
            new_program.metadata["program_version"] = new_program.version
            new_program.metadata["updated_at"] = datetime.utcnow().isoformat()

        return new_program

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

        if (
            "program_version" not in self.metadata
            or self.metadata["program_version"] != self.version
        ):
            logger.error("Program version mismatch or missing in metadata")
            return False

        # Additional validation could be implemented here based on specific requirements
        # For example, validating the structure of the content, checking for required fields, etc.

        logger.info(f"Program {self.id} validation successful")
        return True

    # ------------------------------------------------------------------
    @classmethod
    def from_workspace(cls, root: Path) -> "Program":
        """Create a program from all source files in *root*.

        Args:
            root (Path): Workspace directory containing source files.

        Returns:
            Program: Instance populated with file contents.
        """
        root = root.resolve()
        content: Dict[str, str] = {}
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".txt", ".md"}:
                rel = path.relative_to(root)
                content[str(rel)] = path.read_text(encoding="utf-8")

        return cls(content=content)

    def get_source_files(self) -> Dict[str, str]:
        """Return program source files keyed by relative path."""
        return self.content
