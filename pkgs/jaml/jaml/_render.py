from typing import Dict, Any
import re
from .ast_nodes import (
    PreservedString, 
    DeferredDictComprehension,
    DeferredListComprehension, 
    FoldedExpressionNode,
    TableArraySectionNode,
    TableArrayHeader,
    ComprehensionHeader
)
from ._helpers import resolve_scoped_variable, evaluate_f_string
from .ast_nodes import FoldedExpressionNode
from ._eval import safe_eval  # or import safe_eval as defined in resolve.py


def substitute_deferred(ast_node, env, context=None):
    print("[DEBUG RENDER] Processing node of type:", type(ast_node))

    if isinstance(ast_node, dict) and {"_annotation", "_value"}.issubset(ast_node):
        return substitute_deferred(ast_node["_value"], env, context)

    if isinstance(ast_node, (DeferredDictComprehension, DeferredListComprehension)):
        return ast_node.evaluate(env, context=context)

    elif isinstance(ast_node, FoldedExpressionNode):
        return _render_folded_expression_node(ast_node, env, context=context)

    elif isinstance(ast_node, dict):
        local_env = env.copy() if isinstance(env, dict) else {}
        for k, v in ast_node.items():
            if k == "__comments__":
                continue
            local_env[k] = v["_value"] if isinstance(v, dict) and "_value" in v else v
        result = {}
        for k, v in ast_node.items():
            if k == "__comments__":
                result[k] = v
                continue
            if isinstance(k, (TableArrayHeader, ComprehensionHeader)):
                header_val = k.original.strip('[]') if hasattr(k, 'original') else str(k)
                k = safe_eval(header_val, local_env=local_env) if header_val.startswith('[') else header_val
            if isinstance(v, list) and all(isinstance(item, (dict, TableArraySectionNode)) for item in v):
                result[k] = []
                for item in v:
                    item_env = local_env.copy()
                    if isinstance(item, TableArraySectionNode):
                        if isinstance(item.header, (TableArrayHeader, ComprehensionHeader)):
                            header_env = extract_header_env(item.header, item_env)
                            item_env.update(header_env)
                        result[k].append(substitute_deferred(item.body, item_env, context))
                    else:
                        result[k].append(substitute_deferred(item, item_env, context))
            else:
                result[k] = substitute_deferred(v, local_env, context)
        return result

    elif isinstance(ast_node, list):
        return [substitute_deferred(item, env, context) for item in ast_node]

    elif isinstance(ast_node, PreservedString):
        s = ast_node.origin
        if s.strip() == "":
            return ""
        if s.lstrip().startswith(("f\"", "f'")):
            return evaluate_f_string(s.lstrip(), global_data=env, local_data=env, context=context)
        return _substitute_vars(ast_node.value, env, context=context)

    elif isinstance(ast_node, str):
        if ast_node.strip() == "":
            return ""
        if ast_node.lstrip().startswith(("f\"", "f'")):
            return evaluate_f_string(ast_node.lstrip(), global_data=env, local_data=env, context=context)
        return _substitute_vars(ast_node, env, context=context)

    return ast_node

def _render_folded_expression_node(node: FoldedExpressionNode, env: Dict[str, Any], context: Dict[str, Any] = None) -> Any:
    print("[DEBUG RENDER] Rendering FoldedExpressionNode:", node)
    
    if hasattr(node, 'resolved') and not isinstance(node.resolved, str):
        print("[DEBUG RENDER] Returning non-string cached resolution:", node.resolved)
        return node.resolved

    if hasattr(node, 'resolved') and isinstance(node.resolved, str):
        if not node.origin.strip().startswith("<("):
            print("[DEBUG RENDER] Returning cached string resolution:", node.resolved)
            return node.resolved

    folded_literal = node.origin.strip()
    if not (folded_literal.startswith("<(") and folded_literal.endswith(")>")):
        substituted_literal = _substitute_vars(folded_literal, env, context=context)
        print("[DEBUG RENDER] Folded literal without delimiters after substitution:", substituted_literal)
        return substituted_literal

    def token_to_expr(token):
        print("[DEBUG RENDER] Processing token:", token)
        if isinstance(token, str) and token.strip() in ("<(", ")>"):
            return ""
        if isinstance(token, (int, float)):
            return str(token)
        if hasattr(token, 'origin'):
            return token.origin
        if isinstance(token, str):
            if token.startswith(('@', '%', '$')) and token.endswith('}'):
                return _substitute_vars(token, env, context=context)
            return token
        if hasattr(token, 'children'):
            return " ".join(token_to_expr(child) for child in token.children)
        return str(token)

    if not hasattr(node, 'content_tree') or not node.content_tree:
        expr_string = folded_literal.strip('<()>')
    else:
        expr_string = " ".join(token_to_expr(t) for t in node.content_tree.children).strip()
    print("[DEBUG RENDER] Rebuilt expression string:", expr_string)

    try:
        if re.fullmatch(r'[\d\s+\-*/().]+', expr_string):
            result = eval(compile(expr_string, "<string>", "eval"), {}, {})
        else:
            result = safe_eval(expr_string, local_env=env)
        print("[DEBUG RENDER] Evaluation result:", result)
    except Exception as e:
        print("[DEBUG RENDER] Exception during evaluation:", e)
        result = expr_string

    if isinstance(result, str):
        final_result = _substitute_vars(result, env, context=context)
    else:
        final_result = result

    print("[DEBUG RENDER] Final rendered result:", final_result)
    node.resolved = final_result
    return final_result

def _substitute_vars(expr: str, env: Dict[str, Any], context: Dict[str, Any] = None, quote_strings: bool = True) -> Any:
    print("[DEBUG SUB] Substituting in:", expr)
    
    def _extract_value(x: Any) -> Any:
        from .ast_nodes import PreservedString
        if isinstance(x, PreservedString):
            return x.value
        return x

    def resolve_var(var: str, prefix: str) -> Any:
        if not var.strip():
            return f"{prefix}{{}}"
        keys = var.strip().split('.')
        if prefix == '$':
            val = context if context is not None else {}
        else:
            val = env
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            elif isinstance(val, (list, tuple)) and key.isdigit():
                val = val[int(key)]
            else:
                return f"{prefix}{{{var}}}"
        val = _extract_value(val)
        return repr(val) if quote_strings and isinstance(val, str) else val

    if not expr.strip():
        return ""

    if re.match(r'^[@%$]\{[^}]+\}$', expr):
        prefix = expr[0]
        var = expr[2:-1]
        return resolve_var(var, prefix)

    for prefix, replacer in [
        (r'\$\{([^}]*)\}', lambda m: resolve_var(m.group(1), '$')),
        (r'%\{([^}]*)\}', lambda m: resolve_var(m.group(1), '%')),
        (r'@\{([^}]*)\}', lambda m: resolve_var(m.group(1), '@'))
    ]:
        expr = re.sub(prefix, replacer, expr)
    
    return expr

def extract_header_env(header, env):
    if isinstance(header, ComprehensionHeader):
        header_env = {}
        if header.clauses:
            for clause in header.clauses.clauses:
                for var in clause.loop_vars:
                    var_name = str(var).strip()
                    header_env[var_name] = env.get(var_name, None)
        return header_env
    return {}