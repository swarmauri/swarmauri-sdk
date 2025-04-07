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

def evaluate_f_string(f_str, data):
    """Evaluate an f-string by substituting global (or dotted) interpolations.
    
    f_str is assumed to start with f" or f'
    """
    # Remove the leading f and surrounding quotes.
    inner = f_str[2:-1]

    def repl(match):
        var_name = match.group(1).strip()
        if '.' in var_name:
            value = resolve_scoped_variable(var_name, data)
        else:
            # For unscoped globals, look under __default__
            value = data.get("__default__", {}).get(var_name, match.group(0))
        if value is None:
            return match.group(0)
        # If the value is a PreservedString (or similar), use its unquoted inner value.
        if hasattr(value, 'value'):
            return unquote(value.value)
        elif isinstance(value, str):
            return unquote(value)
        return str(value)

    return re.sub(r'@{([^}]+)}', repl, inner)