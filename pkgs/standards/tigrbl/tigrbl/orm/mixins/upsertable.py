# tigrbl/v3/mixins/upsertable.py
from __future__ import annotations

import warnings

from typing import Any, Mapping, Sequence, Optional, Tuple
from sqlalchemy import and_, inspect as sa_inspect
from tigrbl.types import Session


class Upsertable:
    """
    Hybrid upsert:
      • If __upsert_keys__ is set and fully present -> decide by those keys
      • Else if all PK parts are present            -> decide by PK
      • Else                                        -> no rewrite
    """

    __upsert_keys__: Sequence[str] | None = None  # optional natural key list

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        warnings.warn(
            "Upsertable is deprecated and will be removed in a future release.",
            DeprecationWarning,
            stacklevel=2,
        )
        cls._install_upsertable_hooks()

    @classmethod
    def _install_upsertable_hooks(cls) -> None:
        hooks = {**getattr(cls, "__tigrbl_hooks__", {})}

        def _append(alias: str, phase: str, fn) -> None:
            phase_map = hooks.get(alias) or {}
            lst = list(phase_map.get(phase) or [])
            if fn not in lst:
                lst.append(fn)
            phase_map[phase] = tuple(lst)
            hooks[alias] = phase_map

        for op in ("create", "update", "replace"):
            _append(op, "PRE_TX_BEGIN", cls._make_upsert_rewrite_hook(op))

        setattr(cls, "__tigrbl_hooks__", hooks)

    @classmethod
    def _make_upsert_rewrite_hook(cls, verb: str):
        tab = "".join(w.title() for w in cls.__tablename__.split("_"))

        async def _rewrite(ctx: Mapping[str, Any]) -> None:
            params = ctx["env"].params if ctx.get("env") else {}
            if hasattr(params, "model_dump"):
                params = params.model_dump()
            if not isinstance(params, Mapping):
                return

            db: Session = ctx["db"]
            mapper = sa_inspect(cls)

            # 1) Try natural keys if declared
            key_names: Sequence[str] | None = cls.__upsert_keys__
            if key_names:
                kv = _extract_values(params, key_names)
                if kv is not None:
                    exists = _exists_by_names(cls, db, key_names, kv)
                    _rewrite_by_existence(ctx, tab, verb, exists)
                    return  # done

            # 2) Fall back to PKs if fully present
            pk_cols = tuple(mapper.primary_key)
            pk_names = tuple(c.key for c in pk_cols)
            kv = _extract_values(params, pk_names)
            if kv is None:
                return  # not enough info → no rewrite

            exists = _exists_by_pk(cls, db, pk_cols, kv)
            _rewrite_by_existence(ctx, tab, verb, exists)

        return _rewrite


def _extract_values(
    p: Mapping[str, Any], names: Sequence[str]
) -> Optional[Tuple[Any, ...]]:
    vals = []
    for n in names:
        v = p.get(n)
        if v is None:
            return None
        vals.append(v)
    return tuple(vals)


def _exists_by_names(
    model, db: Session, names: Sequence[str], vals: Tuple[Any, ...]
) -> bool:
    q = db.query(model)
    for n, v in zip(names, vals):
        q = q.filter(getattr(model, n) == v)
    return db.query(q.exists()).scalar() is True


def _exists_by_pk(model, db: Session, pk_cols, pk_vals: Tuple[Any, ...]) -> bool:
    if len(pk_cols) == 1:
        # fast path
        return db.get(model, pk_vals[0]) is not None
    conds = [getattr(model, c.key) == v for c, v in zip(pk_cols, pk_vals)]
    return db.query(db.query(model).filter(and_(*conds)).exists()).scalar() is True


def _rewrite_by_existence(ctx, tab: str, verb: str, exists: bool) -> None:
    if verb == "create" and exists:
        ctx["env"].method = f"{tab}.update"
    elif verb == "update" and not exists:
        ctx["env"].method = f"{tab}.create"
    elif verb == "replace":
        ctx["env"].method = f"{tab}.update" if exists else f"{tab}.create"
