import logging
from unittest.mock import Mock, patch

import pytest
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_evaluatorpool_accessibility.AccessibilityEvaluatorPool import (
    AccessibilityEvaluatorPool,
)

from swarmauri_standard.programs.Program import Program

# Configure logging for tests
logging.basicConfig(level=logging.INFO)


@pytest.fixture
def mock_evaluator():
    """
    Create a mock evaluator instance.

    Returns
    -------
    Mock
        A mock evaluator that implements the EvaluatorBase interface
    """
    evaluator = Mock(spec=EvaluatorBase)
    evaluator.__class__.__name__ = "MockEvaluator"
    evaluator.evaluate_file = Mock(return_value={"score": 0.75})
    evaluator.aggregate_results = Mock(return_value={"score": 0.8})
    return evaluator


@pytest.fixture
def mock_program():
    """
    Create a mock program instance with source files.

    Returns
    -------
    Mock
        A mock Program with test files
    """
    program = Mock(spec=Program)
    program.get_source_files = Mock(
        return_value={
            "test_file.py": "def test_function():\n    pass",
            "another_file.py": "def another_function():\n    pass",
        }
    )
    return program


@pytest.fixture
def evaluator_pool(mock_evaluator):
    """
    Create an AccessibilityEvaluatorPool instance with a mock evaluator.

    Parameters
    ----------
    mock_evaluator : Mock
        The mock evaluator to include in the pool

    Returns
    -------
    AccessibilityEvaluatorPool
        An initialized evaluator pool
    """
    return AccessibilityEvaluatorPool(
        evaluators=[mock_evaluator], weights={"MockEvaluator": 1.0}
    )


@pytest.mark.unit
def test_initialization():
    """Test the initialization of the AccessibilityEvaluatorPool."""
    # Test default initialization
    pool = AccessibilityEvaluatorPool()
    assert pool.type == "AccessibilityEvaluatorPool"
    assert len(pool.evaluators) > 0
    assert pool.weights

    # Test initialization with evaluators and weights
    mock_eval = Mock(spec=EvaluatorBase)
    pool = AccessibilityEvaluatorPool(
        evaluators=[mock_eval], weights={"MockEvaluator": 0.5}
    )
    assert len(pool.evaluators) == 1
    assert pool.weights == {"MockEvaluator": 0.5}


@pytest.mark.unit
def test_initialization_with_invalid_evaluator():
    """Test initialization with an invalid evaluator raises TypeError."""
    with pytest.raises(TypeError):
        AccessibilityEvaluatorPool(evaluators=["not_an_evaluator"])


@pytest.mark.unit
def test_evaluate_empty_evaluators():
    """Test evaluate method with no evaluators returns default values."""
    pool = AccessibilityEvaluatorPool(evaluators=[])
    program = Mock(spec=Program)
    program.get_source_files = Mock(return_value={})
    result = pool.evaluate(program)

    assert result["overall_score"] == 0.0
    assert result["evaluator_scores"] == {}
    assert result["file_scores"] == {}


@pytest.mark.unit
def test_evaluate(evaluator_pool, mock_program, mock_evaluator):
    """Test the evaluate method returns expected results."""
    result = evaluator_pool.evaluate(mock_program)

    assert "overall_score" in result
    assert "evaluator_scores" in result
    assert "file_scores" in result

    assert result["overall_score"] == 0.8
    assert result["evaluator_scores"] == {"MockEvaluator": 0.8}
    assert "test_file.py" in result["file_scores"]

    # Verify that evaluate_file was called for each file
    mock_evaluator.evaluate_file.assert_any_call(
        "test_file.py", "def test_function():\n    pass"
    )


@pytest.mark.unit
def test_evaluate_file(evaluator_pool, mock_evaluator):
    """Test the _evaluate_file method returns expected results."""
    file_path = "test_file.py"
    file_content = "def test_function():\n    pass"

    with patch.object(evaluator_pool, "_should_evaluate_file", return_value=True):
        score = evaluator_pool._evaluate_file(file_path, file_content)

        assert score == 0.75
        mock_evaluator.evaluate_file.assert_called_once_with(file_path, file_content)


@pytest.mark.unit
def test_evaluate_file_skipped(evaluator_pool, mock_evaluator):
    """Test the _evaluate_file method skips files that shouldn't be evaluated."""
    file_path = "test_file.py"
    file_content = "def test_function():\n    pass"

    with patch.object(evaluator_pool, "_should_evaluate_file", return_value=False):
        score = evaluator_pool._evaluate_file(file_path, file_content)

        assert score == 0.0
        mock_evaluator.evaluate_file.assert_not_called()


@pytest.mark.unit
def test_evaluate_file_exception(evaluator_pool, mock_evaluator):
    """Test the _evaluate_file method handles exceptions from evaluators."""
    file_path = "test_file.py"
    file_content = "def test_function():\n    pass"

    with patch.object(evaluator_pool, "_should_evaluate_file", return_value=True):
        mock_evaluator.evaluate_file.side_effect = Exception("Test exception")

        score = evaluator_pool._evaluate_file(file_path, file_content)

        assert score == 0.0
        mock_evaluator.evaluate_file.assert_called_once_with(file_path, file_content)


@pytest.mark.unit
@pytest.mark.parametrize(
    "file_path, content, expected",
    [
        ("test.py", "content", True),
        ("test.bin", "content", False),
        ("test.jpg", "content", False),
        ("test.py", "", False),
    ],
)
def test_should_evaluate_file(file_path, content, expected):
    """Test the _should_evaluate_file method with various file types."""
    pool = AccessibilityEvaluatorPool()

    assert pool._should_evaluate_file(file_path, content) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "scores, weights, expected",
    [
        (
            {"FleschReadingEaseEvaluator": 80},
            {"FleschReadingEaseEvaluator": 1.0},
            0.8,
        ),
        (
            {"FleschReadingEaseEvaluator": 60, "OtherEvaluator": 0.7},
            {"FleschReadingEaseEvaluator": 1.0, "OtherEvaluator": 1.0},
            0.45,
        ),
        ({}, {}, 0.0),
        ({"OtherEvaluator": 0.5}, {"OtherEvaluator": 0}, 0.0),
        ({"OtherEvaluator": 1.5}, {"OtherEvaluator": 1.0}, 0.0),
        ({"OtherEvaluator": -0.5}, {"OtherEvaluator": 1.0}, 1.0),
    ],
)
def test_calculate_overall_score(scores, weights, expected):
    """Test the _calculate_overall_score method with various inputs."""
    pool = AccessibilityEvaluatorPool(weights=weights)
    result = pool._calculate_overall_score(scores)

    # Use approx for floating point comparison
    assert result == pytest.approx(expected, abs=1e-3)


@pytest.mark.unit
def test_configure(evaluator_pool):
    """Test the configure method updates weights correctly."""
    config = {"weights": {"MockEvaluator": 2.0, "OtherEvaluator": 0.5}}
    evaluator_pool.configure(config)

    assert evaluator_pool.weights == {"MockEvaluator": 2.0, "OtherEvaluator": 0.5}


@pytest.mark.unit
def test_add_evaluator(evaluator_pool, mock_evaluator):
    """Ensure add_evaluator is disabled."""
    new_evaluator = Mock(spec=EvaluatorBase)
    with pytest.raises(RuntimeError):
        evaluator_pool.add_evaluator(new_evaluator, 1.5)


@pytest.mark.unit
def test_add_invalid_evaluator(evaluator_pool):
    """Adding any evaluator should raise RuntimeError."""
    with pytest.raises(RuntimeError):
        evaluator_pool.add_evaluator("not_an_evaluator")


@pytest.mark.unit
def test_remove_evaluator(evaluator_pool, mock_evaluator):
    """Test removing an evaluator from the pool."""
    result = evaluator_pool.remove_evaluator("MockEvaluator")

    assert result is True
    assert len(evaluator_pool.evaluators) == 0
    assert "MockEvaluator" not in evaluator_pool.weights


@pytest.mark.unit
def test_remove_nonexistent_evaluator(evaluator_pool):
    """Test removing a nonexistent evaluator returns False."""
    result = evaluator_pool.remove_evaluator("NonexistentEvaluator")

    assert result is False
    assert len(evaluator_pool.evaluators) == 1


@pytest.mark.unit
def test_reset(evaluator_pool, mock_evaluator):
    """Test the reset method resets all evaluators."""
    evaluator_pool.reset()

    mock_evaluator.reset.assert_called_once()


@pytest.mark.unit
def test_auto_register_evaluators(monkeypatch):
    """AccessibilityEvaluatorPool auto-registers evaluators from the package."""
    import swarmauri_evaluatorpool_accessibility as pkg

    class DummyEvaluator(EvaluatorBase):
        def _compute_score(self, program: Program, **kwargs):
            return 0.0, {}

    for name in pkg.__all__:
        if name == "AccessibilityEvaluatorPool":
            continue
        monkeypatch.setattr(pkg, name, type(name, (DummyEvaluator,), {}))

    pool = pkg.AccessibilityEvaluatorPool()

    expected = {name for name in pkg.__all__ if name != "AccessibilityEvaluatorPool"}
    evaluator_names = {e.__class__.__name__ for e in pool.evaluators}

    assert evaluator_names == expected
