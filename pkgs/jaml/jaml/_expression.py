# jaml/_expression.py
from lark import Tree, Token
from typing import Dict, Any, Optional, List
from ._eval import safe_eval
from ._substitute import _substitute_vars

def evaluate_expression_tree(tree: Tree, global_env: Dict, local_env: Optional[Dict] = None, context: Optional[Dict] = None) -> str:
    from ._ast_nodes import BaseNode

    local_env = local_env or {}
    context = context or {}
    
    def evaluate_node(node: Any) -> Any:
        if isinstance(node, BaseNode):
            node.resolve(global_env, local_env, context)
            return node.resolved
        elif isinstance(node, Token):
            if node.type == "OPERATOR":
                return node.value
            elif node.type == "STRING":
                return node.value.strip('"\'')
            elif node.type == "INTEGER":
                return int(node.value, 0)
            elif node.type == "FLOAT":
                return float(node.value)
            elif node.type == "BOOLEAN":
                return node.value == "true"
            elif node.type == "SCOPED_VAR":
                var = node.value
                if var.startswith("${"):
                    return var
                return _substitute_vars(var, global_env, local_env, quote_strings=False)
        elif isinstance(node, Tree) and node.data == "folded_content":
            return evaluate_expression(node.children)
        return str(node)

    def evaluate_expression(nodes: List[Any]) -> str:
        parts = [evaluate_node(n) for n in nodes]
        if any(isinstance(p, str) and p.startswith("${") for p in parts):
            return "<(" + " ".join(str(p) for p in parts) + ")>"
        
        expr_string = " ".join(str(p) for p in parts)
        try:
            if re.fullmatch(r'[\d\s+\-*/().]+', expr_string):
                return str(eval(compile(expr_string, "<string>", "eval"), {}, {}))
            return str(safe_eval(expr_string, local_env=local_env))
        except Exception:
            return expr_string

    return evaluate_expression(tree.children)

def _render_folded_expression_node(node, env: Dict[str, Any], context: Optional[Dict] = None) -> Any:
    from ._ast_nodes import BaseNode, FoldedExpressionNode
    if hasattr(node, 'resolved') and node.resolved is not None:
        if isinstance(node.resolved, str) and '${' in node.resolved:
            expr = node.resolved.lstrip('<(').rstrip(')>')
            parts = expr.split()
            result = []
            i = 0
            while i < len(parts):
                part = parts[i]
                if part.startswith('${'):
                    key = part.lstrip('${').rstrip('}')
                    if key not in context:
                        raise KeyError(f"Missing context variable: {part}")
                    result.append(str(context[key]))
                elif i + 1 < len(parts) and parts[i + 1] == "+":
                    result.append(part)
                    i += 1
                else:
                    result.append(part)
                i += 1
            return "".join(result)
        return node.resolved
    return evaluate_expression_tree(node.content_tree, env, env, context)