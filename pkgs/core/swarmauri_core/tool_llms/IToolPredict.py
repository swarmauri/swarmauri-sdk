from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type

from swarmauri_core.messages.IMessage import IMessage
from swarmauri_core.schema_converters.ISchemaConvert import ISchemaConvert


class IToolPredict(ABC):
    """
    Interface focusing on the basic properties and settings essential for defining models.
    """

    @abstractmethod
    def get_schema_converter(self) -> Type["ISchemaConvert"]:
        pass

    @abstractmethod
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def _format_messages(
        self, messages: List[Type["IMessage"]]
    ) -> List[Dict[str, str]]:
        pass

    @abstractmethod
    def _process_tool_calls(self, tool_calls, toolkit, messages) -> List[IMessage]:
        pass

    @abstractmethod
    def predict(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

    @abstractmethod
    async def apredict(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

    @abstractmethod
    def stream(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

    @abstractmethod
    async def astream(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

    @abstractmethod
    def batch(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

    @abstractmethod
    async def abatch(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass
