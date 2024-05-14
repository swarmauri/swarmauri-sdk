# standard/chains/concrete/ContextChain.py
from typing import Any, Dict, List, Callable
from swarmauri.standard.chains.base.ChainContextBase import ChainContextBase
from swarmauri.standard.chains.base.ChainStep import ChainStep
from swarmauri.core.chains.IChain import IChain

class ContextChain(IChain, ChainContextBase):
    """
    Enhanced to support ChainSteps with return parameters, storing return values as instance state variables.
    Implements the IChain interface including get_schema_info and remove_step methods.
    """
    def __init__(self):
        ChainContextBase.__init__(self)
        self._steps: List[ChainStep] = []

    def add_step(self, key: str, method: Callable[..., Any], *args, ref: str = None, **kwargs):
        # Directly store args, kwargs, and optionally a return_key without resolving them
        step = ChainStep(key, method, args=args, kwargs=kwargs, ref=ref)  # Note the use of 'ref' as 'return_key'
        self._steps.append(step)

    def remove_step(self, step: ChainStep) -> None:
        self._steps = [s for s in self._steps if s.key != step.key]

    def execute(self, *args, **kwargs) -> Any:
        # Execute the chain and manage result storage based on return_key
        for step in self._steps:
            resolved_args = [self._resolve_placeholders(arg) for arg in step.args]
            resolved_kwargs = {k: self._resolve_placeholders(v) for k, v in step.kwargs.items() if k != 'ref'}
            result = step.method(*resolved_args, **resolved_kwargs)
            if step.ref:  # step.ref is used here as the return_key analogy
                resolved_ref = self._resolve_ref(step.ref)
                self.context[resolved_ref] = result
                self.update(**{resolved_ref: result})  # Update context with new state value
        return self.context  # or any specific result you intend to return

    def get_schema_info(self) -> Dict[str, Any]:
        # Implementing required method from IChain; 
        # Adapt the return structure to your needs
        return {
            "steps": [step.key for step in self._steps],
            "state_keys": list(self.context.keys())
        }