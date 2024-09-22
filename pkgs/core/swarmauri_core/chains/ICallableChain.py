from abc import ABC, abstractmethod
from typing import Any, Callable, List, Tuple

CallableDefinition = Tuple[Callable, List[Any], dict]

class ICallableChain(ABC):
    @abstractmethod
    def __call__(self, *initial_args: Any, **initial_kwargs: Any) -> Any:
        """Executes the chain of callables."""
        pass

    @abstractmethod
    def add_callable(self, func: Callable, args: List[Any] = None, kwargs: dict = None) -> None:
        """Adds a new callable to the chain."""
        pass