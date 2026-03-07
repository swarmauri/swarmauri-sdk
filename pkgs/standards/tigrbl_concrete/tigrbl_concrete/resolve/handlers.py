from tigrbl_atoms.atoms.sys.handler_noop import INSTANCE as NOOP
from tigrbl_atoms.atoms.sys.handler_custom import bind as bind_custom

from tigrbl_atoms.atoms.sys.handler_create import INSTANCE as CREATE
from tigrbl_atoms.atoms.sys.handler_read import INSTANCE as READ
from tigrbl_atoms.atoms.sys.handler_update import INSTANCE as UPDATE
from tigrbl_atoms.atoms.sys.handler_replace import INSTANCE as REPLACE
from tigrbl_atoms.atoms.sys.handler_merge import INSTANCE as MERGE
from tigrbl_atoms.atoms.sys.handler_delete import INSTANCE as DELETE
from tigrbl_atoms.atoms.sys.handler_list import INSTANCE as LIST
from tigrbl_atoms.atoms.sys.handler_clear import INSTANCE as CLEAR

from tigrbl_atoms.atoms.sys.handler_bulk_create import INSTANCE as BULK_CREATE
from tigrbl_atoms.atoms.sys.handler_bulk_update import INSTANCE as BULK_UPDATE
from tigrbl_atoms.atoms.sys.handler_bulk_replace import INSTANCE as BULK_REPLACE
from tigrbl_atoms.atoms.sys.handler_bulk_merge import INSTANCE as BULK_MERGE
from tigrbl_atoms.atoms.sys.handler_bulk_delete import INSTANCE as BULK_DELETE

from tigrbl_atoms.atoms.sys.handler_count import INSTANCE as COUNT
from tigrbl_atoms.atoms.sys.handler_exists import INSTANCE as EXISTS
from tigrbl_atoms.atoms.sys.handler_aggregate import INSTANCE as AGGREGATE
from tigrbl_atoms.atoms.sys.handler_group_by import INSTANCE as GROUP_BY


STANDARD_HANDLER_ATOMS = {
    "noop": NOOP,
    "create": CREATE,
    "read": READ,
    "update": UPDATE,
    "replace": REPLACE,
    "merge": MERGE,
    "delete": DELETE,
    "list": LIST,
    "clear": CLEAR,
    "bulk_create": BULK_CREATE,
    "bulk_update": BULK_UPDATE,
    "bulk_replace": BULK_REPLACE,
    "bulk_merge": BULK_MERGE,
    "bulk_delete": BULK_DELETE,
    "count": COUNT,
    "exists": EXISTS,
    "aggregate": AGGREGATE,
    "group_by": GROUP_BY,
}


def resolve_handler_atom(sp):
    if sp.target == "custom":
        if sp.handler is None:
            raise TypeError(f"{sp.alias}: custom op requires handler")
        return bind_custom(sp.handler, name=f"handler.custom.{sp.alias}")

    try:
        return STANDARD_HANDLER_ATOMS[sp.target]
    except KeyError as exc:
        raise TypeError(
            f"{sp.alias}: no canonical handler atom for target={sp.target!r}"
        ) from exc
