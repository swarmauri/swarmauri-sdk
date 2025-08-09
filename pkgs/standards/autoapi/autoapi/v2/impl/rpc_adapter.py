# autoapi/v2/rpc_adapter.py
from __future__ import annotations

from inspect import signature
from typing import Any, get_args, get_origin

from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import inspect as _sa_inspect


def _wrap_rpc(core, IN, OUT, pk_name: str, model):
    p = iter(signature(core).parameters.values())
    first = next(p, None)
    exp_pm = hasattr(IN, "model_validate")
    out_lst = get_origin(OUT) is list
    elem = get_args(OUT)[0] if out_lst else None
    elem_md = callable(getattr(elem, "model_validate", None)) if elem else False
    single = callable(getattr(OUT, "model_validate", None))

    # Precompute mapped column keys for generic overlay of server-injected fields
    try:
        _col_keys = {c.key for c in _sa_inspect(model).columns}
    except Exception:
        _col_keys = set()

    def h(raw: dict, db: Session):
        # --- Normalize `raw` to a dict (handles Pydantic models) ---
        raw_map = raw.model_dump() if hasattr(raw, "model_dump") else raw

        # --- NEW: filter extras before validation to avoid Pydantic "extra=forbid" errors
        if hasattr(IN, "model_validate"):
            try:
                allowed = set(getattr(IN, "model_fields", {}).keys())
            except Exception:
                allowed = None
            if isinstance(raw_map, dict) and allowed:
                raw_for_validate = {k: raw_map[k] for k in raw_map.keys() & allowed}
            else:
                raw_for_validate = raw_map
            obj_in = IN.model_validate(raw_for_validate)
            data = obj_in.model_dump()
        else:
            obj_in = raw_map
            data = raw_map

        # Overlay ANY server-injected mapped columns from raw → payload
        # Only overwrite when payload is missing or None.
        payload = dict(data)
        if _col_keys and isinstance(raw_map, dict):
            for k in _col_keys:
                rv = raw_map.get(k, None)
                if rv is not None and (k not in payload or payload.get(k) is None):
                    payload[k] = rv

        # Dispatch to core (preserve prior calling convention), always using dict payload
        if exp_pm:
            params = list(signature(core).parameters.values())
            if isinstance(raw_map, dict) and pk_name in raw_map and params and params[0].name != pk_name:
                if len(params) >= 3:
                    r = core(raw_map[pk_name], payload, db=db)
                else:
                    r = core(raw_map[pk_name], db=db)
            else:
                r = core(payload, db=db)
        else:
            if isinstance(payload, dict) and pk_name in payload and first and first.name != pk_name:
                r = core(**{first.name: payload.pop(pk_name)}, db=db, **payload)
            else:
                pk_val = raw_map.get(pk_name) if isinstance(raw_map, dict) else None
                r = core(pk_val, payload, db=db)

        # Format response
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
