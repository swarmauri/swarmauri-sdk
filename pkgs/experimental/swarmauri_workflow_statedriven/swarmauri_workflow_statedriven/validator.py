# File: swarmauri/workflows/validator.py

from typing import Any, Dict


def always_valid(state: Dict[str, Any]) -> bool:
    """
    File: workflows/validator.py
    Function: always_valid

    Always returns True, allowing any transition.
    """
    return True


def validate_requirements(state: Dict[str, Any]) -> bool:
    """
    File: workflows/validator.py
    Function: validate_requirements

    Return True if the output of the 'Requirements Gathering' state
    contains the phrase 'system design' (case-insensitive).
    """
    output = state.get("Requirements Gathering", "")
    return "system design" in output.lower()


def validate_design(state: Dict[str, Any]) -> bool:
    """
    File: workflows/validator.py
    Function: validate_design

    Return True if the output of the 'System Design' state
    contains the word 'review' (case-insensitive).
    """
    output = state.get("System Design", "")
    return "review" in output.lower()
