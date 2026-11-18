"""IGrantStore contract."""

from abc import ABC, abstractmethod

from .models import Grant, DelegatedCredential
from swarmauri_core.permissions import Permission


class IGrantStore(ABC):
    """Define the interchangeable GrantStore contract."""

    @abstractmethod
    def create(self, grant: Grant) -> None: ...

    @abstractmethod
    def load(self, grant_id: str) -> Grant: ...

    @abstractmethod
    def save(self, grant: Grant) -> Grant: ...
