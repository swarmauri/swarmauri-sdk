"""
autoapi/v2/rpc_adapter.py – RPC adaptation for AutoAPI.
"""

from __future__ import annotations

from inspect import signature, Parameter
from typing import Any, get_args, get_origin, Iterable

from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import inspect as _sa_inspect


def _wrap_rpc(core, IN, OUT, pk_name: str, model):
    """
    Wrap a CRUD/core function to work with JSON-RPC calls.

    • Validates incoming params against `IN` when available
    • Ensures CREATE paths preserve server-injected fields (tenant_id/owner_id)
    • Chooses model vs. dict payload based on `core`'s type hints
    """

    sig = signature(core)
    params_sig: list[Parameter] = list(sig.parameters.values())

    def _is_create_schema() -> bool:
        name = getattr(IN, "__name__", "")
        return isinstance(name, str) and name.endswith("Create")

    def _core_wants_pydantic_model() -> bool:
        # If any non-db arg is explicitly typed as a Pydantic model, prefer model
        def _is_db(p: Parameter) -> bool:
            return p.name == "db"

        def _is_model_type(t) -> bool:
            return isinstance(t, type) and issubclass(t, BaseModel)

        for p in params_sig:
            if _is_db(p):
                continue
            ann = p.annotation
            if _is_model_type(ann):
                return True
        return False

    # OUT formatting helpers
    out_is_list = get_origin(OUT) is list
    out_elem = get_args(OUT)[0] if out_is_list else None
    elem_has_validate = callable(getattr(out_elem, "model_validate", None)) if out_elem else False
    out_is_single_model = callable(getattr(OUT, "model_validate", None))

    def h(raw: dict, db: Session):
        # 1) Validate input if schema provided
        if hasattr(IN, "model_validate"):
            obj_in = IN.model_validate(raw)
            data = obj_in.model_dump()
            exp_pm = True
        else:
            obj_in = raw
            data = raw
            exp_pm = False

        # 2) CREATE: merge server-injected mapped fields from `raw`
        if _is_create_schema():
            col_keys = {c.key for c in _sa_inspect(model).columns}
            enriched = dict(data)
            for k in col_keys:
                v = raw.get(k, None)  # hooks may have injected these
                if v is not None and (k not in enriched or enriched[k] is None):
                    enriched[k] = v
            payload = enriched
            pass_as_model = False  # pass dict to core.create
        else:
            # Non-create: choose model vs dict by core signature
            pass_as_model = exp_pm and _core_wants_pydantic_model()
            payload = obj_in if pass_as_model else data

        # 3) Dispatch to core with correct positional layout
        #    (support patterns like core(id, payload, db=db) vs core(payload, db=db))
        if pk_name in raw and params_sig and params_sig[0].name != pk_name:
            # core expects (pk, [payload?], db=...)
            if len(params_sig) >= 3:
                r = core(raw[pk_name], payload, db=db)
            else:
                r = core(raw[pk_name], db=db)
        else:
            # core expects ([payload?], db=...)
            # For operations that have no payload (e.g., delete by pk only), payload is ignored
            if pass_as_model or (payload is not raw and payload is not None):
                # payload is either Pydantic model or dict
                # Try to match first param if named differently than pk_name
                first = params_sig[0] if params_sig else None
                if first and first.name not in (pk_name, "db") and first.kind in (
                    Parameter.POSITIONAL_ONLY,
                    Parameter.POSITIONAL_OR_KEYWORD,
                    Parameter.KEYWORD_ONLY,
                ):
                    r = core(payload, db=db)
                else:
                    # No payload parameter; call with db only
                    r = core(db=db)
            else:
                r = core(db=db)

        # 4) Format OUT
        if not out_is_list:
            if isinstance(r, BaseModel):
                return r.model_dump()
            if out_is_single_model:
                return OUT.model_validate(r).model_dump()
            return r

        out: list[Any] = []
        for itm in r:
            if isinstance(itm, BaseModel):
                out.append(itm.model_dump())
            elif elem_has_validate:
                out.append(out_elem.model_validate(itm).model_dump())
            else:
                out.append(itm)
        return out

    return h
