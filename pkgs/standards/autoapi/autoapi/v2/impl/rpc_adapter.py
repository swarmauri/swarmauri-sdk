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
    fn_name = getattr(core, "__name__", "")
    print(
        f"[rpc_adapter] _wrap_rpc: core={fn_name} IN={getattr(IN, '__name__', IN)} "
        f"OUT={OUT} pk_name={pk_name} model={getattr(model, '__name__', model)}"
    )

    # classify verb from core name (we generate _create/_read/_update/_delete/_list/_clear)
    lower = fn_name.lower()
    verb = (
        "create"
        if "create" in lower
        else "update"
        if "update" in lower
        else "read"
        if "read" in lower
        else "delete"
        if "delete" in lower
        else "list"
        if "list" in lower
        else "clear"
        if "clear" in lower
        else "unknown"
    )
    print(f"[rpc_adapter] detected verb={verb}")

    # OUT typing info
    out_is_list = get_origin(OUT) is list
    out_elem = get_args(OUT)[0] if out_is_list else None
    elem_has_validate = (
        callable(getattr(out_elem, "model_validate", None)) if out_elem else False
    )
    out_is_single_model = callable(getattr(OUT, "model_validate", None))

    # discover mapped columns so we can re-overlay server-injected fields
    try:
        _col_keys = {c.key for c in _sa_inspect(model).columns}
        print(f"[rpc_adapter] mapped column keys: {_col_keys}")
    except Exception as e:
        _col_keys = set()
        print(f"[rpc_adapter] WARN: inspect(model) failed: {e!r}")

    def _normalize_raw(raw: Any) -> dict:
        out = raw.model_dump() if hasattr(raw, "model_dump") else raw
        print(f"[rpc_adapter] _normalize_raw -> {type(out).__name__}: {out}")
        return out

    def _forbid_extras(IN) -> bool:
        cfg = getattr(IN, "model_config", None)
        extra = getattr(cfg, "extra", None) if cfg else None
        val = getattr(extra, "value", extra)
        flag = val == "forbid"
        print(f"[rpc_adapter] _forbid_extras: {val!r} -> {flag}")
        return flag

    def _allowed_input_keys(IN) -> set[str]:
        fields = getattr(IN, "model_fields", {}) or {}
        allowed = set(fields.keys())
        for fi in fields.values():
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
        print(f"[rpc_adapter] allowed input keys: {allowed}")
        return allowed

    def _overlay_mapped(payload: dict, raw_map: dict) -> dict:
        if not (_col_keys and isinstance(raw_map, dict)):
            print("[rpc_adapter] overlay: skip (no columns or raw_map not dict)")
            return payload
        out = dict(payload)
        applied = {}
        for k in _col_keys:
            rv = raw_map.get(k, None)
            if rv is not None and (k not in out or out.get(k) is None):
                out[k] = rv
                applied[k] = rv
        print(f"[rpc_adapter] overlay applied: {applied}")
        return out

    expects_pydantic = hasattr(IN, "model_validate")

    def h(raw: dict, db: Session):
        print(f"[rpc_adapter] handler: raw type={type(raw).__name__} raw={raw}")
        raw_map = _normalize_raw(raw)

        # 1) validate / normalize to dict
        if expects_pydantic:
            if _forbid_extras(IN) and isinstance(raw_map, dict):
                allowed = _allowed_input_keys(IN)
                raw_for_validate = {k: raw_map[k] for k in raw_map.keys() & allowed}
                print(f"[rpc_adapter] pre-filtered for forbid: {raw_for_validate}")
            else:
                raw_for_validate = raw_map
                print(
                    f"[rpc_adapter] no pre-filter (forbid inactive): {raw_for_validate}"
                )
            try:
                obj_in = IN.model_validate(raw_for_validate)
                validated = obj_in.model_dump()
            except Exception as ve:
                print(f"[rpc_adapter] VALIDATION ERROR: {ve!r}")
                raise
        else:
            obj_in = raw_map
            validated = raw_map

        print(f"[rpc_adapter] validated payload: {validated}")

        # 2) overlay server-injected mapped fields (tenant_id/owner_id/etc.)
        base_payload = validated if isinstance(validated, dict) else dict(validated)
        payload = _overlay_mapped(base_payload, raw_map)
        print(f"[rpc_adapter] final payload: {payload}")

        # 3) extract pk when needed
        pk_val = None
        if isinstance(raw_map, dict):
            pk_val = raw_map.get(pk_name)
        if pk_val is None and isinstance(payload, dict):
            pk_val = payload.get(pk_name)
        print(f"[rpc_adapter] resolved pk_val={pk_val}")

        # 4) dispatch strictly by verb to avoid misrouting creates
        if verb == "create":
            print("[rpc_adapter] call core(payload, db)")
            r = core(payload, db=db)
        elif verb == "list":
            print("[rpc_adapter] call core(payload, db) [list]")
            r = core(payload, db=db)
        elif verb == "update":
            print("[rpc_adapter] call core(pk, payload, db)")
            r = core(pk_val, payload, db=db)
        elif verb == "read":
            print("[rpc_adapter] call core(pk, db)")
            r = core(pk_val, db=db)
        elif verb == "delete":
            print("[rpc_adapter] call core(pk, db) [delete]")
            r = core(pk_val, db=db)
        elif verb == "clear":
            print("[rpc_adapter] call core(db) [clear]")
            r = core(db=db)
        else:
            # conservative fallback: behave like old adapter but with dicts
            params = list(signature(core).parameters.values())
            print(f"[rpc_adapter] fallback dispatch, params={[p.name for p in params]}")
            if (
                isinstance(raw_map, dict)
                and (pk_name in raw_map)
                and params
                and params[0].name != pk_name
            ):
                if len(params) >= 3:
                    r = core(pk_val, payload, db=db)
                else:
                    r = core(pk_val, db=db)
            else:
                if params and params[0].name not in (None, pk_name, "db"):
                    r = core(payload, db=db)
                else:
                    r = core(db=db)

        print(f"[rpc_adapter] core returned type={type(r).__name__} value={r}")

        # 5) shape output
        if not out_is_list:
            if isinstance(r, BaseModel):
                dumped = r.model_dump()
                print(f"[rpc_adapter] return BaseModel -> {dumped}")
                return dumped
            if out_is_single_model:
                dumped = OUT.model_validate(r).model_dump()
                print(f"[rpc_adapter] return OUT.model_validate() -> {dumped}")
                return dumped
            print(f"[rpc_adapter] return raw -> {r}")
            return r

        out_items = []
        for itm in r:
            if isinstance(itm, BaseModel):
                out_items.append(itm.model_dump())
            elif elem_has_validate:
                out_items.append(out_elem.model_validate(itm).model_dump())
            else:
                out_items.append(itm)
        print(f"[rpc_adapter] return list[{len(out_items)}] -> {out_items}")
        return out_items

    return h
