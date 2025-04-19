# jaml/_fstring.py
import re
from typing import Dict, Any, Optional

from ._utils import unquote
from ._eval import safe_eval

# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

_VAR_RE = re.compile(r'([@%\$])?\{([^}]+)\}')


def _lookup(path: str, *envs: Optional[Dict[str, Any]]) -> Optional[Any]:
    """
    Follow a dotted *path* (e.g. "a.b.c") through each `env` in order,
    unwrapping AST nodes (via .evaluate()) so nested tables work.
    Returns the first successful hit or None.
    """
    keys = path.split(".")
    for env in envs:
        if env is None:
            continue

        # Start from the raw env; if it's an AST node or inline‑table node, unwrap it
        val: Any = env
        if hasattr(val, "evaluate"):
            try:
                val = val.evaluate()
            except Exception:
                # fallback to the raw env if evaluate() fails
                pass

        # Drill down the dotted path
        for key in keys:
            # Unwrap any nested AST node before key lookup
            if hasattr(val, "evaluate"):
                try:
                    val = val.evaluate()
                except Exception:
                    pass

            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                val = None
                break

        if val is not None:
            return val

    return None

# ────────────────────────────────────────────────────────────────────────────
# Public entry‑point
# ────────────────────────────────────────────────────────────────────────────

def _evaluate_f_string(
    f_str: str,
    global_data: Dict,
    local_data: Dict,
    context: Optional[Dict] = None,
) -> str:
    """
    Expand JAM‑style f‑strings.

    Marker semantics
    ────────────────
    • ``@{var}``  → search *only* the global/root mapping
    • ``%{var}``  → start at *local_data* (section scope), fall back to *global_data*
    • ``{expr}``  → same lookup as ``%{}``; if unresolved, try ``safe_eval(expr)``
    • ``${var}``  → search the caller‑supplied *context*, then local, then global

    Unresolved placeholders are returned verbatim so round‑trip fidelity is
    preserved.
    """
    print("[DEBUG _fstring._evaluate_f_string] Original f-string:", f_str)

    # Must begin with f"… or f'…
    if not (f_str.startswith('f"') or f_str.startswith("f'")):
        print("[DEBUG _fstring._evaluate_f_string] Not an f-string; returning as‑is.")
        return f_str

    # Strip leading f and its surrounding quotes
    inner = f_str[1:].lstrip()
    if inner:
        quote_char = inner[0]
        inner = inner[1:-1] if inner.endswith(quote_char) else inner[1:]
    print("[DEBUG _fstring._evaluate_f_string] After removing f prefix and quotes, inner:", inner)

    # ───────────────────────────────────────────────────────── placeholder pass
    def repl(match: "re.Match[str]") -> str:
        scope_marker, content = match.groups()
        content = content.strip()
        print("[DEBUG _fstring._evaluate_f_string] Processing content:", content, "marker:", scope_marker)

        # ${...} → context‑scoped (render‑time)
        if scope_marker == "$":
            # If no context was supplied (e.g. during resolve‑time) leave it
            # untouched so it can be handled later.
            if context is None:
                return match.group(0)

            value = _lookup(content, context, local_data, global_data)
            if value is None:
                print("[DEBUG _fstring._evaluate_f_string] Context lookup failed for", content)
                return match.group(0)

            if hasattr(value, "value"):
                return unquote(value.value)
            if isinstance(value, str):
                return unquote(value)
            return str(value)

        # Determine lookup order for @{…}, %{…}, and bare {…}
        if scope_marker == "@":                    # global‑only
            value = _lookup(content, global_data)
        else:                                      # '%' or bare
            value = _lookup(content, local_data, global_data)

        # For bare {expr} try evaluating an expression if lookup failed
        if value is None and scope_marker not in ("@", "%"):
            try:
                value = safe_eval(content, local_env=local_data)
                print("[DEBUG _fstring._evaluate_f_string] Evaluated expression:", content, "to:", value)
            except Exception as exc:
                print("[DEBUG _fstring._evaluate_f_string] Expression evaluation failed:", exc)
                return match.group(0)

        if value is None:
            print("[DEBUG _fstring._evaluate_f_string] Content unresolved:", match.group(0))
            return match.group(0)

        # Collapse AST nodes or quoted literals
        if hasattr(value, "value"):
            return unquote(value.value)
        if isinstance(value, str):
            return unquote(value)
        return str(value)

    substituted = _VAR_RE.sub(repl, inner)
    print("[DEBUG _fstring._evaluate_f_string] After substitution:", substituted)

    # If the whole string now looks like a simple literal/expression, eval it
    if re.fullmatch(r'[\d\s+\-*/().]+|true|false|null', substituted, flags=re.I):
        try:
            evaluated = safe_eval(substituted, local_env=local_data)
            print("[DEBUG _fstring._evaluate_f_string] safe_eval result:", evaluated)
            return str(evaluated)
        except Exception as exc:
            print("[DEBUG _fstring._evaluate_f_string] safe_eval failed:", exc)

    return substituted
