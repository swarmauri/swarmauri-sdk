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

_SLH_DSA: tuple[Alg, ...] = (
    "SLH-DSA-SHA2-128s",
    "SLH-DSA-SHA2-128f",
    "SLH-DSA-SHAKE-128s",
    "SLH-DSA-SHAKE-128f",
    "SLH-DSA-SHAKE-192s",
    "SLH-DSA-SHAKE-192f",
    "SLH-DSA-SHAKE-256s",
    "SLH-DSA-SHAKE-256f",
)
_SLH_DSA_LEVEL = {
    "SLH-DSA-SHA2-128s": 1,
    "SLH-DSA-SHA2-128f": 1,
    "SLH-DSA-SHAKE-128s": 1,
    "SLH-DSA-SHAKE-128f": 1,
    "SLH-DSA-SHAKE-192s": 3,
    "SLH-DSA-SHAKE-192f": 3,
    "SLH-DSA-SHAKE-256s": 5,
    "SLH-DSA-SHAKE-256f": 5,
}


@ComponentBase.register_type(CipherSuiteBase, "Fips205CipherSuite")
class Fips205CipherSuite(CipherSuiteBase):
    """FIPS 205 compliant SLH-DSA signing suite."""

    def suite_id(self) -> str:
        return "fips-205"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {"sign": _SLH_DSA, "verify": _SLH_DSA}

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return "SLH-DSA-SHAKE-192s"

    def policy(self) -> Mapping[str, object]:
        return {
            "fips": "205",
            "nist_document": "SLH-DSA",
            "nist_security_levels": _SLH_DSA_LEVEL,
        }

    def features(self) -> Features:
        return {
            "suite": "fips-205",
            "version": 1,
            "dialects": {"provider": list(_SLH_DSA)},
            "ops": {
                "sign": {"default": "SLH-DSA-SHAKE-192s", "allowed": list(_SLH_DSA)},
            },
            "constraints": {"nistSecurityLevels": _SLH_DSA_LEVEL},
            "compliance": {"fips205": True, "pqc": True},
            "notes": [
                "Implements the SPHINCS+ based SLH-DSA parameter sets from FIPS 205.",
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
        mapped = {"provider": f"slh-dsa:{chosen}"}

        constraints = {"nistLevel": _SLH_DSA_LEVEL[chosen], "category": "post-quantum"}

        return {
            "op": op,
            "alg": chosen,
            "dialect": chosen_dialect,
            "mapped": mapped,
            "params": resolved,
            "constraints": constraints,
            "policy": self.policy(),
        }
