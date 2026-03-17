from functools import lru_cache


@lru_cache(maxsize=None)
def collect_decorated_schemas(model: type):
    out = {}
    for base in reversed(model.__mro__):
        for obj in vars(base).values():
            decl = getattr(obj, "__tigrbl_schema_decl__", None)
            if decl is None:
                continue
            alias = getattr(decl, "alias", None)
            kind = getattr(decl, "kind", None)
            if not alias or kind not in {"in", "out"}:
                continue
            out.setdefault(alias, {})[kind] = obj
    return out


__all__ = ["collect_decorated_schemas"]
