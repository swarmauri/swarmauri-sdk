"""
api.py - Public API for Cayaml

This module exports two sets of functions (plain mode vs. round-trip mode),
plus additional "_all" variants for multi-document loading:

Plain mode (single doc):
  - loads(yaml_str)
  - load(file_obj)
  - dumps(data)
  - dump(data, file_obj)

Plain mode (multi-doc):
  - loads_all(yaml_str)
  - load_all(file_obj)

Round-trip mode (single doc):
  - round_trip_loads(yaml_str)
  - round_trip_load(file_obj)
  - round_trip_dumps(data)
  - round_trip_dump(data, file_obj)

Round-trip mode (multi-doc):
  - round_trip_loads_all(yaml_str)
  - round_trip_load_all(file_obj)
"""

from .parser import _internal_parse_stream, _internal_to_ast
from .unparser import _internal_dump_plain, _internal_dump_round_trip
from .plain_conversion import to_plain
from .ast_nodes import Node, YamlStream


# -----------------------------
# Plain mode (single-document)
# -----------------------------
def loads(yaml_str: str):
    """
    Parse a YAML string (plain mode) and return plain Python objects (dict, list, scalars).
    If multiple documents exist, this returns only the first one.
    """
    docs = loads_all(yaml_str)
    return docs[0] if docs else None


def load(file_obj):
    """
    Parse YAML from a file-like object (plain mode) and return plain Python objects.
    If multiple documents exist, this returns only the first one.
    """
    yaml_str = file_obj.read()
    return loads(yaml_str)


def dumps(data) -> str:
    """
    Convert plain Python objects into a YAML-formatted string (without preserving formatting metadata).
    """
    if not isinstance(data, Node):
        data = _internal_to_ast(data)
    return _internal_dump_plain(data)


def dump(data, file_obj):
    """
    Dump plain Python objects to a file-like object as YAML.
    """
    file_obj.write(dumps(data))


# -----------------------------
# Plain mode (multi-document)
# -----------------------------
def loads_all(yaml_str: str):
    """
    Parse a YAML string in plain mode.
    Return a list of plain Python objects, one per document in the stream.
    """
    yaml_stream = _internal_parse_stream(yaml_str)
    if not isinstance(yaml_stream, YamlStream):
        # If for some reason only one doc was found, wrap it in a list
        return [to_plain(yaml_stream)]
    return [to_plain(doc) for doc in yaml_stream.documents]


def load_all(file_obj):
    """
    Parse YAML from a file-like object in plain mode.
    Return a list of plain Python objects, one per document.
    """
    yaml_str = file_obj.read()
    return loads_all(yaml_str)


# --------------------------------
# Round-trip mode (single-doc)
# --------------------------------
def round_trip_loads(yaml_str: str):
    """
    Parse a YAML string in round-trip mode (preserving formatting).
    If multiple documents exist, returns only the first one.
    """
    docs = round_trip_loads_all(yaml_str)
    return docs[0] if docs else None


def round_trip_load(file_obj):
    """
    Round-trip from a file-like object.
    If multiple docs, returns only the first one.
    """
    yaml_str = file_obj.read()
    return round_trip_loads(yaml_str)


def round_trip_dumps(data) -> str:
    """
    Convert the AST (or plain objects -> AST) to YAML, preserving formatting.
    """
    if not isinstance(data, Node):
        data = _internal_to_ast(data)
    return _internal_dump_round_trip(data)


def round_trip_dump(data, file_obj):
    """
    Dump the AST to a file, preserving formatting.
    """
    file_obj.write(round_trip_dumps(data))


# --------------------------------
# Round-trip mode (multi-doc)
# --------------------------------
def round_trip_loads_all(yaml_str: str):
    """
    Parse a YAML string in round-trip mode, returning multiple docs as a list of DocumentNodes.
    """
    yaml_stream = _internal_parse_stream(yaml_str)
    if isinstance(yaml_stream, YamlStream):
        return yaml_stream.documents
    return [yaml_stream]


def round_trip_load_all(file_obj):
    """
    Parse from a file in round-trip mode, returning multiple docs as DocumentNodes.
    """
    yaml_str = file_obj.read()
    return round_trip_loads_all(yaml_str)
