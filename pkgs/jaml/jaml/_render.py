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
from ._eval import safe_eval

def substitute_deferred(ast_node, env, context=None):
    print("[DEBUG RENDER] Processing node of type:", type(ast_node))

    if isinstance(ast_node, dict) and {"_annotation", "_value"}.issubset(ast_node):
        return substitute_deferred(ast_node["_value"], env, context)

    if isinstance(ast_node, (DeferredDictComprehension, DeferredListComprehension)):
        return ast_node.evaluate(env, context=context)

    if isinstance(ast_node, ComprehensionHeader):
        print("[DEBUG RENDER] Evaluating ComprehensionHeader:", ast_node)
        local_env = env.copy() if isinstance(env, dict) else {}
        result = {}
        clauses = ast_node.clauses
        if not clauses:
            print("[DEBUG RENDER] No clauses in ComprehensionHeader")
            return result
        header_expr = ast_node.header_expr
        # Iterate over clauses
        def evaluate_clauses(clauses, index, env):
            if index >= len(clauses.clauses):
                # Base case: evaluate header and create table
                try:
                    header_val = evaluate_f_string(str(header_expr), global_data=env, local_data=env, context=context)
                    table = {"__header__": header_val}
                    # Add alias KV pairs
                    for alias in ast_node.aliases:
                        table[alias] = env.get(alias)
                    # Merge existing assignments
                    if header_val in env:
                        table.update(substitute_deferred(env[header_val], env, context))
                    result[header_val] = table
                except Exception as e:
                    print("[DEBUG RENDER] Failed to evaluate header:", e)
                return
            clause = clauses.clauses[index]
            # Evaluate iterable
            iterable = substitute_deferred(clause.iterable, env, context)
            # Iterate over items
            for item in iterable:
                # Set loop variables
                for var in clause.loop_vars:
                    if isinstance(var, tuple) and len(var) == 2:
                        var_name, alias_clause = var
                        env[str(var_name)] = item
                        alias_name = re.match(r'[@%$]\{([^}]+)\}', alias_clause.scoped_var).group(1)
                        env[alias_name] = item
                    else:
                        env[str(var)] = item
                # Evaluate conditions
                conditions_pass = True
                for cond in clause.conditions:
                    try:
                        cond_val = safe_eval(str(cond), local_env=env)
                        if not cond_val:
                            conditions_pass = False
                            break
                    except Exception as e:
                        print("[DEBUG RENDER] Failed to evaluate condition:", e)
                        conditions_pass = False
                        break
                if conditions_pass:
                    evaluate_clauses(clauses, index + 1, env.copy())
        evaluate_clauses(clauses, 0, local_env)
        return result

    if isinstance(ast_node, FoldedExpressionNode):
        return _render_folded_expression_node(ast_node, env, context=context)

    if isinstance(ast_node, dict):
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
                k = header_val  # Defer evaluation to ComprehensionHeader branch
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

    if isinstance(ast_node, list):
        return [substitute_deferred(item, env, context) for item in ast_node]

    if isinstance(ast_node, PreservedString):
        s = ast_node.origin
        if s.strip() == "":
            return ""
        if s.lstrip().startswith(("f\"", "f'")):
            return evaluate_f_string(s.lstrip(), global_data=env, local_data=env, context=context)
        return _substitute_vars(ast_node.value, env, context=context)

    if isinstance(ast_node, str):
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
                print("[DEBUG SUB] Failed to resolve:", f"{prefix}{{{var}}}")
                return f"{prefix}{{{var}}}"
        val = _extract_value(val)
        return repr(val) if quote_strings and isinstance(val, str) else val

    if not expr.strip():
        return ""

    # Handle full variable expressions
    if re.match(r'^[@%$]\{[^}]+\}$', expr):
        prefix = expr[0]
        var = expr[2:-1]
        return resolve_var(var, prefix)

    # Substitute within strings
    def replace_var(match):
        prefix = match.group(1) or ''
        var = match.group(2)
        return str(resolve_var(var, prefix))

    expr = re.sub(r'([@%$])?\{([^}]+)\}', replace_var, expr)
    
    # Clean up spaces and quotes for paths
    if '/' in expr:
        expr = expr.replace(" / ", "/").strip("'").strip('"')
    
    return expr

def extract_header_env(header, env):
    if isinstance(header, ComprehensionHeader):
        header_env = {}
        for alias in header.aliases:
            header_env[alias] = env.get(alias, None)
        return header_env
    return {}