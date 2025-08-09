"""
autoapi/v2/crud_builder.py  –  CRUD building functionality for AutoAPI.

This module contains the logic for building CRUD operations from SQLAlchemy
models, including database operations and schema generation.
"""

from __future__ import annotations

from typing import Dict

from sqlalchemy import inspect as _sa_inspect


from ..jsonrpc_models import create_standardized_error
from .schema import _schema, create_list_schema
from ..types import Session


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _invoke_all_registrars(model: type, api) -> None:
    """
    Call every distinct  __autoapi_register_hooks__  found in the MRO,
    but bind each descriptor to *model*, so cls-param is correct.
    """
    print(f"_invoke_all_registrars for model={model} api={api}")
    seen: set[type] = set()  # guard: one call per base

    for base in reversed(model.__mro__):  # parents first
        if "__autoapi_register_hooks__" not in base.__dict__:
            continue
        if base in seen:  # already invoked
            continue

        print(f"Registering hooks from base {base}")
        raw = base.__dict__["__autoapi_register_hooks__"]  # the descriptor
        bound_fn = raw.__get__(None, model)  # bind to *model* 🔑
        bound_fn(api)
        seen.add(base)


# ----------------------------------------------------------------------


def _not_found() -> None:
    """Raise a standardized 404 error."""
    print("_not_found called")
    http_exc, _, _ = create_standardized_error(404, rpc_code=-32094)
    raise http_exc


def _commit_or_http(db: Session) -> None:
    """
    Flush/commit and translate SQLAlchemy errors into standardized HTTP errors.

    Args:
        db: Database session

    Raises:
        HTTPException: Standardized error based on database error type
    """
    from sqlalchemy.exc import IntegrityError, SQLAlchemyError
    import re

    _DUP_RE = re.compile(
        r"Key \((?P<col>[^)]+)\)=\((?P<val>[^)]+)\) already exists", re.I
    )

    print("_commit_or_http start")
    try:
        db.flush() if db.in_nested_transaction() else db.commit()
        print("_commit_or_http success")
    except IntegrityError as exc:
        db.rollback()
        raw = str(exc.orig)
        print(f"IntegrityError encountered: {raw}")
        if getattr(exc.orig, "pgcode", None) in ("23505",) or "already exists" in raw:
            m = _DUP_RE.search(raw)
            msg = (
                f"Duplicate value '{m['val']}' for field '{m['col']}'."
                if m
                else "Duplicate key value violates a unique constraint."
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
        db.rollback()
        print(f"SQLAlchemyError encountered: {exc}")
        http_exc, _, _ = create_standardized_error(
            500, message=f"Database error: {exc}"
        )
        raise http_exc from exc


def create_crud_operations(model: type, pk_name: str) -> Dict[str, callable]:
    """
    Create CRUD operations for a given model.

    Args:
        model: SQLAlchemy ORM model
        pk_name: Primary key field name

    Returns:
        Dictionary of CRUD operation functions
    """
    print(f"create_crud_operations for model={model} pk_name={pk_name}")
    mapper = _sa_inspect(model)
    pk_col = next(iter(model.__table__.primary_key.columns))
    pk_type = getattr(pk_col.type, "python_type", str)

    # Generate schemas
    SCreate = _schema(model, verb="create")
    SRead = _schema(model, verb="read")
    SUpdate = _schema(model, verb="update", exclude={pk_name})
    SListIn = create_list_schema(model)

    def _create(p: SCreate, db: Session):
        """Create a new model instance."""
        print(f"_create called with {p}")
        data = p.model_dump() if hasattr(p, "model_dump") else dict(p)
        col_kwargs = {
            k: v for k, v in data.items() if k in {c.key for c in mapper.attrs}
        }
        virt_kwargs = {k: v for k, v in data.items() if k not in col_kwargs}
        obj = model(**col_kwargs)
        for k, v in virt_kwargs.items():
            setattr(obj, k, v)
        db.add(obj)
        _commit_or_http(db)
        db.refresh(obj)
        print(f"_create returning {obj}")
        return obj

    def _read(i, db: Session):
        """Read a model instance by ID."""
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
        """Update a model instance."""
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

        _commit_or_http(db)
        db.refresh(obj)
        print(f"_update returning {obj}")
        return obj

    def _delete(i, db: Session):
        """Delete a model instance."""
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
        _commit_or_http(db)
        print(f"_delete removed {i}")
        return {pk_name: i}

    def _list(p: SListIn, db: Session):
        """List model instances with filtering."""
        print(f"_list called with params={p}")
        d = p.model_dump(exclude_defaults=True, exclude_none=True)
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
        """Clear all instances of the model."""
        print("_clear called")
        deleted = db.query(model).delete()
        _commit_or_http(db)
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
            "create": SCreate,
            "read": SRead,
            "update": SUpdate,
            "list": SListIn,
            "delete": _schema(model, verb="delete", include={pk_name}),
        },
    }


def _crud(self, model: type) -> None:
    """
    Public entry: call `api._crud(User)` to expose canonical CRUD & list routes.

    Args:
        self: AutoAPI instance
        model: SQLAlchemy ORM model to create CRUD operations for
    """
    tab = model.__tablename__
    print(f"_crud called for table={tab}")

    if tab in self._registered_tables:
        print(f"_crud skipping {tab}, already registered")
        return
    self._registered_tables.add(tab)

    pk = next(iter(model.__table__.primary_key.columns)).name
    print(f"Primary key for {tab} is {pk}")

    # Create CRUD operations
    crud_ops = create_crud_operations(model, pk)

    # Register with route builder
    self._register_routes_and_rpcs(
        model,
        tab,
        pk,
        crud_ops["schemas"]["create"],
        crud_ops["schemas"]["read"],
        crud_ops["schemas"]["delete"],
        crud_ops["schemas"]["update"],
        crud_ops["schemas"]["list"],
        crud_ops["create"],
        crud_ops["read"],
        crud_ops["update"],
        crud_ops["delete"],
        crud_ops["list"],
        crud_ops["clear"],
    )
    print(f"_crud registered routes for {tab}")

    # ───────────────────────────────────────────────────────────────
    # Support for self-registering models / mixins
    # Any class that defines
    #     def __autoapi_register_hooks__(api): ...
    # will be handed **this** AutoAPI instance so it can attach its
    # hooks directly (Upsertable, audit mixins, etc.).
    _invoke_all_registrars(model, self)
