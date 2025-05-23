# jaml/_eval.py
from typing import Dict, Any
import ast
import operator as op
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # caller can override


def safe_eval(expr: str, local_env: Dict[str, Any] | None = None) -> Any:
    """
    Safely evaluate a restricted Python expression.

    Supported:
      • arithmetic + boolean ops
      • comparisons
      • literals  (list / tuple / set / dict)
      • list-, set- & generator-comprehensions   ◀ NEW
      • ternary expressions (a if cond else b)
      • calls to a small allow-list of built-ins
    """
    local_env = local_env or {}

    # ── allow-lists ────────────────────────────────────────────────────
    _ops = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.FloorDiv: op.floordiv,
        ast.Mod: op.mod,
        ast.Pow: op.pow,
    }
    _boolops = {ast.And, ast.Or}
    _cmpops = {
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
        ast.In,
        ast.NotIn,
        ast.Is,
        ast.IsNot,
    }
    _funcs = {"enumerate": enumerate, "false": False, "true": True, "null": None}

    # ── helpers ───────────────────────────────────────────────────────
    def _eval(node: ast.AST):
        # ── NEW: f-string nodes ───────────────────────────────────────────
        if isinstance(node, ast.JoinedStr):  # complete f-string
            parts = []
            for piece in node.values:
                parts.append(_eval(piece))
            return "".join(parts)

        if isinstance(node, ast.FormattedValue):  # an {expr[:spec]!c} piece
            val = _eval(node.value)
            # handle !s / !r / !a conversions
            if node.conversion == -1:
                pass
            elif node.conversion == ord("s"):
                val = str(val)
            elif node.conversion == ord("r"):
                val = repr(val)
            elif node.conversion == ord("a"):
                val = ascii(val)
            else:
                raise ValueError("Unsupported f-string conversion")

            # handle optional format spec
            if node.format_spec is not None:
                spec = _eval(node.format_spec)
                val = format(val, spec)
            return str(val)

        # ── NEW: attribute access (obj.attr or mapping-style) ──────────────
        if isinstance(node, ast.Attribute):
            obj = _eval(node.value)
            attr = node.attr
            if attr.startswith("_"):
                raise ValueError("Access to private/protected attributes is disallowed")
            # Treat dict-like objects as attribute-accessible by key
            if isinstance(obj, dict):
                if attr in obj:
                    return obj[attr]
                raise ValueError(f"Key '{attr}' not found in mapping")
            if hasattr(obj, attr):
                return getattr(obj, attr)
            raise ValueError(f"Attribute '{attr}' not found")

        # literals / names ------------------------------------------------
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in local_env:
                return local_env[node.id]
            if node.id in _funcs:
                return _funcs[node.id]
            raise ValueError(f"Name not allowed: {node.id}")

        # arithmetic / unary ops -----------------------------------------
        if isinstance(node, ast.BinOp):
            if type(node.op) not in _ops:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return _ops[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")

        # boolean ops -----------------------------------------------------
        if isinstance(node, ast.BoolOp):
            if type(node.op) not in _boolops:
                raise ValueError(
                    f"Unsupported boolean operator: {type(node.op).__name__}"
                )
            vals = [_eval(v) for v in node.values]
            return all(vals) if isinstance(node.op, ast.And) else any(vals)

        # ternary ---------------------------------------------------------
        if isinstance(node, ast.IfExp):
            return _eval(node.body) if _eval(node.test) else _eval(node.orelse)

        # comparisons -----------------------------------------------------
        if isinstance(node, ast.Compare):
            left = _eval(node.left)
            for op_node, comp in zip(node.ops, node.comparators):
                cmp = _eval(comp)
                t = type(op_node)
                if t not in _cmpops:
                    raise ValueError(f"Unsupported comparison operator: {t.__name__}")
                ok = (
                    (t is ast.Eq and left == cmp)
                    or (t is ast.NotEq and left != cmp)
                    or (t is ast.Lt and left < cmp)
                    or (t is ast.LtE and left <= cmp)
                    or (t is ast.Gt and left > cmp)
                    or (t is ast.GtE and left >= cmp)
                    or (t is ast.In and left in cmp)
                    or (t is ast.NotIn and left not in cmp)
                    or (t is ast.Is and left is cmp)
                    or (t is ast.IsNot and left is not cmp)
                )
                if not ok:
                    return False
                left = cmp
            return True

        # calls -----------------------------------------------------------
        if isinstance(node, ast.Call):
            func = _eval(node.func)
            args = [_eval(a) for a in node.args]
            kwargs = {kw.arg: _eval(kw.value) for kw in node.keywords}
            return func(*args, **kwargs)

        # literals --------------------------------------------------------
        if isinstance(node, ast.List):
            return [_eval(elt) for elt in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(_eval(elt) for elt in node.elts)
        if isinstance(node, ast.Set):
            return {_eval(elt) for elt in node.elts}
        if isinstance(node, ast.Dict):
            return {_eval(k): _eval(v) for k, v in zip(node.keys, node.values)}

        # comprehensions (list, set, generator) ---------------------------  ◀ NEW
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):

            def _comp_recurse(gen_idx: int):
                if gen_idx == len(node.generators):
                    yield _eval(node.elt)
                    return
                gen = node.generators[gen_idx]
                for item in _eval(gen.iter):
                    if not isinstance(gen.target, ast.Name):
                        raise ValueError("Unsupported comprehension target")
                    # save / restore binding to avoid leaks
                    name = gen.target.id
                    prev = local_env.get(name, object())
                    local_env[name] = item
                    try:
                        if gen.ifs and not all(_eval(cond) for cond in gen.ifs):
                            continue
                        yield from _comp_recurse(gen_idx + 1)
                    finally:
                        if prev is object():
                            local_env.pop(name, None)
                        else:
                            local_env[name] = prev

            output = list(_comp_recurse(0))
            # Always return the collection intact;
            # header logic will decide what to do with it.
            if isinstance(node, ast.GeneratorExp):
                return output  # ← keep list, don’t join
            if isinstance(node, ast.ListComp):
                return output
            return set(output)  # ast.SetComp

        # subscripting ----------------------------------------------------
        if isinstance(node, ast.Subscript):
            value = _eval(node.value)
            slice_val = _eval(
                node.slice.value if isinstance(node.slice, ast.Index) else node.slice
            )
            return value[slice_val]

        # fallback --------------------------------------------------------
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")

    # ── entry-point ─────────────────────────────────────────────────────
    try:
        # wrap top-level bare f-string into a literal so ast.parse works
        if isinstance(expr, str) and expr.lstrip().startswith('f"'):
            expr = f"({expr})"  # minimal wrapper
        logger.debug(f"evaluating {expr}")
        tree = ast.parse(expr, mode="eval")
        return _eval(tree)
    except Exception as exc:
        logger.exception(f"Evaluation failed: {exc}")
        raise
