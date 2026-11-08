from pydantic import BaseModel


class ApprovalDecision(BaseModel):
    """Approve or decline an exact pending invocation."""

    approval_id: str
    approved: bool
