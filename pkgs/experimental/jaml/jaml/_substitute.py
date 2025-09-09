import re
from typing import Optional


def _substitute_vars(
    expr: str,
    global_env: dict,
    local_env: dict,
    context: Optional[dict] = None,
    quote_strings: bool = True,
) -> str:
    context = context or {}

    def repl_local(m):
        var = m.group(1).strip()
        if local_env and var in local_env:
            value = local_env[var]
            if quote_strings and isinstance(value, str):
                return repr(value)
            return str(value)
        return f"%{{{var}}}"

    def repl_global(m):
        var = m.group(1).strip()
        if "." in var:
            section, key = var.split(".", 1)
            sect_val = global_env.get(section)
            if isinstance(sect_val, dict) and key in sect_val:
                value = sect_val[key]
                if quote_strings and isinstance(value, str):
                    return repr(value)
                return str(value)
        if var in global_env:
            value = global_env[var]
            if quote_strings and isinstance(value, str):
                return repr(value)
            return str(value)
        return f"@{{{var}}}"

    def repl_context(m):
        var = m.group(1).strip()
        if var in context:
            value = context[var]
            if quote_strings and isinstance(value, str):
                return repr(value)
            return str(value)
        return f"${{{var}}}"

    tmp = re.sub(r"%\{([^}]+)\}", repl_local, expr)
    tmp = re.sub(r"@\{([^}]+)\}", repl_global, tmp)
    tmp = re.sub(r"\$\{([^}]+)\}", repl_context, tmp)
    return tmp
