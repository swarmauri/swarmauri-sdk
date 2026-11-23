class ToolExecutionError(RuntimeError):
    """Base error for tool execution policy and lifecycle failures."""


class ToolApprovalRequiredError(ToolExecutionError):
    """Approval was required but no decision was available."""


class ToolApprovalDeniedError(ToolExecutionError):
    """Execution was rejected by the approval callback."""


class ToolExecutionTimeoutError(ToolExecutionError):
    """Execution exceeded its configured timeout."""


class DuplicateToolCallError(ToolExecutionError):
    """An active execution already owns the call identifier."""
