from collections import defaultdict
from enum import Enum, auto
from functools import wraps
from inspect import signature
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Literal,
    Protocol,
    Type,
    get_args,
    get_origin,
)

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, create_model
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, declarative_base


# ────────────────── JSON-RPC envelopes (unchanged) ────────────────────
class _RPCReq(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: dict
    id: str | int | None = None


class _RPCRes(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    result: Any | None = None
    error: dict | None = None
    id: str | int | None = None


def _ok(data: Any, q: _RPCReq) -> _RPCRes:
    return _RPCRes(result=data, id=q.id)


def _err(c: int, m: str, q: _RPCReq) -> _RPCRes:
    return _RPCRes(error={"code": c, "message": m}, id=q.id)


# ─────────────────────────── AutoAPI  ─────────────────────────────────
class AutoAPI:
    # ── lifecycle phases & hook machinery baked-in ────────────────────
    class Phase(Enum):
        PRE_TX_BEGIN = auto()
        POST_HANDLER = auto()
        PRE_COMMIT = auto()
        POST_COMMIT = auto()
        POST_RESPONSE = auto()
        ON_ERROR = auto()

    class _Hook(Protocol):
        async def __call__(self, ctx: Dict[str, Any]) -> None: ...

    def __init__(
        self,
        base: declarative_base,
        get_db: Callable[[], Session],  # plain callable, no DI
        *,
        include: set[type] | None = None,
        authorise: Callable[[str, Request], bool] | None = None,
        prefix: str = "",
    ) -> None:
        self.base = base
        self.get_db = get_db
        self.include = include
        self.authorise = authorise

        self.router = APIRouter(prefix=prefix)
        self._rpc: Dict[str, Callable[[dict, Session], Any]] = {}
        self.rpc = self._rpc

        # 1️⃣  registry   phase  ➜  { method|None : [hooks…] }
        self._hook_registry: Dict[
            AutoAPI.Phase, Dict[str | None, list[AutoAPI._Hook]]
        ] = defaultdict(lambda: defaultdict(list))

        # 2️⃣  helper – name remains _hook_deco
        def _hook_deco(
            phase: AutoAPI.Phase,
            fn: Callable[[Dict[str, Any]], Any] | None = None,
            *,
            method: str | None = None,  # None ⇒ global
        ):
            """
            ▸ Decorator:   @api._hook_deco(api.Phase.POST_COMMIT, method="users.list")
            ▸ Direct call: api._hook_deco(api.Phase.POST_COMMIT, cb, method="users.list")
            """

            def _registrar(f: Callable[[Dict[str, Any]], Any]):
                # promote sync → async exactly once
                if not callable(getattr(f, "__await__", None)):

                    async def _wrap(ctx: Dict[str, Any]):
                        f(ctx)

                    async_fn: AutoAPI._Hook = _wrap  # type: ignore
                else:
                    async_fn = f  # type: ignore
                self._hook_registry[phase][method].append(async_fn)  # FIFO append
                return f

            return _registrar if fn is None else _registrar(fn)

        # keep the original public names
        self._hook_deco = _hook_deco
        self.register_hook = _hook_deco  # imperative alias
        self.hook = _hook_deco  # optional short alias

        # generate CRUD + RPC for each ORM class
        for m in base.registry.mappers:
            cls = m.class_
            if include and cls not in include:
                continue
            self._crud(cls)

        # meta & gateway routes -----------------------------------------
        @self.router.get("/methodz")
        def _methods() -> list[str]:
            return sorted(self._rpc.keys())

        @self.router.get("/healthz")
        def _health(db: Session = Depends(self.get_db)):
            try:
                db.execute("SELECT 1")
                return {"ok": True}
            finally:
                db.close()

        @self.router.post("/rpc", response_model=_RPCRes)
        async def _gateway(
            req: Request,
            db: Session = Depends(self.get_db),  # ← DI here
        ) -> _RPCRes:
            ctx: Dict[str, Any] = {"request": req}

            # -------- parse envelope ----------
            try:
                env = _RPCReq.model_validate(await req.json())
                ctx["env"] = env
            except Exception as exc:
                await self._run(self.Phase.ON_ERROR, ctx | {"error": exc})
                dummy = _RPCReq(jsonrpc="2.0", method="", params={}, id=None)
                return _err(-32700, f"Parse error: {exc}", dummy)

            # -------- authorisation ----------
            if self.authorise and not self.authorise(env.method, req):
                return _err(403, "Forbidden", env)

            fn = self._rpc.get(env.method)
            if not fn:
                return _err(-32601, "Method not found", env)

            # -------- open DB session ----------
            ctx["db"] = db
            try:
                await self._run(self.Phase.PRE_TX_BEGIN, ctx)
                result = fn(env.params, db)  # may raise
                ctx["result"] = result
                await self._run(self.Phase.POST_HANDLER, ctx)

                if db.in_transaction():
                    await self._run(self.Phase.PRE_COMMIT, ctx)
                    db.commit()
                    await self._run(self.Phase.POST_COMMIT, ctx)

                payload = _ok(result, env)
                await self._run(self.Phase.POST_RESPONSE, ctx | {"response": payload})
                return payload

            except Exception as exc:
                db.rollback()
                await self._run(self.Phase.ON_ERROR, ctx | {"error": exc})
                if isinstance(exc, HTTPException):
                    return _err(exc.status_code, exc.detail, env)
                return _err(-32000, str(exc), env)

            finally:
                db.close()

    async def _run(self, phase: Phase, ctx: Dict[str, Any]) -> None:
        env = ctx.get("env")
        method = getattr(env, "method", None) if env else None  # ← fixed

        for fn in self._hook_registry[phase].get(method, []):  # method-specific
            await fn(ctx)
        for fn in self._hook_registry[phase].get(None, []):  # global
            await fn(ctx)

    # ── transactional decorator (instance-aware) ──────────────────────
    def transactional(self, fn: Callable[..., Any]):
        """
        Decorator to wrap an RPC handler in an explicit DB transaction.
        """

        @wraps(fn)
        def wrapper(params, db: Session, *a, **k):
            db.begin()
            try:
                res = fn(params, db, *a, **k)
                db.commit()
                return res
            except Exception:
                db.rollback()
                raise

        return wrapper

    # ── helper: commit or flush (unchanged logic) ─────────────────────
    @staticmethod
    def _commit_or_flush(db: Session) -> None:
        if db.in_nested_transaction():
            db.flush()
        else:
            db.commit()

    # ── pydantic schema synthesiser (unchanged) ───────────────────────
    @staticmethod
    def _schema(
        orm_cls: type,
        *,
        name: str,
        include: set[str] | None = None,
        exclude: set[str] | None = None,
    ) -> Type[BaseModel]:
        fields: Dict[str, tuple[type, Field]] = {}
        for col in orm_cls.__table__.columns:  # type: ignore[attr-defined]
            if include and col.name not in include:
                continue
            if exclude and col.name in exclude:
                continue
            typ = getattr(col.type, "python_type", Any)
            required = None if col.nullable or col.default is not None else ...
            fields[col.name] = (typ, Field(required))
        cfg = ConfigDict(from_attributes=True)
        M = create_model(name, __config__=cfg, **fields)  # type: ignore[arg-type]
        M.model_rebuild(force=True)
        return M

    # ── CRUD + RPC generation per ORM model ───────────────────────────
    def _crud(self, model: Type) -> None:
        tab = model.__tablename__
        pk_name = next(iter(model.__table__.primary_key.columns)).name

        # Pydantic schemas
        SCreate = self._schema(model, name=f"{tab}Create", exclude={pk_name})
        SRead = self._schema(model, name=f"{tab}Read")
        SDel = self._schema(model, name=f"{tab}Delete", include={pk_name})
        SUpdate = self._schema(
            model, name=f"{tab}Update", include=set(SCreate.model_fields)
        )

        def _make_list_schema() -> Type[BaseModel]:
            fld: Dict[str, tuple[type, Field]] = {
                "skip": (int, Field(0, ge=0)),
                "limit": (int | None, Field(None, ge=1)),
            }
            for col in model.__table__.columns:  # type: ignore[attr-defined]
                py_t = getattr(col.type, "python_type", Any)
                fld[col.name] = (py_t | None, Field(None))
            cfg = ConfigDict(extra="forbid")
            M = create_model(f"{tab}ListParams", __config__=cfg, **fld)  # type: ignore[arg-type]
            M.model_rebuild(force=True)
            return M

        SListIn = _make_list_schema()

        # ── REST handlers (manual DB session mgmt) ────────────────────
        sub = APIRouter(prefix=f"/{tab}", tags=[tab])

        @sub.post("", response_model=SRead)
        def _create(p: SCreate, db: Session = Depends(self.get_db)):
            obj = model(**p.model_dump())
            db.add(obj)
            try:
                self._commit_or_flush(db)
            except IntegrityError as exc:
                db.rollback()
                raise HTTPException(409, str(exc.orig))  # 409 Conflict
            db.refresh(obj)
            return obj

        @sub.get("/{item_id}", response_model=SRead)
        def _read(item_id: str, db: Session = Depends(self.get_db)) -> SRead:
            if (o := db.get(model, item_id)) is None:
                raise HTTPException(404)
            return o

        @sub.delete("/{item_id}", response_model=SDel)
        def _delete(item_id: str, db: Session = Depends(self.get_db)):
            if (o := db.get(model, item_id)) is None:
                raise HTTPException(404)
            db.delete(o)
            self._commit_or_flush(db)
            return {pk_name: item_id}

        @sub.patch("/{item_id}", response_model=SRead)
        def _update(item_id: str, p: SUpdate, db: Session = Depends(self.get_db)):
            if (o := db.get(model, item_id)) is None:
                raise HTTPException(404)
            for k, v in p.model_dump(exclude_unset=True).items():
                setattr(o, k, v)
            self._commit_or_flush(db)
            db.refresh(o)
            return o

        @sub.delete("", response_model=dict)
        def _clear(db: Session = Depends(self.get_db)):
            n = db.query(model).delete()  # bulk delete
            self._commit_or_flush(db)
            return {"deleted": n}

        @sub.get("", response_model=list[SRead])
        def _list(
            p: SListIn = Depends(), db: Session = Depends(self.get_db)
        ) -> list[SRead]:
            data = p.model_dump(exclude_defaults=True, exclude_none=True)
            skip = data.pop("skip", 0)
            limit = data.pop("limit", None)

            q = db.query(model)
            for col, val in data.items():  # apply column = value filters
                q = q.filter(getattr(model, col) == val)

            q = q.offset(skip)
            if limit is not None:
                q = q.limit(limit)
            return q.all()

        self.router.include_router(sub)

        # ── JSON-RPC mirrors (use same DB session as gateway) ─────────
        def _wrap(core, IN, OUT):
            params_iter = iter(signature(core).parameters.values())
            first_param = next(params_iter, None)  # ← no StopIteration
            try:
                expects_pm = bool(first_param) and issubclass(
                    first_param.annotation, BaseModel
                )
            except TypeError:
                expects_pm = False
            first_name = first_param.name if first_param else None

            # identify list element model if OUT is list[Model]
            out_is_list = get_origin(OUT) is list
            elem_model = get_args(OUT)[0] if out_is_list else None
            elem_validator = (
                callable(getattr(elem_model, "model_validate", None))
                if elem_model
                else False
            )
            single_validator = callable(getattr(OUT, "model_validate", None))

            def handler(raw: dict, db: Session):
                # ---------- IN ----------
                obj_in = (
                    IN.model_validate(raw) if hasattr(IN, "model_validate") else raw
                )

                if expects_pm:  # CREATE
                    res = core(obj_in, db=db)
                else:  # READ / DELETE / LIST
                    data = (
                        obj_in.model_dump() if isinstance(obj_in, BaseModel) else obj_in
                    )
                    if pk_name in data and first_name != pk_name:
                        data[first_name] = data.pop(pk_name)
                    res = core(**data, db=db)

                # ---------- OUT ----------
                # single
                if not out_is_list:
                    if isinstance(res, BaseModel):
                        return res.model_dump()
                    if single_validator:  # ORM row → Pydantic
                        return OUT.model_validate(res).model_dump()
                    return res  # already a dict

                # list
                serialised = []
                for item in res:
                    if isinstance(item, BaseModel):
                        serialised.append(item.model_dump())
                    elif elem_validator:
                        serialised.append(elem_model.model_validate(item).model_dump())
                    else:
                        serialised.append(item)
                return serialised

            return handler

        self._rpc[f"{tab}.create"] = _wrap(_create, SCreate, SRead)
        self._rpc[f"{tab}.read"] = _wrap(_read, SDel, SRead)
        self._rpc[f"{tab}.update"] = _wrap(_update, SUpdate, SRead)
        self._rpc[f"{tab}.delete"] = _wrap(_delete, SDel, SDel)
        self._rpc[f"{tab}.list"] = _wrap(_list, SListIn, list[SRead])
        self._rpc[f"{tab}.clear"] = _wrap(_clear, dict, dict)
