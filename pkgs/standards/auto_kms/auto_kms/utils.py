from __future__ import annotations

import base64
from typing import Any, Mapping, Optional

from starlette.requests import Request

from swarmauri_core.crypto.types import ExportPolicy, KeyType, KeyUse


def b64e(data: bytes) -> str:
    return base64.b64encode(data).decode()


def _add_padding(data_b64: str) -> str:
    """Pad ``data_b64`` so its length is a multiple of four."""
    return data_b64 + "=" * (-len(data_b64) % 4)


def b64d(data_b64: str) -> bytes:
    return base64.b64decode(_add_padding(data_b64))


def b64d_optional(data_b64: Optional[str]) -> Optional[bytes]:
    return base64.b64decode(_add_padding(data_b64)) if data_b64 else None


def params(ctx) -> Mapping[str, Any]:
    p = getattr(ctx.get("env"), "params", {}) or {}
    return p.model_dump() if hasattr(p, "model_dump") else p


def coerce_enum(enum_cls, value: Any, *, synonyms: dict[str, str] | None = None):
    if isinstance(value, enum_cls):
        return value
    if value is None:
        raise KeyError(enum_cls.__name__)
    s = str(value)
    try:
        return getattr(enum_cls, s.upper())
    except Exception:
        pass
    try:
        return enum_cls(s)
    except Exception:
        pass
    if synonyms:
        alt = synonyms.get(s.upper())
        if alt:
            return enum_cls(alt)
    raise KeyError(f"Unsupported {enum_cls.__name__}: {value!r}")


def coerce_key_type_from_params(p: Mapping[str, Any]) -> KeyType:
    raw = p.get("key_type") or p.get("type") or p.get("kty")
    if raw is None:
        alg = p.get("algorithm") or p.get("alg")
        if alg:
            a = str(getattr(alg, "value", alg)).upper()
            if a.startswith("AES"):
                raw = "symmetric"
            elif "ED25519" in a:
                raw = "ed25519"
            elif "X25519" in a:
                raw = "x25519"
            elif "RSA" in a:
                raw = "rsa"
            elif any(k in a for k in ("EC", "P-", "SECP", "ECDSA")):
                raw = "ec"
    if raw is None:
        raise KeyError("key_type")
    return coerce_enum(
        KeyType,
        raw,
        synonyms={
            "SYMMETRIC": "symmetric",
            "ED25519": "ed25519",
            "X25519": "x25519",
            "RSA": "rsa",
            "EC": "ec",
        },
    )


def coerce_uses_from_params(p: Mapping[str, Any]) -> tuple[KeyUse, ...]:
    arr = p.get("uses")
    if not arr:
        return (KeyUse.ENCRYPT, KeyUse.DECRYPT)
    out: list[KeyUse] = []
    for u in arr:
        out.append(
            coerce_enum(
                KeyUse,
                u,
                synonyms={
                    "ENC": "encrypt",
                    "DEC": "decrypt",
                    "SIGN": "sign",
                    "VERIFY": "verify",
                    "WRAP": "wrap",
                    "UNWRAP": "unwrap",
                },
            )
        )
    return tuple(out)


def coerce_export_policy(val: Any) -> ExportPolicy:
    if val is None:
        return ExportPolicy("public_only")
    return coerce_enum(
        ExportPolicy,
        val,
        synonyms={
            "NONE": "none",
            "PUBLIC": "public_only",
            "SECRET": "secret_when_allowed",
        },
    )


def auth_tenant_from_ctx(ctx) -> Optional[str]:
    req: Request = ctx.get("request")
    if not req:
        return None
    c = getattr(req.state, "ctx", {}) or {}
    auth = c.get("__autoapi_auth_context__", {}) or {}
    return auth.get("tenant_id") or auth.get("tid")


def asdict_desc(d) -> dict:
    return {
        "kid": d.kid,
        "name": getattr(d, "name", None),
        "type": getattr(d.type, "value", str(d.type)),
        "state": getattr(d.state, "value", str(d.state)),
        "primary_version": d.primary_version,
        "uses": [getattr(u, "value", str(u)) for u in d.uses],
        "export_policy": getattr(d.export_policy, "value", str(d.export_policy)),
        "tags": d.tags,
        "versions": [
            {
                "version": v.version,
                "created_at": v.created_at,
                "state": getattr(v.state, "value", str(v.state)),
                "thumbprint": getattr(v, "thumbprint", None),
            }
            for v in d.versions
        ],
    }
