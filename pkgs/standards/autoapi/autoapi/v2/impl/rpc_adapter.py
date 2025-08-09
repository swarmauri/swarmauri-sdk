"""
autoapi/v2/rpc_adapter.py  –  RPC adaptation functionality for AutoAPI.

Adapts CRUD/core callables for JSON-RPC:
• Validates input with a Pydantic model when provided
• Avoids extra=forbid explosions by filtering unknown keys pre-validation
• Always passes a dict payload to cores (no `.get` on models)
• Restores ANY server-injected mapped columns (tenant_id, owner_id, etc.)
• Prints detailed debug info at every step to aid diagnosis
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
        core:  core CRUD function
        IN:    input schema class (Pydantic) or dict-like
        OUT:   output schema class
        pk_name: primary key parameter name
        model: SQLAlchemy model class (for mapped column discovery)
    """
    print(f"[rpc_adapter] _wrap_rpc: core={getattr(core,'__name__',core)} "
          f"IN={getattr(IN,'__name__',IN)} OUT={OUT} pk_name={pk_name} model={getattr(model,'__name__',model)}")

    # Precompute some adapter metadata
    sig = signature(core)
    params_list = list(sig.parameters.values())
    first_param = params_list[0] if params_list else None

    expects_pydantic = hasattr(IN, "model_validate")
    out_is_list = get_origin(OUT) is list
    out_elem = get_args(OUT)[0] if out_is_list else None
    elem_has_validate = callable(getattr(out_elem, "model_validate", None)) if out_elem else False
    out_is_single_model = callable(getattr(OUT, "model_validate", None))

    print(f"[rpc_adapter] core signature: {sig}")
    print(f"[rpc_adapter] expects_pydantic={expects_pydantic} out_is_list={out_is_list} "
          f"elem_has_validate={elem_has_validate} out_is_single_model={out_is_single_model} "
          f"first_param={getattr(first_param,'name',None)}")

    # Discover mapped column keys so server-injected fields can be restored post-validation
    try:
        _col_keys = {c.key for c in _sa_inspect(model).columns}
        print(f"[rpc_adapter] mapped column keys: {_col_keys}")
    except Exception as e:
        _col_keys = set()
        print(f"[rpc_adapter] WARNING: could not inspect model columns: {e!r}")

    # Helpers -----------------------------------------------------------------

    def _normalize_raw(raw: Any) -> dict:
        """Ensure we have a plain dict for safe .get / membership."""
        out = raw.model_dump() if hasattr(raw, "model_dump") else raw
        print(f"[rpc_adapter] _normalize_raw -> type={type(out).__name__} value={out}")
        return out

    def _forbid_extras(IN) -> bool:
        """Detect pydantic v2 extra='forbid' in model_config (enum or str)."""
        cfg = getattr(IN, "model_config", None)
        extra = getattr(cfg, "extra", None) if cfg else None
        value = getattr(extra, "value", extra)
        flag = (value == "forbid")
        print(f"[rpc_adapter] _forbid_extras: model_config.extra={value!r} -> {flag}")
        return flag

    def _allowed_input_keys(IN) -> set[str]:
        """Collect canonical field names + common alias surfaces."""
        fields = getattr(IN, "model_fields", {}) or {}
        allowed = set(fields.keys())
        # add alias and validation_alias (best-effort)
        for name, fi in fields.items():
            alias = getattr(fi, "alias", None)
            if isinstance(alias, str):
                allowed.add(alias)
            valias = getattr(fi, "validation_alias", None)
            try:
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
        print(f"[rpc_adapter] _allowed_input_keys: {allowed}")
        return allowed

    def _overlay_mapped(payload: dict, raw_map: dict) -> dict:
        """Overlay any mapped column from raw_map into payload when missing/None."""
        if not (_col_keys and isinstance(raw_map, dict)):
            print("[rpc_adapter] _overlay_mapped: skip (no column keys or raw_map not dict)")
            return payload
        out = dict(payload)
        applied = {}
        for k in _col_keys:
            rv = raw_map.get(k, None)
            if rv is not None and (k not in out or out.get(k) is None):
                out[k] = rv
                applied[k] = rv
        print(f"[rpc_adapter] _overlay_mapped applied: {applied} -> payload={out}")
        return out

    # Adapter -----------------------------------------------------------------

    def h(raw: dict, db: Session):
        """
        Handle RPC call by converting parameters and formatting response.

        Args:
            raw: incoming RPC params (dict or Pydantic model)
            db:  SQLAlchemy Session
        """
        print(f"[rpc_adapter] handler(raw type={type(raw).__name__}): raw={raw}")
        raw_map = _normalize_raw(raw)

        # 1) Validate (or pass-through) input
        if expects_pydantic:
            # only pre-filter if model truly forbids extras
            if _forbid_extras(IN) and isinstance(raw_map, dict):
                allowed = _allowed_input_keys(IN)
                raw_for_validate = {k: raw_map[k] for k in raw_map.keys() & allowed}
                print(f"[rpc_adapter] pre-filter (extra=forbid): raw_for_validate={raw_for_validate}")
            else:
                raw_for_validate = raw_map
                print(f"[rpc_adapter] no pre-filter: raw_for_validate={raw_for_validate}")

            try:
                obj_in = IN.model_validate(raw_for_validate)
                validated = obj_in.model_dump()
                print(f"[rpc_adapter] validated={validated}")
            except Exception as ve:
                print(f"[rpc_adapter] VALIDATION ERROR: {ve!r} for input={raw_for_validate}")
                raise
        else:
            obj_in = raw_map
            validated = raw_map
            print(f"[rpc_adapter] bypass validation; validated={validated}")

        # 2) Restore ANY server-injected mapped columns (e.g., tenant_id/owner_id)
        before_overlay = validated if isinstance(validated, dict) else dict(validated)
        print(f"[rpc_adapter] payload before overlay: {before_overlay}")
        payload = _overlay_mapped(before_overlay, raw_map)
        print(f"[rpc_adapter] payload after overlay: {payload}")

        # 3) Dispatch to core – always pass a dict payload
        print(f"[rpc_adapter] dispatch: params_list={[p.name for p in params_list]} "
              f"pk_in_raw={isinstance(raw_map, dict) and (pk_name in raw_map)}")
        if expects_pydantic:
            if isinstance(raw_map, dict) and pk_name in raw_map and params_list and params_list[0].name != pk_name:
                if len(params_list) >= 3:
                    print(f"[rpc_adapter] calling core(pk, payload, db) -> pk={raw_map[pk_name]}")
                    r = core(raw_map[pk_name], payload, db=db)
                else:
                    print(f"[rpc_adapter] calling core(pk, db) -> pk={raw_map[pk_name]}")
                    r = core(raw_map[pk_name], db=db)
            else:
                if first_param and first_param.name not in (None, pk_name, "db"):
                    print("[rpc_adapter] calling core(payload, db)")
                    r = core(payload, db=db)
                else:
                    print("[rpc_adapter] calling core(db=db)")
                    r = core(db=db)
        else:
            if isinstance(payload, dict) and pk_name in payload and first_param and first_param.name != pk_name:
                pd = dict(payload)
                pk_val = pd.pop(pk_name)
                print(f"[rpc_adapter] calling core({first_param.name}=..., db, **payload) with pk from payload={pk_val}")
                r = core(**{first_param.name: pk_val}, db=db, **pd)
            else:
                pk_val = raw_map.get(pk_name) if isinstance(raw_map, dict) else None
                print(f"[rpc_adapter] calling core(pk, payload, db) -> pk={pk_val}")
                r = core(pk_val, payload, db=db)

        print(f"[rpc_adapter] core returned type={type(r).__name__} value={r}")

        # 4) Shape output per OUT schema
        if not out_is_list:
            if isinstance(r, BaseModel):
                dumped = r.model_dump()
                print(f"[rpc_adapter] return BaseModel.dump={dumped}")
                return dumped
            if out_is_single_model:
                dumped = OUT.model_validate(r).model_dump()
                print(f"[rpc_adapter] return OUT.model_validate().dump={dumped}")
                return dumped
            print(f"[rpc_adapter] return raw={r}")
            return r

        out: list[Any] = []
        for itm in r:
            if isinstance(itm, BaseModel):
                out.append(itm.model_dump())
            elif elem_has_validate:
                out.append(out_elem.model_validate(itm).model_dump())
            else:
                out.append(itm)
        print(f"[rpc_adapter] return list[{len(out)}]={out}")
        return out

    return h
