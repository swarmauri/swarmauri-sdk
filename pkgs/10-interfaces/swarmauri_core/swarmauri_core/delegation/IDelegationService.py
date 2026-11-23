"""IDelegationService contract."""

from abc import ABC, abstractmethod

from .models import Grant, DelegatedCredential
from swarmauri_core.permissions import Permission


class IDelegationService(ABC):
    """Define the interchangeable DelegationService contract."""

    @abstractmethod
    def root(
        self,
        task_id: str,
        holder: str,
        permissions: tuple[Permission, ...],
        remaining_depth: int = 3,
    ) -> Grant: ...

    @abstractmethod
    def delegate(
        self,
        parent_id: str,
        actor: str,
        recipient: str,
        permissions: tuple[Permission, ...],
    ) -> Grant: ...

    @abstractmethod
    def validate(
        self, grant_id: str, holder: str, permission: Permission
    ) -> Grant: ...

    @abstractmethod
    def revoke(self, grant_id: str) -> Grant: ...

    @abstractmethod
    async def credential(
        self, grant_id: str, actor: str, audience: str, permission: Permission
    ) -> DelegatedCredential: ...

    @abstractmethod
    async def verify(
        self, token: str, audience: str, permission: Permission
    ) -> Grant: ...
