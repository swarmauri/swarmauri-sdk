from abc import ABC, abstractmethod
from swarmauri_core.parsers.IParser import IParser


class IAgentParser(ABC):

    @property
    @abstractmethod
    def parser(self) -> IParser:
        pass

    @parser.setter
    @abstractmethod
    def parser(self) -> IParser:
        pass
