"""
autoapi/v2/crud_builder.py  –  CRUD building functionality for AutoAPI.

This module contains the logic for building CRUD operations from SQLAlchemy
models, including database operations and schema generation.
"""

from __future__ import annotations

from typing import Dict

from ..jsonrpc_models import create_standardized_error
from .schema import _schema, create_list_schema
from ..types import Session
from ..naming import camel_to_snake


# ----------------------------------------------------------------------
def _invoke_all_registrars(model: type, api) -> None:
    """
    Call every distinct  __autoapi_register_hooks__  found in the MRO,
    but bind each descriptor to *model*, so cls-param is correct.
    """
    print(f"_invoke_all_registrars for model={model} api={api}")
    seen: set[type] = set()

    for base in reversed(model.__mro__):
        if "__autoapi_register_hooks__" not in base.__dict__:
            continue
        if base in seen:
            continue
        print(f"Registering hooks from base {base}")
        raw = base.__dict__["__autoapi_register_hooks__"]
        bound_fn = raw.__get__(None, model)
        bound_fn(api)
        seen.add(base)


# ----------------------------------------------------------------------
def _not_found() -> None:
    """Raise a standardized 404 error."""
    print("_not_found called")
    http_exc, _, _ = create_standardized_error(404, rpc_code=-32094)
    raise http_exc


def _flush_or_http(db: Session) -> None:
    """
    Flush pending changes and translate SQLAlchemy errors into standardized HTTP errors.

    NOTE: We do NOT commit here. The transaction boundary is owned by _invoke(),
    which will run PRE_COMMIT/POST_COMMIT hooks around the commit.
    """
    from sqlalchemy.exc import IntegrityError, SQLAlchemyError
    import re

    _DUP_RE = re.compile(
        r"Key \((?P<col>[^)]+)\)=\((?P<val>[^)]+)\) already exists", re.I
    )
    _SQLITE_DUP_RE = re.compile(
        r"UNIQUE constraint failed: (?P<table>[^.]+)\.(?P<col>[^,\s]+)", re.I
    )

    print("_flush_or_http (flush-only) start")
    try:
        # Always flush; outer transaction (in _invoke) will commit/rollback.
        db.flush()
        print("_flush_or_http flush success")
    except IntegrityError as exc:
        # Do NOT rollback here; let the outer transaction manager handle it.
        raw = str(exc.orig)
        print(f"IntegrityError encountered during flush: {raw}")
        if (
            getattr(exc.orig, "pgcode", None) in ("23505",)
            or "already exists" in raw
            or "UNIQUE constraint failed" in raw
        ):
            m = _DUP_RE.search(raw) or _SQLITE_DUP_RE.search(raw)
            msg = (
                f"Duplicate value '{m['val']}' for field '{m['col']}'."
                if m and "val" in m.groupdict()
                else (
                    f"Duplicate value for field '{m['col']}'."
                    if m
                    else "Duplicate key value violates a unique constraint."
                )
            )
            http_exc, _, _ = create_standardized_error(
                409, message=msg, rpc_code=-32099
            )
            raise http_exc from exc
        if getattr(exc.orig, "pgcode", None) in ("23503",) or "foreign key" in raw:
            http_exc, _, _ = create_standardized_error(422, rpc_code=-32097)
            raise http_exc from exc
        http_exc, _, _ = create_standardized_error(422, message=raw, rpc_code=-32098)
        raise http_exc from exc
    except SQLAlchemyError as exc:
        # Do NOT rollback here; let the outer transaction manager handle it.
        print(f"SQLAlchemyError encountered during flush: {exc}")
        http_exc, _, _ = create_standardized_error(
            500, message=f"Database error: {exc}"
        )
        raise http_exc from exc


def create_crud_operations(model: type, pk_name: str) -> Dict[str, callable]:
    """
    Create CRUD operations for a given model.
    """
    print(f"create_crud_operations for model={model} pk_name={pk_name}")
    pk_col = next(iter(model.__table__.primary_key.columns))
    pk_type = getattr(pk_col.type, "python_type", str)

    # ── Schemas ───────────────────────────────────────────────────────────
    # Output for read:
    SReadOut = _schema(model, verb="read")
    # Create/update/list:
    SCreate = _schema(model, verb="create")
    SUpdate = _schema(model, verb="update", exclude={pk_name})
    SListIn = create_list_schema(model)
    # Distinct pk-only *input* models for read vs delete (names differ for clarity)
    SReadIn = _schema(
        model, verb="delete", include={pk_name}, name=f"{model.__name__}ReadIn"
    )
    SDeleteIn = _schema(
        model, verb="delete", include={pk_name}, name=f"{model.__name__}DeleteIn"
    )

    # ── CRUD impls ────────────────────────────────────────────────────────
    def _create(p: SCreate, db: Session):
        print(f"_create called with {p}")
        data = p.model_dump() if hasattr(p, "model_dump") else dict(p)
        # Only use table-backed columns to avoid touching the mapper
        col_names = {c.name for c in model.__table__.columns}
        col_kwargs = {k: v for k, v in data.items() if k in col_names}
        virt_kwargs = {k: v for k, v in data.items() if k not in col_names}
        obj = model(**col_kwargs)
        for k, v in virt_kwargs.items():
            setattr(obj, k, v)
        db.add(obj)
        _flush_or_http(db)
        db.refresh(obj)
        print(f"_create returning {obj}")
        return obj

    def _read(i, db: Session):
        print(f"_read called with id={i}")
        if isinstance(i, str) and pk_type is not str:
            try:
                i = pk_type(i)
            except Exception:
                pass
        obj = db.get(model, i)
        if obj is None:
            _not_found()
        print(f"_read returning {obj}")
        return obj

    def _update(i, p: SUpdate, db: Session, *, full=False):
        print(f"_update called with id={i} payload={p} full={full}")
        if isinstance(p, dict):
            p = SUpdate(**p)
        if isinstance(i, str) and pk_type is not str:
            try:
                i = pk_type(i)
            except Exception:
                pass
        obj = db.get(model, i)
        if obj is None:
            _not_found()

        if full:
            for col in model.__table__.columns:
                if col.name != pk_name and not col.info.get("no_update"):
                    setattr(obj, col.name, getattr(p, col.name, None))
        else:
            for k, v in p.model_dump(exclude_unset=True).items():
                setattr(obj, k, v)

        _flush_or_http(db)
        db.refresh(obj)
        print(f"_update returning {obj}")
        return obj

    def _delete(i, db: Session):
        print(f"_delete called with id={i}")
        if isinstance(i, str) and pk_type is not str:
            try:
                i = pk_type(i)
            except Exception:
                pass
        obj = db.get(model, i)
        if obj is None:
            _not_found()
        db.delete(obj)
        _flush_or_http(db)
        print(f"_delete removed {i}")
        return {pk_name: i}

    def _list(p: SListIn, db: Session):
        print(f"_list called with params={p}")
        d = (
            p.model_dump(exclude_defaults=True, exclude_none=True)
            if hasattr(p, "model_dump")
            else dict(p)
        )
        qry = (
            db.query(model)
            .filter_by(**{k: d[k] for k in d if k not in ("skip", "limit")})
            .offset(d.get("skip", 0))
        )
        if lim := d.get("limit"):
            qry = qry.limit(lim)
        result = qry.all()
        print(f"_list returning {result}")
        return result

    def _clear(db: Session):
        print("_clear called")
        deleted = db.query(model).delete()
        _flush_or_http(db)
        print(f"_clear removed {deleted} rows")
        return {"deleted": deleted}

    return {
        "create": _create,
        "read": _read,
        "update": _update,
        "delete": _delete,
        "list": _list,
        "clear": _clear,
        "schemas": {
            # distinct IN/OUT for read:
            "read_in": SReadIn,
            "read_out": SReadOut,
            # delete input:
            "delete_in": SDeleteIn,
            # legacy/compat (existing code may expect these keys):
            "create": SCreate,
            "read": SReadOut,
            "update": SUpdate,
            "list": SListIn,
            "delete": SDeleteIn,
        },
    }


def _crud(self, model: type) -> None:
    """
    Public entry: call `api._crud(User)` to expose canonical CRUD & list routes.
    """
    resource = camel_to_snake(model.__name__)
    print(f"_crud called for model={resource}")

    if resource in self._registered_tables:
        print(f"_crud skipping {resource}, already registered")
        return
    self._registered_tables.add(resource)

    pk = next(iter(model.__table__.primary_key.columns)).name
    print(f"Primary key for {resource} is {pk}")

    crud_ops = create_crud_operations(model, pk)

    # NOTE: _register_routes_and_rpcs must accept distinct read/delete IN models.
    # Signature: (model, tab, pk, SCreate, SReadOut, SReadIn, SDeleteIn, SUpdate, SListIn, f_create, f_read, f_update, f_delete, f_list, f_clear)
    self._register_routes_and_rpcs(
        model,
        resource,
        pk,
        crud_ops["schemas"]["create"],
        crud_ops["schemas"]["read_out"],
        crud_ops["schemas"]["read_in"],  # NEW: read input (pk-only)
        crud_ops["schemas"]["delete_in"],  # NEW: delete input (pk-only)
        crud_ops["schemas"]["update"],
        crud_ops["schemas"]["list"],
        crud_ops["create"],
        crud_ops["read"],
        crud_ops["update"],
        crud_ops["delete"],
        crud_ops["list"],
        crud_ops["clear"],
    )
    print(f"_crud registered routes for {resource}")

    _invoke_all_registrars(model, self)
