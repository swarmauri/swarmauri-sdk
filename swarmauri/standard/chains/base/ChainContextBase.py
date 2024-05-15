from typing import Any, Callable, Dict, List
import re

from swarmauri.core.chains.IChainContext import IChainContext

class ChainContextBase(IChainContext):
    def __init__(self, context: Dict = {}):
        self._context = context

    @property
    def context(self) -> Dict[str, Any]:
        return self._context

    @context.setter
    def context(self, value: Dict[str, Any]) -> None:
        self._context = value

    def update(self, **kwargs):
        self._context.update(kwargs)

    def get_value(self, key: str) -> Any:
        return self._context.get(key)

    def _resolve_fstring(self, template: str) -> str:
        pattern = re.compile(r'{([^}]+)}')
        def replacer(match):
            expression = match.group(1)
            try:
                return str(eval(expression, {}, self._context))
            except Exception as e:
                print(f"Failed to resolve expression: {expression}. Error: {e}")
                return f"{{{expression}}}"
        return pattern.sub(replacer, template)

    def _resolve_placeholders(self, value: Any) -> Any:
        if isinstance(value, str):
            return self._resolve_fstring(value)
        elif isinstance(value, dict):
            return {k: self._resolve_placeholders(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._resolve_placeholders(v) for v in value]
        else:
            return value

    def _resolve_ref(self, value: Any) -> Any:
        if isinstance(value, str) and value.startswith('$'):
            placeholder = value[1:]
            return placeholder
        return value