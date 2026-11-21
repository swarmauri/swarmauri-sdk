import json
from typing import Any, Literal

from pydantic import BaseModel, Field
from swarmauri_core.run_stores import RunCheckpoint
from swarmauri_standard.messages.AnswerMessage import AnswerMessage
from swarmauri_standard.messages.QuestionMessage import QuestionMessage

from .ApprovalDecision import ApprovalDecision
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
    tool_step_protocol: str | None = None
    pending_calls: list[dict[str, Any]] = Field(default_factory=list)
    pending_results: list[dict[str, Any]] = Field(default_factory=list)
    approval_requests: dict[str, ApprovalRequest] = Field(default_factory=dict)
    approval_decisions: dict[str, ApprovalDecision] = Field(
        default_factory=dict
    )
    approval: ApprovalRequest | None = None
    result: str | None = None

    @classmethod
    def from_checkpoint(cls, checkpoint: RunCheckpoint) -> "RunState":
        """Read typed runner state from an opaque checkpoint."""
        data = json.loads(checkpoint.payload)
        if (
            not isinstance(data, dict)
            or data.get("run_id") != checkpoint.run_id
        ):
            raise ValueError("Checkpoint payload does not match its run ID")
        data["revision"] = checkpoint.revision
        return cls.model_validate(data)

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
