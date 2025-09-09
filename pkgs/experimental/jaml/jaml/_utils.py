# jaml/_utils.py
from typing import Any


def unquote(s):
    if (s.startswith('"') and s.endswith('"')) or (
        s.startswith("'") and s.endswith("'")
    ):
        return s[1:-1]
    return s


def resolve_scoped_variable(var_name, data):
    """Resolve a dotted variable name in the configuration AST."""
    parts = var_name.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


# ────────────────────────────────────────────────────────────────
# ⑥ strip surrounding quotes from plain strings
def _strip_quotes(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_quotes(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_strip_quotes(v) for v in obj]
    if (
        isinstance(obj, str)
        and len(obj) >= 2
        and (
            (obj.startswith('"') and obj.endswith('"'))
            or (obj.startswith("'") and obj.endswith("'"))
        )
    ):
        return obj[1:-1]
    return obj
