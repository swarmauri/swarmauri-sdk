# jaml/api.py
import os
from typing import IO, Any, Dict
from lark import UnexpectedToken, UnexpectedCharacters, UnexpectedEOF

from ._lark_parser import parser  # Assuming lark_parser.py defines parser
from ._transformer import ConfigTransformer
from ._config import Config

# -------------------------------------
# 1) File Extension Helper
# -------------------------------------


def check_extension(filename: str) -> None:
    """
    Ensure the filename has a supported extension (.jml or .jaml).

    :param filename: Name of the file.
    :raises ValueError: If the extension is not supported.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in (".jml", ".jaml"):
        raise ValueError("Unsupported file extension. Allowed: .jml or .jaml")


# -------------------------------------
# 2) Non-Round-Trip API
# -------------------------------------


def dumps(obj: Dict[str, Any]) -> str:
    """
    Serialize a plain Python dict into a minimal JML string (non-round-trip).
    Discards comments, merges, or advanced formatting.

    :param obj: Dictionary to serialize.
    :return: JML-formatted string.
    """
    # Build a temporary Config from the dictionary
    config = Config(obj)
    # Use the new .dump() method
    dumped = config.dump()
    print("[DEBUG API] dumps:\n", dumped)
    return dumped


def dump(obj: Dict[str, Any], fp: IO[str]) -> None:
    """
    Serialize a plain dict into JML and write to a file-like object (non-round-trip).

    :param obj: Dictionary to serialize.
    :param fp: File-like object to write to.
    """
    fp.write(dumps(obj))


def loads(s: str) -> Dict[str, Any]:
    """
    Parse a JML string into a plain Python dictionary.

    :param s: JML string to parse.
    :return: Parsed dictionary.
    :raises SyntaxError: If parsing fails.
    """
    try:
        parse_tree = parser.parse(s)
        print("[DEBUG API] loads parse_tree:\n", parse_tree)
    except UnexpectedToken as e:
        raise SyntaxError(
            f"Unexpected token at line {e.line}, column {e.column}: {e}"
        ) from e
    except UnexpectedCharacters as e:
        raise SyntaxError(
            f"Unexpected character at line {e.line}, column {e.column}: {e}"
        ) from e
    except UnexpectedEOF as e:
        raise SyntaxError("Unexpected end of input") from e

    transformer = ConfigTransformer()
    transformer._context = type("Context", (), {"text": s})
    config = transformer.transform(parse_tree)
    # Preserve surrounding quotes during load to match specification tests
    return config.resolve(strip_quotes=False)


def load(fp: IO[str]) -> Dict[str, Any]:
    """
    Parse JML content from a file-like object into a plain dictionary.

    :param fp: File-like object to read from.
    :return: Parsed dictionary.
    """
    return loads(fp.read())


# -------------------------------------
# 3) Round-Trip API
# -------------------------------------


def round_trip_dumps(config: Config) -> str:
    """
    Serialize a Config object back to a JML-formatted string, preserving layout,
    comments, merges, etc., as supported by the unparser.

    :param config: Config object from round_trip_loads/load.
    :return: JML-formatted string.
    """
    dumped = config.dump()
    print("[DEBUG API] round_trip_dumps:\n", dumped)
    return dumped


def round_trip_dump(config: Config, fp: IO[str]) -> None:
    """
    Serialize a Config object into JML, writing to a file-like object (round-trip).

    :param config: Config object to serialize.
    :param fp: File-like object to write to.
    """
    fp.write(round_trip_dumps(config))


def round_trip_loads(s: str) -> Config:
    """
    Parse a JML string into a Config object, preserving round-trip data.

    :param s: JML string to parse.
    :return: Config object.
    :raises SyntaxError: If parsing fails.
    """
    try:
        parse_tree = parser.parse(s)
        print("[DEBUG API] round_trip_loads parse_tree:\n", parse_tree)
    except UnexpectedToken as e:
        raise SyntaxError(
            f"Unexpected token at line {e.line}, column {e.column}: {e}"
        ) from e
    except UnexpectedCharacters as e:
        raise SyntaxError(
            f"Unexpected character at line {e.line}, column {e.column}: {e}"
        ) from e
    except UnexpectedEOF as e:
        raise SyntaxError("Unexpected end of input") from e

    transformer = ConfigTransformer()
    transformer._context = type("Context", (), {"text": s})
    config = transformer.transform(parse_tree)
    print("[DEBUG API] round_trip_loads config:\n", config)
    return config


def round_trip_load(fp: IO[str]) -> Config:
    """
    Parse JML content from a file-like object into a Config object, preserving round-trip data.

    :param fp: File-like object to read from.
    :return: Config object.
    """
    return round_trip_loads(fp.read())


# -------------------------------------
# 4) Resolve API
# -------------------------------------


def resolve(config: Config) -> Config:
    """
    Evaluate all purely static expressions in the Config object, leaving ${...}
    placeholders for the render step.

    :param config: Config object from round_trip_loads/load.
    :return: Config object with static expressions resolved.
    """
    config.resolve()
    print("[DEBUG API] resolve config:\n", config._data)
    return config


# -------------------------------------
# 5) Render API
# -------------------------------------


def render(config: Config, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Substitute deferred ${...} placeholders in the Config object using the provided context.

    :param config: Config object from round_trip_loads/load, preferably resolved.
    :param context: Dictionary with context variables (default: empty).
    :return: Rendered dictionary with all placeholders substituted.
    """
    context = context or {}
    rendered = config.render(context)
    print("[DEBUG API] render output:\n", rendered)
    return rendered
