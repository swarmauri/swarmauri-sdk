import pytest
import tempfile
import os
from unittest.mock import MagicMock

from swarmauri_evaluator_externalimports.ExternalImportsEvaluator import (
    ExternalImportsEvaluator,
)
from swarmauri_core.programs.IProgram import IProgram


@pytest.fixture
def evaluator():
    """
    Fixture that returns an instance of ExternalImportsEvaluator.

    Returns:
        ExternalImportsEvaluator: A new instance of the evaluator.
    """
    return ExternalImportsEvaluator()


@pytest.fixture
def mock_program():
    """
    Fixture that creates a mock program with a temporary directory.

    Returns:
        MagicMock: A mock program object with a path attribute.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        program = MagicMock(spec=IProgram)
        program.path = temp_dir
        yield program


@pytest.mark.unit
def test_evaluator_initialization(evaluator):
    """
    Test that the evaluator initializes correctly.

    Args:
        evaluator: The evaluator fixture.
    """
    assert evaluator.type == "ExternalImportsEvaluator"
    assert isinstance(evaluator.standard_modules, set)
    assert len(evaluator.standard_modules) > 0


@pytest.mark.unit
def test_is_standard_module(evaluator):
    """
    Test the _is_standard_module method.

    Args:
        evaluator: The evaluator fixture.
    """
    # Standard library modules should return True
    assert evaluator._is_standard_module("os")
    assert evaluator._is_standard_module("sys")
    assert evaluator._is_standard_module("json")
    assert evaluator._is_standard_module("logging")

    # Non-standard modules should return False
    assert not evaluator._is_standard_module("pandas")
    assert not evaluator._is_standard_module("tensorflow")
    assert not evaluator._is_standard_module("nonexistent_module")


@pytest.mark.unit
def test_extract_imports():
    """Test the _extract_imports method with various import patterns."""
    evaluator = ExternalImportsEvaluator()

    # Create a temporary Python file with imports
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w+", delete=False
    ) as temp_file:
        temp_file.write("""
import os
import sys as system
from datetime import datetime
from collections import defaultdict as dd
import pandas as pd
from tensorflow import keras
from nonexistent_module import something
""")
        temp_file_path = temp_file.name

    try:
        imports = evaluator._extract_imports(temp_file_path)

        # Check that all imports were detected
        assert len(imports) == 7

        # Check specific imports
        import_modules = {imp["module"] for imp in imports}
        assert "os" in import_modules
        assert "sys" in import_modules
        assert "datetime.datetime" in import_modules
        assert "collections.defaultdict" in import_modules
        assert "pandas" in import_modules
        assert "tensorflow.keras" in import_modules
        assert "nonexistent_module.something" in import_modules

        # Check standard library detection
        standard_imports = [imp for imp in imports if imp.get("is_standard", False)]
        non_standard_imports = [
            imp for imp in imports if not imp.get("is_standard", True)
        ]

        assert len(standard_imports) == 4  # os, sys, datetime, collections
        assert len(non_standard_imports) == 3  # pandas, tensorflow, nonexistent_module

    finally:
        # Clean up
        os.unlink(temp_file_path)


@pytest.mark.unit
def test_compute_score_no_external_imports(mock_program):
    """
    Test computing a score for a program with no external imports.

    Args:
        mock_program: The mock program fixture.
    """
    evaluator = ExternalImportsEvaluator()

    # Create a Python file with only standard library imports
    file_path = os.path.join(mock_program.path, "standard_imports.py")
    with open(file_path, "w") as f:
        f.write("""
import os
import sys
from datetime import datetime
from collections import defaultdict

def main():
    print("Hello, world!")
    
if __name__ == "__main__":
    main()
""")

    score, metadata = evaluator._compute_score(mock_program)

    # Perfect score since there are no external imports
    assert score == 1.0
    assert metadata["external_imports_count"] == 0
    assert len(metadata["external_modules"]) == 0
    assert metadata["files_analyzed"] == 1


@pytest.mark.unit
def test_compute_score_with_external_imports(mock_program):
    """
    Test computing a score for a program with external imports.

    Args:
        mock_program: The mock program fixture.
    """
    evaluator = ExternalImportsEvaluator()

    # Create a Python file with external imports
    file_path = os.path.join(mock_program.path, "external_imports.py")
    with open(file_path, "w") as f:
        f.write("""
import os
import pandas as pd
from tensorflow import keras
import numpy as np

def process_data():
    data = pd.DataFrame()
    model = keras.Sequential()
    return np.mean(data)
""")

    score, metadata = evaluator._compute_score(mock_program)

    # Score should be reduced due to 3 external modules
    expected_score = 1.0 - (3 * 0.1)  # Base score - (3 modules * penalty per module)
    assert score == expected_score
    assert metadata["external_imports_count"] == 3
    assert len(metadata["external_modules"]) == 3
    assert set(metadata["external_modules"]) == {"pandas", "tensorflow", "numpy"}


@pytest.mark.unit
def test_compute_score_with_syntax_error(mock_program):
    """
    Test computing a score for a program with a syntax error.

    Args:
        mock_program: The mock program fixture.
    """
    evaluator = ExternalImportsEvaluator()

    # Create a Python file with a syntax error
    file_path = os.path.join(mock_program.path, "syntax_error.py")
    with open(file_path, "w") as f:
        f.write("""
import os
import pandas as pd
from tensorflow import keras

def broken_function():
    if True
        print("Missing colon after if condition")
""")

    score, metadata = evaluator._compute_score(mock_program)

    # The evaluator should handle the syntax error gracefully
    assert 0.0 <= score <= 1.0
    assert "files_analyzed" in metadata
    assert metadata["files_analyzed"] == 1


@pytest.mark.unit
def test_compute_score_multiple_files(mock_program):
    """
    Test computing a score for a program with multiple files.

    Args:
        mock_program: The mock program fixture.
    """
    evaluator = ExternalImportsEvaluator()

    # Create multiple Python files with various imports
    file1_path = os.path.join(mock_program.path, "file1.py")
    with open(file1_path, "w") as f:
        f.write("""
import os
import pandas as pd
""")

    file2_path = os.path.join(mock_program.path, "file2.py")
    with open(file2_path, "w") as f:
        f.write("""
import sys
from tensorflow import keras
""")

    file3_path = os.path.join(mock_program.path, "file3.py")
    with open(file3_path, "w") as f:
        f.write("""
import json
import pandas as pd  # Duplicate external import
""")

    score, metadata = evaluator._compute_score(mock_program)

    # Should detect 2 unique external modules (pandas and tensorflow)
    expected_score = 1.0 - (2 * 0.1)  # Base score - (2 modules * penalty per module)
    assert score == expected_score
    assert metadata["external_imports_count"] == 3  # Total count of external imports
    assert len(metadata["external_modules"]) == 2  # Unique external modules
    assert set(metadata["external_modules"]) == {"pandas", "tensorflow"}
    assert metadata["files_analyzed"] == 3


@pytest.mark.unit
def test_initialize_standard_modules():
    """Test that standard modules are correctly initialized."""
    evaluator = ExternalImportsEvaluator()

    # Check that common standard modules are included
    common_std_modules = [
        "os",
        "sys",
        "json",
        "datetime",
        "collections",
        "re",
        "math",
        "logging",
        "pathlib",
        "typing",
    ]

    for module in common_std_modules:
        assert module in evaluator.standard_modules, (
            f"{module} should be in standard modules"
        )


@pytest.mark.unit
def test_nested_directory_structure(mock_program):
    """
    Test that the evaluator handles nested directory structures.

    Args:
        mock_program: The mock program fixture.
    """
    evaluator = ExternalImportsEvaluator()

    # Create a nested directory structure
    nested_dir = os.path.join(mock_program.path, "pkg", "subpkg")
    os.makedirs(nested_dir, exist_ok=True)

    # Create Python files in different directories
    with open(os.path.join(mock_program.path, "root_file.py"), "w") as f:
        f.write("import os\nimport pandas as pd\n")

    with open(os.path.join(mock_program.path, "pkg", "mid_file.py"), "w") as f:
        f.write("import sys\nfrom numpy import array\n")

    with open(os.path.join(nested_dir, "deep_file.py"), "w") as f:
        f.write("import json\nimport matplotlib.pyplot as plt\n")

    score, metadata = evaluator._compute_score(mock_program)

    # Should find 3 Python files with 3 unique external modules
    assert metadata["files_analyzed"] == 3
    assert len(metadata["external_modules"]) == 3
    assert set(metadata["external_modules"]) == {"pandas", "numpy", "matplotlib"}


@pytest.mark.unit
def test_no_python_files(mock_program):
    """
    Test computing a score for a program with no Python files.

    Args:
        mock_program: The mock program fixture.
    """
    evaluator = ExternalImportsEvaluator()

    # Create a non-Python file
    file_path = os.path.join(mock_program.path, "not_python.txt")
    with open(file_path, "w") as f:
        f.write("This is not a Python file.")

    score, metadata = evaluator._compute_score(mock_program)

    # Perfect score since there are no Python files with imports
    assert score == 1.0
    assert metadata["files_analyzed"] == 0
    assert metadata["external_imports_count"] == 0


@pytest.mark.unit
def test_file_io_error_handling():
    """Test that the evaluator handles file I/O errors gracefully."""
    evaluator = ExternalImportsEvaluator()

    # Test with a non-existent file
    imports = evaluator._extract_imports("nonexistent_file.py")

    # Should return a list with an error entry
    assert len(imports) == 1
    assert "error" in imports[0]
    assert "file" in imports[0]
