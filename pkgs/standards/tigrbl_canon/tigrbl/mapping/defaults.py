from __future__ import annotations

from typing import Any

DEFAULTS: dict[str, Any] = {
    # wire/out
    "exclude_none": False,
    "omit_nulls": False,  # alias; normalized in config resolver
    "response_extras_overwrite": False,
    "extras_overwrite": False,  # alias
    # wire/in
    "reject_unknown_fields": False,
    # refresh
    "refresh_policy": "auto",  # 'auto' | 'always' | 'never'
    "refresh_after_write": None,  # Optional[bool] -> normalized into refresh_policy
    # validation/docs
    "required_policy": {},  # dict[op][field] = bool
    # misc buckets developers may use
    "openapi": {},
    "docs": {},
    "openrpc": {},
    "lens": {},
    "trace": {"enabled": True},
}
