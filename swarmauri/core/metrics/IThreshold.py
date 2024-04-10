from abc import ABC, abstractmethod

class IThreshold(ABC):
    @property
    @abstractmethod
    def k(self) -> int:
        pass

    @k.setter
    @abstractmethod
    def k(self, value: int) -> None:
        pass

