from swarmauri_core.tracing.IChainTracer import IChainTracer
from typing import Callable, List, Tuple, Dict, Any   
        
class ChainTracer(IChainTracer):
    def __init__(self):
        self.traces = []

    def process_chain(self, chain: List[Tuple[Callable[..., Any], List[Any], Dict[str, Any]]]) -> "ChainTracer":
        """
        Processes each item in the operation chain by executing the specified external function
        with its args and kwargs. Logs starting, annotating, and ending the trace based on tuple position.

        Args:
            chain (List[Tuple[Callable[..., Any], List[Any], Dict[str, Any]]]): A list where each tuple contains:
                - An external function to execute.
                - A list of positional arguments for the function.
                - A dictionary of keyword arguments for the function.
        """
        for i, (func, args, kwargs) in enumerate(chain):
            # Infer operation type and log
            
            if i == 0:
                operation = "Start"
                self.start_trace(*args, **kwargs)
            elif i == len(chain) - 1:
                operation = "End"
                self.end_trace(*args, **kwargs)
            else:
                operation = "Annotate"
                self.annotate_trace(*args, **kwargs)
                
            # For the actual external function call
            result = func(*args, **kwargs)
            print(f"Function '{func.__name__}' executed with result: {result}")

            self.traces.append((operation, func, args, kwargs, result))

        return self

    def start_trace(self, *args, **kwargs) -> None:
        print(f"Starting trace with args: {args}, kwargs: {kwargs}")
        
    def annotate_trace(self, *args, **kwargs) -> None:
        print(f"Annotating trace with args: {args}, kwargs: {kwargs}")

    def end_trace(self, *args, **kwargs) -> None:
        print(f"Ending trace with args: {args}, kwargs: {kwargs}")

    def show(self) -> None:
        for entry in self.traces:
            print(entry)