from typing import Any, Literal
from uuid import uuid4

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.messages.MessageBase import MessageBase


@ComponentBase.register_type(MessageBase, "QuestionMessage")
class QuestionMessage(MessageBase):
    """Record a structured request for human input."""

    content: str = Field(min_length=1)
    role: Literal["assistant"] = "assistant"
    type: Literal["QuestionMessage"] = "QuestionMessage"
    question_id: str = Field(default_factory=lambda: str(uuid4()))
    choices: list[str] = Field(default_factory=list)
    answer_schema: dict[str, Any] = Field(
        default_factory=lambda: {"type": "string"}
    )
