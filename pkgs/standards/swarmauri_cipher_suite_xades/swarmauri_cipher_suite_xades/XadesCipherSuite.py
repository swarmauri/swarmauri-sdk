from __future__ import annotations

from typing import Iterable, Mapping, Optional

from swarmauri_base.cipher_suites import CipherSuiteBase
from swarmauri_core.cipher_suites import (
    Alg,
    CipherOp,
    Features,
    KeyRef,
    NormalizedDescriptor,
    ParamMapping,
)

_SIG = ("RSA-PSS-SHA256", "ECDSA-SHA256", "EdDSA")
_C14N = (
    "http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
    "http://www.w3.org/2001/10/xml-exc-c14n#",
)


class XadesCipherSuite(CipherSuiteBase):
    """Skeleton suite for XAdES policy."""

    type = "XadesCipherSuite"

    def suite_id(self) -> str:
        return "xades"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {"sign": _SIG, "verify": _SIG}

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return "RSA-PSS-SHA256"

    def features(self) -> Features:
        return {
            "suite": "xades",
            "version": 1,
            "dialects": {"xmlsig": list(_SIG)},
            "constraints": {"canonicalization": list(_C14N)},
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
            "dialect": "xmlsig" if dialect is None else dialect,
            "mapped": {"xmlsig": chosen, "provider": chosen},
            "params": dict(params or {}),
            "constraints": {},
            "policy": self.policy(),
        }
