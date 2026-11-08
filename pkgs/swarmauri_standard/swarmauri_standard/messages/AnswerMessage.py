from typing import Literal

from pydantic import JsonValue
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.messages.MessageBase import MessageBase


@ComponentBase.register_type(MessageBase, "AnswerMessage")
class AnswerMessage(MessageBase):
    """Record the answer to a particular question."""

    content: str = ""
    role: Literal["user"] = "user"
    type: Literal["AnswerMessage"] = "AnswerMessage"
    question_id: str
    answer: JsonValue
