"""
autoapi/v2/rpc_adapter.py  –  RPC adaptation functionality for AutoAPI.

This module contains the logic for wrapping CRUD functions to work with
JSON-RPC calls, handling parameter validation and response formatting.
"""

from __future__ import annotations

from inspect import signature
from typing import Any, get_args, get_origin

from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import inspect as _sa_inspect


def _wrap_rpc(core, IN, OUT, pk_name: str, model):
    """
    Wrap a CRUD function to work with JSON-RPC calls.

    Args:
        core: The core CRUD function to wrap
        IN: Input schema class or dict
        OUT: Output schema class
        pk_name: Primary key field name
        model: SQLAlchemy model class

    Returns:
        Wrapped function that handles RPC parameter conversion
    """
    p = iter(signature(core).parameters.values())
    first = next(p, None)
    exp_pm = hasattr(IN, "model_validate")
    out_lst = get_origin(OUT) is list
    elem = get_args(OUT)[0] if out_lst else None
    elem_md = callable(getattr(elem, "model_validate", None)) if elem else False
    single = callable(getattr(OUT, "model_validate", None))

    # Heuristic: input model for create typically ends with "Create"
    def _is_create_schema() -> bool:
        name = getattr(IN, "__name__", "")
        return isinstance(name, str) and name.endswith("Create")

    def h(raw: dict, db: Session):
        """
        Handle RPC call by converting parameters and formatting response.

        Args:
            raw: Raw RPC parameters dict (already mutated by PRE hooks)
            db: Database session

        Returns:
            Formatted response data
        """
        obj_in = IN.model_validate(raw) if hasattr(IN, "model_validate") else raw
        data = obj_in.model_dump() if isinstance(obj_in, BaseModel) else obj_in

        # ---- CREATE special case ------------------------------------------------
        # Pydantic validation may drop server-injected fields (e.g., tenant_id/owner_id)
        # if they are not present on the Create schema. Merge mapped columns back from
        # the raw (post-hook) payload before calling core.
        if _is_create_schema():
            # Map of ORM column keys for the target model
            col_keys = {c.key for c in _sa_inspect(model).columns}

            # Start from validated payload, then overlay server-injected mapped fields
            enriched = dict(data)
            for k in col_keys:
                v = raw.get(k, None)  # hooks may have added tenant_id/owner_id, etc.
                if v is not None and (k not in enriched or enriched[k] is None):
                    enriched[k] = v

            # Call core with a dict payload (crud layer should accept dict or model)
            r = core(enriched, db=db)

        # ---- Non-create paths (keep existing behavior) --------------------------
        else:
            if exp_pm:
                params = list(signature(core).parameters.values())
                if pk_name in raw and params and params[0].name != pk_name:
                    if len(params) >= 3:
                        r = core(raw[pk_name], obj_in, db=db)
                    else:
                        r = core(raw[pk_name], db=db)
                else:
                    r = core(obj_in, db=db)
            else:
                if pk_name in data and first and first.name != pk_name:
                    r = core(**{first.name: data.pop(pk_name)}, db=db, **data)
                else:
                    r = core(raw[pk_name], data, db=db)

        # ---- Format response based on output schema -----------------------------
        if not out_lst:
            if isinstance(r, BaseModel):
                return r.model_dump()
            if single:
                return OUT.model_validate(r).model_dump()
            return r

        # Handle list responses
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
