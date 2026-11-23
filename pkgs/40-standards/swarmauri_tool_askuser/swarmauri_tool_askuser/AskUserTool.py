from collections.abc import Callable
from typing import Any, Literal

from jsonschema import Draft202012Validator
from pydantic import Field, JsonValue
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.messages.AnswerMessage import AnswerMessage
from swarmauri_standard.messages.QuestionMessage import QuestionMessage


def validate_answer(question: QuestionMessage, answer: AnswerMessage) -> None:
    """Validate an answer against the original question."""
    if answer.question_id != question.question_id:
        raise ValueError("Answer does not match the pending question")
    if question.choices and answer.answer not in question.choices:
        raise ValueError("Answer must be one of the offered choices")
    Draft202012Validator(question.answer_schema).validate(answer.answer)


@ComponentBase.register_type(ToolBase, "AskUserTool")
class AskUserTool(ToolBase):
    """Ask a person a structured question through the configured host."""

    name: str = "AskUserTool"
    description: str = "Ask a person for information needed to continue."
    type: Literal["AskUserTool"] = "AskUserTool"
    input_handler: Callable[[QuestionMessage], JsonValue | QuestionMessage] = (
        Field(exclude=True)
    )
    parameters: list[ParameterBase] = Field(
        default_factory=lambda: [
            ParameterBase(
                name="prompt",
                input_type="string",
                description="Question to ask",
                required=True,
            ),
            ParameterBase(
                name="choices",
                input_type="array",
                items={"type": "string"},
                description="Permitted string answers",
                required=False,
            ),
            ParameterBase(
                name="answer_schema",
                input_type="object",
                description="JSON Schema for the answer",
                required=False,
            ),
        ]
    )

    def __call__(
        self,
        prompt: str,
        choices: list[str] | None = None,
        answer_schema: dict[str, Any] | None = None,
    ) -> AnswerMessage | QuestionMessage:
        question = QuestionMessage(
            content=prompt,
            choices=choices or [],
            answer_schema={"type": "string"}
            if answer_schema is None
            else answer_schema,
        )
        Draft202012Validator.check_schema(question.answer_schema)
        value = self.input_handler(question)
        if isinstance(value, QuestionMessage):
            if value != question:
                raise ValueError(
                    "A deferred question must match the original request"
                )
            return question
        answer = AnswerMessage(question_id=question.question_id, answer=value)
        validate_answer(question, answer)
        return answer
