import re

def unquote(s):
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s

def resolve_scoped_variable(var_name, data):
    """Resolve a dotted variable name in the configuration AST.
    
    For example, if var_name is 'path.base', then traverse data to return:
      data["path"]["base"]
    """
    parts = var_name.split('.')
    current = data
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current

def evaluate_f_string(f_str, global_data, local_data):
    """
    Evaluate an f-string by substituting interpolations.
    This function supports two kinds of markers:
      - Global markers: @{...} (using global_data, with dotted names resolved in global_data)
      - Self/local markers: %{...} (using local_data, with dotted names resolved in local_data)
      
    f_str is assumed to start with f" or f'
    """
    # Remove the leading f and surrounding quotes.
    inner = f_str[2:-1]

    # This regex now captures a scope marker (@ or %) and the variable name.
    pattern = re.compile(r'([@%]){([^}]+)}')
    
    def repl(match):
        scope_marker = match.group(1)
        var_name = match.group(2).strip()
        if scope_marker == '@':
            # For unscoped globals, if there is no dot, look in __default__.
            if '.' in var_name:
                value = resolve_scoped_variable(var_name, global_data)
            else:
                value = global_data.get("__default__", {}).get(var_name, match.group(0))
        elif scope_marker == '%':
            # For self-scope, use the local context.
            if '.' in var_name:
                value = resolve_scoped_variable(var_name, local_data)
            else:
                value = local_data.get(var_name, match.group(0))
        else:
            value = match.group(0)
        if value is None:
            return match.group(0)
        if hasattr(value, 'value'):
            return unquote(value.value)
        elif isinstance(value, str):
            return unquote(value)
        return str(value)

    evaluated = re.sub(pattern, repl, inner)
    return evaluated
