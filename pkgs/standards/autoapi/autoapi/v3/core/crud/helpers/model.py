from __future__ import annotations

from typing import Any, Dict, Mapping, Tuple


def _pk_columns(model: type) -> Tuple[Any, ...]:
    table = getattr(model, "__table__", None)
    if table is None:
        raise ValueError(f"{model.__name__} has no __table__")
    pks = tuple(table.primary_key.columns)  # type: ignore[attr-defined]
    if not pks:
        raise ValueError(f"{model.__name__} has no primary key")
    return pks


def _single_pk_name(model: type) -> str:
    pks = _pk_columns(model)
    if len(pks) != 1:
        raise NotImplementedError(
            f"{model.__name__} has composite PK; not supported by default core"
        )
    return pks[0].name


def _coerce_pk_value(model: type, value: Any) -> Any:
    if value is None:
        return None
    try:
        col = _pk_columns(model)[0]
        py_type = col.type.python_type  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - best effort
        return value
    if isinstance(value, py_type):
        return value
    try:
        return py_type(value)
    except Exception:  # pragma: no cover - fallback to original
        return value


def _model_columns(model: type) -> Tuple[str, ...]:
    table = getattr(model, "__table__", None)
    if table is None:
        return ()
    return tuple(c.name for c in table.columns)


def _colspecs(model: type) -> Mapping[str, Any]:
    specs = getattr(model, "__autoapi_colspecs__", None)
    if isinstance(specs, Mapping):
        return specs
    specs = getattr(model, "__autoapi_cols__", None)
    if isinstance(specs, Mapping):
        return specs
    return {}


def _filter_in_values(
    model: type, data: Mapping[str, Any], verb: str
) -> Dict[str, Any]:
    specs = _colspecs(model)
    if not specs:
        return dict(data)
    out: Dict[str, Any] = {}
    for k, v in data.items():
        sp = specs.get(k)
        if sp is None:
            out[k] = v
            continue
        io = getattr(sp, "io", None)
        allowed = True
        if io is not None:
            in_verbs = getattr(io, "in_verbs", ())
            mutable = getattr(io, "mutable_verbs", ())
            if in_verbs and verb not in in_verbs:
                allowed = False
            if mutable and verb not in mutable:
                allowed = False
        if allowed:
            out[k] = v
    return out


def _immutable_columns(model: type, verb: str) -> set[str]:
    specs = _colspecs(model)
    if not specs:
        return set()
    imm: set[str] = set()
    for name, sp in specs.items():
        io = getattr(sp, "io", None)
        mutable = getattr(io, "mutable_verbs", ()) if io else ()
        if mutable and verb not in mutable:
            imm.add(name)
    return imm
