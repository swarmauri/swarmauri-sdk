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

_ML_DSA: tuple[Alg, ...] = ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")
_ML_DSA_LEVEL = {"ML-DSA-44": 1, "ML-DSA-65": 3, "ML-DSA-87": 5}


@ComponentBase.register_type(CipherSuiteBase, "Fips204CipherSuite")
class Fips204CipherSuite(CipherSuiteBase):
    """FIPS 204 compliant ML-DSA signing suite."""

    def suite_id(self) -> str:
        return "fips-204"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {"sign": _ML_DSA, "verify": _ML_DSA}

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return "ML-DSA-65"

    def policy(self) -> Mapping[str, object]:
        return {
            "fips": "204",
            "nist_document": "ML-DSA",
            "nist_security_levels": _ML_DSA_LEVEL,
        }

    def features(self) -> Features:
        return {
            "suite": "fips-204",
            "version": 1,
            "dialects": {"provider": list(_ML_DSA)},
            "ops": {
                "sign": {"default": "ML-DSA-65", "allowed": list(_ML_DSA)},
            },
            "constraints": {"nistSecurityLevels": _ML_DSA_LEVEL},
            "compliance": {"fips204": True, "pqc": True},
            "notes": [
                "Implements the ML-DSA (Dilithium) parameter sets from FIPS 204.",
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
        chosen_dialect = "provider" if dialect is None else dialect
        mapped = {"provider": f"ml-dsa:{chosen}"}

        constraints = {"nistLevel": _ML_DSA_LEVEL[chosen], "category": "post-quantum"}

        return {
            "op": op,
            "alg": chosen,
            "dialect": chosen_dialect,
            "mapped": mapped,
            "params": resolved,
            "constraints": constraints,
            "policy": self.policy(),
        }
