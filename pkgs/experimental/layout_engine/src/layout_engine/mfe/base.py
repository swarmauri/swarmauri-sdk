from __future__ import annotations
from abc import ABC, abstractmethod, Iterable, Mapping
from .spec import Remote

class IRemoteRegistry(ABC):
    @abstractmethod
    def register(self, remote: Remote) -> None: raise NotImplementedError
    @abstractmethod
    def register_many(self, remotes: Iterable[Remote]) -> None: raise NotImplementedError
    @abstractmethod
    def get(self, id: str) -> Remote: raise NotImplementedError
    @abstractmethod
    def try_get(self, id: str) -> Remote | None: raise NotImplementedError
    @abstractmethod
    def remove(self, id: str) -> None: raise NotImplementedError
    @abstractmethod
    def all(self) -> Iterable[Remote]: raise NotImplementedError
    @abstractmethod
    def to_dict(self) -> dict[str, dict]: raise NotImplementedError
    @abstractmethod
    def update_from_dict(self, data: Mapping[str, Mapping]) -> None: raise NotImplementedError
