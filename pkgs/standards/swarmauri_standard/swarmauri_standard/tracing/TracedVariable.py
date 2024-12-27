from typing import Any
from swarmauri_standard.tracing.SimpleTracer import SimpleTracer

class TracedVariable:
    """
    Wrapper class to trace multiple changes to a variable within the context manager.
    """
    def __init__(self, name: str, value: Any, tracer: SimpleTracer):
        self.name = name
        self._value = value
        self._tracer = tracer
        self._changes = []  # Initialize an empty list to track changes

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_value: Any):
        # Record the change before updating the variable's value
        change_annotation = {"from": self._value, "to": new_value}
        self._changes.append(change_annotation)
        
        # Update the trace by appending the latest change to the list under a single key
        # Note that the key is now constant and does not change with each update
        self._tracer.annotate_trace(key=f"{self.name}_changes", value=self._changes)
        
        self._value = new_value