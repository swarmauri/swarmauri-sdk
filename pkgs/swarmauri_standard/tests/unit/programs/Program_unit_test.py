from datetime import datetime
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from swarmauri_core.programs.IProgram import DiffType

from swarmauri_standard.programs.Program import Program


@pytest.fixture
def sample_program_data() -> Dict[str, Any]:
    """
    Fixture providing sample program data for testing.

    Returns:
        Dictionary containing sample program data
    """
    return {
        "type": "Program",
        "id": "test-id-123",
        "version": "1.0.0",
        "metadata": {
            "program_id": "test-id-123",
            "program_version": "1.0.0",
            "created_at": "2023-01-01T00:00:00",
        },
        "content": {"key1": "value1", "key2": "value2"},
    }


@pytest.fixture
def program(sample_program_data) -> Program:
    """
    Fixture providing a sample Program instance.

    Args:
        sample_program_data: Sample data fixture

    Returns:
        Program instance initialized with sample data
    """
    return Program(
        id=sample_program_data["id"],
        version=sample_program_data["version"],
        metadata=sample_program_data["metadata"],
        content=sample_program_data["content"],
    )


@pytest.mark.unit
def test_program_init_with_values():
    """Test Program initialization with provided values."""
    program_id = "test-id-123"
    version = "2.0.0"
    metadata = {"key": "value"}
    content = {"content_key": "content_value"}

    program = Program(
        id=program_id, version=version, metadata=metadata, content=content
    )

    assert program.id == program_id
    assert program.version == version
    assert "key" in program.metadata
    assert program.metadata["key"] == "value"
    assert program.metadata["program_id"] == program_id
    assert program.metadata["program_version"] == version
    assert "created_at" in program.metadata
    assert program.content == content


@pytest.mark.unit
def test_program_init_without_values():
    """Test Program initialization with default values."""
    with patch(
        "uuid.uuid4",
        return_value=MagicMock(hex="mock-uuid", __str__=lambda _: "mock-uuid"),
    ):
        program = Program()

        assert program.id == "mock-uuid"
        assert program.version == "1.0.0"
        assert isinstance(program.metadata, dict)
        assert isinstance(program.content, dict)
        assert program.metadata["program_id"] == "mock-uuid"
        assert program.metadata["program_version"] == "1.0.0"
        assert "created_at" in program.metadata


@pytest.mark.unit
def test_program_type():
    """Test that the program type is correctly set."""
    program = Program()
    assert program.type == "Program"
    assert Program._program_type == "standard"


@pytest.mark.unit
def test_diff(program):
    """Test the diff method."""
    other_program = Program(
        id=program.id,
        version=program.version,
        metadata=program.metadata.copy(),
        content={"key1": "changed", "key3": "new_value"},
    )

    diff = program.diff(other_program)

    assert isinstance(diff, dict)
    assert "content" in diff
    assert diff["content"]["key1"]["old"] == "value1"
    assert diff["content"]["key1"]["new"] == "changed"
    assert diff["content"]["key2"]["old"] == "value2"
    assert diff["content"]["key2"]["new"] is None
    assert diff["content"]["key3"]["old"] is None
    assert diff["content"]["key3"]["new"] == "new_value"


@pytest.mark.unit
def test_apply_diff(program):
    """Test applying a diff to create a new program."""
    diff: DiffType = {
        "content": {
            "key1": {"old": "value1", "new": "changed"},
            "key2": {"old": "value2", "new": None},
            "key3": {"old": None, "new": "new_value"},
        }
    }

    with patch("swarmauri_standard.programs.Program.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = datetime(2023, 1, 2)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        new_program = program.apply_diff(diff)

    assert new_program.id == program.id
    assert new_program.version == "1.0.1"  # Version incremented
    assert new_program.metadata["program_version"] == "1.0.1"
    assert new_program.metadata["updated_at"] == "2023-01-02T00:00:00"
    assert new_program.content == {"key1": "changed", "key3": "new_value"}


@pytest.mark.unit
def test_validate_valid_program(program):
    """Test validation of a valid program."""
    with patch("swarmauri_standard.programs.Program.logger") as mock_logger:
        result = program.validate()

        assert result is True
        mock_logger.info.assert_any_call(
            f"Validating standard program with ID {program.id}"
        )
        mock_logger.info.assert_any_call(f"Program {program.id} validation successful")


@pytest.mark.unit
def test_validate_invalid_program_id():
    """Test validation with invalid program ID in metadata."""
    program = Program(id="test-id")
    program.metadata["program_id"] = "different-id"

    with patch("swarmauri_standard.programs.Program.logger") as mock_logger:
        result = program.validate()

        assert result is False
        mock_logger.error.assert_called_with(
            "Program ID mismatch or missing in metadata"
        )


@pytest.mark.unit
def test_validate_invalid_program_version():
    """Test validation with invalid program version in metadata."""
    program = Program(id="test-id", version="1.0.0")
    program.metadata["program_version"] = "2.0.0"

    with patch("swarmauri_standard.programs.Program.logger") as mock_logger:
        result = program.validate()

        assert result is False
        mock_logger.error.assert_called_with(
            "Program version mismatch or missing in metadata"
        )


@pytest.mark.unit
def test_from_workspace_and_get_source_files(tmp_path):
    """Test creating a Program from a workspace directory."""
    file_path = tmp_path / "example.py"
    file_path.write_text("print('hello')")

    program = Program.from_workspace(tmp_path)

    assert "example.py" in program.content
    assert program.get_source_files()["example.py"] == "print('hello')"
