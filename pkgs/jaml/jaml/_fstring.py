# jaml/_fstring.py
import re
from typing import Dict, Any, Optional
from ._utils import unquote
from ._eval import safe_eval

def _evaluate_f_string(f_str: str, global_data: Dict, local_data: Dict, context: Optional[Dict] = None) -> str:
    print("[DEBUG EVAL_F_STRING] Original f-string:", f_str)
    
    if not (f_str.startswith('f"') or f_str.startswith("f'")):
        print("[DEBUG EVAL_F_STRING] Not an f-string; returning as-is.")
        return f_str

    inner = f_str[1:].lstrip()
    if inner and inner[0] in ('"', "'"):
        quote_char = inner[0]
        if inner.endswith(quote_char):
            inner = inner[1:-1]
        else:
            inner = inner[1:]
    print("[DEBUG EVAL_F_STRING] After removing f prefix and quotes, inner:", inner)
    
    pattern = re.compile(r'([@%\$])?\{([^}]+)\}')
    def repl(match):
        scope_marker = match.group(1)
        content = match.group(2).strip()
        print("[DEBUG EVAL_F_STRING] Processing content:", content, "marker:", scope_marker)

        value = None
        if scope_marker == '@':
            keys = content.split('.')
            val = global_data if global_data is not None else {}
            for key in keys:
                if isinstance(val, dict) and key in val:
                    val = val[key]
                else:
                    val = None
                    break
            value = val
        elif scope_marker == '%':
            keys = content.split('.')
            val = local_data if local_data is not None else {}
            for key in keys:
                if isinstance(val, dict) and key in val:
                    val = val[key]
                else:
                    val = None
                    break
            value = val
        elif scope_marker == '$':
            return match.group(0)  # Defer context
        else:
            keys = content.split('.')
            val = local_data if local_data is not None else {}
            for key in keys:
                if isinstance(val, dict) and key in val:
                    val = val[key]
                else:
                    val = None
                    break
            value = val
            if value is None:
                try:
                    value = safe_eval(content, local_env=local_data)
                    print("[DEBUG EVAL_F_STRING] Evaluated expression:", content, "to:", value)
                except Exception as e:
                    print("[DEBUG EVAL_F_STRING] Expression evaluation failed:", e)
                    return match.group(0)

        if value is None:
            print("[DEBUG EVAL_F_STRING] Content unresolved:", match.group(0))
            return match.group(0)
        if hasattr(value, 'value'):
            return unquote(value.value)
        elif isinstance(value, str):
            return unquote(value)
        return str(value)

    result = re.sub(pattern, repl, inner)
    print("[DEBUG EVAL_F_STRING] After substitution:", result)
    
    if re.match(r'^[\d\s+\-*/().]+$|^(true|false|null)$', result):
        try:
            evaluated = safe_eval(result, local_env=local_data)
            print("[DEBUG EVAL_F_STRING] safe_eval result:", evaluated)
            return str(evaluated)
        except Exception as e:
            print("[DEBUG EVAL_F_STRING] safe_eval failed:", e)
    return result