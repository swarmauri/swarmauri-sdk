import json
from abc import abstractmethod
from typing import (
    Any,
    ClassVar,
    Dict,
    FrozenSet,
    List,
    Literal,
    Optional,
    Type,
)

from pydantic import ConfigDict, Field, PrivateAttr, SecretStr, model_validator
from swarmauri_core.tool_llms.IToolPredict import IToolPredict

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.schema_converters.SchemaConverterBase import (
    SchemaConverterBase,
)
from swarmauri_base.utils.allowed_models import is_model_allowed


@ComponentBase.register_model()
class ToolLLMBase(IToolPredict, ComponentBase):
    resource: Optional[str] = Field(
        default=ResourceTypes.TOOL_LLM.value, frozen=True
    )
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["ToolLLMBase"] = "ToolLLMBase"
    api_key: Optional[SecretStr] = Field(default=None, exclude=True)
    allowed_models: List[str] = Field(default_factory=list)
    timeout: float = 600.0
    max_retries: int = Field(default=3, ge=1)
    retry_delay: float = Field(default=2.0, ge=0)
    BASE_URL: str = None
    _headers: Dict[str, str] = PrivateAttr(default_factory=dict)

    capabilities: ClassVar[FrozenSet[str]] = frozenset()
    retryable_status_codes: ClassVar[FrozenSet[int]] = frozenset(
        {408, 409, 425, 429, 500, 502, 503, 504, 529}
    )

    @model_validator(mode="after")
    def _validate_name_in_allowed_models(self):
        name = self.name
        allowed_models = self.allowed_models
        if name and not is_model_allowed(name, allowed_models):
            raise ValueError(
                (
                    f"Model name {name} is not allowed. Choose from "
                    f"{allowed_models}"
                )
            )
        return self

    def add_allowed_model(self, model: str) -> None:
        """
        Add a new model to the list of allowed models.

        Raises:
            ValueError: If the model is already in the allowed models list.
        """
        if model in self.allowed_models:
            raise ValueError(f"Model '{model}' is already allowed.")
        self.allowed_models.append(model)

    def remove_allowed_model(self, model: str) -> None:
        """
        Remove a model from the list of allowed models.

        Raises:
            ValueError: If the model is not in the allowed models list.
        """
        if model not in self.allowed_models:
            raise ValueError(
                f"Model '{model}' is not in the allowed models list."
            )
        self.allowed_models.remove(model)

    @abstractmethod
    def get_schema_converter(self) -> Type["SchemaConverterBase"]:
        raise NotImplementedError(
            "get_schema_converter() not implemented in subclass yet."
        )

    def _schema_convert_tools(
        self, tools: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        converter = self.get_schema_converter()
        return [converter.convert(tools[tool]) for tool in tools]

    def _format_messages(
        self, messages: List[Type[MessageBase]]
    ) -> List[Dict[str, str]]:
        raise NotImplementedError(
            "_format_messages() not implemented in subclass yet."
        )

    def _process_tool_calls(
        self, tool_calls, toolkit, messages
    ) -> List[MessageBase]:
        """
        Processes a list of tool calls and appends the results to the messages
        list.

        Args:
            tool_calls (list): A list of dictionaries representing tool calls.
            Each dictionary should contain
                               a "function" key with a nested dictionary that
                               includes the "name" and "arguments"
                               of the function to be called, and an "id" key
                               for the tool call identifier.
            toolkit (ToolkitBase): An object that provides access to tools via
            the `get_tool_by_name` method.
            messages (list): A list of message dictionaries to which the
            results of the tool calls will be appended.

        Returns:
            List[MessageBase]: The updated list of messages with the results of
            the tool calls appended.
        """
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call["function"]["name"]

                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call["function"]["arguments"])
                func_result = func_call(**func_args)

                messages.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(func_result),
                    }
                )
        return messages

    @abstractmethod
    def predict(self, *args, **kwargs):
        raise NotImplementedError("predict() not implemented in subclass yet.")

    @abstractmethod
    async def apredict(self, *args, **kwargs):
        raise NotImplementedError(
            "apredict() not implemented in subclass yet."
        )

    @abstractmethod
    def stream(self, *args, **kwargs):
        raise NotImplementedError("stream() not implemented in subclass yet.")

    @abstractmethod
    async def astream(self, *args, **kwargs):
        raise NotImplementedError("astream() not implemented in subclass yet.")

    @abstractmethod
    def batch(self, *args, **kwargs):
        raise NotImplementedError("batch() not implemented in subclass yet.")

    @abstractmethod
    async def abatch(self, *args, **kwargs):
        raise NotImplementedError("abatch() not implemented in subclass yet.")
