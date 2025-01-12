from abc import ABC, abstractmethod
from typing import Any


class ISensor(ABC):

    @abstractmethod
    def read(self) -> Any:
        pass
