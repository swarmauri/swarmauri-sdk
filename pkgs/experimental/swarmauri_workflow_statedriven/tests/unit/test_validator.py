# File: tests/workflows/test_validator.py

import pytest
from swarmauri_workflow_statedriven.validator import (
    always_valid,
    validate_requirements,
    validate_design,
)


@pytest.mark.unit
def test_always_valid_always_returns_true():
    """
    File: workflows/validator.py
    Function: always_valid
    """
    assert always_valid({}) is True
    assert always_valid({"anything": 123}) is True


@pytest.mark.unit
def test_validate_requirements_false_when_phrase_missing():
    """
    File: workflows/validator.py
    Function: validate_requirements
    """
    # No key present
    assert validate_requirements({}) is False
    # Empty string
    assert validate_requirements({"Requirements Gathering": ""}) is False
    # Irrelevant content
    assert (
        validate_requirements({"Requirements Gathering": "collect user stories"})
        is False
    )


@pytest.mark.unit
def test_validate_requirements_true_when_phrase_present():
    """
    File: workflows/validator.py
    Function: validate_requirements
    """
    # Exact match, case‑insensitive
    state = {"Requirements Gathering": "The SYSTEM design must be modular."}
    assert validate_requirements(state) is True
    # Phrase embedded in text
    state = {"Requirements Gathering": "Include system Design and architecture."}
    assert validate_requirements(state) is True


@pytest.mark.unit
def test_validate_design_false_when_word_missing():
    """
    File: workflows/validator.py
    Function: validate_design
    """
    # No key present
    assert validate_design({}) is False
    # Empty string
    assert validate_design({"System Design": ""}) is False
    # Irrelevant content
    assert validate_design({"System Design": "architecture sketched"}) is False


@pytest.mark.unit
def test_validate_design_true_when_word_present():
    """
    File: workflows/validator.py
    Function: validate_design
    """
    # Exact word, case‑insensitive
    state = {"System Design": "Ready for REVIEW."}
    assert validate_design(state) is True
    # Word embedded in sentence
    state = {"System Design": "Please review the diagrams."}
    assert validate_design(state) is True
