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

_COSE_SIGN = (-8, -7, -35, -36, -37, -38, -39)
_COSE_AEAD = (1, 2, 3)


@ComponentBase.register_type(CipherSuiteBase, "CoseCipherSuite")
class CoseCipherSuite(CipherSuiteBase):
    """COSE algorithm registry surface."""

    def suite_id(self) -> str:
        return "cose"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {
            "sign": tuple(str(value) for value in _COSE_SIGN),
            "verify": tuple(str(value) for value in _COSE_SIGN),
            "encrypt": tuple(str(value) for value in _COSE_AEAD),
            "decrypt": tuple(str(value) for value in _COSE_AEAD),
        }

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return {"sign": "-8", "encrypt": "3"}.get(op, "3")

    def features(self) -> Features:
        return {
            "suite": "cose",
            "version": 1,
            "dialects": {
                "cose": list({*self.supports()["sign"], *self.supports()["encrypt"]})
            },
            "ops": {
                "sign": {"default": "-8", "allowed": list(self.supports()["sign"])},
                "encrypt": {
                    "default": "3",
                    "allowed": list(self.supports()["encrypt"]),
                },
            },
            "constraints": {"aead": {"tagBits": 128, "nonceLen": 12}},
            "compliance": {"fips": False},
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
        chosen = str(alg or self.default_alg(op, for_key=key))
        if chosen not in allowed:
            raise ValueError(f"{chosen=} not supported for {op=}")

        resolved = dict(params or {})
        if chosen in {"1", "2", "3"}:
            resolved.setdefault("tagBits", 128)
            resolved.setdefault("nonceLen", 12)
        mapped = {
            "cose": int(chosen),
            "provider": chosen,
        }
        return {
            "op": op,
            "alg": chosen,
            "dialect": "cose" if dialect is None else dialect,
            "mapped": mapped,
            "params": resolved,
            "constraints": {},
            "policy": self.policy(),
        }
