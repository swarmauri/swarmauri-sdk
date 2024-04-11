from typing import Any, Dict, List, Callable
from abc import ABC, abstractmethod
from standard.chains.base.ChainStepBase import ChainStepBase

class StateChain:
    """
    Enhanced to support ChainSteps with return parameters, storing return values as instance state variables.
    """
    def __init__(self):
        self._steps: List[ChainStepBase] = []
        self._context: Dict[str, Any] = {}

    def add_step(self, key: str, method: Callable[..., Any], *args, return_key: str = None, **kwargs):
        # Directly store args, kwargs and optionally a return_key without resolving them
        step = ChainStepBase(key, method, args=args, kwargs=kwargs, return_key=return_key)
        self._steps.append(step)

    def execute_chain(self):
        for step in self._steps:
            # Resolve placeholders right before execution
            resolved_args = [self._resolve_placeholders(arg) for arg in step.raw_args]
            resolved_kwargs = {k: self._resolve_placeholders(v) for k, v in step.raw_kwargs.items()}
            result = step.method(*resolved_args, **resolved_kwargs)

            # If a return_key is provided, store the result under that key in the context
            if step.return_key:
                resolved_return_key = self._resolve_placeholders(step.return_key)
                self._context[resolved_return_key] = result

    def _resolve_placeholders(self, value: Any) -> Any:
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            placeholder = value[2:-1]
            return self._context.get(placeholder, value)
        return value
    
    def set_context(self, **kwargs):
        self._context.update(kwargs)