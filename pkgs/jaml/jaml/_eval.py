# _eval.py

from typing import Any, Dict

from .ast_nodes import (
    DocumentNode,
    SectionNode,
    KeyValueNode,
    ScalarNode,
    ArrayNode,
    TableNode,
    LogicExpressionNode,
)


def _eval_ast_logical_expressions(ast: DocumentNode, context: Dict[str, Any] = None) -> DocumentNode:
    """
    Traverse the entire AST, evaluating LogicExpressionNode nodes using the given context.
    Returns the same AST with any logic expressions replaced by their evaluated results 
    (usually as ScalarNode or TableNode, depending on what the expression yields).
    
    :param ast: The DocumentNode AST.
    :param context: A dictionary for variable bindings or function references used in expressions.
    :return: The AST with logic expressions evaluated.
    """
    if context is None:
        context = {}

    for section in ast.sections:
        for i, kv in enumerate(section.keyvalues):
            evaluated_value = _evaluate_node(kv.value, context)
            kv.value = evaluated_value

    return ast


def _evaluate_node(node, context: Dict[str, Any]):
    """
    Recursively evaluate a node:
      - If it's a LogicExpressionNode, parse/eval the expression
      - If it's an ArrayNode, evaluate each item
      - If it's a TableNode, evaluate each key-value
      - Otherwise (ScalarNode, etc.), return it as is
    """
    if isinstance(node, LogicExpressionNode):
        return _eval_logic_expression(node, context)

    elif isinstance(node, ArrayNode):
        # Evaluate each item in the array
        new_items = []
        for item in node.items:
            new_items.append(_evaluate_node(item, context))
        return ArrayNode(items=new_items)

    elif isinstance(node, TableNode):
        # Evaluate each key-value in the table
        new_kvs = []
        for kv in node.keyvalues:
            evaluated_value = _evaluate_node(kv.value, context)
            new_kvs.append(KeyValueNode(
                key=kv.key,
                type_annotation=kv.type_annotation,
                value=evaluated_value
            ))
        return TableNode(keyvalues=new_kvs)

    # For ScalarNode or other types, just return as is
    return node


def _eval_logic_expression(expr_node: LogicExpressionNode, context: Dict[str, Any]):
    """
    Evaluate the LogicExpressionNode using your language rules. 
    This function can parse the expression syntax and produce a result (e.g., Python value).
    
    Return a new Node representing the result (often a ScalarNode).
    
    Example: If your expression is a simple Python snippet like "x + 1",
    you might do something like:
    
        code = compile(expr_node.expression, "<jml_expr>", "eval")
        value = eval(code, {}, context)
        return ScalarNode(value=value)
    
    BUT be aware that using eval can be a security risk if you parse untrusted input.
    You might want to parse it yourself or use a safer method.
    
    If your language has custom syntax, parse it here and evaluate accordingly.
    """
    expr_str = expr_node.expression

    # Example: naive usage of Python eval (NOT recommended for untrusted input)
    try:
        code = compile(expr_str, "<jml_expr>", "eval")
        result = eval(code, {}, context)
    except Exception as e:
        # Handle or log the error as needed
        result = f"<Error evaluating expression: {expr_str}>"

    # Return a ScalarNode with the result. If result is a list/dict/bool,
    # you could optionally convert it to an ArrayNode, TableNode, or so forth.
    return ScalarNode(value=result)
