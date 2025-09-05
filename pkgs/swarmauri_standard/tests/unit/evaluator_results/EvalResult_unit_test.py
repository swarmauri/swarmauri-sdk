import logging
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest
from swarmauri_core.programs.IProgram import IProgram

from swarmauri_standard.evaluator_results.EvalResult import EvalResult

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_program():
    """
    Fixture providing a mock program instance.

    Returns
    -------
    MagicMock
        A mock object implementing IProgram interface
    """
    program = MagicMock(spec=IProgram)
    program.id = "test-program-id"
    return program


@pytest.fixture
def sample_metadata() -> Dict[str, Any]:
    """
    Fixture providing sample metadata for testing.

    Returns
    -------
    Dict[str, Any]
        Sample metadata dictionary
    """
    return {
        "evaluator": "test_evaluator",
        "timestamp": "2023-01-01T12:00:00Z",
        "details": {"precision": 0.95, "recall": 0.87, "f1_score": 0.91},
    }


@pytest.fixture
def eval_result(mock_program, sample_metadata):
    """
    Fixture providing a sample EvalResult instance.

    Parameters
    ----------
    mock_program : MagicMock
        Mock program object
    sample_metadata : Dict[str, Any]
        Sample metadata dictionary

    Returns
    -------
    EvalResult
        Initialized evaluation result for testing
    """
    return EvalResult(score=0.85, metadata=sample_metadata, program=mock_program)


@pytest.mark.unit
def test_init_valid_parameters(mock_program, sample_metadata):
    """
    Test initialization with valid parameters.

    Parameters
    ----------
    mock_program : MagicMock
        Mock program object
    sample_metadata : Dict[str, Any]
        Sample metadata dictionary
    """
    result = EvalResult(score=0.85, metadata=sample_metadata, program=mock_program)

    assert result.score == 0.85
    assert result.metadata == sample_metadata
    assert result.program == mock_program
    assert result.type == "EvalResult"


@pytest.mark.unit
def test_init_with_integer_score(mock_program, sample_metadata):
    """
    Test initialization with an integer score.

    Parameters
    ----------
    mock_program : MagicMock
        Mock program object
    sample_metadata : Dict[str, Any]
        Sample metadata dictionary
    """
    result = EvalResult(score=1, metadata=sample_metadata, program=mock_program)

    assert result.score == 1
    assert isinstance(result.score, (int, float))


@pytest.mark.unit
def test_init_with_invalid_score_type(mock_program, sample_metadata):
    """
    Test initialization with an invalid score type.

    Parameters
    ----------
    mock_program : MagicMock
        Mock program object
    sample_metadata : Dict[str, Any]
        Sample metadata dictionary
    """
    with pytest.raises(TypeError, match="Score must be a number"):
        EvalResult(score="not_a_number", metadata=sample_metadata, program=mock_program)


@pytest.mark.unit
def test_init_with_none_program(sample_metadata):
    """
    Test initialization with None as program.

    Parameters
    ----------
    sample_metadata : Dict[str, Any]
        Sample metadata dictionary
    """
    with pytest.raises(ValueError, match="Program cannot be None"):
        EvalResult(score=0.85, metadata=sample_metadata, program=None)


@pytest.mark.unit
def test_init_with_invalid_metadata_keys(mock_program):
    """
    Test initialization with invalid metadata keys.

    Parameters
    ----------
    mock_program : MagicMock
        Mock program object
    """
    invalid_metadata = {123: "value"}  # Non-string key

    with pytest.raises(TypeError, match="All metadata keys must be strings"):
        EvalResult(score=0.85, metadata=invalid_metadata, program=mock_program)


@pytest.mark.unit
def test_update_metadata(eval_result):
    """
    Test updating metadata.

    Parameters
    ----------
    eval_result : EvalResult
        Evaluation result fixture
    """
    new_metadata = {"new_key": "new_value", "timestamp": "updated_timestamp"}

    # Store original metadata for comparison
    original_metadata = eval_result.metadata.copy()

    eval_result.update_metadata(new_metadata)

    # Check that new keys were added and existing keys were updated
    assert eval_result.metadata["new_key"] == "new_value"
    assert eval_result.metadata["timestamp"] == "updated_timestamp"

    # Check that other original keys remain unchanged
    for key in original_metadata:
        if key != "timestamp":
            assert eval_result.metadata[key] == original_metadata[key]


@pytest.mark.unit
def test_update_metadata_with_invalid_keys(eval_result):
    """
    Test updating metadata with invalid keys.

    Parameters
    ----------
    eval_result : EvalResult
        Evaluation result fixture
    """
    invalid_metadata = {123: "value"}  # Non-string key

    with pytest.raises(TypeError, match="All metadata keys must be strings"):
        eval_result.update_metadata(invalid_metadata)


@pytest.mark.unit
@pytest.mark.parametrize(
    "this_score,other_score,expected",
    [
        (0.85, 0.75, 1),  # This result is better
        (0.75, 0.85, -1),  # Other result is better
        (0.85, 0.85, 0),  # Results are equal
    ],
)
def test_compare_to(this_score, other_score, expected, mock_program, sample_metadata):
    """
    Test comparing two evaluation results.

    Parameters
    ----------
    this_score : float
        Score for this evaluation result
    other_score : float
        Score for the other evaluation result
    expected : int
        Expected comparison result
    mock_program : MagicMock
        Mock program object
    sample_metadata : Dict[str, Any]
        Sample metadata dictionary
    """
    this_result = EvalResult(
        score=this_score, metadata=sample_metadata, program=mock_program
    )
    other_result = EvalResult(
        score=other_score, metadata=sample_metadata, program=mock_program
    )

    assert this_result.compare_to(other_result) == expected


@pytest.mark.unit
def test_compare_to_invalid_type(eval_result):
    """
    Test comparing with an invalid type.

    Parameters
    ----------
    eval_result : EvalResult
        Evaluation result fixture
    """
    with pytest.raises(TypeError, match="Cannot compare EvalResult with"):
        eval_result.compare_to("not_an_eval_result")


@pytest.mark.unit
def test_validate_metadata_non_dict():
    """
    Test validating non-dictionary metadata.
    """
    with pytest.raises(ValueError, match="Metadata must be a dictionary"):
        # We need to access the protected method for testing
        EvalResult._validate_metadata(None, "not_a_dict")


@pytest.mark.unit
def test_validate_metadata_non_string_keys():
    """
    Test validating metadata with non-string keys.
    """
    invalid_metadata = {123: "value"}

    with pytest.raises(TypeError, match="All metadata keys must be strings"):
        # We need to access the protected method for testing
        EvalResult._validate_metadata(None, invalid_metadata)
