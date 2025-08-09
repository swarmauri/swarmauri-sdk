"""
autoapi/v2/impl/rpc_adapter.py  –  RPC adaptation functionality for AutoAPI.

Adapts CRUD/core callables for JSON-RPC:
• Validates input with a Pydantic model when provided
• Avoids extra=forbid explosions by filtering unknown keys pre-validation
• Always passes a dict payload to cores (no `.get` on models)
• Restores ANY server-injected mapped columns (tenant_id, owner_id, etc.)
"""

from __future__ import annotations

from inspect import signature
from typing import Any, get_args, get_origin

from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import inspect as _sa_inspect


def _wrap_rpc(core, IN, OUT, pk_name: str, model):
    sig = signature(core)
    first_param = next(iter(sig.parameters.values()), None)

    expects_pydantic = hasattr(IN, "model_validate")
    out_is_list = get_origin(OUT) is list
    out_elem = get_args(OUT)[0] if out_is_list else None
    elem_has_validate = callable(getattr(out_elem, "model_validate", None)) if out_elem else False
    out_is_single_model = callable(getattr(OUT, "model_validate", None))

    # Discover mapped column keys so server-injected fields can be restored post-validation
    try:
        _col_keys = {c.key for c in _sa_inspect(model).columns}
    except Exception:
        _col_keys = set()

    # ---------- helpers ----------

    def _normalize_raw(raw: Any) -> dict:
        """Ensure we have a plain dict for safe .get / membership."""
        return raw.model_dump() if hasattr(raw, "model_dump") else raw

    def _forbid_extras(IN) -> bool:
        """Detect pydantic v2 extra='forbid' in model_config (enum or str)."""
        cfg = getattr(IN, "model_config", None)
        if not cfg:
            return False
        extra = getattr(cfg, "extra", None)
        return getattr(extra, "value", extra) == "forbid"

    def _allowed_input_keys(IN) -> set[str]:
        """Collect canonical field names + common alias surfaces."""
        fields = getattr(IN, "model_fields", {}) or {}
        allowed = set(fields.keys())
        for fi in fields.values():
            alias = getattr(fi, "alias", None)
            if isinstance(alias, str):
                allowed.add(alias)
            valias = getattr(fi, "validation_alias", None)
            try:
                # AliasChoices / AliasPath best-effort
                choices = getattr(valias, "choices", None)
                if isinstance(choices, (list, tuple, set)):
                    for a in choices:
                        if isinstance(a, str):
                            allowed.add(a)
                alias_attr = getattr(valias, "alias", None)
                if isinstance(alias_attr, str):
                    allowed.add(alias_attr)
            except Exception:
                pass
        return allowed

    def _overlay_mapped(payload: dict, raw_map: dict) -> dict:
        """Overlay any mapped column from raw_map into payload when missing/None."""
        if not (_col_keys and isinstance(raw_map, dict)):
            return payload
        out = dict(payload)
        for k in _col_keys:
            rv = raw_map.get(k, None)
            if rv is not None and (k not in out or out.get(k) is None):
                out[k] = rv
        return out

    # ---------- adapter ----------

    def h(raw: dict, db: Session):
        raw_map = _normalize_raw(raw)

        # 1) validate (or pass-through) input
        if expects_pydantic:
            # only pre-filter if model truly forbids extras
            if _forbid_extras(IN) and isinstance(raw_map, dict):
                allowed = _allowed_input_keys(IN)
                raw_for_validate = {k: raw_map[k] for k in raw_map.keys() & allowed}
            else:
                raw_for_validate = raw_map

            obj_in = IN.model_validate(raw_for_validate)
            validated = obj_in.model_dump()
        else:
            obj_in = raw_map
            validated = raw_map

        # 2) restore ANY server-injected mapped columns (e.g., tenant_id/owner_id)
        payload = _overlay_mapped(validated if isinstance(validated, dict) else dict(validated), raw_map)

        # 3) dispatch to core – always pass a dict payload
        if expects_pydantic:
            params = list(sig.parameters.values())
            if isinstance(raw_map, dict) and pk_name in raw_map and params and params[0].name != pk_name:
                if len(params) >= 3:
                    r = core(raw_map[pk_name], payload, db=db)
                else:
                    r = core(raw_map[pk_name], db=db)
            else:
                if first_param and first_param.name not in (None, pk_name, "db"):
                    r = core(payload, db=db)
                else:
                    r = core(db=db)
        else:
            if isinstance(payload, dict) and pk_name in payload and first_param and first_param.name != pk_name:
                pd = dict(payload)
                r = core(**{first_param.name: pd.pop(pk_name)}, db=db, **pd)
            else:
                pk_val = raw_map.get(pk_name) if isinstance(raw_map, dict) else None
                r = core(pk_val, payload, db=db)

        # 4) shape output per OUT schema
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
