# api.py

import os
from typing import IO, Any, Dict

# If you have helper modules for evaluating expressions or merges:
from ._eval import _eval_ast_logical_expressions
from ._helpers import _process_table_merges

# Core JML modules
from .parser import JMLParser
from .unparser import JMLUnparser
from .ast_nodes import (
    DocumentNode,
    SectionNode,
    KeyValueNode,
    ScalarNode,
    ArrayNode,
    TableNode,
    LogicExpressionNode,
)

# -------------------------------------
# 1) File Extension Helper (optional)
# -------------------------------------

def check_extension(filename: str) -> None:
    """
    Ensure the filename has a supported extension (.jml or .jaml).
    
    :param filename: Name of the file.
    :raises ValueError: If the extension is not supported.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ('.jml', '.jaml'):
        raise ValueError("Unsupported file extension. Allowed: .jml or .jaml")

# -------------------------------------
# 2) Non-Round-Trip Helpers
# -------------------------------------

def _ast_to_plain(ast: DocumentNode) -> Dict[str, Dict[str, Any]]:
    """
    Convert a DocumentNode AST into a plain Python dictionary.
    This discards comments, merges, and formatting, preserving only the data.
    """
    return ast.to_plain_data()

def _plain_to_ast(data: Dict[str, Dict[str, Any]]) -> DocumentNode:
    """
    Convert a plain Python dictionary into a minimal DocumentNode.
    This is used for simple dumps().
    """
    document = DocumentNode()
    for section_name, kv_pairs in data.items():
        section_node = SectionNode(name=section_name)
        for key, raw_value in kv_pairs.items():
            value_node = _plain_value_to_ast_node(raw_value)
            # Attempt a basic type_annotation
            type_annotation = _guess_basic_type_annotation(raw_value)
            kv_node = KeyValueNode(key=key, type_annotation=type_annotation, value=value_node)
            section_node.keyvalues.append(kv_node)
        document.sections.append(section_node)
    return document

def _plain_value_to_ast_node(value: Any):
    """
    Convert a Python scalar, list, or dict into an AST node:
      - str, bool, int, float, None -> ScalarNode
      - list -> ArrayNode
      - dict -> TableNode
    """
    if isinstance(value, (str, bool, int, float)) or value is None:
        return ScalarNode(value=value)
    elif isinstance(value, list):
        items = [_plain_value_to_ast_node(v) for v in value]
        return ArrayNode(items=items)
    elif isinstance(value, dict):
        kv_nodes = []
        for k, v in value.items():
            val_node = _plain_value_to_ast_node(v)
            kv_nodes.append(KeyValueNode(key=k, value=val_node))
        return TableNode(keyvalues=kv_nodes)
    else:
        # Fallback: store as string
        return ScalarNode(value=str(value))

def _guess_basic_type_annotation(value: Any) -> str:
    """
    A naive guess of the type annotation for non-round-trip usage.
    """
    if isinstance(value, str):
        return "str"
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "float"
    elif value is None:
        return "null"
    elif isinstance(value, list):
        return "list"
    elif isinstance(value, dict):
        return "table"
    else:
        return "unknown"

def _plain_dumps(data: Dict[str, Dict[str, Any]]) -> str:
    """
    Create a minimal JML string for a plain dictionary:
    
        [section_name]
        key: type = value
    """
    ast = _plain_to_ast(data)
    # Use a custom unparser for minimal style, or just re-use the round-trip unparser
    unparser = JMLUnparser(ast)
    return unparser.unparse()

# -------------------------------------
# 3) Non-Round-Trip API
# -------------------------------------

def dumps(obj: Dict[str, Any]) -> str:
    """
    Serialize a plain Python dict into a minimal JML string (non-round-trip).
    Discards comments, merges, or advanced formatting.
    """
    return _plain_dumps(obj)

def dump(obj: Dict[str, Any], fp: IO[str]) -> None:
    """
    Serialize a plain dict into JML and write to a file-like object (non-round-trip).
    """
    fp.write(dumps(obj))

def loads(s: str) -> Dict[str, Any]:
    """
    Parse a JML string (non-round-trip), returning a plain Python dict of data.
    This discards formatting and merges.
    """
    parser = JMLParser()
    ast_document = parser.parse(s)
    return _ast_to_plain(ast_document)

def load(fp: IO[str]) -> Dict[str, Any]:
    """
    Parse JML content from a file-like object into a plain dict (non-round-trip).
    """
    return loads(fp.read())

# -------------------------------------
# 4) Round-Trip API
# -------------------------------------

def round_trip_dumps(ast: DocumentNode) -> str:
    """
    Serialize a DocumentNode AST back to a JML-formatted string,
    preserving layout, comments, merges, etc. (as far as your unparser allows).
    """
    unparser = JMLUnparser(ast)
    return unparser.unparse()

def round_trip_dump(ast: DocumentNode, fp: IO[str]) -> None:
    """
    Serialize a DocumentNode AST into JML, writing to a file-like object (round-trip).
    """
    fp.write(round_trip_dumps(ast))

def round_trip_loads(s: str) -> DocumentNode:
    """
    Parse a JML string into a DocumentNode AST, preserving all data
    for round-trip usage (including comments, merges, layout if your parser tracks them).
    """
    parser = JMLParser()
    ast = parser.parse(s)
    # If you have merges or other post-processing:
    ast = _process_table_merges(ast)
    return ast

def round_trip_load(fp: IO[str]) -> DocumentNode:
    """
    Parse JML content from a file-like object into a DocumentNode AST, preserving round-trip data.
    """
    return round_trip_loads(fp.read())

# -------------------------------------
# 5) Render API (optional advanced usage)
# -------------------------------------

def render(input_jml: str, context: dict = None) -> str:
    """
    Render a JML string by processing merges, logic expressions, or other dynamic features,
    while preserving as much original formatting as possible.
    
    :param input_jml: The JML text to process.
    :param context: Optional dictionary of variables for logic expressions.
    :return: The transformed JML string.
    """
    if context is None:
        context = {}

    # 1) Parse into an AST (round-trip mode).
    ast = round_trip_loads(input_jml)

    # 2) Evaluate expressions (if you have that functionality):
    ast = _eval_ast_logical_expressions(ast, context)

    # 3) Process merges (if your language supports table merges):
    ast = _process_table_merges(ast)

    # 4) Unparse the result back to JML, preserving comments/format.
    return round_trip_dumps(ast)
