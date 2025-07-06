"""
autoapi_impl.py
Long-form helpers for AutoAPI.  These stay 100 % framework-agnostic
and receive `self` explicitly, so we can bind them onto AutoAPI later.
"""
import uuid
from inspect import signature
from typing  import Any, get_origin, get_args, Type, Any, List


from fastapi                import HTTPException, APIRouter, Depends, Request
from pydantic               import BaseModel, Field, create_model, ConfigDict
from sqlalchemy.orm         import Session
from inspect                import isawaitable
from sqlalchemy.ext.asyncio import AsyncSession

from .mixins                import Replaceable, BulkCapable, AsyncCapable

async def _run(core, *args):
    rv = core(*args)
    return await rv if isawaitable(rv) else rv

def _canonical(table: str, verb: str) -> str:
    """PascalCase table + '.' + lowerCamel verb."""
    to_pascal = ''.join(w.title() for w in table.split('_'))
    return f"{to_pascal}.{verb}"

# ---------------------------------------------------------------------------
def _register_routes_and_rpcs(      # noqa: N802 (keep camel to match caller)
    self,
    model:      type,
    tab:        str,
    pk:         str,
    SCreate, SRead, SDel, SUpdate, SListIn,
    _create, _read, _update, _delete, _list, _clear,
) -> None:
    """
    Build verb-spec table, REST routers, and RPC adapters for *one*
    SQLAlchemy model.
    """

    # ── choose sync or async provider per model ──────────────────────
    is_async_model = issubclass(model, AsyncCapable)
    provider       = self.get_async_db if is_async_model else self.get_db

    # ---------- verb specification -----------------------------------
    spec: List[tuple] = [
        ("create",  "POST",    "",            SCreate,           SRead,        _create),
        ("list",    "GET",     "",            SListIn,           List[SRead],  _list),
        ("clear",   "DELETE",  "",            None,              dict,         _clear),
        ("read",    "GET",     "/{item_id}",  SDel,              SRead,        _read),
        ("update",  "PATCH",   "/{item_id}",  SUpdate,           SRead,        _update),
        ("delete",  "DELETE",  "/{item_id}",  SDel,              SDel,         _delete),
    ]
    if issubclass(model, Replaceable):
        spec.append(("replace", "PUT", "/{item_id}", SCreate, SRead,
                     lambda i, p, db: _update(i, p, db, full=True)))
    if issubclass(model, BulkCapable):
        spec += [
            ("bulk_create", "POST",  "/bulk", List[SCreate], List[SRead], _create),
            ("bulk_delete", "DELETE","/bulk", List[SDel],    dict,        _delete),
        ]

    # ---------- routers ----------------------------------------------
    flat   = APIRouter(prefix=f"/{tab}", tags=[tab])
    nested_prefix = self._nested_prefix(model)
    routers = (flat,) if nested_prefix is None else (
        flat,
        APIRouter(prefix=nested_prefix, tags=[f"nested-{tab}"])
    )

    # ---------- guard factory ----------------------------------------
    def _guard_factory(scope: str):
        async def _guard(request: Request):
            if self.authorize and not self.authorize(scope, request):
                raise HTTPException(403, "RBAC")
        return Depends(_guard)

    # ---------- single registration loop -----------------------------
    for verb, http, path, In, Out, core in spec:
        method_id = _canonical(tab, verb)

        # REST handler factory (always async def − works for both modes)
        def ep_factory(verb=verb, http=http, path=path, In=In, core=core):
            if verb == "list":
                async def ep(p: In = Depends(),
                             db = Depends(provider)):
                    return await _run(core, p, db)

            elif "{item_id}" in path and http in ("GET", "DELETE"):
                async def ep(item_id: Any,
                             db = Depends(provider)):
                    return await _run(core, item_id, db)

            elif http in ("PATCH", "PUT"):
                async def ep(item_id: Any, p: In,
                             db = Depends(provider)):
                    return await _run(core, item_id, p, db)

            elif In is not None:  # create & bulk ops
                async def ep(p: In,
                             db = Depends(provider)):
                    return await _run(core, p, db)

            else:                 # clear
                async def ep(db = Depends(provider)):
                    return await _run(core, db)

            ep.__name__ = f"{verb}_{tab}"
            return ep

        # register on each router (flat and optional nested)
        for router in routers:
            router.add_api_route(
                path,
                ep_factory(),
                methods=[http],
                response_model=Out,
                dependencies=[self._authn_dep, _guard_factory(method_id)],
            )

        # RPC binding (wrap_rpc already async-aware)
        self.rpc[method_id] = self._wrap_rpc(core, In or dict, Out, pk, model)

        # ordered set of canonical method names
        self._method_ids.setdefault(method_id, None)

    # ---------- mount routers on parent ------------------------------
    self.router.include_router(flat)
    if nested_prefix:
        self.router.include_router(routers[1])



# ────────────────────────── _schema ──────────────────────────
def _schema(
    self, orm_cls: type, *, name: str,
    include: set[str] | None = None,
    exclude: set[str] | None = None,
):
    """Return a minimal Pydantic model that mirrors *orm_cls*."""
    flds = {
        c.name: (
            getattr(c.type, "python_type", Any),
            Field(None if c.nullable or c.default is not None else ...)
        )
        for c in orm_cls.__table__.columns
        if (include is None or c.name in include)
           and (exclude is None or c.name not in exclude)
    }
    cfg = ConfigDict(from_attributes=True)
    M   = create_model(name, __config__=cfg, **flds)
    M.model_rebuild(force=True)
    return M


# ────────────────────────── _crud ────────────────────────────
def _crud(self, model: type) -> None:
    """
    Register REST + RPC endpoints for *model*.
    Extracted verbatim from the original class for clarity
    (trimmed comments for brevity).
    """
    tab, pk = model.__tablename__, next(iter(model.__table__.primary_key.columns)).name

    # ---------- Pydantic schemas ----------
    _S         = lambda n, **kw: self._schema(model, name=n, **kw)
    SCreate    = _S(f"{tab}Create", exclude={pk})
    SRead      = _S(f"{tab}Read")
    SDel       = _S(f"{tab}Delete", include={pk})
    SUpdate    = _S(f"{tab}Update", include=set(SCreate.model_fields))

    def _SList():
        base = dict(skip=(int, Field(0, ge=0)),
                    limit=(int | None, Field(None, ge=1)))
        cols = {c.name: (getattr(c.type, "python_type", Any) | None, Field(None))
                for c in model.__table__.columns}
        return create_model(
            f"{tab}ListParams",
            __config__=ConfigDict(extra="forbid"),
            **base, **cols
        )
    SListIn = _SList()

    safe   = lambda db: (db.flush() if db.in_nested_transaction() else db.commit())
    _404   = lambda: HTTPException(404)

    def _create(p, db): o = model(**p.model_dump()); db.add(o); safe(db); db.refresh(o); return o
    def _read(i, db):   return (o := db.get(model, i)) or _404()
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

    # bulk helpers, nested routers, RPC wrapping … unchanged ↓
    # (retain full original logic here or split further if desired)
    # ...
    self._register_routes_and_rpcs(
        model, tab, pk,
        SCreate, SRead, SDel, SUpdate, SListIn,
        _create, _read, _update, _delete, _list, _clear
    )


# ────────────────────────── _wrap_rpc ─────────────────────────
def _wrap_rpc(self, core, IN, OUT, pk_name, model):
    """
    Adapter that maps JSON-RPC envelopes to *core* call signatures.
    """
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
            # route primary-key positional / keyword gymnastics
            if pk_name in data and first and first.name != pk_name:
                r = core(**{first.name: data.pop(pk_name)}, db=db, **data)
            else:
                r = core(**data, db=db)

        # normalise output
        if not out_lst:
            if isinstance(r, BaseModel):          return r.model_dump()
            if single:                            return OUT.model_validate(r).model_dump()
            return r

        out = []
        for itm in r:
            if isinstance(itm, BaseModel):        out.append(itm.model_dump())
            elif elem_md:                         out.append(elem.model_validate(itm).model_dump())
            else:                                 out.append(itm)
        return out

    return h

def commit_or_flush(self, db: Session):
    db.flush() if db.in_nested_transaction() else db.commit()