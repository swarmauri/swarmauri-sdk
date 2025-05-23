"""
__init__.py

This file exposes the public API of the JML library.
"""

from .api import (
    dump as dump,
    dumps as dumps,
    load as load,
    loads as loads,
    round_trip_dump as round_trip_dump,
    round_trip_dumps as round_trip_dumps,
    round_trip_load as round_trip_load,
    round_trip_loads as round_trip_loads,
    check_extension as check_extension,
    resolve as resolve,
    render as render,
)
from ._lark_parser import parser as parser

__all__ = [
    "dump",
    "dumps",
    "load",
    "loads",
    "round_trip_dump",
    "round_trip_dumps",
    "round_trip_load",
    "round_trip_loads",
    "check_extension",
    "resolve",
    "render",
    "parser",
]
