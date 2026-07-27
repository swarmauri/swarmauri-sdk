from abc import ABC, abstractmethod
from typing import Any

from swarmauri_core.messages.IMessage import IMessage
from swarmauri_core.schema_converters.ISchemaConvert import ISchemaConvert


class IToolPredict(ABC):
    """
    Interface focusing on the basic properties and settings essential for
    defining models.
    """

    @abstractmethod
    def get_schema_converter(self) -> type["ISchemaConvert"]:
        pass

    @abstractmethod
    def _schema_convert_tools(self, tools) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def _format_messages(
        self, messages: list[type["IMessage"]]
    ) -> list[dict[str, str]]:
        pass

    @abstractmethod
    def _process_tool_calls(
        self, tool_calls, toolkit, messages
    ) -> list[IMessage]:
        pass

    @abstractmethod
    def predict(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """

    @abstractmethod
    async def apredict(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """

    @abstractmethod
    def stream(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """

    @abstractmethod
    async def astream(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """

    @abstractmethod
    def batch(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """

    @abstractmethod
    async def abatch(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
