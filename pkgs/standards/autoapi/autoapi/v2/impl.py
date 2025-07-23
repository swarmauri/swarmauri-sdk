"""
autoapi/v2/impl.py  –  framework-agnostic helpers rebound onto AutoAPI.
This version **delegates all lifecycle handling to `_runner._invoke`**, so
REST and JSON-RPC calls now share *exactly* the same hook, transaction,
and error semantics.

Compatible with FastAPI ≥ 0.110, Pydantic 2.x, SQLAlchemy 2.x.
"""

from __future__ import annotations

import re
import uuid
from inspect import isawaitable, signature
from typing import (
    Any,
    Dict,
    List,
    Set,
    Tuple,
    Type,
    get_args,
    get_origin,
)

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Request
from pydantic import BaseModel, ConfigDict, Field, create_model
from sqlalchemy import inspect as _sa_inspect
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ._runner import _invoke  # ← unified lifecycle
from .jsonrpc_models import _RPCReq  # ← fabricated envelope
from .info_schema import check as _info_check
from .mixins import AsyncCapable, BulkCapable, Replaceable
from .types import _SchemaVerb, hybrid_property

# ────────────────────────────────────────────────────────────────────────────
_DUP_RE = re.compile(r"Key \((?P<col>[^)]+)\)=\((?P<val>[^)]+)\) already exists", re.I)
_SchemaCache: Dict[Tuple[type, str, frozenset, frozenset], Type] = {}


def _not_found() -> None:
    raise HTTPException(404, "Item not found")


def _commit_or_http(db: Session) -> None:
    """flush/commit and translate SQLAlchemy errors into HTTP*"""
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


# ───────────────────────── helpers ──────────────────────────────────────────
async def _run(core, *a):  # legacy helper (still used)
    rv = core(*a)
    return await rv if isawaitable(rv) else rv


def _canonical(table: str, verb: str) -> str:
    return f"{''.join(w.title() for w in table.split('_'))}.{verb}"


def _strip_parent_fields(base: type, *, drop: set[str]) -> type:
    """
    Return a shallow clone of *base* with every field in *drop* removed, so that
    child schemas used by nested routes do not expose parent identifiers.
    """
    if not drop:
        return base

    if get_origin(base) in (list, List):  # List[Model] → List[Stripped]
        elem = get_args(base)[0]
        return list[_strip_parent_fields(elem, drop=drop)]

    if isinstance(base, type) and issubclass(base, BaseModel):
        fld_spec = {
            n: (fld.annotation, fld)
            for n, fld in base.model_fields.items()
            if n not in drop
        }
        cfg = getattr(base, "model_config", ConfigDict())
        cls = create_model(f"{base.__name__}SansParents", __config__=cfg, **fld_spec)
        cls.model_rebuild(force=True)
        return cls

    return base  # primitive / dict / etc.


COMMON_ERRORS = {
    400: {"description": "Bad Request: malformed input"},
    404: {"description": "Not Found"},
    409: {"description": "Conflict: duplicate key"},
    422: {"description": "Unprocessable Entity: constraint failed"},
    500: {"description": "Internal Server Error"},
}

# ───────────────────── register one model’s REST/RPC ───────────────────────


def _register_routes_and_rpcs(  # noqa: N802 – bound as method
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
    """
    Build both REST and RPC surfaces for one SQLAlchemy model.

    The REST routes are thin facades: each fabricates a _RPCReq envelope and
    delegates to `_invoke`, ensuring lifecycle parity with /rpc.
    """
    import functools
    import inspect
    import re
    from typing import Annotated, List

    from fastapi import HTTPException

    # ---------- sync / async detection --------------------------------
    is_async = (
        bool(self.get_async_db)
        if self.get_db is None
        else issubclass(model, AsyncCapable)
    )
    provider = self.get_async_db if is_async else self.get_db

    pk_col = next(iter(model.__table__.primary_key.columns))
    pk_type = getattr(pk_col.type, "python_type", str)

    # ---------- verb specification -----------------------------------
    spec: List[tuple] = [
        ("create", "POST", "", 201, SCreate, SRead, _create),
        ("list", "GET", "", 200, SListIn, List[SRead], _list),
        ("clear", "DELETE", "", 204, None, None, _clear),
        ("read", "GET", "/{item_id}", 200, SDel, SRead, _read),
        ("update", "PATCH", "/{item_id}", 200, SUpdate, SRead, _update),
        ("delete", "DELETE", "/{item_id}", 204, SDel, None, _delete),
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
            ("bulk_create", "POST", "/bulk", 201, List[SCreate], List[SRead], _create),
            ("bulk_delete", "DELETE", "/bulk", 204, List[SDel], None, _delete),
        ]

    # ---------- nested routing ---------------------------------------
    raw_pref = self._nested_prefix(model) or ""
    nested_pref = re.sub(r"/{2,}", "/", raw_pref).rstrip("/") or None
    nested_vars = re.findall(r"{(\w+)}", raw_pref)

    flat_router = APIRouter(prefix=f"/{tab}", tags=[tab])
    routers = (
        (flat_router,)
        if nested_pref is None
        else (flat_router, APIRouter(prefix=nested_pref, tags=[f"nested-{tab}"]))
    )

    # ---------- RBAC guard -------------------------------------------
    def _guard(scope: str):
        async def inner(request: Request):
            if self.authorize and not self.authorize(scope, request):
                raise HTTPException(403, "RBAC")

        return Depends(inner)

    # ---------- endpoint factory -------------------------------------
    for verb, http, path, status, In, Out, core in spec:
        m_id = _canonical(tab, verb)

        def _factory(is_nested_router, *, verb=verb, path=path, In=In, core=core):
            params: list[inspect.Parameter] = [
                inspect.Parameter(  # ← request always first
                    "request",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Request,
                )
            ]

            # parent keys become path vars
            if is_nested_router:
                for nv in nested_vars:
                    params.append(
                        inspect.Parameter(
                            nv,
                            inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            annotation=Annotated[str, Path(...)],
                        )
                    )

            # primary key path var
            if "{item_id}" in path:
                params.append(
                    inspect.Parameter(
                        "item_id",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=pk_type,
                    )
                )

            # payload (query for list, body for others)
            def _visible(t: type) -> type:
                return (
                    _strip_parent_fields(t, drop=set(nested_vars))
                    if is_nested_router
                    else t
                )

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

            # ---- callable body ---------------------------------------
            async def _impl(**kw):
                db: Session | AsyncSession = kw.pop("db")
                req: Request = kw.pop("request")  # always present
                p = kw.pop("p", None)
                item_id = kw.pop("item_id", None)
                parent_kw = {k: kw[k] for k in nested_vars if k in kw}

                # assemble RPC-style param dict
                match verb:
                    case "read" | "delete":
                        rpc_params = {pk: item_id}
                    case "update" | "replace":
                        rpc_params = {pk: item_id, **p.model_dump(exclude_unset=True)}
                    case "list":
                        rpc_params = p.model_dump()
                    case _:
                        rpc_params = p.model_dump() if p is not None else {}

                if parent_kw:
                    rpc_params.update(parent_kw)

                env = _RPCReq(id=None, method=m_id, params=rpc_params)
                ctx = {"request": req, "db": db, "env": env}

                args = {
                    "create": (p,),
                    "bulk_create": (p,),
                    "bulk_delete": (p,),
                    "list": (p,),
                    "clear": (),
                    "read": (item_id,),
                    "delete": (item_id,),
                    "update": (item_id, p),
                    "replace": (item_id, p),
                }[verb]

                if isinstance(db, AsyncSession):

                    def exec_fn(_m, _p, _db=db):
                        return _db.run_sync(lambda s: core(*args, s))

                    return await _invoke(
                        self, m_id, params=rpc_params, ctx=ctx, exec_fn=exec_fn
                    )

                def _direct_call(_m, _p, _db=db):
                    return core(*args, _db)

                return await _invoke(
                    self, m_id, params=rpc_params, ctx=ctx, exec_fn=_direct_call
                )

            _impl.__name__ = f"{verb}_{tab}"
            wrapped = functools.wraps(_impl)(_impl)
            wrapped.__signature__ = inspect.Signature(parameters=params)
            return wrapped

        # mount on routers
        for rtr in routers:
            rtr.add_api_route(
                path,
                _factory(rtr is not flat_router),
                methods=[http],
                status_code=status,
                response_model=Out,
                responses=COMMON_ERRORS,
                dependencies=[self._authn_dep, _guard(m_id)],
            )

        # JSON-RPC shim
        self.rpc[m_id] = self._wrap_rpc(core, In or dict, Out, pk, model)
        self._method_ids.setdefault(m_id, None)

    # include routers
    self.router.include_router(flat_router)
    if len(routers) > 1:
        self.router.include_router(routers[1])


# ───────────────────────── schema builder ───────────────────────────────


def _schema(  # noqa: N802
    self,
    orm_cls: type,
    *,
    name: str | None = None,
    include: Set[str] | None = None,
    exclude: Set[str] | None = None,
    verb: _SchemaVerb = "create",
):
    """
    Build (and cache) a verb-specific Pydantic schema from *orm_cls*.
    Supports rich Column.info["autoapi"] metadata.
    """
    cache_key = (orm_cls, verb, frozenset(include or ()), frozenset(exclude or ()))
    if cache_key in _SchemaCache:
        return _SchemaCache[cache_key]

    mapper = _sa_inspect(orm_cls)
    fields: Dict[str, Tuple[type, Field]] = {}

    attrs = list(mapper.attrs) + [
        v for v in orm_cls.__dict__.values() if isinstance(v, hybrid_property)
    ]
    for attr in attrs:
        is_hybrid = isinstance(attr, hybrid_property)
        is_col_attr = not is_hybrid and hasattr(attr, "columns")
        if not is_hybrid and not is_col_attr:
            continue

        col = attr.columns[0] if is_col_attr and attr.columns else None
        meta_src = (
            col.info
            if col is not None and hasattr(col, "info")
            else getattr(attr, "info", {})
        )
        meta = meta_src.get("autoapi", {}) or {}

        attr_name = getattr(attr, "key", getattr(attr, "__name__", None))
        _info_check(meta, attr_name, orm_cls.__name__)

        # hybrids must opt-in
        if is_hybrid and not meta.get("hybrid"):
            continue

        # legacy flags
        if verb == "create" and col is not None and col.info.get("no_create"):
            continue
        if (
            verb in {"update", "replace"}
            and col is not None
            and col.info.get("no_update")
        ):
            continue

        if verb in meta.get("disable_on", []):
            continue
        if meta.get("write_only") and verb == "read":
            continue
        if meta.get("read_only") and verb != "read":
            continue
        if is_hybrid and attr.fset is None and verb in {"create", "update", "replace"}:
            continue
        if include and attr_name not in include:
            continue
        if exclude and attr_name in exclude:
            continue

        # type / required / default
        if col is not None:
            try:
                py_t = col.type.python_type
            except Exception:
                py_t = Any
            is_nullable = bool(getattr(col, "nullable", True))
            has_default = getattr(col, "default", None) is not None
            required = not is_nullable and not has_default
        else:  # hybrid
            py_t = getattr(attr, "python_type", meta.get("py_type", Any))
            required = False

        if "default_factory" in meta:
            fld = Field(default_factory=meta["default_factory"])
            required = False
        else:
            fld = Field(None if not required else ...)

        if "examples" in meta:
            fld = Field(fld.default, examples=meta["examples"])

        fields[attr_name] = (py_t, fld)

    model_name = name or f"{orm_cls.__name__}{verb.capitalize()}"
    cfg = ConfigDict(from_attributes=True)

    schema_cls = create_model(
        model_name,
        __config__=cfg,
        **fields,
    )
    schema_cls.model_rebuild(force=True)
    _SchemaCache[cache_key] = schema_cls
    return schema_cls


# ───────────────────────── CRUD builder ────────────────────────────────


def _crud(self, model: type) -> None:  # noqa: N802
    """
    Public entry: call `api._crud(User)` to expose canonical CRUD & list routes.
    """
    tab = model.__tablename__
    mapper = _sa_inspect(model)

    if tab in self._registered_tables:
        return
    self._registered_tables.add(tab)

    pk = next(iter(model.__table__.primary_key.columns)).name

    def _S(verb: str, **kw):
        return self._schema(model, verb=verb, **kw)

    SCreate = _S("create")
    SRead = _S("read")
    SDel = _S("delete", include={pk})
    SUpdate = _S("update", exclude={pk})

    def _SList():
        base = dict(skip=(int, Field(0, ge=0)), limit=(int | None, Field(None, ge=10)))
        _scalars = {str, int, float, bool, bytes, uuid.UUID}
        cols: dict[str, tuple[type, Field]] = {}
        for c in model.__table__.columns:
            if c.name == pk:
                continue
            py_t = getattr(c.type, "python_type", Any)
            if py_t in _scalars:
                cols[c.name] = (py_t | None, Field(None))
        return create_model(
            f"{tab}ListParams", __config__=ConfigDict(extra="forbid"), **base, **cols
        )

    SListIn = _SList()

    # ----- DB helpers -------------------------------------------------
    def _create(p: SCreate, db):
        data = p.model_dump()
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
        return obj

    def _read(i, db):
        obj = db.get(model, i)
        if obj is None:
            _not_found()
        return obj

    def _update(i, p: SUpdate, db, *, full=False):
        if isinstance(p, dict):
            p = SUpdate(**p)
        if isinstance(i, str):
            i = uuid.UUID(i)
        obj = db.get(model, i)
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

    def _delete(i, db):
        obj = db.get(model, i)
        if obj is None:
            _not_found()
        db.delete(obj)
        _commit_or_http(db)
        return {pk: i}

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

    # ----- register with route builder --------------------------------
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


# ───────────────────────── RPC adapter (unchanged) ──────────────────────
def _wrap_rpc(self, core, IN, OUT, pk_name, model):  # noqa: N802
    p = iter(signature(core).parameters.values())
    first = next(p, None)
    exp_pm = hasattr(IN, "model_validate")
    out_lst = get_origin(OUT) is list
    elem = get_args(OUT)[0] if out_lst else None
    elem_md = callable(getattr(elem, "model_validate", None)) if elem else False
    single = callable(getattr(OUT, "model_validate", None))

    def h(raw: dict, db: Session):
        obj_in = IN.model_validate(raw) if hasattr(IN, "model_validate") else raw
        data = obj_in.model_dump() if isinstance(obj_in, BaseModel) else obj_in
        if exp_pm:
            r = core(obj_in, db=db)
        else:
            if pk_name in data and first and first.name != pk_name:
                r = core(**{first.name: data.pop(pk_name)}, db=db, **data)
            else:
                r = core(raw[pk_name], data, db=db)

        if not out_lst:
            if isinstance(r, BaseModel):
                return r.model_dump()
            if single:
                return OUT.model_validate(r).model_dump()
            return r

        out: list[Any] = []
        for itm in r:
            if isinstance(itm, BaseModel):
                out.append(itm.model_dump())
            elif elem_md:
                out.append(elem.model_validate(itm).model_dump())
            else:
                out.append(itm)
        return out

    return h


def _commit_or_flush(self, db: Session):  # legacy helper
    db.flush() if db.in_nested_transaction() else db.commit()
