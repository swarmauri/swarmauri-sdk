from typing import Dict, Any
import ast
import operator as op

import logging

logger = logging.getLogger(__name__)          # put this with your other imports
logger.setLevel(logging.DEBUG)                # caller can override

def safe_eval(expr: str, local_env: Dict[str, Any] = None) -> any:
    logging.debug(f"expr: {expr}")
    local_env = local_env or {}
    allowed_operators = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.FloorDiv: op.floordiv,
        ast.Mod: op.mod,
        ast.Pow: op.pow
    }
    allowed_boolops = {ast.And, ast.Or}
    allowed_cmpops = {
        ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
        ast.In, ast.NotIn, ast.Is, ast.IsNot,
    }
    allowed_functions = {
        "enumerate": enumerate,
        "false": False,
        "true": True,
        "null": None
    }

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            if node.id in local_env:
                return local_env[node.id]
            if node.id in allowed_functions:
                return allowed_functions[node.id]
            raise ValueError(f"Name not allowed: {node.id}")
        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type not in allowed_operators:
                raise ValueError(f"Unsupported operator: {op_type.__name__}")
            return allowed_operators[op_type](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.USub):
                return -operand
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        elif isinstance(node, ast.BoolOp):
            if type(node.op) not in allowed_boolops:
                raise ValueError(f"Unsupported boolean operator: {type(node.op).__name__}")
            if isinstance(node.op, ast.And):
                result = True
                for value in node.values:
                    result = result and _eval(value)
                    if not result:
                        break
                return result
            elif isinstance(node.op, ast.Or):
                result = False
                for value in node.values:
                    result = result or _eval(value)
                    if result:
                        break
                return result
        elif isinstance(node, ast.IfExp):
            test = _eval(node.test)
            return _eval(node.body) if test else _eval(node.orelse)
        elif isinstance(node, ast.Compare):
            left = _eval(node.left)
            for operator, comparator in zip(node.ops, node.comparators):
                right = _eval(comparator)
                op_type = type(operator)
                if op_type not in allowed_cmpops:
                    raise ValueError(f"Unsupported comparison operator: {op_type.__name__}")
                if op_type is ast.Eq:
                    if not (left == right):
                        return False
                elif op_type is ast.NotEq:
                    if not (left != right):
                        return False
                elif op_type is ast.Lt:
                    if not (left < right):
                        return False
                elif op_type is ast.LtE:
                    if not (left <= right):
                        return False
                elif op_type is ast.Gt:
                    if not (left > right):
                        return False
                elif op_type is ast.GtE:
                    if not (left >= right):
                        return False
                elif op_type is ast.In:
                    if not (left in right):
                        return False
                elif op_type is ast.NotIn:
                    if not (left not in right):
                        return False
                elif op_type is ast.Is:
                    if not (left is right):
                        return False
                elif op_type is ast.IsNot:
                    if not (left is not right):
                        return False
                left = right
            return True
        elif isinstance(node, ast.Call):
            func = _eval(node.func)
            args = [_eval(arg) for arg in node.args]
            kwargs = {kw.arg: _eval(kw.value) for kw in node.keywords}
            return func(*args, **kwargs)
        elif isinstance(node, ast.List):
            return [_eval(elt) for elt in node.elts]
        elif isinstance(node, ast.Tuple):
            return tuple(_eval(elt) for elt in node.elts)
        elif isinstance(node, ast.Set):
            return {_eval(elt) for elt in node.elts}
        elif isinstance(node, ast.GeneratorExp):
            if len(node.generators) != 1:
                raise ValueError("Only single generator expressions supported")
            comp = node.generators[0]
            iter_val = _eval(comp.iter)
            result = []
            for item in iter_val:
                if isinstance(comp.target, ast.Name):
                    local_env[comp.target.id] = item
                else:
                    raise ValueError("Unsupported comprehension target")
                if comp.ifs and not all(_eval(if_node) for if_node in comp.ifs):
                    continue
                result.append(_eval(node.elt))
            if all(isinstance(x, str) for x in result):
                return "".join(result)
            return result
        elif isinstance(node, ast.Subscript):
            value = _eval(node.value)
            if isinstance(node.slice, ast.Index):  # Python <3.9
                slice_val = _eval(node.slice.value)
            else:
                slice_val = _eval(node.slice)
            return value[slice_val]
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")

    try:
        tree = ast.parse(expr, mode='eval')
        return _eval(tree)
    except Exception as e:
        logger.exception(f"Evaluation failed: {e}")
        raise