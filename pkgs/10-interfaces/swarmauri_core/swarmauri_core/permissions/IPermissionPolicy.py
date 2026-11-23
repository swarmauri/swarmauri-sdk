"""IPermissionPolicy contract."""

from abc import ABC, abstractmethod

from .models import AuthorizationDecision, Permission


class IPermissionPolicy(ABC):
    """Define the interchangeable PermissionPolicy contract."""

    @abstractmethod
    def authorize(
        self, available: tuple[Permission, ...], requested: Permission
    ) -> AuthorizationDecision: ...

    @abstractmethod
    def attenuate(
        self,
        available: tuple[Permission, ...],
        requested: tuple[Permission, ...],
    ) -> tuple[Permission, ...]: ...
