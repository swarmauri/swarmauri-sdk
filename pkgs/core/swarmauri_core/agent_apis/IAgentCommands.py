from abc import ABC, abstractmethod
from typing import Any, List


class IAgentCommands(ABC):
    """
    Interface for the API object that enables a SwarmAgent to host various API
    routes.
    """

    @abstractmethod
    def invoke(self, request: Any) -> Any:
        """
        Handles invocation requests synchronously.

        Parameters:
            request (Any): The incoming request payload.

        Returns:
            Any: The response payload.
        """

    @abstractmethod
    async def ainvoke(self, request: Any) -> Any:
        """
        Handles invocation requests asynchronously.

        Parameters:
            request (Any): The incoming request payload.

        Returns:
            Any: The response payload.
        """

    @abstractmethod
    def batch(self, requests: list[Any]) -> list[Any]:
        """
        Handles batched invocation requests synchronously.

        Parameters:
            requests (List[Any]): A list of incoming request payloads.

        Returns:
            List[Any]: A list of responses.
        """

    @abstractmethod
    async def abatch(self, requests: list[Any]) -> list[Any]:
        """
        Handles batched invocation requests asynchronously.

        Parameters:
            requests (List[Any]): A list of incoming request payloads.

        Returns:
            List[Any]: A list of responses.
        """

    @abstractmethod
    def stream(self, request: Any) -> Any:
        """
        Handles streaming requests.

        Parameters:
            request (Any): The incoming request payload.

        Returns:
            Any: A streaming response.
        """

    @abstractmethod
    def get_schema_config(self) -> dict:
        """
        Retrieves the schema configuration for the API.

        Returns:
            dict: The schema configuration.
        """
