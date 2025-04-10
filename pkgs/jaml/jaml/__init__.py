"""
__init__.py

This file exposes the public API of the JML library.
"""

from .api import (
    dump,
    dumps,
    load,
    loads,
    round_trip_dump,
    round_trip_dumps,
    round_trip_load,
    round_trip_loads,
    check_extension,
    resolve,
    render,
)
from .lark_parser import parser