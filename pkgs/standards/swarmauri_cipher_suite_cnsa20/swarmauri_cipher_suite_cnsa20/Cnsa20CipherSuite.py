from __future__ import annotations

from typing import Iterable, Mapping, Optional

from swarmauri_base.cipher_suites import CipherSuiteBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.cipher_suites import (
    Alg,
    CipherOp,
    Features,
    KeyRef,
    NormalizedDescriptor,
    ParamMapping,
)

_CLASSIC_SIGN = ("ES384", "PS384")
_PQC_SIGN = (
    "ML-DSA-44",
    "ML-DSA-65",
    "ML-DSA-87",
    "SLH-DSA-SHAKE-192s",
    "SLH-DSA-SHAKE-192f",
    "SLH-DSA-SHAKE-256s",
    "SLH-DSA-SHAKE-256f",
)
_SIGN = (*_CLASSIC_SIGN, *_PQC_SIGN)
_ENC = ("A256GCM",)
_KEM = ("ML-KEM-768", "ML-KEM-1024")

_ML_DSA_LEVEL = {"ML-DSA-44": 1, "ML-DSA-65": 3, "ML-DSA-87": 5}
_SLH_DSA_LEVEL = {
    "SLH-DSA-SHAKE-192s": 3,
    "SLH-DSA-SHAKE-192f": 3,
    "SLH-DSA-SHAKE-256s": 5,
    "SLH-DSA-SHAKE-256f": 5,
}
_ML_KEM_LEVEL = {"ML-KEM-768": 3, "ML-KEM-1024": 5}


@ComponentBase.register_type(CipherSuiteBase, "Cnsa20CipherSuite")
class Cnsa20CipherSuite(CipherSuiteBase):
    """Skeleton suite for CNSA 2.0 policy."""

    def suite_id(self) -> str:
        return "cnsa-2.0"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {
            "sign": _SIGN,
            "verify": _SIGN,
            "encrypt": _ENC,
            "decrypt": _ENC,
            "wrap": _KEM,
            "unwrap": _KEM,
        }

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        defaults = {
            "sign": "ML-DSA-65",
            "encrypt": "A256GCM",
            "wrap": "ML-KEM-768",
        }
        if op == "verify":
            return defaults["sign"]
        if op == "unwrap":
            return defaults["wrap"]
        return defaults.get(op, "A256GCM")

    def policy(self) -> Mapping[str, object]:
        return {
            "cnsa_version": "2.0",
            "classical": {
                "hash": "SHA384",
                "allowed_curves": ["P-384"],
                "min_rsa_bits": 3072,
            },
            "post_quantum": {
                "ml_dsa": _ML_DSA_LEVEL,
                "slh_dsa": _SLH_DSA_LEVEL,
                "ml_kem": _ML_KEM_LEVEL,
            },
        }

    def features(self) -> Features:
        return {
            "suite": "cnsa-2.0",
            "version": 2,
            "dialects": {
                "jwa": list({*_CLASSIC_SIGN, *_ENC}),
                "provider": list({*_SIGN, *_ENC, *_KEM}),
            },
            "constraints": {
                "min_rsa_bits": 3072,
                "allowed_curves": ["P-384"],
                "hash": "SHA384",
                "aead": {"tagBits": 128, "nonceLen": 12},
                "post_quantum_levels": {
                    **_ML_DSA_LEVEL,
                    **_SLH_DSA_LEVEL,
                    **_ML_KEM_LEVEL,
                },
            },
            "compliance": {"cnsa": True, "pqc": True},
            "ops": {
                "sign": {"default": "ML-DSA-65", "allowed": list(_SIGN)},
                "encrypt": {"default": "A256GCM", "allowed": list(_ENC)},
                "wrap": {"default": "ML-KEM-768", "allowed": list(_KEM)},
            },
            "notes": [
                "Includes ML-DSA, SLH-DSA, and ML-KEM selections from NSA CNSA 2.0.",
            ],
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
        allowed = set(self.supports().get(op, ()))
        chosen = alg or self.default_alg(op)
        if chosen not in allowed:
            raise ValueError(f"{chosen=} not supported for {op=}")

        resolved = dict(params or {})
        constraints: dict[str, object] = {}

        if chosen in _ENC:
            resolved.setdefault("tagBits", 128)
            resolved.setdefault("nonceLen", 12)
            constraints.update({"aead": {"tagBits": 128, "nonceLen": 12}})
        if chosen in _CLASSIC_SIGN:
            constraints.update(
                {
                    "minKeyBits": 3072,
                    "hash": "SHA384",
                    "allowed_curves": ["P-384"],
                }
            )
        if chosen in _PQC_SIGN:
            level = _ML_DSA_LEVEL.get(chosen) or _SLH_DSA_LEVEL.get(chosen)
            constraints.update({"nistLevel": level, "category": "post-quantum"})
        if chosen in _KEM:
            level = _ML_KEM_LEVEL[chosen]
            constraints.update({"nistLevel": level, "category": "post-quantum"})

        mapped: dict[str, object] = {"provider": chosen}
        chosen_dialect = dialect

        if chosen in _CLASSIC_SIGN or chosen in _ENC:
            mapped["jwa"] = chosen
            if chosen_dialect is None:
                chosen_dialect = "jwa"
        if chosen_dialect is None:
            chosen_dialect = "provider"

        return {
            "op": op,
            "alg": chosen,
            "dialect": chosen_dialect,
            "mapped": mapped,
            "params": resolved,
            "constraints": constraints,
            "policy": self.policy(),
        }
