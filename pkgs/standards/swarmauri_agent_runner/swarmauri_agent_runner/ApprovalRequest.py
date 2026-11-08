from typing import Any

from pydantic import BaseModel


class ApprovalRequest(BaseModel):
    """Describe a pending invocation for human review."""

    approval_id: str
    call_id: str
    tool_name: str
    arguments: dict[str, Any]
    scope: str
