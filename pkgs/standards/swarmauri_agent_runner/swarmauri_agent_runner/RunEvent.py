from typing import Literal

from pydantic import BaseModel

from .ApprovalRequest import ApprovalRequest
from swarmauri_standard.messages.QuestionMessage import QuestionMessage


class RunEvent(BaseModel):
    """Expose the current human interaction or run result."""

    run_id: str
    kind: Literal["input_required", "approval_required", "completed"]
    question: QuestionMessage | None = None
    approval: ApprovalRequest | None = None
    result: str | None = None
