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

    def resolve(self):
        resolved_data = {}
        from ._ast_nodes import BaseNode
        for section, values in self._data.items():
            if section == '__comments__':
                resolved_data[section] = values
                continue
            if isinstance(values, (str, bool, int, float, type(None))):
                resolved_data[section] = values
                continue
            # Initialize nested dictionary for sections
            resolved_data[section] = {}
            if isinstance(values, dict):
                for key, value in values.items():
                    if isinstance(value, BaseNode):
                        resolved_data[section][key] = value.evaluate()
                    else:
                        resolved_data[section][key] = value
        return resolved_data


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