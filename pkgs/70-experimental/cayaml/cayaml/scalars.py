"""Internal YAML parser support for Cayaml."""

import math
import re

from .errors import YamlParseError
from .tags import CORE_TAGS

DECIMAL_INT_RE = re.compile(r"^[+-]?(?:0|[0-9](?:_?[0-9])*)$")
BINARY_INT_RE = re.compile(r"^[+-]?0b[0-1](?:_?[0-1])*$")
OCTAL_INT_RE = re.compile(r"^[+-]?0o[0-7](?:_?[0-7])*$")
HEX_INT_RE = re.compile(r"^[+-]?0x[0-9a-fA-F](?:_?[0-9a-fA-F])*$")
DECIMAL_FLOAT_RE = re.compile(
    r"^[+-]?(?:(?:[0-9](?:_?[0-9])*)\.(?:[0-9](?:_?[0-9])*)?"
    r"|\.(?:[0-9](?:_?[0-9])*))(?:[eE][+-]?[0-9](?:_?[0-9])*)?$"
)
EXPONENT_FLOAT_RE = re.compile(
    r"^[+-]?[0-9](?:_?[0-9])*[eE][+-]?[0-9](?:_?[0-9])*$"
)


def parse_quoted_scalar(value: str):
    """Decode YAML single- and double-quoted scalar text."""
    if len(value) < 2:
        return value
    quote = value[0]
    inner = value[1:-1]
    if quote == "'":
        return inner.replace("''", "'")

    escapes = {
        "0": "\0",
        "a": "\a",
        "b": "\b",
        "t": "\t",
        "\t": "\t",
        "n": "\n",
        "v": "\v",
        "f": "\f",
        "r": "\r",
        "e": "\x1b",
        "N": "\u0085",
        "_": "\u00a0",
        "L": "\u2028",
        "P": "\u2029",
        '"': '"',
        "/": "/",
        "\\": "\\",
        " ": " ",
    }

    def decode_numeric_escape(start: int, length: int) -> tuple[str, int]:
        digits = inner[start : start + length]
        if len(digits) != length or not re.fullmatch(r"[0-9a-fA-F]+", digits):
            raise YamlParseError(f"invalid escape sequence: \\{escape}")
        try:
            return chr(int(digits, 16)), start + length
        except ValueError as exc:
            raise YamlParseError(
                f"invalid escape sequence: \\{escape}"
            ) from exc

    result = []
    i = 0
    while i < len(inner):
        char = inner[i]
        if char != "\\":
            result.append(char)
            i += 1
            continue
        i += 1
        if i >= len(inner):
            result.append("\\")
            break
        escape = inner[i]
        if escape in escapes:
            result.append(escapes[escape])
            i += 1
        elif escape == "x":
            decoded, i = decode_numeric_escape(i + 1, 2)
            result.append(decoded)
        elif escape == "u":
            decoded, i = decode_numeric_escape(i + 1, 4)
            result.append(decoded)
        elif escape == "U":
            decoded, i = decode_numeric_escape(i + 1, 8)
            result.append(decoded)
        else:
            raise YamlParseError(f"invalid escape sequence: \\{escape}")
    return "".join(result)


def parse_yaml_int(value: object) -> int | None:
    """Parse a YAML 1.2 integer scalar, or return None if not an integer."""
    text = str(value).replace("_", "")
    raw = str(value)
    if BINARY_INT_RE.match(raw):
        return int(text, 2)
    if OCTAL_INT_RE.match(raw):
        sign = -1 if text.startswith("-") else 1
        digits = text.lstrip("+-")[2:]
        return sign * int(digits, 8)
    if HEX_INT_RE.match(raw):
        return int(text, 16)
    if DECIMAL_INT_RE.match(raw):
        return int(text, 10)
    return None


def parse_yaml_float(value: object) -> float | None:
    """Parse a YAML 1.2 float scalar, or return None if not a float."""
    raw = str(value)
    lower = raw.lower()
    if lower in (".inf", "+.inf"):
        return math.inf
    if lower == "-.inf":
        return -math.inf
    if lower == ".nan":
        return math.nan
    if DECIMAL_FLOAT_RE.match(raw) or EXPONENT_FLOAT_RE.match(raw):
        return float(raw.replace("_", ""))
    return None


def parse_scalar(value: str, tag: str | None = None):
    """
    Convert a scalar string into int, float, bool, None, or leave as string.
    This function also strips quotes if present.
    """
    value = value.strip()
    # Remove quotes if present:
    if value.startswith(('"', "'")) and not value.endswith(value[0]):
        raise YamlParseError(f"unterminated quoted scalar: {value}")
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        unquoted = parse_quoted_scalar(value)
    else:
        unquoted = value

    tag = CORE_TAGS.get(tag, tag)

    if tag == "!":
        return unquoted
    if tag == "tag:yaml.org,2002:str":
        return unquoted
    if tag == "tag:yaml.org,2002:int":
        parsed_int = parse_yaml_int(unquoted)
        if parsed_int is None:
            raise YamlParseError(f"invalid scalar for tag !!int: {value}")
        return parsed_int
    if tag == "tag:yaml.org,2002:float":
        parsed_float = parse_yaml_float(unquoted)
        if parsed_float is None:
            raise YamlParseError(f"invalid scalar for tag !!float: {value}")
        return parsed_float
    if tag == "tag:yaml.org,2002:bool":
        lower_bool = str(unquoted).lower()
        if lower_bool not in ("true", "false"):
            raise YamlParseError(f"invalid scalar for tag !!bool: {value}")
        return lower_bool == "true"
    if tag == "tag:yaml.org,2002:null":
        return None
    if tag == "tag:yaml.org,2002:binary":
        return "".join(str(unquoted).split())

    if unquoted != value:
        return unquoted

    if value == "":
        return None

    lower = value.lower()
    # Handle booleans
    if lower == "true":
        return True
    if lower == "false":
        return False

    # Handle null
    if lower in ("null", "~"):
        return None

    parsed_int = parse_yaml_int(value)
    if parsed_int is not None:
        return parsed_int

    parsed_float = parse_yaml_float(value)
    if parsed_float is not None:
        return parsed_float

    if "\n" in value:
        return value
    return " ".join(value.split())
