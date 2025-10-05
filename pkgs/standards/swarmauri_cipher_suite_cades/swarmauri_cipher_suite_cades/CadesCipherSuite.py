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

_SIG = ("RSA-PSS-SHA256", "ECDSA-SHA256", "EdDSA")


@ComponentBase.register_type(CipherSuiteBase, "CadesCipherSuite")
class CadesCipherSuite(CipherSuiteBase):
    """Skeleton suite for CAdES policy."""

    def suite_id(self) -> str:
        return "cades"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {"sign": _SIG, "verify": _SIG}

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return "RSA-PSS-SHA256"

    def features(self) -> Features:
        return {
            "suite": "cades",
            "version": 1,
            "dialects": {"cms": list(_SIG)},
            "constraints": {"tsa": {"required": False}},
            "ops": {"sign": {"default": "RSA-PSS-SHA256", "allowed": list(_SIG)}},
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
        chosen = alg or self.default_alg(op)
        if chosen not in allowed:
            raise ValueError(f"{chosen=} not supported for {op=}")

        return {
            "op": op,
            "alg": chosen,
            "dialect": "cms" if dialect is None else dialect,
            "mapped": {"cms": chosen, "provider": chosen},
            "params": dict(params or {}),
            "constraints": {},
            "policy": self.policy(),
        }
