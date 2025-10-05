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

_IPSEC_AEAD = ("AES-GCM-16", "CHACHA20-POLY1305")
_IPSEC_PRF = ("HMAC-SHA2-256", "HMAC-SHA2-384")
_IPSEC_DH = ("group14", "group19", "group20", "group31")


@ComponentBase.register_type(CipherSuiteBase, "IpsecCipherSuite")
class IpsecCipherSuite(CipherSuiteBase):
    """Skeleton suite for IKE/IPsec policy."""

    def suite_id(self) -> str:
        return "ipsec"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {"encrypt": _IPSEC_AEAD, "decrypt": _IPSEC_AEAD}

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return "AES-GCM-16"

    def features(self) -> Features:
        return {
            "suite": "ipsec",
            "version": 1,
            "dialects": {"ike": list(_IPSEC_AEAD)},
            "constraints": {"prf": _IPSEC_PRF, "dh": _IPSEC_DH, "pfs": True},
            "ops": {"encrypt": {"default": "AES-GCM-16", "allowed": list(_IPSEC_AEAD)}},
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
            "dialect": "ike" if dialect is None else dialect,
            "mapped": {"ike": chosen, "provider": chosen},
            "params": dict(params or {}),
            "constraints": {},
            "policy": self.policy(),
        }
