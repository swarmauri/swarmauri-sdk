from typing import Any, Dict, List, Callable
from swarmauri.standard.chains.base.ChainStepBase import ChainStepBase
from swarmauri.core.chains.IChain import IChain

class StateChain(IChain):
    """
    Enhanced to support ChainSteps with return parameters, storing return values as instance state variables.
    Implements the IChain interface including get_schema_info and remove_step methods.
    """
    def __init__(self):
        self._steps: List[ChainStepBase] = []
        self._context: Dict[str, Any] = {}
    
    def add_step(self, key: str, method: Callable[..., Any], *args, ref: str = None, **kwargs):
        # Directly store args, kwargs, and optionally a return_key without resolving them
        step = ChainStepBase(key, method, args=args, kwargs=kwargs, ref=ref)  # Note the use of 'ref' as 'return_key'
        self._steps.append(step)
    
    def remove_step(self, step: ChainStepBase) -> None:
        self._steps = [s for s in self._steps if s.key != step.key]
    
    def execute(self, *args, **kwargs) -> Any:
        # Execute the chain and manage result storage based on return_key
        for step in self._steps:
            resolved_args = [self._resolve_placeholders(arg) for arg in step.args]
            resolved_kwargs = {k: self._resolve_placeholders(v) for k, v in step.kwargs.items() if k != 'ref'}
            result = step.method(*resolved_args, **resolved_kwargs)
            if step.ref:  # step.ref is used here as the return_key analogy
                print('step.ref', step.ref)
                resolved_ref = self._resolve_ref(step.ref)
                print(resolved_ref)
                self._context[resolved_ref] = result
        return self._context  # or any specific result you intend to return
    
    def _resolve_ref(self, value: Any) -> Any:
        if isinstance(value, str) and value.startswith('$'):
            placeholder = value[2:-1]
            return placeholder
        return value
    
    def _resolve_placeholders(self, value: Any) -> Any:
        if isinstance(value, str) and value.startswith('$'):
            placeholder = value[2:-1]
            return self._context.get(placeholder)
        return value

    def set_context(self, **kwargs):
        self._context.update(kwargs)
    
    def get_schema_info(self) -> Dict[str, Any]:
        # Implementing required method from IChain; 
        # Adapt the return structure to your needs
        return {
            "steps": [step.key for step in self._steps],
            "context_keys": list(self._context.keys())
        }