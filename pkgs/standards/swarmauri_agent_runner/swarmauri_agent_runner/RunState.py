from typing import Any, Literal

from pydantic import BaseModel, Field
from swarmauri_standard.messages.AnswerMessage import AnswerMessage
from swarmauri_standard.messages.QuestionMessage import QuestionMessage

from .ApprovalRequest import ApprovalRequest
from .RunEvent import RunEvent


class RunState(BaseModel):
    """Persist the model transcript and the pending interaction."""

    run_id: str
    revision: int = 0
    status: Literal[
        "ready",
        "dispatching",
        "input_required",
        "approval_required",
        "completed",
    ] = "ready"
    messages: list[dict[str, Any]] = Field(default_factory=list)
    questions: list[QuestionMessage] = Field(default_factory=list)
    answers: list[AnswerMessage] = Field(default_factory=list)
    pending_call: dict[str, Any] | None = None
    approval: ApprovalRequest | None = None
    result: str | None = None

    def event(self) -> RunEvent | None:
        """Return the current human interaction or completion event."""
        if self.status == "input_required":
            return RunEvent(
                run_id=self.run_id,
                kind="input_required",
                question=self.questions[-1],
            )
        if self.status == "approval_required":
            return RunEvent(
                run_id=self.run_id,
                kind="approval_required",
                approval=self.approval,
            )
        if self.status == "completed":
            return RunEvent(
                run_id=self.run_id, kind="completed", result=self.result
            )
        return None
