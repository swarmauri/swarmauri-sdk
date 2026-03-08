from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import commit_tx as _commit_tx
from . import handler_bulk_create as _handler_bulk_create
from . import handler_bulk_delete as _handler_bulk_delete
from . import handler_bulk_merge as _handler_bulk_merge
from . import handler_bulk_replace as _handler_bulk_replace
from . import handler_bulk_update as _handler_bulk_update
from . import handler_clear as _handler_clear
from . import handler_create as _handler_create
from . import handler_delete as _handler_delete
from . import handler_list as _handler_list
from . import handler_merge as _handler_merge
from . import handler_noop as _handler_noop
from . import handler_persistence as _handler_persistence
from . import handler_read as _handler_read
from . import handler_replace as _handler_replace
from . import handler_update as _handler_update
from . import start_tx as _start_tx

RunFn = Callable[[Optional[object], Any], Any]

_ORDERED: Tuple[Tuple[str, str, str, RunFn], ...] = (
    ("sys", "start_tx", _start_tx.ANCHOR, _start_tx.INSTANCE),
    (
        "sys",
        "handler_persistence",
        _handler_persistence.ANCHOR,
        _handler_persistence.INSTANCE,
    ),
    ("sys", "handler_create", _handler_create.ANCHOR, _handler_create.INSTANCE),
    ("sys", "handler_read", _handler_read.ANCHOR, _handler_read.INSTANCE),
    ("sys", "handler_update", _handler_update.ANCHOR, _handler_update.INSTANCE),
    ("sys", "handler_replace", _handler_replace.ANCHOR, _handler_replace.INSTANCE),
    ("sys", "handler_merge", _handler_merge.ANCHOR, _handler_merge.INSTANCE),
    ("sys", "handler_noop", _handler_noop.ANCHOR, _handler_noop.INSTANCE),
    ("sys", "handler_delete", _handler_delete.ANCHOR, _handler_delete.INSTANCE),
    ("sys", "handler_list", _handler_list.ANCHOR, _handler_list.INSTANCE),
    ("sys", "handler_clear", _handler_clear.ANCHOR, _handler_clear.INSTANCE),
    (
        "sys",
        "handler_bulk_create",
        _handler_bulk_create.ANCHOR,
        _handler_bulk_create.INSTANCE,
    ),
    (
        "sys",
        "handler_bulk_update",
        _handler_bulk_update.ANCHOR,
        _handler_bulk_update.INSTANCE,
    ),
    (
        "sys",
        "handler_bulk_replace",
        _handler_bulk_replace.ANCHOR,
        _handler_bulk_replace.INSTANCE,
    ),
    (
        "sys",
        "handler_bulk_merge",
        _handler_bulk_merge.ANCHOR,
        _handler_bulk_merge.INSTANCE,
    ),
    (
        "sys",
        "handler_bulk_delete",
        _handler_bulk_delete.ANCHOR,
        _handler_bulk_delete.INSTANCE,
    ),
    ("sys", "commit_tx", _commit_tx.ANCHOR, _commit_tx.INSTANCE),
)

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    (domain, subject): (anchor, run) for domain, subject, anchor, run in _ORDERED
}

__all__ = ["REGISTRY", "RunFn"]
