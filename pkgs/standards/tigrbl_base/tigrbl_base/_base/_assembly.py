from __future__ import annotations

from functools import singledispatch
from typing import Any, Iterable


_CHILD_ATTRS = ("routers", "tables", "ops", "hooks", "schemas", "columns")


def iter_children(spec: Any) -> Iterable[tuple[str, str, Any]]:
    for namespace in _CHILD_ATTRS:
        children = getattr(spec, namespace, ()) or ()
        if isinstance(children, dict):
            for key, child in children.items():
                yield namespace, str(key), child
            continue
        for child in tuple(children):
            key = str(
                getattr(child, "name", None)
                or getattr(child, "alias", None)
                or id(child)
            )
            yield namespace, key, child


def bind_child(parent: Any, namespace: str, key: str, child: Any) -> Any:
    slot = getattr(parent, namespace, None)
    if hasattr(slot, "__setitem__"):
        try:
            slot[key] = child
            return child
        except Exception:
            pass
    for attr in ("app", "parent", "owner"):
        if hasattr(child, attr):
            try:
                setattr(child, attr, parent)
            except Exception:
                pass
    return child


@singledispatch
def maybe_convert(parent: Any, namespace: str, key: str, child: Any) -> Any:
    return child


def assemble(owner: Any) -> Any:
    collector = getattr(type(owner), "collect", None)
    spec = collector(owner) if callable(collector) else owner
    for namespace, key, child in iter_children(spec):
        assembled_child = assemble(child)
        converted = maybe_convert(owner, namespace, key, assembled_child)
        bind_child(owner, namespace, key, converted)
    finalize = getattr(owner, "finalize", None)
    if callable(finalize):
        finalize(spec)
    return owner
