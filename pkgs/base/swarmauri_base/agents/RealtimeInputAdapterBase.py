from abc import ABC, abstractmethod
from typing import Any

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.live_models.LiveInputBase import LiveInputBase


class RealtimeInputAdapterBase(ComponentBase, ABC):
    @abstractmethod
    def adapt(self, value: Any) -> LiveInputBase: ...
