"""Live-model interface."""

from abc import ABC, abstractmethod

from swarmauri_core.models.IModel import IModel

from .ILiveConfig import ILiveConfig
from .ILiveSession import ILiveSession


class ILiveModel(IModel, ABC):
    @abstractmethod
    def connect(self, config: ILiveConfig) -> ILiveSession: ...

    @abstractmethod
    async def aconnect(self, config: ILiveConfig) -> ILiveSession: ...
