"""
autoapi_impl.py  –  framework-agnostic helpers rebound onto AutoAPI.
Compatible with FastAPI 1.5, Pydantic 2.x, SQLAlchemy 2.x.
"""
import uuid
from inspect import signature, isawaitable
from typing  import Any, List, get_origin, get_args, Annotated, ForwardRef

from fastapi                 import APIRouter, Depends, HTTPException, Request
from pydantic                import BaseModel, Field, create_model, ConfigDict
from sqlalchemy.orm          import Session
from sqlalchemy.ext.asyncio  import AsyncSession

from .mixins import Replaceable, BulkCapable, AsyncCapable

# ───────────────────────── small utils ───────────────────────────────────
async def _run(core, *a):
    rv = core(*a)
    return await rv if isawaitable(rv) else rv


def _canonical(table: str, verb: str) -> str:
    return f"{''.join(w.title() for w in table.split('_'))}.{verb}"


# ───────────────────── register one model’s REST/RPC ────────────────────
def _register_routes_and_rpcs(      # noqa: N802
    self,
    model:      type,
    tab:        str,
    pk:         str,
    SCreate, SRead, SDel, SUpdate, SListIn,
    _create, _read, _update, _delete, _list, _clear,
) -> None:

    is_async   = issubclass(model, AsyncCapable)
    provider   = self.get_async_db if is_async else self.get_db

    spec: List[tuple] = [
        ("create",  "POST",    "",            SCreate,           SRead,        _create),
        ("list",    "GET",     "",            SListIn,           List[SRead],  _list),
        ("clear",   "DELETE",  "",            None,              dict,         _clear),
        ("read",    "GET",     "/{item_id}",  SDel,              SRead,        _read),
        ("update",  "PATCH",   "/{item_id}",  SUpdate,           SRead,        _update),
        ("delete",  "DELETE",  "/{item_id}",  SDel,              SDel,         _delete),
    ]
    if issubclass(model, Replaceable):
        spec.append(("replace", "PUT", "/{item_id}",
                     SCreate, SRead,
                     lambda i, p, db: _update(i, p, db, full=True)))
    if issubclass(model, BulkCapable):
        spec += [
            ("bulk_create", "POST",   "/bulk", List[SCreate], List[SRead], _create),
            ("bulk_delete", "DELETE", "/bulk", List[SDel],    dict,        _delete),
        ]

    flat        = APIRouter(prefix=f"/{tab}", tags=[tab])
    nested_pref = self._nested_prefix(model)
    routers     = (flat,) if nested_pref is None else (
                  flat,
                  APIRouter(prefix=nested_pref, tags=[f"nested-{tab}"]),
                 )

    def _guard(scope: str):
        async def g(request: Request):
            if self.authorize and not self.authorize(scope, request):
                raise HTTPException(403, "RBAC")
        return Depends(g)

    for verb, http, path, In, Out, core in spec:
        m_id = _canonical(tab, verb)

        # -------- endpoint factory --------------------------------------
        def _ep_factory(verb=verb, path=path, In=In, core=core):
            if verb == "list":
                async def ep(
                    db: Annotated[Any, Depends(provider)],
                    p: Annotated[In, Depends()]
                ):
                    return await _run(core, p, db)

            elif "{item_id}" in path and http in ("GET", "DELETE"):
                async def ep(
                    item_id: Any,
                    db: Annotated[Any, Depends(provider)]
                ):
                    return await _run(core, item_id, db)

            elif http in ("PATCH", "PUT"):
                async def ep(
                    item_id: Any,
                    p: Annotated[In, Depends()],
                    db: Annotated[Any, Depends(provider)]
                ):
                    return await _run(core, item_id, p, db)

            elif In is not None:  # create & bulk
                async def ep(
                    p: Annotated[In, Depends()],
                    db: Annotated[Any, Depends(provider)]
                ):
                    return await _run(core, p, db)

            else:                 # clear
                async def ep(db: Annotated[Any, Depends(provider)]):
                    return await _run(core, db)

            ep.__name__ = f"{verb}_{tab}"
            return ep

        for r in routers:
            r.add_api_route(
                path,
                _ep_factory(),
                methods=[http],
                response_model=Out,
                dependencies=[self._authn_dep, _guard(m_id)],
            )

        self.rpc[m_id] = self._wrap_rpc(core, In or dict, Out, pk, model)
        self._method_ids.setdefault(m_id, None)

    self.router.include_router(flat)
    if nested_pref:
        self.router.include_router(routers[1])


# ───────────────────────── schema helper ────────────────────────────────
def _schema(self, orm_cls: type, *, name: str,
            include: set[str] | None = None,
            exclude: set[str] | None = None):
    flds = {
        c.name: (
            getattr(c.type, "python_type", Any),
            Field(None if c.nullable or c.default is not None else ...),
        )
        for c in orm_cls.__table__.columns
        if (include is None or c.name in include)
           and (exclude is None or c.name not in exclude)
    }
    cfg = ConfigDict(from_attributes=True)
    M   = create_model(name, __config__=cfg, **flds)  # type: ignore[arg-type]
    M.model_rebuild(force=True)
    return M


# ───────────────────────── CRUD builder ────────────────────────────────
def _crud(self, model: type) -> None:                         # noqa: N802
    tab = model.__tablename__
    # ─── duplicate-registration guard ────────────────────────────────
    if tab in self._registered_tables:          # ❷ fast-exit if already done
        return
    self._registered_tables.add(tab)
    # ----------------------------------------------------------------

    pk  = next(iter(model.__table__.primary_key.columns)).name

    _S      = lambda n, **kw: self._schema(model, name=n, **kw)
    SCreate = _S(f"{tab}Create", exclude={pk})
    SRead   = _S(f"{tab}Read")
    SDel    = _S(f"{tab}Delete", include={pk})
    SUpdate = _S(f"{tab}Update", include=set(SCreate.model_fields))

    def _SList():
        base = dict(skip=(int, Field(0, ge=0)),
                    limit=(int | None, Field(None, ge=1)))
        def _safe_py(col):
            try:
                t = col.type.python_type                       # may raise
            except Exception:
                return Any
            # Filter out internal / undefined SQLAlchemy artifacts
            if isinstance(t, ForwardRef) or getattr(t, "__module__", "").startswith("sqlalchemy."):
                return Any
            return t
        cols = {c.name: (_safe_py(c) | None, Field(None))
                for c in model.__table__.columns}
        return create_model(f"{tab}ListParams",
                            __config__=ConfigDict(extra="forbid"),
                            **base, **cols)
    SListIn = _SList()
    SListIn.model_rebuild(force=True)      # ✱ resolve any forward refs

    safe = lambda db: (db.flush() if db.in_nested_transaction() else db.commit())
    _404 = lambda: HTTPException(404)

    def _create(p, db):
        o = model(**p.model_dump()); db.add(o); safe(db); db.refresh(o); return o

    def _read(i, db):
        return (o := db.get(model, i)) or _404()

    def _update(i, p, db, *, full=False):
        o = db.get(model, i) or _404()
        if full:
            for c in model.__table__.columns:
                if c.name != pk:
                    setattr(o, c.name, getattr(p, c.name, None))
        else:
            for k, v in p.model_dump(exclude_unset=True).items():
                setattr(o, k, v)
        safe(db); db.refresh(o); return o

    _delete = lambda i, db: (db.delete(db.get(model, i) or _404()),
                             safe(db), {pk: i})[-1]

    def _list(p, db):
        d = p.model_dump(exclude_defaults=True, exclude_none=True)
        q = (db.query(model)
               .filter_by(**{k: d[k] for k in d if k not in ("skip", "limit")})
               .offset(d.get("skip", 0)))
        if lim := d.get("limit"):
            q = q.limit(lim)
        return q.all()

    _clear = lambda db: {"deleted": db.query(model).delete() or safe(db)}

    self._register_routes_and_rpcs(
        model, tab, pk,
        SCreate, SRead, SDel, SUpdate, SListIn,
        _create, _read, _update, _delete, _list, _clear
    )


# ───────────────────────── RPC adapter (unchanged) ──────────────────────
def _wrap_rpc(self, core, IN, OUT, pk_name, model):           # noqa: N802
    p       = iter(signature(core).parameters.values())
    first   = next(p, None)
    exp_pm  = bool(first) and isinstance(first.annotation, type) \
              and issubclass(first.annotation, BaseModel)
    out_lst = get_origin(OUT) is list
    elem    = get_args(OUT)[0] if out_lst else None
    elem_md = callable(getattr(elem, "model_validate", None)) if elem else False
    single  = callable(getattr(OUT, "model_validate", None))

    def h(raw: dict, db: Session):
        obj_in = IN.model_validate(raw) if hasattr(IN, "model_validate") else raw
        data   = obj_in.model_dump() if isinstance(obj_in, BaseModel) else obj_in

        if exp_pm:
            r = core(obj_in, db=db)
        else:
            if pk_name in data and first and first.name != pk_name:
                r = core(**{first.name: data.pop(pk_name)}, db=db, **data)
            else:
                r = core(**data, db=db)

        if not out_lst:
            if isinstance(r, BaseModel): return r.model_dump()
            if single:                  return OUT.model_validate(r).model_dump()
            return r

        out: list[Any] = []
        for itm in r:
            if isinstance(itm, BaseModel): out.append(itm.model_dump())
            elif elem_md:                  out.append(elem.model_validate(itm).model_dump())
            else:                          out.append(itm)
        return out

    return h


def commit_or_flush(self, db: Session):
    db.flush() if db.in_nested_transaction() else db.commit()
