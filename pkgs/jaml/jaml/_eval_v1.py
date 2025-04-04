import re
from .ast_nodes import DocumentNode, SectionNode, KeyValueNode, ScalarNode, ArrayNode, TableNode, LogicExpressionNode

def _eval_ast_logical_expressions(ast: DocumentNode, context: dict) -> DocumentNode:
    # Helper to resolve values from the external context.
    def _resolve_context(path: str):
        parts = path.split('.')
        val = context
        for part in parts:
            if not isinstance(val, dict):
                return None
            val = val.get(part)
            if val is None:
                return None
        return val

    # Process each section and key-value pair.
    for section in ast.sections:
        for kv in section.keyvalues:
            if kv.logic is not None:
                raw_expr = kv.logic.raw_text
                if raw_expr.startswith("~(") and raw_expr.endswith(")"):
                    inner_expr = raw_expr[2:-1].strip()
                else:
                    inner_expr = raw_expr

                # Use str() conversion for context and AST lookups if type_annotation is "str"
                if kv.type_annotation == "str":
                    inner_expr = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_.]*)', r'str(_get_context("\1"))', inner_expr)
                    inner_expr = re.sub(r'@([a-zA-Z_][a-zA-Z0-9_.]*)', r'str(_get_ast("\1"))', inner_expr)
                else:
                    inner_expr = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_.]*)', r'_get_context("\1")', inner_expr)
                    inner_expr = re.sub(r'@([a-zA-Z_][a-zA-Z0-9_.]*)', r'_get_ast("\1")', inner_expr)

                # Define a local _resolve_ast that takes into account the current section for local references.
                def _resolve_ast(path: str, current_section=section):
                    parts = path.split('.')
                    if len(parts) == 1:
                        key = parts[0]
                        for local_kv in current_section.keyvalues:
                            if local_kv.key == key:
                                return local_kv.value.value if hasattr(local_kv.value, "value") else None
                        return None
                    else:
                        section_name = parts[0]
                        key = parts[1]
                        for sec in ast.sections:
                            if sec.name == section_name:
                                for kv_item in sec.keyvalues:
                                    if kv_item.key == key:
                                        return kv_item.value.value if hasattr(kv_item.value, "value") else None
                        return None

                safe_context = {
                    "true": True,
                    "false": False,
                    "_get_context": _resolve_context,
                    "_get_ast": _resolve_ast,
                    "str": str,
                }
                if context:
                    safe_context.update(context)

                try:
                    result = eval(inner_expr, {"__builtins__": {}}, safe_context)
                except Exception as e:
                    result = f"Error: {e}"

                # Update the AST node based on the type of result.
                if isinstance(result, list):
                    result_nodes = [ScalarNode(value=item) for item in result]
                    kv.value = ArrayNode(items=result_nodes)
                    kv.type_annotation = "list"
                elif isinstance(result, dict):
                    result_kvs = []
                    for k, v in result.items():
                        result_kvs.append(KeyValueNode(key=k, type_annotation="str", value=ScalarNode(value=v)))
                    kv.value = TableNode(keyvalues=result_kvs)
                    kv.type_annotation = "table"
                else:
                    kv.value = ScalarNode(value=result)
                    if isinstance(result, str):
                        kv.type_annotation = "str"
                    elif isinstance(result, bool):
                        kv.type_annotation = "bool"
                    elif isinstance(result, int):
                        kv.type_annotation = "int"
                    elif isinstance(result, float):
                        kv.type_annotation = "float"
                    elif result is None:
                        kv.type_annotation = "null"
                    else:
                        kv.type_annotation = "unknown"
                kv.logic = None
    return ast
