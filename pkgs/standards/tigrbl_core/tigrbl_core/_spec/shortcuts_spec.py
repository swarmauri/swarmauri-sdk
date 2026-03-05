from __future__ import annotations

from typing import Any

from .field_spec import FieldSpec as F
from .io_spec import IOSpec as IO
from .storage_spec import StorageSpec as S


def makeColumn(*args: Any, **kwargs: Any):
    from tigrbl.shortcuts.column import makeColumn as _makeColumn

    return _makeColumn(*args, **kwargs)


def makeVirtualColumn(*args: Any, **kwargs: Any):
    from tigrbl.shortcuts.column import makeVirtualColumn as _makeVirtualColumn

    return _makeVirtualColumn(*args, **kwargs)


def acol(*args: Any, **kwargs: Any):
    from tigrbl.shortcuts.column import acol as _acol

    return _acol(*args, **kwargs)


def vcol(*args: Any, **kwargs: Any):
    from tigrbl.shortcuts.column import vcol as _vcol

    return _vcol(*args, **kwargs)


__all__ = ["F", "IO", "S", "makeColumn", "makeVirtualColumn", "acol", "vcol"]
