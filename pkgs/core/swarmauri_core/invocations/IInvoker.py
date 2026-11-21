"""IInvoker contract."""

from abc import ABC, abstractmethod

from .models import InvocationRequest, InvocationContext, InvocationResult


class IInvoker(ABC):
    """Define the interchangeable Invoker contract."""

    @abstractmethod
    async def invoke(
        self, request: InvocationRequest, context: InvocationContext
    ) -> InvocationResult: ...
