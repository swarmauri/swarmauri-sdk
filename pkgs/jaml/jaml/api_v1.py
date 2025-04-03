"""
api.py

This module provides the public API for our custom JML markup language.

There are two sets of methods:

1. Non-Round-Trip Methods:
   - dump, dumps, load, loads
   These methods convert between a plain JML string and a plain Python dict,
   without preserving comments or formatting.

2. Round-Trip Methods:
   - round_trip_dump, round_trip_dumps, round_trip_load, round_trip_loads
   These methods convert between a JML string (or file) and an AST (DocumentNode),
   preserving the original formatting, comments, and logical expressions.

Supported file extensions: .jml, .jaml
"""

import os
from ._eval import _eval_ast_logical_expressions
from ._helpers import _process_table_merges
from .parser import JMLParser
from .unparser import JMLUnparser
from .ast_nodes import DocumentNode, SectionNode, KeyValueNode, ScalarNode, ArrayNode, TableNode, LogicExpressionNode

# --- File Extension Check ---

def check_extension(filename: str) -> None:
    """
    Ensure the filename has a supported extension (.jml or .jaml).
    
    :param filename: Name of the file.
    :raises ValueError: If the extension is not supported.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ('.jml', '.jaml'):
        raise ValueError("Unsupported file extension. Supported extensions are .jml and .jaml")

# --- Helpers for Non Round-Trip Conversion ---

def _ast_to_plain(ast: DocumentNode) -> dict:
    """
    Convert a DocumentNode AST into a plain Python dictionary.
    This strips out comments, formatting, and preserves only the key-value data.
    
    :param ast: The DocumentNode to convert.
    :return: A plain dict representation.
    """
    plain = {}
    for section in ast.sections:
        sec_dict = {}
        for kv in section.keyvalues:
            # For non-round-trip, we assume that if a logical expression exists,
            # its value has been computed externally. Here, we extract the simple value.
            if hasattr(kv.value, "value"):
                sec_dict[kv.key] = kv.value.value
            else:
                sec_dict[kv.key] = kv.value
        plain[section.name] = sec_dict
    return plain

def _plain_to_ast(obj: dict) -> DocumentNode:
    """
    Convert a plain Python dictionary into a DocumentNode AST.
    This is a basic conversion that does not preserve original formatting or comments.
    
    :param obj: The plain dictionary.
    :return: A DocumentNode representing the data.
    """
    sections = []
    for sec_name, content in obj.items():
        kv_nodes = []
        for key, value in content.items():
            # Determine type annotation based on Python type.
            if isinstance(value, str):
                type_annotation = "str"
                scalar = ScalarNode(value=value)
            elif isinstance(value, bool):
                type_annotation = "bool"
                scalar = ScalarNode(value=value)
            elif isinstance(value, int):
                type_annotation = "int"
                scalar = ScalarNode(value=value)
            elif isinstance(value, float):
                type_annotation = "float"
                scalar = ScalarNode(value=value)
            elif value is None:
                type_annotation = "null"
                scalar = ScalarNode(value=None)
            elif isinstance(value, list):
                type_annotation = "list"
                scalar = ArrayNode(items=[ScalarNode(item) for item in value])
            elif isinstance(value, dict):
                type_annotation = "table"
                kvs = []
                for k, v in value.items():
                    kvs.append(KeyValueNode(key=k, type_annotation="str", value=ScalarNode(v)))
                scalar = TableNode(keyvalues=kvs)
            else:
                type_annotation = "unknown"
                scalar = ScalarNode(value=str(value))
            kv = KeyValueNode(key=key, type_annotation=type_annotation, value=scalar)
            kv_nodes.append(kv)
        section_node = SectionNode(name=sec_name, keyvalues=kv_nodes)
        sections.append(section_node)
    return DocumentNode(sections=sections)

def plain_dumps(obj: dict) -> str:
    """
    Serialize a plain Python dict into a simple JML-formatted string.
    This method does not preserve comments or formatting.
    
    :param obj: The plain dict to serialize.
    :return: A JML-formatted string.
    """
    lines = []
    for section, content in obj.items():
        lines.append(f"[{section}]")
        for key, value in content.items():
            if isinstance(value, str):
                type_ann = "str"
                val_str = f'"{value}"'
            elif isinstance(value, bool):
                type_ann = "bool"
                val_str = "true" if value else "false"
            elif isinstance(value, int):
                type_ann = "int"
                val_str = str(value)
            elif isinstance(value, float):
                type_ann = "float"
                val_str = str(value)
            elif value is None:
                type_ann = "null"
                val_str = "null"
            elif isinstance(value, list):
                type_ann = "list"
                items = ", ".join(f'"{item}"' if isinstance(item, str) else str(item) for item in value)
                val_str = f"[{items}]"
            elif isinstance(value, dict):
                type_ann = "table"
                items = ", ".join(f'{k} = "{v}"' if isinstance(v, str) else f'{k} = {v}' for k, v in value.items())
                val_str = f"{{ {items} }}"
            else:
                type_ann = "unknown"
                val_str = str(value)
            lines.append(f"{key}: {type_ann} = {val_str}")
        lines.append("")
    return "\n".join(lines)

def plain_dump(obj: dict, fp) -> None:
    """
    Serialize a plain dict into JML format (non round-trip) and write to a file-like object.
    
    :param obj: The plain dict to serialize.
    :param fp: A file-like object opened for writing.
    """
    s = plain_dumps(obj)
    fp.write(s)

# --- Non Round-Trip Methods (Plain Text) ---

def loads(s: str) -> dict:
    # Parse text into an AST (maybe the same parser or a simpler parser).
    parser = JMLParser()
    ast_document = parser.parse(s)
    # Convert the AST to a plain Python dict.
    plain_data = ast_document.to_plain_data()
    return plain_data


def load(fp,) -> dict:
    """
    Deserialize JML content from a file-like object (non round-trip) into a plain Python dict.
    
    :param fp: A file-like object opened for reading.
    :param context: Optional context.
    :return: A plain dict representation.
    """
    s = fp.read()
    return loads(s)

def dumps(obj: dict) -> str:
    """
    Serialize a plain Python dict into a JML-formatted string (non round-trip).
    This does not preserve original formatting or comments.
    
    :param obj: The plain dict.
    :return: A JML-formatted string.
    """
    return plain_dumps(obj)

def dump(obj: dict, fp) -> None:
    """
    Serialize a plain Python dict into JML format (non round-trip) and write to a file-like object.
    
    :param obj: The plain dict.
    :param fp: A file-like object opened for writing.
    """
    s = dumps(obj)
    fp.write(s)

# --- Round-Trip Methods (Working with AST) ---

def round_trip_loads(s: str) -> DocumentNode:
    """
    Deserialize JML content from a string into a DocumentNode AST,
    preserving formatting, comments, and logical expressions.
    
    :param s: A JML-formatted string.
    :param context: Optional context for dynamic evaluations.
    :return: A DocumentNode AST.
    """
    parser = JMLParser()
    ast = parser.parse(s)
    ast = _process_table_merges(ast)
    # (Optionally, evaluate dynamic logic using 'context' here)
    return ast

def round_trip_load(fp) -> DocumentNode:
    """
    Deserialize JML content from a file-like object into a DocumentNode AST.
    
    :param fp: A file-like object opened for reading.
    :param context: Optional context.
    :return: A DocumentNode AST.
    """
    s = fp.read()
    return round_trip_loads(s)

def round_trip_dumps(ast: DocumentNode) -> str:
    """
    Serialize a DocumentNode AST back into a JML-formatted string,
    preserving original formatting, comments, and logical expressions.
    
    :param ast: The DocumentNode AST.
    :return: A JML-formatted string.
    """
    unparser = JMLUnparser(ast)
    return unparser.unparse()

def round_trip_dump(ast: DocumentNode, fp) -> None:
    """
    Serialize a DocumentNode AST and write the JML-formatted string to a file-like object.
    
    :param ast: The DocumentNode AST.
    :param fp: A file-like object opened for writing.
    """
    s = round_trip_dumps(ast)
    fp.write(s)

# --- Rendering Methods ---


def render(input_jml: str, context: dict = {}) -> str:
    """
    Render a JML string by processing logical expressions and alias merging.
    This preserves formatting, comments, and performs dynamic evaluations.
    """
    # Parse into an AST (round-trip mode).
    ast = round_trip_loads(input_jml)
    # Evaluate logical expressions.
    ast = _eval_ast_logical_expressions(ast, context)
    # Process merge operators in tables.
    ast = _process_table_merges(ast)
    # Dump the AST back to a JML string.
    return round_trip_dumps(ast)
