"""
autoapi_impl.py  –  helpers rebound onto AutoAPI.
Compatible with FastAPI 1.5, Pydantic 2.x, SQLAlchemy 2.x.
"""

from __future__ import annotations

import re
from inspect import isawaitable, signature
from typing import Any, List, get_args, get_origin
from collections.abc import MutableMapping, MutableSequence

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Request
from pydantic import BaseModel, ConfigDict, Field, create_model
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .mixins import AsyncCapable, BulkCapable, Replaceable
from .types import _SchemaVerb

# ───────────────────────── misc helpers ────────────────────────────────
def _not_found() -> None:
    raise HTTPException(404, "Item not found")


_DUP_RE = re.compile(r"Key \((?P<col>[^)]+)\)=\((?P<val>[^)]+)\) already exists", re.I)


def _commit_or_http(db: Session) -> None:
    try:
        db.flush() if db.in_nested_transaction() else db.commit()
    except IntegrityError as exc:
        db.rollback()
        raw = str(exc.orig)
        if getattr(exc.orig, "pgcode", None) in ("23505",) or "already exists" in raw:
            m = _DUP_RE.search(raw)
            msg = (
                f"Duplicate value '{m['val']}' for field '{m['col']}'."
                if m
                else "Duplicate key value violates a unique constraint."
            )
            raise HTTPException(409, msg) from exc
        if getattr(exc.orig, "pgcode", None) in ("23503",) or "foreign key" in raw:
            raise HTTPException(422, "Foreign-key constraint failed.") from exc
        raise HTTPException(422, raw) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(500, f"Database error: {exc}") from exc


# ────────────────────── mutable-→plain coercion ────────────────────────
def _coerce_mutable(obj: Any) -> Any:
    """Recursively convert SQLAlchemy MutableDict/MutableList into plain dict/list."""
    if isinstance(obj, MutableMapping):
        return {k: _coerce_mutable(v) for k, v in obj.items()}
    if isinstance(obj, MutableSequence) and not isinstance(obj, (str, bytes, bytearray)):
        return [_coerce_mutable(v) for v in obj]
    return obj


# ──────────────────────── schema helpers ───────────────────────────────
def _strip_parent_fields(base: type, *, drop: set[str]) -> type:
    """
    Return a shallow clone with every field in *drop* removed
    (affects **schema only**, not runtime enforcement).
    """
    if not drop:
        return base

    # Case 1: List[Model] → List[StrippedModel]
    if get_origin(base) in (list, List):
        elem = get_args(base)[0]
        stripped = _strip_parent_fields(elem, drop=drop)
        return list[stripped]  # Py ≥3.9 generics

    # Case 2: plain Pydantic model
    if isinstance(base, type) and issubclass(base, BaseModel):
        fld_spec = {
            name: (fld.annotation, fld)
            for name, fld in base.model_fields.items()
            if name not in drop
        }
        cfg = getattr(base, "model_config", ConfigDict())
        cls = create_model(f"{base.__name__}SansParents", __config__=cfg, **fld_spec)
        cls.model_rebuild(force=True)
        return cls

    # Fallback: untouched (e.g. dict, str, int …)
    return base


# ─────────────────────────── tiny utils ────────────────────────────────
async def _run(core, *a):
    rv = core(*a)
    return await rv if isawaitable(rv) else rv


def _canonical(table: str, verb: str) -> str:
    return f"{''.join(w.title() for w in table.split('_'))}.{verb}"


def _nested_prefix_clean(raw: str) -> str | None:
    """Normalise nested-router prefixes."""
    if not raw:
        return None
    pref = re.sub(r"{[^}/]+}", "", raw)           # drop placeholders
    pref = re.sub(r"/{2,}", "/", pref).rstrip("/")  # squeeze "//" & trim tail
    return pref or None


COMMON_ERRORS = {
    400: {"description": "Bad Request: malformed input"},
    404: {"description": "Not Found"},
    409: {"description": "Conflict: duplicate key"},
    422: {"description": "Unprocessable Entity: constraint failed"},
    500: {"description": "Internal Server Error"},
}

# ─────────────────────── route / RPC builder ───────────────────────────
def _register_routes_and_rpcs(  # noqa: N802
    self,
    model: type,
    tab: str,
    pk: str,
    SCreate,
    SRead,
    SDel,
    SUpdate,
    SListIn,
    _create,
    _read,
    _update,
    _delete,
    _list,
    _clear,
) -> None:
    import functools
    import inspect
    import re
    from typing import Annotated, List

    from fastapi import HTTPException

    # Determine sync / async DB provider
    is_async = (
        bool(self.get_async_db)
        if self.get_db is None
        else issubclass(model, AsyncCapable)
    )
    provider = self.get_async_db if is_async else self.get_db

    pk_col = next(iter(model.__table__.primary_key.columns))
    pk_type = getattr(pk_col.type, "python_type", str)

    # verb  http  path  status  In-model   Out-model  core-fn
    spec: List[tuple] = [
        ("create",  "POST",    "",              201, SCreate,        SRead,        _create),
        ("list",    "GET",     "",              200, SListIn,        List[SRead],  _list),
        ("clear",   "DELETE",  "",              204, None,           None,         _clear),
        ("read",    "GET",     "/{item_id}",    200, SDel,           SRead,        _read),
        ("update",  "PATCH",   "/{item_id}",    200, SUpdate,        SRead,        _update),
        ("delete",  "DELETE",  "/{item_id}",    204, SDel,           None,         _delete),
    ]
    if issubclass(model, Replaceable):
        spec.append(
            (
                "replace",
                "PUT",
                "/{item_id}",
                200,
                SCreate,
                SRead,
                functools.partial(_update, full=True),
            )
        )
    if issubclass(model, BulkCapable):
        spec += [
            ("bulk_create",  "POST",    "/bulk", 201, List[SCreate], List[SRead], _create),
            ("bulk_delete",  "DELETE",  "/bulk", 204, List[SDel],    None,        _delete),
        ]

    # nested routing support -------------------------------------------------
    raw_pref    = self._nested_prefix(model) or ""
    nested_pref = re.sub(r"/{2,}", "/", raw_pref).rstrip("/") or None
    nested_vars = re.findall(r"{(\w+)}", raw_pref)

    flat_router = APIRouter(prefix=f"/{tab}", tags=[tab])
    routers     = (
        (flat_router,)
        if nested_pref is None
        else (flat_router, APIRouter(prefix=nested_pref, tags=[f"nested-{tab}"]))
    )

    # RBAC guard -------------------------------------------------------------
    def _guard(scope: str):
        async def inner(request: Request):
            if self.authorize and not self.authorize(scope, request):
                raise HTTPException(403, "RBAC")
        return Depends(inner)

    # endpoint factory -------------------------------------------------------
    for verb, http, path, status, In, Out, core in spec:
        m_id = _canonical(tab, verb)

        def _factory(is_nested_router, *, verb=verb, path=path, In=In, core=core):
            params: list[inspect.Parameter] = []

            # parent keys
            if is_nested_router:
                for nv in nested_vars:
                    params.append(
                        inspect.Parameter(
                            nv,
                            inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            annotation=Annotated[str, Path(...)],
                        )
                    )

            # primary-key path variable
            if "{item_id}" in path:
                params.append(
                    inspect.Parameter(
                        "item_id",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=pk_type,
                    )
                )

            def _visible(t: type) -> type:
                return _strip_parent_fields(t, drop=set(nested_vars)) if is_nested_router else t

            # payloads – body or query
            if verb == "list":
                params.append(
                    inspect.Parameter(
                        "p",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[_visible(In), Depends()],
                    )
                )
            elif In is not None and verb not in ("read", "delete", "clear"):
                params.append(
                    inspect.Parameter(
                        "p",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=Annotated[_visible(In), Body(embed=False)],
                    )
                )

            # DB session
            params.append(
                inspect.Parameter(
                    "db",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Any, Depends(provider)],
                )
            )

            # ---- actual endpoint body ---------------------------------------
            async def _impl(**kw):
                db        = kw.pop("db")
                p         = kw.pop("p", None)
                item_id   = kw.pop("item_id", None)
                parent_kw = {k: kw[k] for k in nested_vars if k in kw}

                # inject path vars into body model if necessary
                if p is not None and parent_kw:
                    p = p.model_copy(update=parent_kw)

                # delegate to core
                async def call_sync(fn, *args):
                    if isinstance(db, AsyncSession):
                        return await db.run_sync(lambda s: fn(*args, s))
                    return fn(*args, db)

                match verb:
                    case "list":
                        res = await call_sync(core, p)
                        return [SRead.model_validate(o) for o in res]
                    case "read" | "delete":
                        res = await call_sync(core, item_id)
                        return (
                            res if verb == "delete" else SRead.model_validate(res)
                        )
                    case "update" | "replace":
                        res = await call_sync(core, item_id, p)
                        return SRead.model_validate(res)
                    case "clear":
                        return await call_sync(core)
                    case _:
                        # create / bulk_create / bulk_delete
                        res = await call_sync(core, p)
                        if verb.startswith("bulk"):
                            return [SRead.model_validate(o) for o in res]
                        return SRead.model_validate(res)

            _impl.__name__ = f"{verb}_{tab}"
            wrapped = functools.wraps(_impl)(_impl)
            wrapped.__signature__ = inspect.Signature(parameters=params)
            return wrapped

        # mount on every router
        for r in routers:
            r.add_api_route(
                path,
                _factory(r is not flat_router),
                methods=[http],
                status_code=status,
                response_model=Out,
                responses=COMMON_ERRORS,
                dependencies=[self._authn_dep, _guard(m_id)],
            )

        # JSON-RPC shim
        self.rpc[m_id] = self._wrap_rpc(core, In or dict, Out, pk, model)
        self._method_ids.setdefault(m_id, None)

    # final include
    self.router.include_router(flat_router)
    if len(routers) > 1:
        self.router.include_router(routers[1])

# ───────────────────────── schema builder ───────────────────────────────
def _schema(  # noqa: N802
    self,
    orm_cls: type,
    *,
    name: str | None = None,
    include: set[str] | None = None,
    exclude: set[str] | None = None,
    verb: _SchemaVerb = "create",
):
    """Build a throw-away Pydantic model mirroring *orm_cls*."""
    model_name = name or f"{orm_cls.__name__}{verb.title()}"

    def _should_use(col) -> bool:
        if include is not None and col.name not in include:
            return False
        if exclude is not None and col.name in exclude:
            return False
        if verb == "create" and col.info.get("no_create"):
            return False
        if verb == "update" and col.info.get("no_update"):
            return False
        return True

    flds = {
        c.name: (
            getattr(c.type, "python_type", Any),
            Field(None if c.nullable or c.default is not None else ...),
        )
        for c in orm_cls.__table__.columns
        if _should_use(c)
    }
    cfg = ConfigDict(from_attributes=True)
    M   = create_model(model_name, __config__=cfg, **flds)  # type: ignore[arg-type]
    M.model_rebuild(force=True)
    return M

# ───────────────────────── CRUD scaffold ───────────────────────────────
def _crud(self, model: type) -> None:  # noqa: N802
    tab = model.__tablename__
    if tab in self._registered_tables:
        return
    self._registered_tables.add(tab)

    pk = next(iter(model.__table__.primary_key.columns)).name

    # helper to build the canonical schemas
    _S       = lambda verb, **kw: self._schema(model, verb=verb, **kw)
    SCreate  = _S("create")                    # PK excluded
    SRead    = _S("read")                      # full set
    SDel     = _S("delete", include={pk})      # only PK
    SUpdate  = _S("update", exclude={pk})      # optional / nowritable gone

    def _SList():
        base = dict(skip=(int, Field(0, ge=0)), limit=(int | None, Field(None, ge=1)))
        cols = {
            c.name: (getattr(c.type, "python_type", Any) | None, Field(None))
            for c in model.__table__.columns
        }
        return create_model(
            f"{tab}ListParams", __config__=ConfigDict(extra="forbid"), **base, **cols
        )

    SListIn = _SList()

    # ------- core helpers --------------------------------------------------
    def _create(p: SCreate, db):
        obj = model(**p.model_dump())
        db.add(obj)
        _commit_or_http(db)
        db.refresh(obj)
        return obj

    def _read(item_id, db):
        obj = db.get(model, item_id)
        if obj is None:
            _not_found()
        return obj

    def _update(item_id, p: SUpdate, db, *, full: bool = False):
        obj = db.get(model, item_id)
        if obj is None:
            _not_found()

        if full:
            for col in model.__table__.columns:
                if col.name != pk and not col.info.get("no_update"):
                    setattr(obj, col.name, getattr(p, col.name, None))
        else:
            for k, v in p.model_dump(exclude_unset=True).items():
                setattr(obj, k, v)

        _commit_or_http(db)
        db.refresh(obj)
        return obj

    def _delete(item_id, db):
        obj = db.get(model, item_id)
        if obj is None:
            _not_found()
        db.delete(obj)
        _commit_or_http(db)
        return {pk: item_id}

    def _list(p: SListIn, db):
        d = p.model_dump(exclude_defaults=True, exclude_none=True)
        qry = (
            db.query(model)
            .filter_by(**{k: d[k] for k in d if k not in ("skip", "limit")})
            .offset(d.get("skip", 0))
        )
        if lim := d.get("limit"):
            qry = qry.limit(lim)
        return qry.all()

    def _clear(db):
        deleted = db.query(model).delete()
        _commit_or_http(db)
        return {"deleted": deleted}

    # ------- register ------------------------------------------------------
    self._register_routes_and_rpcs(
        model,
        tab,
        pk,
        SCreate,
        SRead,
        SDel,
        SUpdate,
        SListIn,
        _create,
        _read,
        _update,
        _delete,
        _list,
        _clear,
    )

# ───────────────────────── RPC adapter (generic) ───────────────────────
def _wrap_rpc(self, core, IN, OUT, pk_name: str, model):  # noqa: N802
    """
    Generic JSON-RPC → CRUD shim (works for every core signature).
    """
    sig        = signature(core)
    params     = list(sig.parameters.values())
    # accept both "<table>_id" (REST path) *and* raw PK name
    pk_param   = next(
        (p for p in params if p.name in (pk_name, "item_id")),
        None,
    )
    dto_param  = next(
        (
            p for p in params
            if isinstance(p.annotation, type) and issubclass(p.annotation, BaseModel)
        ),
        None,
    )

    out_is_list  = get_origin(OUT) is list
    out_elem     = get_args(OUT)[0] if out_is_list else None
    out_elem_md  = callable(getattr(out_elem, "model_validate", None))
    out_single   = callable(getattr(OUT, "model_validate", None))

    def handler(raw: dict, db: Session):
        obj_in = IN.model_validate(raw) if hasattr(IN, "model_validate") else raw
        data   = obj_in.model_dump() if isinstance(obj_in, BaseModel) else obj_in

        # -------- build call-time kwargs -----------------------------------
        kwargs: dict[str, Any] = {"db": db}
        if pk_param and pk_name in data:
            kwargs[pk_param.name] = data.pop(pk_name)
        if dto_param:
            dto_cls = dto_param.annotation
            kwargs[dto_param.name] = dto_cls.model_validate(data)
        else:
            kwargs.update(data)

        # -------- invoke core ----------------------------------------------
        result = core(**kwargs)

        # -------- normalise return -----------------------------------------
        if not out_is_list:
            return (
                result
                if not out_single
                else OUT.model_validate(result).model_dump()
            )

        # list-return
        out: list[Any] = []
        for itm in result:
            if isinstance(itm, BaseModel):
                out.append(itm.model_dump())
            elif out_elem_md:
                out.append(out_elem.model_validate(itm).model_dump())
            else:
                out.append(_coerce_mutable(itm))
        return out

    return handler
