from typing import Dict, Any
import re
from lark import Token
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

def substitute_deferred(ast_node, env, context=None, section_data=None):
    print("[DEBUG RENDER] Processing node of type:", type(ast_node))
    print("[DEBUG RENDER] Environment:", env)
    print("[DEBUG RENDER] Context:", context)
    print("[DEBUG RENDER] Section data:", section_data)

    if isinstance(ast_node, dict) and {"_annotation", "_value"}.issubset(ast_node):
        return substitute_deferred(ast_node["_value"], env, context, section_data)

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

        def evaluate_clauses(clauses, index, env):
            if index >= len(clauses.clauses):
                try:
                    header_val = evaluate_f_string(
                        str(header_expr),
                        global_data=env,
                        local_data=env,
                        context=context
                    )
                    print("[DEBUG RENDER] Header value:", header_val)
                    table = {"__header__": header_val}
                    for alias in ast_node.aliases:
                        table[alias] = env.get(alias)
                    if hasattr(ast_node, 'inline_assignments') and ast_node.inline_assignments:
                        table.update(substitute_deferred(ast_node.inline_assignments, env, context))
                    elif header_val in env:
                        table.update(substitute_deferred(env[header_val], env, context))
                    result[header_val] = table
                except Exception as e:
                    print("[DEBUG RENDER] Failed to evaluate header:", e)
                return

            clause = clauses.clauses[index]
            iterable = substitute_deferred(clause.iterable, env, context)
            print("[DEBUG RENDER] Iterable resolved to:", iterable)
            if iterable is None or iterable == clause.iterable:
                print("[DEBUG RENDER] Error: Iterable not substituted:", clause.iterable)
                iterable = []
            if not isinstance(iterable, (list, tuple)):
                print("[DEBUG RENDER] Warning: Iterable is not a sequence:", iterable)
                iterable = [iterable] if iterable else []

            for item in iterable:
                for var in clause.loop_vars:
                    if isinstance(var, tuple) and len(var) == 2:
                        var_name, alias_clause = var
                        var_name = str(var_name)
                        env[var_name] = item
                        alias_match = re.match(r'[@%$]\{([^}]+)\}', alias_clause.scoped_var)
                        if alias_match:
                            alias_name = alias_match.group(1)
                            env[alias_name] = item
                            print("[DEBUG RENDER] Set alias:", alias_name, "=", item)
                        else:
                            print("[DEBUG RENDER] Warning: Malformed alias:", alias_clause.scoped_var)
                    else:
                        env[str(var)] = item
                        print("[DEBUG RENDER] Set loop var:", str(var), "=", item)

                conditions_pass = True
                for cond in clause.conditions:
                    try:
                        cond_str = " ".join(str(c) for c in cond if not isinstance(c, Token) or c.type != "NEWLINE")
                        parts = cond_str.split('.')
                        current = env
                        for part in parts:
                            if isinstance(current, dict) and part in current:
                                current = current[part]
                            else:
                                print("[DEBUG RENDER] Failed to resolve condition part:", part)
                                conditions_pass = False
                                break
                        else:
                            cond_val = bool(current)
                            print("[DEBUG RENDER] Condition", cond_str, "=", cond_val)
                            if not cond_val:
                                conditions_pass = False
                                break
                    except Exception as e:
                        print("[DEBUG RENDER] Failed to evaluate condition:", cond, "Error:", e)
                        conditions_pass = False
                        break
                if conditions_pass:
                    evaluate_clauses(clauses, index + 1, env.copy())

        evaluate_clauses(clauses, 0, local_env)
        print("[DEBUG RENDER] ComprehensionHeader result:", result)
        return result

    if isinstance(ast_node, FoldedExpressionNode):
        return _render_folded_expression_node(ast_node, env, context)

    if isinstance(ast_node, dict):
        local_env = env.copy() if isinstance(env, dict) else {}
        result = {}

        # First pass: Build hierarchical local_env mirroring AST structure
        for k, v in ast_node.items():
            if k == "__comments__":
                continue
            if isinstance(k, (ComprehensionHeader, TableArrayHeader)):
                # Headers will be processed later
                continue
            if isinstance(v, dict):
                # Section: Create nested dictionary and process assignments
                section_env = local_env.setdefault(k, {})
                for sk, sv in v.items():
                    # Render sub-value with section-specific local_data
                    section_env[sk] = substitute_deferred(sv, local_env, context, section_data=section_env)
                    print("[DEBUG RENDER] Set local_env[{}][{}] = {}".format(k, sk, section_env[sk]))
            else:
                # Simple assignment at root level
                local_env[k] = substitute_deferred(v, local_env, context, section_data=None)
                print("[DEBUG RENDER] Set local_env[{}] = {}".format(k, local_env[k]))

        # Second pass: Process ComprehensionHeader keys
        for k, v in ast_node.items():
            if isinstance(k, ComprehensionHeader):
                header_val = substitute_deferred(k, local_env, context)
                result.update(header_val)
                local_env.update({hk: hv for hk, hv in header_val.items()})

        # Third pass: Assign final values to result
        for k, v in ast_node.items():
            if k == "__comments__":
                result[k] = v
                continue
            if isinstance(k, ComprehensionHeader):
                continue
            if isinstance(k, TableArrayHeader):
                header_val = k.original.strip('[]') if hasattr(k, 'original') else str(k)
                k = header_val
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
                # Use pre-rendered value from local_env
                result[k] = local_env[k]
                print("[DEBUG RENDER] Assigned result[{}] = {}".format(k, result[k]))

        return result

    if isinstance(ast_node, list):
        return [substitute_deferred(item, env, context, section_data) for item in ast_node]

    if isinstance(ast_node, PreservedString):
        s = ast_node.origin
        if s.strip() == "":
            return ""
        if s.lstrip().startswith(("f\"", "f'")):
            # Use section_data if provided for local scope, else fall back to env
            local_data = section_data if section_data is not None else env
            result = evaluate_f_string(s.lstrip(), global_data=env, local_data=local_data, context=context)
            print("[DEBUG RENDER] Resolved f-string {} to {}".format(s, result))
            return result
        return _substitute_vars(ast_node, env, context=context)

    if isinstance(ast_node, str):
        if ast_node.strip() == "":
            return ""
        if ast_node.lstrip().startswith(("f\"", "f'")):
            local_data = section_data if section_data is not None else env
            result = evaluate_f_string(ast_node.lstrip(), global_data=env, local_data=local_data, context=context)
            print("[DEBUG RENDER] Resolved f-string {} to {}".format(ast_node, result))
            return result
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
        current = val
        print("[DEBUG SUB] Resolving", f"{prefix}{{{var}}}", "with keys:", keys, "in env:", current)
        for i, key in enumerate(keys):
            try:
                if isinstance(current, dict):
                    current = current[key]
                elif isinstance(current, (list, tuple)) and key.isdigit():
                    current = current[int(key)]
                elif i == 0 and prefix in ('@', '%'):
                    if key in current:
                        current = current[key]
                    else:
                        print("[DEBUG SUB] Alias not found:", key)
                        return f"{prefix}{{{var}}}"
                else:
                    print("[DEBUG SUB] Failed to resolve key:", key, "in:", current)
                    return f"{prefix}{{{var}}}"
            except (KeyError, IndexError, TypeError) as e:
                print("[DEBUG SUB] Resolution error for:", f"{prefix}{{{var}}}", "at key:", key, "Error:", e)
                return f"{prefix}{{{var}}}"
        current = _extract_value(current)
        print("[DEBUG SUB] Resolved", f"{prefix}{{{var}}}", "to:", current)
        return repr(current) if quote_strings and isinstance(current, str) else current

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
    
    print("[DEBUG SUB] Final substituted expr:", expr)
    return expr

def extract_header_env(header, env):
    if isinstance(header, ComprehensionHeader):
        header_env = {}
        for alias in header.aliases:
            header_env[alias] = env.get(alias, None)
        return header_env
    return {}

