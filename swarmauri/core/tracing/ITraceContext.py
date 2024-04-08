from abc import ABC, abstractmethod
from typing import Any

class ITraceContext(ABC):
    """
    Interface for a trace context, representing a single trace instance.
    This context carries the state and metadata of the trace across different system components.
    """

    @abstractmethod
    def get_trace_id(self) -> str:
        """
        Retrieves the unique identifier for this trace.

        Returns:
            str: The unique trace identifier.
        """
        pass

    @abstractmethod
    def add_attribute(self, key: str, value: Any):
        """
        Adds or updates an attribute associated with this trace.

        Args:
            key (str): The attribute key or name.
            value (Any): The value of the attribute.
        """
        pass