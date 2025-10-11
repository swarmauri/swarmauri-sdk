from __future__ import annotations

from typing import Iterable, Mapping, Optional

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.cipher_suites import CipherSuiteBase
from swarmauri_core.cipher_suites import (
    Alg,
    CipherOp,
    Features,
    KeyRef,
    NormalizedDescriptor,
    ParamMapping,
)

_ALG_METADATA: Mapping[str, Mapping[str, object]] = {
    "SLH-DSA-SHA2-128s": {
        "hash": "SHA2-256",
        "category": 1,
        "variant": "small",
        "signature_bytes": 7856,
    },
    "SLH-DSA-SHA2-128f": {
        "hash": "SHA2-256",
        "category": 1,
        "variant": "fast",
        "signature_bytes": 16976,
    },
    "SLH-DSA-SHA2-192s": {
        "hash": "SHA2-384",
        "category": 3,
        "variant": "small",
        "signature_bytes": 16224,
    },
    "SLH-DSA-SHA2-192f": {
        "hash": "SHA2-384",
        "category": 3,
        "variant": "fast",
        "signature_bytes": 35664,
    },
    "SLH-DSA-SHA2-256s": {
        "hash": "SHA2-512",
        "category": 5,
        "variant": "small",
        "signature_bytes": 29792,
    },
    "SLH-DSA-SHA2-256f": {
        "hash": "SHA2-512",
        "category": 5,
        "variant": "fast",
        "signature_bytes": 49856,
    },
    "SLH-DSA-SHAKE-128s": {
        "hash": "SHAKE128",
        "category": 1,
        "variant": "small",
        "signature_bytes": 7856,
    },
    "SLH-DSA-SHAKE-128f": {
        "hash": "SHAKE128",
        "category": 1,
        "variant": "fast",
        "signature_bytes": 16976,
    },
    "SLH-DSA-SHAKE-192s": {
        "hash": "SHAKE256",
        "category": 3,
        "variant": "small",
        "signature_bytes": 16224,
    },
    "SLH-DSA-SHAKE-192f": {
        "hash": "SHAKE256",
        "category": 3,
        "variant": "fast",
        "signature_bytes": 35664,
    },
    "SLH-DSA-SHAKE-256s": {
        "hash": "SHAKE256",
        "category": 5,
        "variant": "small",
        "signature_bytes": 29792,
    },
    "SLH-DSA-SHAKE-256f": {
        "hash": "SHAKE256",
        "category": 5,
        "variant": "fast",
        "signature_bytes": 49856,
    },
}

_ALLOWED_SIGN = tuple(_ALG_METADATA.keys())


@ComponentBase.register_type(CipherSuiteBase, "Fips205CipherSuite")
class Fips205CipherSuite(CipherSuiteBase):
    """FIPS 205 SLH-DSA compliant algorithm surface."""

    def suite_id(self) -> str:
        return "fips205-slh-dsa"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {
            "sign": _ALLOWED_SIGN,
            "verify": _ALLOWED_SIGN,
        }

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        if op not in {"sign", "verify"}:
            raise ValueError(f"{op=} not supported by FIPS 205 suite")
        return _ALLOWED_SIGN[0]

    def policy(self) -> Mapping[str, object]:
        return {
            "fips": True,
            "standard": "FIPS 205",
            "stateless": True,
            "algorithms": {
                alg: {
                    "hash": meta["hash"],
                    "category": meta["category"],
                    "variant": meta["variant"],
                    "signature_bytes": meta["signature_bytes"],
                }
                for alg, meta in _ALG_METADATA.items()
            },
            "hash_families": sorted({meta["hash"] for meta in _ALG_METADATA.values()}),
            "security_categories": sorted(
                {meta["category"] for meta in _ALG_METADATA.values()}
            ),
        }

    def features(self) -> Features:
        default_alg = _ALLOWED_SIGN[0]
        return {
            "suite": self.suite_id(),
            "version": 1,
            "dialects": {"slh-dsa": list(_ALLOWED_SIGN)},
            "ops": {
                "sign": {"default": default_alg, "allowed": list(_ALLOWED_SIGN)},
                "verify": {"default": default_alg, "allowed": list(_ALLOWED_SIGN)},
            },
            "constraints": {
                "stateless": True,
                "securityCategories": sorted(
                    {meta["category"] for meta in _ALG_METADATA.values()}
                ),
                "signatureBytes": {
                    alg: int(meta["signature_bytes"])
                    for alg, meta in _ALG_METADATA.items()
                },
            },
            "compliance": {"fips": True, "fips205": True},
        }

    def normalize(
        self,
        *,
        op: CipherOp,
        alg: Optional[Alg] = None,
        key: Optional[KeyRef] = None,
        params: Optional[ParamMapping] = None,
        dialect: Optional[str] = None,
    ) -> NormalizedDescriptor:
        allowed = tuple(self.supports().get(op, ()))
        if not allowed:
            raise ValueError(f"{op=} not supported by FIPS 205 suite")

        chosen = alg or self.default_alg(op, for_key=key)
        if chosen not in allowed:
            raise ValueError(f"{chosen=} not allowed by FIPS 205 for {op=}")

        meta = _ALG_METADATA[chosen]
        resolved = dict(params or {})
        resolved.setdefault("hash", meta["hash"])
        resolved.setdefault("securityCategory", meta["category"])
        resolved.setdefault("variant", meta["variant"])
        resolved.setdefault("signatureBytes", meta["signature_bytes"])
        resolved.setdefault("stateless", True)

        return {
            "op": op,
            "alg": chosen,
            "dialect": "slh-dsa" if dialect is None else dialect,
            "mapped": {"slh-dsa": chosen, "provider": chosen},
            "params": resolved,
            "constraints": {
                "stateless": True,
                "securityCategory": meta["category"],
            },
            "policy": self.policy(),
        }
