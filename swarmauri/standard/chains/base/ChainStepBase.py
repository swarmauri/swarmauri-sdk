from typing import Any, Callable, List, Dict
from swarmauri.core.chains.IChainStep import IChainStep

class ChainStepBase(IChainStep):
    """
    Represents a single step within an execution chain.
    """
    
    def __init__(self, 
        key: str, 
        method: Callable, 
        args: List[Any] = None, 
        kwargs: Dict[str, Any] = None, 
        ref: str = None):
        """
        Initialize a chain step.

        Args:
            key (str): Unique key or identifier for the step.
            method (Callable): The callable object (function or method) to execute in this step.
            args (List[Any], optional): Positional arguments for the callable.
            kwargs (Dict[str, Any], optional): Keyword arguments for the callable.
            ref (str, optional): Reference to another component or context variable, if applicable.
        """
        self.key = key
        self.method = method
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.ref = ref
        
