from collections.abc import MutableMapping
from typing import Any, Dict, Optional, IO
from ._fstring import _evaluate_f_string

class Config(MutableMapping):
    from ._ast_nodes import StartNode

    def __init__(self, ast: StartNode):
        self._ast = ast
        self._data = ast.data
        print('[DEBUG CONFIG INIT]:', self._data, self._ast)

    def __getitem__(self, key: str) -> Any:
        parts = key.split(".")
        current = self._data
        for part in parts:
            if isinstance(current, dict):
                current = current[part]
            else:
                raise KeyError(key)
        return current

    def __setitem__(self, key: str, value: Any):
        parts = key.split(".")
        current = self._data
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value
        self._sync_ast(key, value)

    def _sync_ast(self, key: str, value: Any):
        parts = key.split(".")
        current = self._ast.data
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value

    def __delitem__(self, key: str):
        parts = key.split(".")
        current = self._data
        for part in parts[:-1]:
            current = current[part]
        del current[parts[-1]]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"Config({self._data})"

    def loads(self):
        pass

    def load(self):
        pass

    def dumps(self) -> str:
        return self._ast.emit()

    def dump(obj: Dict[str, Any], fp: IO[str]) -> None:
        """
        Serialize a plain dict into JML and write to a file-like object (non-round-trip).
        
        :param obj: Dictionary to serialize.
        :param fp: File-like object to write to.
        """
        fp.write(dumps(obj))

    def resolve(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        from ._ast_nodes import BaseNode
        """
        Return a plain‑Python dict with every BaseNode evaluated **and**
        every f‑string expanded against the current global scope.
        """
        context = context or {}

        def _resolve_value(val: Any) -> Any:
            # Collapse AST nodes first
            if isinstance(val, BaseNode):
                val = val.evaluate()

            # Recurse into tables/sections
            if isinstance(val, dict):
                return {k: _resolve_value(v) for k, v in val.items()}

            # Expand f‑strings of the form f"@{var}/path"
            if isinstance(val, str) and val.startswith('f"') and val.endswith('"'):
                try:
                    return _evaluate_f_string(val, self._data, context)
                except KeyError:
                    # Leave unresolved if the variable isn’t defined yet
                    return val

            return val

        return {k: _resolve_value(v) if k != "__comments__" else v
                for k, v in self._data.items()}

    def render(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        context = context or {}
        rendered_data = {}
        for section, values in self._data.items():
            if section == '__comments__':
                rendered_data[section] = values
                continue
            if isinstance(values, str):
                if values.startswith('f"') and values.endswith('"'):
                    try:
                        rendered_value = _evaluate_f_string(values, self._data, context)
                        print(f"[DEBUG RENDER F-STRING]: {values} -> {rendered_value}")
                        rendered_data[section] = rendered_value
                    except KeyError as e:
                        print(f"[DEBUG RENDER ERROR]: {e}")
                        rendered_data[section] = values
                else:
                    rendered_data[section] = values
                continue
            rendered_data[section] = {}
            for key, value in values.items():
                if isinstance(value, str) and value.startswith('f"') and value.endswith('"'):
                    try:
                        rendered_value = _evaluate_f_string(value, self._data, context)
                        print(f"[DEBUG RENDER F-STRING]: {value} -> {rendered_value}")
                        rendered_data[section][key] = rendered_value
                    except KeyError as e:
                        print(f"[DEBUG RENDER ERROR]: {e}")
                        rendered_data[section][key] = value
                else:
                    rendered_data[section][key] = value
        return rendered_data