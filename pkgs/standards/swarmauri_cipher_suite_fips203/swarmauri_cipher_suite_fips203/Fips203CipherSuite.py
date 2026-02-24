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

_ML_KEM: tuple[Alg, ...] = ("ML-KEM-512", "ML-KEM-768", "ML-KEM-1024")
_ML_KEM_LEVEL = {"ML-KEM-512": 1, "ML-KEM-768": 3, "ML-KEM-1024": 5}


@ComponentBase.register_type(CipherSuiteBase, "Fips203CipherSuite")
class Fips203CipherSuite(CipherSuiteBase):
    """FIPS 203 compliant ML-KEM cipher suite."""

    def suite_id(self) -> str:
        return "fips-203"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {"wrap": _ML_KEM, "unwrap": _ML_KEM}

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return "ML-KEM-768"

    def policy(self) -> Mapping[str, object]:
        return {
            "fips": "203",
            "nist_document": "ML-KEM",
            "nist_security_levels": _ML_KEM_LEVEL,
        }

    def features(self) -> Features:
        return {
            "suite": "fips-203",
            "version": 1,
            "dialects": {"provider": list(_ML_KEM)},
            "ops": {
                "wrap": {"default": "ML-KEM-768", "allowed": list(_ML_KEM)},
            },
            "constraints": {"nistSecurityLevels": _ML_KEM_LEVEL},
            "compliance": {"fips203": True, "pqc": True},
            "notes": [
                "Implements the CRYSTALS-Kyber based ML-KEM selections from FIPS 203.",
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
        mapped = {"provider": f"ml-kem:{chosen}"}

        constraints = {"nistLevel": _ML_KEM_LEVEL[chosen], "category": "post-quantum"}

        return {
            "op": op,
            "alg": chosen,
            "dialect": chosen_dialect,
            "mapped": mapped,
            "params": resolved,
            "constraints": constraints,
            "policy": self.policy(),
        }
