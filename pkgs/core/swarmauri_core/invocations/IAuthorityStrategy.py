"""IAuthorityStrategy contract."""

from abc import ABC, abstractmethod

from .models import InvocationRequest, InvocationContext


class IAuthorityStrategy(ABC):
    """Define the interchangeable AuthorityStrategy contract."""

    @abstractmethod
    async def credential(
        self,
        request: InvocationRequest,
        context: InvocationContext,
        audience: str,
    ) -> str: ...
