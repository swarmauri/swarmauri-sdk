"""
Folded‑expression evaluation for the *resolve* phase.

• Substitutes @{…} / %{…} immediately (supports dotted paths).
• Leaves ${…} placeholders for render‑time.
• Executes constant arithmetic / concatenation with safe_eval.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from lark import Token, Tree

from ._eval import safe_eval


# ───────────────────────────── token classes ──────────────────────────────
_STR_TOKENS = {
    "SINGLE_QUOTED_STRING",
    "TRIPLE_QUOTED_STRING",
    "TRIPLE_BACKTICK_STRING",
    "BACKTICK_STRING",
}

_SCOPE_PREFIX = {
    "GLOBAL_SCOPED_VAR": "@",
    "LOCAL_SCOPED_VAR": "%",
    "CONTEXT_SCOPED_VAR": "$",
}


# ───────────────────────────── helpers ─────────────────────────────────────
def _lookup(path: str, *envs: Dict[str, Any]) -> Optional[Any]:
    """Return the first hit for a dotted path in the provided envs."""
    parts = path.split(".")
    for env in envs:
        cur: Any = env
        for p in parts:
            if not (isinstance(cur, dict) and p in cur):
                cur = None
                break
            cur = cur[p]
        if cur is not None:
            return cur
    return None


def _tok_to_py(
    tok: Token,
    g: Dict[str, Any],
    local_env: Dict[str, Any],
    c: Dict[str, Any],
) -> str:
    """Convert a Lark token to a Python snippet (or placeholder)."""
    # ──────────────────────────────── Strings ────────────────────────────────
    if tok.type in _STR_TOKENS:
        raw = tok.value
        # If the first and last chars are matching quotes/backticks, strip them
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'", "`"):
            raw = raw[1:-1]
        return repr(raw)

    # ───────────────────────────── Numerics & Booleans ─────────────────────────
    if tok.type in {"INTEGER", "FLOAT"}:
        return tok.value
    if tok.type == "BOOLEAN":
        return "True" if tok.value == "true" else "False"

    # ───────────────────────────── Operators ────────────────────────────────
    if tok.type == "OPERATOR":
        return tok.value

    # ───────────────────────── Scope‑prefixed vars ───────────────────────────
    if tok.type in _SCOPE_PREFIX:
        marker = _SCOPE_PREFIX[tok.type]
        inner = tok.value[2:-1]  # strip the @{…}, %{…}, or ${…}

        # Context‑scoped (${…})
        if marker == "$":
            ctx = c or {}
            val = _lookup(inner, ctx)
            if val is not None:
                if hasattr(val, "evaluate"):
                    val = val.evaluate()
                return repr(val)
            return tok.value

        # Global (@{…}) or local (%{…})
        val = _lookup(inner, g) if marker == "@" else _lookup(inner, local_env, g)
        if val is None:
            return tok.value
        if hasattr(val, "evaluate"):
            val = val.evaluate()
        if isinstance(val, str):
            # strip any leftover quotes
            val = val.strip("\"'")
        return repr(val)

    # ────────────────────────────── Fallback ────────────────────────────────
    return tok.value


# ─────────────────────────── public entry‑point ───────────────────────────
def evaluate_expression_tree(
    tree: Tree,
    global_env: Dict[str, Any],
    local_env: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Any:
    """Resolve a `<( … )>` expression, substituting @{…} and %{…} immediately.
    Leaves ${…} intact and wraps in an f-string if any remain."""
    from lark import Token
    from ._ast_nodes import (
        BaseNode,
        HspacesNode,
        InlineWhitespaceNode,
        WhitespaceNode,
        IntegerNode,
        FloatNode,
        BooleanNode,
    )

    # Debug entry
    print("[DEBUG EXPR] → evaluate_expression_tree called")
    local_env = local_env or {}
    context = context or {}
    print(f"[DEBUG EXPR] Global env: {global_env}")
    print(f"[DEBUG EXPR] Local env:  {local_env}")
    print(f"[DEBUG EXPR] Context:    {context}")

    # Collect only meaningful children (drop whitespace tokens/nodes)
    items = [
        c
        for c in getattr(tree, "children", [])
        if not (
            (isinstance(c, Token) and c.type in ("HSPACES", "INLINE_WS", "WHITESPACE"))
            or isinstance(c, (HspacesNode, InlineWhitespaceNode, WhitespaceNode))
        )
    ]
    print(
        f"[DEBUG EXPR] Expression items: {[getattr(c, 'value', repr(c)) for c in items]}"
    )

    parts: List[str] = []
    for c in items:
        # 1) AST‐level boolean → Python literal
        if isinstance(c, BooleanNode):
            snippet = "True" if c.value.lower() == "true" else "False"
            print(f"[DEBUG EXPR] AST boolean node: {snippet}")
            parts.append(snippet)
            continue

        # 2) AST‐level integers/floats → raw digits
        if isinstance(c, (IntegerNode, FloatNode)):
            snippet = c.value
            print(f"[DEBUG EXPR] AST numeric node: {snippet}")
            parts.append(snippet)
            continue

        # 3) Raw Token integers/floats (just in case)
        if isinstance(c, Token) and c.type in {"INTEGER", "FLOAT"}:
            snippet = c.value
            print(f"[DEBUG EXPR] Token numeric: {snippet}")
            parts.append(snippet)
            continue

        # 4) Other tokens → normal converter
        if isinstance(c, Token):
            snippet = _tok_to_py(c, global_env, local_env, context)
            # strip accidental quotes around digit‐only strings
            if (
                snippet.startswith(("'", '"'))
                and snippet.endswith(("'", '"'))
                and snippet[1:-1].isdigit()
            ):
                snippet = snippet[1:-1]

        # 5) AST nodes carrying a Token in .meta
        elif (
            isinstance(c, BaseNode) and hasattr(c, "meta") and isinstance(c.meta, Token)
        ):
            snippet = _tok_to_py(c.meta, global_env, local_env, context)

        # 6) Other AST nodes → resolve then stringify
        elif isinstance(c, BaseNode):
            try:
                c.resolve(global_env, local_env, context)
            except Exception:
                pass
            val = getattr(c, "resolved", None) or getattr(c, "value", None)
            if isinstance(val, str):
                snippet = repr(val.strip("\"'"))
            else:
                snippet = str(val)

        # 7) Fallback
        else:
            snippet = str(c)

        parts.append(snippet)
        print(f"[DEBUG EXPR] Part snippet: {snippet}")

    # ────────────────────────────────────────────
    # **FIX**: join with spaces so that 'if' / 'else' remain valid
    py_expr = " ".join(parts)
    print(f"[DEBUG EXPR] Built py_expr: {py_expr}")

    # Static-only: no ${…}, so safe_eval
    if "${" not in py_expr:
        try:
            result = safe_eval(py_expr, local_env=local_env)
            print(f"[DEBUG EXPR] Static eval result: {result}")
            return result
        except Exception as e:
            print(f"[DEBUG EXPR] Static eval error: {e}")
            return py_expr

    # Mixed dynamic: preserve ${…}
    placeholder_idxs = [
        idx
        for idx, part in enumerate(parts)
        if isinstance(part, str) and part.startswith("${")
    ]
    if placeholder_idxs:
        i0 = placeholder_idxs[0]
        if i0 > 0 and parts[i0 - 1] == "+":
            static_parts = parts[: i0 - 1]
        else:
            static_parts = parts[:i0]
        placeholder_text = parts[i0]
        static_expr = "".join(static_parts)
        try:
            static_value = str(safe_eval(static_expr, local_env=local_env))
        except Exception as e:
            print(f"[DEBUG EXPR] Static prefix eval error: {e}")
            static_value = static_expr
        f_res = f'f"{static_value}{placeholder_text}"'
        print(f"[DEBUG EXPR] Final f-string result: {f_res}")
        return f_res

    # No placeholders detected, fallback
    return py_expr


# ───────────────────── used by Config.render fallback ─────────────────────
def _render_folded_expression_node(
    node,
    env: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
):
    from ._ast_nodes import FoldedExpressionNode

    if isinstance(node, FoldedExpressionNode) and node.resolved is not None:
        return node.resolved
    return evaluate_expression_tree(node.content_tree, env, env, context)
