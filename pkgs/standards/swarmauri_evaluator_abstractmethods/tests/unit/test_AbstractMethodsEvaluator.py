import ast
import logging
from unittest.mock import MagicMock

import pytest
from swarmauri_core.programs.IProgram import IProgram
from swarmauri_evaluator_abstractmethods.AbstractMethodsEvaluator import (
    AbstractMethodsEvaluator,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def evaluator():
    """
    Fixture that creates an AbstractMethodsEvaluator instance.

    Returns:
        AbstractMethodsEvaluator: An instance of the evaluator
    """
    return AbstractMethodsEvaluator()


@pytest.fixture
def mock_program():
    """
    Fixture that creates a mock program.

    Returns:
        MagicMock: A mock program object
    """
    program = MagicMock(spec=IProgram)
    program.get_source_files = MagicMock(return_value={})
    return program


@pytest.mark.unit
def test_initialization(evaluator):
    """
    Test that the evaluator initializes with correct default values.

    Args:
        evaluator: AbstractMethodsEvaluator instance
    """
    assert evaluator.type == "AbstractMethodsEvaluator"
    assert evaluator.ignore_private is True
    assert evaluator.ignore_dunder is True
    assert evaluator.abc_base_classes == ["ABC", "abc.ABC"]


@pytest.mark.unit
def test_is_abstract_class(evaluator):
    """
    Test the _is_abstract_class method with various class definitions.
    """
    # Create a class that inherits from ABC
    abc_class_code = "class TestClass(ABC): pass"
    tree = ast.parse(abc_class_code)
    class_node = tree.body[0]
    assert evaluator._is_abstract_class(class_node) is True

    # Create a class that inherits from abc.ABC
    abc_qualified_class_code = "class TestClass(abc.ABC): pass"
    tree = ast.parse(abc_qualified_class_code)
    class_node = tree.body[0]
    assert evaluator._is_abstract_class(class_node) is True

    # Create a class that doesn't inherit from ABC
    non_abc_class_code = "class TestClass: pass"
    tree = ast.parse(non_abc_class_code)
    class_node = tree.body[0]
    assert evaluator._is_abstract_class(class_node) is False


@pytest.mark.unit
def test_has_abstractmethod_decorator(evaluator):
    """
    Test the _has_abstractmethod_decorator method with various method definitions.
    """
    # Method with abstractmethod decorator
    method_code = """
@abstractmethod
def test_method(self):
    pass
"""
    tree = ast.parse(method_code)
    method_node = tree.body[0]
    assert evaluator._has_abstractmethod_decorator(method_node) is True

    # Method with abc.abstractmethod decorator
    method_code = """
@abc.abstractmethod
def test_method(self):
    pass
"""
    tree = ast.parse(method_code)
    method_node = tree.body[0]
    assert evaluator._has_abstractmethod_decorator(method_node) is True

    # Method without abstractmethod decorator
    method_code = """
def test_method(self):
    pass
"""
    tree = ast.parse(method_code)
    method_node = tree.body[0]
    assert evaluator._has_abstractmethod_decorator(method_node) is False


@pytest.mark.unit
def test_get_full_name(evaluator):
    """
    Test the _get_full_name method with attribute nodes.
    """
    # Create an attribute node for abc.ABC
    code = "abc.ABC"
    tree = ast.parse(code)
    attribute_node = tree.body[0].value
    assert evaluator._get_full_name(attribute_node) == "abc.ABC"

    # Create an attribute node for a deeper nested attribute
    code = "module.submodule.attribute"
    tree = ast.parse(code)
    attribute_node = tree.body[0].value
    assert evaluator._get_full_name(attribute_node) == "module.submodule.attribute"


@pytest.mark.unit
def test_check_file_with_compliant_code(evaluator):
    """
    Test the _check_file method with code that properly uses abstractmethod.
    """
    file_path = "test_file.py"
    source_code = """
from abc import ABC, abstractmethod

class TestClass(ABC):
    @abstractmethod
    def abstract_method(self):
        pass
"""
    issues = evaluator._check_file(file_path, source_code)
    assert len(issues) == 1
    assert issues[0]["has_abstractmethod"] is True
    assert issues[0]["class_name"] == "TestClass"
    assert issues[0]["method_name"] == "abstract_method"


@pytest.mark.unit
def test_check_file_with_non_compliant_code(evaluator):
    """
    Test the _check_file method with code that doesn't properly use abstractmethod.
    """
    file_path = "test_file.py"
    source_code = """
from abc import ABC, abstractmethod

class TestClass(ABC):
    def non_abstract_method(self):
        pass
"""
    issues = evaluator._check_file(file_path, source_code)
    assert len(issues) == 1
    assert issues[0]["has_abstractmethod"] is False
    assert issues[0]["class_name"] == "TestClass"
    assert issues[0]["method_name"] == "non_abstract_method"


@pytest.mark.unit
def test_check_file_with_syntax_error(evaluator):
    """
    Test the _check_file method with code that has syntax errors.
    """
    file_path = "test_file.py"
    source_code = """
from abc import ABC, abstractmethod

class TestClass(ABC):
    def method_with_syntax_error(self)
        pass
"""
    issues = evaluator._check_file(file_path, source_code)
    assert len(issues) == 1
    assert "Syntax error" in issues[0]["message"]


@pytest.mark.unit
def test_check_file_with_ignore_private(evaluator):
    """
    Test the _check_file method with private methods that should be ignored.
    """
    evaluator = AbstractMethodsEvaluator(ignore_private=True)
    file_path = "test_file.py"
    source_code = """
from abc import ABC, abstractmethod

class TestClass(ABC):
    def public_method(self):
        pass
    
    def _private_method(self):
        pass
"""
    issues = evaluator._check_file(file_path, source_code)
    assert len(issues) == 1
    assert issues[0]["method_name"] == "public_method"


@pytest.mark.unit
def test_check_file_with_ignore_dunder():
    """
    Test the _check_file method with dunder methods that should be ignored.
    """
    evaluator = AbstractMethodsEvaluator(ignore_dunder=True)
    file_path = "test_file.py"
    source_code = """
from abc import ABC, abstractmethod

class TestClass(ABC):
    def regular_method(self):
        pass
        
    def __dunder_method__(self):
        pass
"""
    issues = evaluator._check_file(file_path, source_code)
    assert len(issues) == 1
    assert issues[0]["method_name"] == "regular_method"


@pytest.mark.unit
def test_compute_score_perfect_compliance(mock_program, evaluator):
    """
    Test the _compute_score method with code that has perfect compliance.

    Args:
        mock_program: Mock program fixture
    """
    source_code = """
from abc import ABC, abstractmethod

class TestClass(ABC):
    @abstractmethod
    def method1(self):
        pass
        
    @abstractmethod
    def method2(self):
        pass
"""

    mock_program.get_source_files.return_value = {"test_file.py": source_code}

    score, metadata = evaluator._compute_score(mock_program)

    assert score == 1.0
    assert metadata["total_methods"] == 2
    assert metadata["total_abstract_methods"] == 2
    assert metadata["total_missing_decorators"] == 0
    assert metadata["percentage_compliant"] == 100.0


@pytest.mark.unit
def test_compute_score_partial_compliance(mock_program, evaluator):
    """
    Test the _compute_score method with code that has partial compliance.

    Args:
        mock_program: Mock program fixture
    """
    source_code = """
from abc import ABC, abstractmethod

class TestClass(ABC):
    @abstractmethod
    def method1(self):
        pass

    def method2(self):
        pass
"""

    mock_program.get_source_files.return_value = {"test_file.py": source_code}

    score, metadata = evaluator._compute_score(mock_program)

    assert score == 0.5
    assert metadata["total_methods"] == 2
    assert metadata["total_abstract_methods"] == 1
    assert metadata["total_missing_decorators"] == 1
    assert metadata["percentage_compliant"] == 50.0


@pytest.mark.unit
def test_compute_score_no_abstract_classes(mock_program, evaluator):
    """
    Test the _compute_score method with code that has no abstract classes.

    Args:
        mock_program: Mock program fixture
    """
    source_code = """
class TestClass:
    def method1(self):
        pass
        
    def method2(self):
        pass
"""

    mock_program.get_source_files.return_value = {"test_file.py": source_code}

    score, metadata = evaluator._compute_score(mock_program)

    assert score == 1.0
    assert metadata["total_methods"] == 0
    assert metadata["total_abstract_classes"] == 0


@pytest.mark.unit
def test_compute_score_multiple_files(mock_program, evaluator):
    """
    Test the _compute_score method with multiple source files.

    Args:
        mock_program: Mock program fixture
    """
    evaluator = AbstractMethodsEvaluator()

    source_code1 = """
from abc import ABC, abstractmethod

class TestClass1(ABC):
    @abstractmethod
    def method1(self):
        pass
        
    def method2(self):
        pass
"""

    source_code2 = """
from abc import ABC, abstractmethod

class TestClass2(ABC):
    @abstractmethod
    def method3(self):
        pass
        
    @abstractmethod
    def method4(self):
        pass
"""

    mock_program.get_source_files.return_value = {
        "test_file1.py": source_code1,
        "test_file2.py": source_code2,
    }

    score, metadata = evaluator._compute_score(mock_program)

    assert score == 0.75
    assert metadata["total_methods"] == 4
    assert metadata["total_abstract_methods"] == 3
    assert metadata["total_missing_decorators"] == 1
    assert metadata["percentage_compliant"] == 75.0


@pytest.mark.unit
def test_aggregate_scores(evaluator):
    """
    Test the aggregate_scores method with multiple evaluation scores.
    """
    scores = [1.0, 0.5, 0.75]
    metadata_list = [
        {
            "issues": [{"id": 1}],
            "total_abstract_classes": 1,
            "total_methods": 2,
            "total_abstract_methods": 2,
            "total_missing_decorators": 0,
        },
        {
            "issues": [{"id": 2}, {"id": 3}],
            "total_abstract_classes": 1,
            "total_methods": 2,
            "total_abstract_methods": 1,
            "total_missing_decorators": 1,
        },
        {
            "issues": [{"id": 4}],
            "total_abstract_classes": 2,
            "total_methods": 4,
            "total_abstract_methods": 3,
            "total_missing_decorators": 1,
        },
    ]

    aggregated_score, aggregated_metadata = evaluator.aggregate_scores(
        scores, metadata_list
    )

    assert aggregated_score == 0.75
    assert aggregated_metadata["score_count"] == 3
    assert len(aggregated_metadata["issues"]) == 4
    assert aggregated_metadata["total_abstract_classes"] == 4
    assert aggregated_metadata["total_methods"] == 8
    assert aggregated_metadata["total_abstract_methods"] == 6
    assert aggregated_metadata["total_missing_decorators"] == 2
    assert aggregated_metadata["percentage_compliant"] == 75.0


@pytest.mark.unit
def test_aggregate_scores_empty_list(evaluator):
    """
    Test the aggregate_scores method with an empty list of scores.
    """
    aggregated_score, aggregated_metadata = evaluator.aggregate_scores([], [])

    assert aggregated_score == 0.0
    assert "error" in aggregated_metadata
