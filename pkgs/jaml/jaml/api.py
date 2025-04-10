import os
from typing import IO, Any, Dict

from lark import UnexpectedToken, UnexpectedCharacters, UnexpectedEOF

from pprint import pprint

# Using the lark parser and transformer modules:
from .lark_parser import parser
from ._transformer import ConfigTransformer

from ._resolve import resolve_ast
from ._render import substitute_deferred

from .unparser import JMLUnparser


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
        ast = parser.parse(s)
        print("[DEBUG]: ")
        pprint(ast)
    except UnexpectedToken as e:
        raise SyntaxError("UnexpectedToken") from e
    except UnexpectedCharacters as e:
        raise SyntaxError("UnexpectedCharacters") from e
    except UnexpectedEOF as e:
        raise SyntaxError("UnexpectedEOF") from e

    transformer = ConfigTransformer()
    # Create a dummy context object with a 'text' attribute containing the original input.
    transformer._context = type("Context", (), {"text": s})
    return transformer.transform(ast)


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
    print("[DEBUG]: ")
    pprint(ast)
    unparser = JMLUnparser(ast)
    return unparser.unparse()


def round_trip_dump(ast: Any, fp: IO[str]) -> None:
    """
    Serialize an AST into JML, writing to a file-like object (round-trip).
    """
    fp.write(round_trip_dumps(ast))


def round_trip_loads(s: str):
    ast = parser.parse(s)
    print("[DEBUG]: ")
    pprint(ast)
    transformer = ConfigTransformer()
    # Create a dummy context object with a 'text' attribute containing the original input.
    transformer._context = type("Context", (), {"text": s})
    return transformer.transform(ast)


def round_trip_load(fp: IO[str]) -> Any:
    """
    Parse JML content from a file-like object into an AST, preserving round-trip data.
    """
    return round_trip_loads(fp.read())

# -------------------------------------
# 3) Resolve API
# -------------------------------------

def resolve(ast: Any) -> Any:
    """
    Partially evaluate all purely static expressions in the given AST, leaving 
    only those placeholders that rely on dynamic context (i.e. ${...}) for the 
    final render step.

    This does not accept an external environment or context — all static data 
    must already exist within the AST (e.g., from global/local assignments).
    The returned AST can then be:

      1) Dumped to text via round_trip_dumps(ast),
      2) Passed to render() (after converting to text) to finalize dynamic placeholders.

    :param ast: The AST produced by round_trip_loads() or similar.
    :return: A new AST (or updated in-place, depending on your implementation)
             with static expressions evaluated.
    """
    return resolve_ast(ast)

# -------------------------------------
# 4) Render API (optional advanced usage)
# -------------------------------------

def render(text, context={}):
    """
    Re-parse the dumped text, then walk the AST to substitute deferred placeholders.
    """
    ast = loads(text)
    env = {}
    env.update(context)
    # Also inject the booleans
    env["true"] = True
    env["false"] = False
    print("[DEBUG]: ")
    pprint(ast)
    return substitute_deferred(ast, env)

