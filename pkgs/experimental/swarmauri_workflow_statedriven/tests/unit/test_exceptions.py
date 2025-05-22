# File: tests/workflows/test_exceptions.py

import pytest
from swarmauri_workflow_statedriven.exceptions import (
    WorkflowError,
    InvalidTransitionError,
    ValidationError,
)


@pytest.mark.unit
def test_exceptions_inheritance():
    """
    File: workflows/exceptions.py
    Classes: WorkflowError, InvalidTransitionError, ValidationError
    """
    # Base hierarchy
    assert issubclass(WorkflowError, Exception)
    assert issubclass(InvalidTransitionError, WorkflowError)
    assert issubclass(ValidationError, WorkflowError)


@pytest.mark.unit
def test_workflow_error_message():
    """
    File: workflows/exceptions.py
    Class: WorkflowError
    """
    msg = "workflow failure"
    with pytest.raises(WorkflowError) as exc:
        raise WorkflowError(msg)
    assert str(exc.value) == msg


@pytest.mark.unit
def test_invalid_transition_error_message():
    """
    File: workflows/exceptions.py
    Class: InvalidTransitionError
    """
    msg = "invalid transition occurred"
    with pytest.raises(InvalidTransitionError) as exc:
        raise InvalidTransitionError(msg)
    assert str(exc.value) == msg


@pytest.mark.unit
def test_validation_error_message():
    """
    File: workflows/exceptions.py
    Class: ValidationError
    """
    msg = "validation failed"
    with pytest.raises(ValidationError) as exc:
        raise ValidationError(msg)
    assert str(exc.value) == msg
