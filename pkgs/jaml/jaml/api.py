import os
from typing import IO, Any, Dict

from lark import UnexpectedToken, UnexpectedCharacters, UnexpectedEOF

# Using the lark parser and transformer modules:
from .lark_parser import parser
from .lark_nodes import ConfigTransformer

from .unparser import JMLUnparser
# Removed reference to the old ast_nodes.DocumentNode


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
    
    This implementation directly unparses the plain dict using JMLUnparser.
    Leading and trailing whitespace in string values is preserved.
    """
    unparser = JMLUnparser(obj)
    return unparser.unparse()


def dump(obj: Dict[str, Any], fp: IO[str]) -> None:
    """
    Serialize a plain dict into JML and write to a file-like object (non-round-trip).
    """
    fp.write(dumps(obj))


def loads(s: str) -> Dict[str, Any]:
    """
    Parse a JML string into a plain Python dictionary.
    """
    try:
        ast_tree = parser.parse(s)
        from pprint import pformat
        print(f"[DEBUG]: {pformat(ast_tree)}")
    except UnexpectedToken as e:
        raise SyntaxError("UnexpectedToken") from e
    except UnexpectedCharacters as e:
        raise SyntaxError("UnexpectedCharacters") from e
    except UnexpectedEOF as e:
        raise SyntaxError("UnexpectedEOF") from e

    transformer = ConfigTransformer()
    # Create a dummy context object with a 'text' attribute containing the original input.
    transformer._context = type("Context", (), {"text": s})
    return transformer.transform(ast_tree)


def load(fp: IO[str]) -> Dict[str, Any]:
    """
    Parse JML content from a file-like object into a plain dictionary.
    """
    return loads(fp.read())

# -------------------------------------
# 3) Round-Trip API
# -------------------------------------

def round_trip_dumps(ast: Any) -> str:
    """
    Serialize an AST (as constructed by the lark parser) back to a JML-formatted string,
    preserving layout, comments, merges, etc. (as far as the unparser supports it).

    If the provided AST is not a plain dictionary, transform it using the ConfigTransformer.
    """
    # Transform the AST to a plain dict if needed.
    ast = ConfigTransformer().transform(ast)
    print(f"[DEBUG]: {ast}")
    unparser = JMLUnparser(ast)
    return unparser.unparse()


def round_trip_dump(ast: Any, fp: IO[str]) -> None:
    """
    Serialize an AST into JML, writing to a file-like object (round-trip).
    """
    fp.write(round_trip_dumps(ast))


def round_trip_loads(s: str):
    tree = parser.parse(s)
    transformer = ConfigTransformer()
    # Create a dummy context object with a 'text' attribute containing the original input.
    transformer._context = type("Context", (), {"text": s})
    return transformer.transform(tree)


def round_trip_load(fp: IO[str]) -> Any:
    """
    Parse JML content from a file-like object into an AST, preserving round-trip data.
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

    # 1) Parse into an AST (round-trip mode) using the lark parser.
    ast = round_trip_loads(input_jml)

    # 2) (Optional) Evaluate expressions or process merges here.
    # e.g., ast = _eval_ast_logical_expressions(ast, context)
    # e.g., ast = ast.merge_documents(ast)

    # 3) Unparse the result back to JML.
    return round_trip_dumps(ast)
