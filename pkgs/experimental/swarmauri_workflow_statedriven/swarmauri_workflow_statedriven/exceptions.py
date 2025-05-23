# File: swarmauri/workflows/exceptions.py


class WorkflowError(Exception):
    """
    Base exception for all workflow-related errors.
    """

    pass


class InvalidTransitionError(WorkflowError):
    """
    Raised when a transition references undefined states
    or cannot be added to the workflow.
    """

    pass


class ValidationError(WorkflowError):
    """
    Raised when a node's output fails its validation rule.
    """

    pass
