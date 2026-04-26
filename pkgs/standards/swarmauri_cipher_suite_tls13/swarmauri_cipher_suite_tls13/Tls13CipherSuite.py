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

_TLS13_CLASSIC = (
    "TLS_AES_128_GCM_SHA256",
    "TLS_AES_256_GCM_SHA384",
    "TLS_CHACHA20_POLY1305_SHA256",
)

_TLS13_PQ_HYBRID = ("TLS_AES_256_GCM_SHA384_KYBER768",)

_TLS13_ALL = _TLS13_CLASSIC + _TLS13_PQ_HYBRID

_PQ_PROVIDER_HINTS: Mapping[str, str] = {
    "TLS_AES_256_GCM_SHA384_KYBER768": "ML-KEM-768",
}


@ComponentBase.register_type(CipherSuiteBase, "Tls13CipherSuite")
class Tls13CipherSuite(CipherSuiteBase):
    """TLS 1.3 record protection algorithms."""

    def suite_id(self) -> str:
        return "tls13"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {
            "encrypt": _TLS13_ALL,
            "decrypt": _TLS13_ALL,
        }

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return "TLS_AES_256_GCM_SHA384_KYBER768"

    def features(self) -> Features:
        return {
            "suite": "tls13",
            "version": 1,
            "dialects": {"tls": list(_TLS13_ALL)},
            "ops": {
                "encrypt": {
                    "default": self.default_alg("encrypt"),
                    "allowed": list(_TLS13_ALL),
                }
            },
            "constraints": {"record_max": 16384, "aead": {"tagBits": 128}},
            "compliance": {
                "fips": False,
                "pq_ready": True,
                "min_key_sizes": {
                    "symmetric": 256,
                    "kem": "ML-KEM-768",
                },
            },
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
            raise ValueError(f"{chosen=} not supported for {op=} in TLS1.3")

        resolved = dict(params or {})
        provider_hint = _PQ_PROVIDER_HINTS.get(chosen, chosen)

        mapped = {"tls": chosen, "provider": provider_hint}

        return {
            "op": op,
            "alg": chosen,
            "dialect": "tls" if dialect is None else dialect,
            "mapped": mapped,
            "params": resolved,
            "constraints": {"record_max": 16384, "tagBits": 128},
            "policy": self.policy(),
        }
