import os
from typing import IO, Any, Dict

# If you have helper modules for evaluating expressions or merges:
# from ._eval import _eval_ast_logical_expressions

# Core JML modules
# from .parser import JMLParser
from .lark_parser import parser
from .lark_nodes import ConfigTransformer

from .unparser import JMLUnparser
from .ast_nodes import DocumentNode

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
# 2) Non-Round-Trip API
# -------------------------------------

def dumps(obj: Dict[str, Any]) -> str:
    """
    Serialize a plain Python dict into a minimal JML string (non-round-trip).
    Discards comments, merges, or advanced formatting.
    
    This implementation converts the plain dict to an AST by invoking the
    bound class method `from_plain_data()` on DocumentNode, then unparses it.
    Leading and trailing whitespace in string values is preserved.
    """
    # Convert the plain dictionary to an AST.
    ast_document = DocumentNode.from_plain_data(obj)
    # Unparse the AST back to a JML string.
    unparser = JMLUnparser(ast_document)
    return unparser.unparse()

def dump(obj: Dict[str, Any], fp: IO[str]) -> None:
    """
    Serialize a plain dict into JML and write to a file-like object (non-round-trip).
    """
    fp.write(dumps(obj))

def loads(s: str) -> Dict[str, Any]:
    """
    Parse a JML string into a plain Python dictionary.
    Returns native types (e.g. plain strings, ints, lists, dicts),
    not AST nodes.
    """
    # parser = JMLParser()
    ast_tree = parser.parse(s)
    # Convert the AST to plain data using the bound method on DocumentNode.
    return ConfigTransformer().transform(ast_tree)

def load(fp: IO[str]) -> Dict[str, Any]:
    """
    Parse JML content from a file-like object into a plain dictionary.
    """
    return loads(fp.read())

# -------------------------------------
# 3) Round-Trip API
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
    # parser = JMLParser()
    return parser.parse(s)

def round_trip_load(fp: IO[str]) -> DocumentNode:
    """
    Parse JML content from a file-like object into a DocumentNode AST, preserving round-trip data.
    """
    return round_trip_loads(fp.read())

# -------------------------------------
# 4) Render API (optional advanced usage)
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
    # ast = _eval_ast_logical_expressions(ast, context)

    # 3) Process merges (if your language supports table merges):
    # ast = ast.merge_documents(ast)

    # 4) Unparse the result back to JML.
    return round_trip_dumps(ast)
