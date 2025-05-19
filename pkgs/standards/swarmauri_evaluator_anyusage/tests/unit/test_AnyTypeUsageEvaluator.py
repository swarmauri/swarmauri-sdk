import os
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import pytest
from swarmauri_evaluator_anyusage.AnyTypeUsageEvaluator import AnyTypeUsageEvaluator


@pytest.fixture
def evaluator():
    """
    Fixture that provides an instance of AnyTypeUsageEvaluator.

    Returns:
        AnyTypeUsageEvaluator: An instance of the evaluator
    """
    return AnyTypeUsageEvaluator()


@pytest.fixture
def mock_program():
    """
    Fixture that provides a mock program object.

    Returns:
        MagicMock: A mock program object with necessary attributes
    """
    program = MagicMock()
    program.name = "test_program"
    program.path = "/path/to/program"
    return program


@pytest.mark.unit
def test_initialization():
    """Test the initialization of AnyTypeUsageEvaluator with default values."""
    evaluator = AnyTypeUsageEvaluator()
    assert evaluator.type == "AnyTypeUsageEvaluator"
    assert evaluator.penalty_per_occurrence == 0.1
    assert evaluator.max_penalty == 1.0


@pytest.mark.unit
def test_initialization_with_custom_values():
    """Test the initialization of AnyTypeUsageEvaluator with custom values."""
    evaluator = AnyTypeUsageEvaluator(penalty_per_occurrence=0.2, max_penalty=0.5)
    assert evaluator.type == "AnyTypeUsageEvaluator"
    assert evaluator.penalty_per_occurrence == 0.2
    assert evaluator.max_penalty == 0.5


@pytest.mark.unit
def test_get_python_files(evaluator, mock_program):
    """Test the _get_python_files method to ensure it finds Python files."""
    with patch("os.walk") as mock_walk:
        mock_walk.return_value = [
            ("/path/to/program", ["dir1"], ["file1.py", "file2.txt"]),
            ("/path/to/program/dir1", [], ["file3.py", "file4.md"]),
        ]

        files = evaluator._get_python_files(mock_program)

        assert len(files) == 2
        assert "/path/to/program/file1.py" in files
        assert "/path/to/program/dir1/file3.py" in files
        assert "/path/to/program/file2.txt" not in files
        assert "/path/to/program/dir1/file4.md" not in files


@pytest.mark.unit
def test_get_python_files_no_path(evaluator):
    """Test the _get_python_files method when program.path is not available."""
    program = MagicMock()
    program.path = None

    with patch("os.walk") as mock_walk, patch("os.getcwd") as mock_getcwd:
        mock_getcwd.return_value = "/current/dir"
        mock_walk.return_value = [("/current/dir", [], ["file1.py"])]

        files = evaluator._get_python_files(program)

        mock_getcwd.assert_called_once()
        assert len(files) == 1
        assert "/current/dir/file1.py" in files


@pytest.mark.unit
def test_analyze_file_for_any_with_ast(evaluator):
    """Test the _analyze_file_for_any method with AST parsing."""
    file_content = """
from typing import Any, List

def func(param: Any) -> Any:
    x: Any = 123
    return x

class MyClass:
    attr: List[Any] = []
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name

    try:
        occurrences = evaluator._analyze_file_for_any(temp_file_path)

        # We expect to find at least 5 occurrences of Any
        assert len(occurrences) >= 5

        # Check that we have line numbers and context for each occurrence
        for occurrence in occurrences:
            assert "line" in occurrence
            assert "context" in occurrence
            assert isinstance(occurrence["line"], int)
            assert isinstance(occurrence["context"], str)
    finally:
        os.unlink(temp_file_path)


@pytest.mark.unit
def test_analyze_file_for_any_with_regex(evaluator):
    """Test the _analyze_file_for_any method with regex fallback."""
    file_content = """
# This file has a syntax error
from typing import Any, List

def func(param: Any) -> Any:
    x: Any = 123
    return x

class MyClass:
    attr: List[Any] = []
    
# Syntax error below
if True
    print("missing colon")
"""

    with (
        patch("ast.parse", side_effect=SyntaxError("invalid syntax")),
        patch("builtins.open", mock_open(read_data=file_content)),
    ):
        occurrences = evaluator._analyze_file_for_any("dummy_path.py")

        # We should still find occurrences with regex even with syntax error
        assert len(occurrences) > 0

        # Check that we have line numbers and context for each occurrence
        for occurrence in occurrences:
            assert "line" in occurrence
            assert "context" in occurrence


@pytest.mark.unit
def test_analyze_file_for_any_file_error(evaluator):
    """Test the _analyze_file_for_any method when file cannot be opened."""
    with patch("builtins.open", side_effect=IOError("File not found")):
        occurrences = evaluator._analyze_file_for_any("nonexistent_file.py")
        assert len(occurrences) == 0


@pytest.mark.unit
@pytest.mark.parametrize(
    "num_occurrences,expected_score",
    [
        (0, 1.0),  # No Any usage -> perfect score
        (5, 0.5),  # 5 occurrences with 0.1 penalty each -> 0.5 penalty
        (15, 0.0),  # 15 occurrences with 0.1 penalty each -> max penalty (1.0)
    ],
)
def test_compute_score(evaluator, mock_program, num_occurrences, expected_score):
    """Test the _compute_score method with different numbers of Any occurrences."""
    # Mock the methods to control the test
    with (
        patch.object(evaluator, "_get_python_files") as mock_get_files,
        patch.object(evaluator, "_analyze_file_for_any") as mock_analyze,
    ):
        mock_get_files.return_value = ["file1.py", "file2.py"]

        if num_occurrences == 0:
            # No occurrences in any file
            mock_analyze.return_value = []
        else:
            # Distribute occurrences across files
            occurrences_per_file = num_occurrences // 2
            mock_analyze.side_effect = [
                [
                    {"line": i, "context": f"context {i}"}
                    for i in range(1, occurrences_per_file + 1)
                ],
                [
                    {"line": i, "context": f"context {i}"}
                    for i in range(1, num_occurrences - occurrences_per_file + 1)
                ],
            ]

        score, metadata = evaluator._compute_score(mock_program)

        assert score == expected_score
        assert metadata["total_any_occurrences"] == num_occurrences
        assert "detailed_occurrences" in metadata
        assert "penalty_applied" in metadata
        assert "files_analyzed" in metadata
        assert metadata["files_analyzed"] == 2


@pytest.mark.unit
def test_compute_score_custom_penalties(mock_program):
    """Test the _compute_score method with custom penalty settings."""
    evaluator = AnyTypeUsageEvaluator(penalty_per_occurrence=0.2, max_penalty=0.6)

    # Mock the methods to control the test
    with (
        patch.object(evaluator, "_get_python_files") as mock_get_files,
        patch.object(evaluator, "_analyze_file_for_any") as mock_analyze,
    ):
        mock_get_files.return_value = ["file1.py"]

        # 4 occurrences with 0.2 penalty each = 0.8 total, but max is 0.6
        mock_analyze.return_value = [
            {"line": i, "context": f"context {i}"} for i in range(1, 5)
        ]

        score, metadata = evaluator._compute_score(mock_program)

        assert score == 0.4  # 1.0 - 0.6 (capped at max_penalty)
        assert metadata["total_any_occurrences"] == 4
        assert metadata["penalty_applied"] == 0.6


@pytest.mark.unit
def test_serialization(evaluator):
    """Test serialization and deserialization of the evaluator."""
    # Serialize to JSON
    json_data = evaluator.model_dump_json()

    # Deserialize from JSON
    deserialized = AnyTypeUsageEvaluator.model_validate_json(json_data)

    # Check that the deserialized object has the same attributes
    assert deserialized.type == evaluator.type
    assert deserialized.penalty_per_occurrence == evaluator.penalty_per_occurrence
    assert deserialized.max_penalty == evaluator.max_penalty
