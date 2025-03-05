from abc import abstractmethod
from typing import Optional, List, Literal, Type, Any, Dict
from pydantic import ConfigDict, model_validator, Field, PrivateAttr, SecretStr

from swarmauri_core.tool_llms.IToolPredict import IToolPredict
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.messages.MessageBase import MessageBase

@ComponentBase.register_model()
class ToolLLMBase(IToolPredict, ComponentBase):
    allowed_models: List[str] = []
    resource: Optional[str] = Field(default=ResourceTypes.TOOL_LLM.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["ToolLLMBase"] = "ToolLLMBase"
    api_key: Optional[SecretStr] = None
    allowed_models: List[str] = []
    timeout: float = 600.0
    BASE_URL: str = None
    _headers: Dict[str, str] = PrivateAttr(default=None)

    @model_validator(mode="after")
    @classmethod
    def _validate_name_in_allowed_models(cls, values):
        name = values.name
        allowed_models = values.allowed_models
        if name and name not in allowed_models:
            raise ValueError(
                f"Model name {name} is not allowed. Choose from {allowed_models}"
            )
        return values

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
            raise ValueError(f"Model '{model}' is not in the allowed models list.")
        self.allowed_models.remove(model)


    #@abstractmethod #Enforce soon
    def get_schema_converter(self) -> Type["SchemaConverterBase"]:
        raise NotImplementedError("get_schema_converter() not implemented in subclass yet.")

    @abstractmethod
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        raise NotImplementedError("_schema_convert_tools() not implemented in subclass yet.")

    @abstractmethod
    def _format_messages(
        self, messages: List[Type[MessageBase]]
    ) -> List[Dict[str, str]]:
        raise NotImplementedError("_format_messages() not implemented in subclass yet.")

    @abstractmethod
    def _process_tool_calls(self, tool_calls, toolkit, messages) -> List[MessageBase]:
        raise NotImplementedError("_process_tool_calls() not implemented in subclass yet.")

    @abstractmethod
    def predict(self, *args, **kwargs):
        raise NotImplementedError("predict() not implemented in subclass yet.")

    @abstractmethod
    async def apredict(self, *args, **kwargs):
        raise NotImplementedError("apredict() not implemented in subclass yet.")

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
