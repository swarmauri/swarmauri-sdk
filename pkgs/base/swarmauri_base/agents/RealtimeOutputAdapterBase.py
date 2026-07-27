from abc import ABC, abstractmethod
from typing import Any

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.live_models.LiveEventBase import LiveEventBase


class RealtimeOutputAdapterBase(ComponentBase, ABC):
    @abstractmethod
    def handle(self, event: LiveEventBase) -> Any: ...

    @abstractmethod
    async def ahandle(self, event: LiveEventBase) -> Any: ...
