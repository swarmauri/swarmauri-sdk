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
        # 1) Validate if schema exists; always derive a dict payload
        obj_in = IN.model_validate(raw) if hasattr(IN, "model_validate") else raw
        data = obj_in.model_dump() if isinstance(obj_in, BaseModel) else obj_in

        # 2) Overlay ANY server-injected mapped columns from raw → payload
        #    Only overwrite when payload is missing or None.
        payload = dict(data)
        if _col_keys:
            for k in _col_keys:
                rv = raw.get(k, None)
                if rv is not None and (k not in payload or payload.get(k) is None):
                    payload[k] = rv

        # 3) Dispatch to core (preserve prior calling convention), always using dict payload
        if exp_pm:
            params = list(signature(core).parameters.values())
            if pk_name in raw and params and params[0].name != pk_name:
                if len(params) >= 3:
                    r = core(raw[pk_name], payload, db=db)
                else:
                    r = core(raw[pk_name], db=db)
            else:
                r = core(payload, db=db)
        else:
            if pk_name in payload and first and first.name != pk_name:
                r = core(**{first.name: payload.pop(pk_name)}, db=db, **payload)
            else:
                r = core(raw.get(pk_name), payload, db=db)

        # 4) Format response
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
