from __future__ import annotations
from abc import ABC, abstractmethod, Iterable, Mapping, Any, Optional
from .spec import ComponentSpec

class IComponentRegistry(ABC):
    """ABC for storing and resolving ComponentSpec entries by role."""
    @abstractmethod
    def register(self, spec: ComponentSpec) -> None:
        raise NotImplementedError
    @abstractmethod
    def register_many(self, specs: Iterable[ComponentSpec]) -> None:
        raise NotImplementedError
    @abstractmethod
    def override(self, role: str, **fields: Any) -> ComponentSpec:
        raise NotImplementedError
    @abstractmethod
    def get(self, role: str) -> ComponentSpec:
        raise NotImplementedError
    @abstractmethod
    def try_get(self, role: str) -> Optional[ComponentSpec]:
        raise NotImplementedError
    @abstractmethod
    def has(self, role: str) -> bool:
        raise NotImplementedError
    @abstractmethod
    def list(self) -> Iterable[ComponentSpec]:
        raise NotImplementedError
    @abstractmethod
    def resolve_props(self, role: str, overrides: Mapping[str, Any] | None = None) -> dict:
        raise NotImplementedError
    @abstractmethod
    def to_dict(self) -> dict[str, dict]:
        raise NotImplementedError
    @abstractmethod
    def update_from_dict(self, data: Mapping[str, Mapping[str, Any]]) -> None:
        raise NotImplementedError
