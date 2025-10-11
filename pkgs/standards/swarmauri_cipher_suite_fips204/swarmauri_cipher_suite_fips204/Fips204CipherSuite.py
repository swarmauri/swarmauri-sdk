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

_ALLOWED_KEM = ("ML-KEM-512", "ML-KEM-768", "ML-KEM-1024")
_KEM_METADATA: Mapping[Alg, Mapping[str, object]] = {
    "ML-KEM-512": {
        "securityLevel": 1,
        "ciphertextBytes": 768,
        "sharedSecretBytes": 32,
    },
    "ML-KEM-768": {
        "securityLevel": 3,
        "ciphertextBytes": 1088,
        "sharedSecretBytes": 32,
    },
    "ML-KEM-1024": {
        "securityLevel": 5,
        "ciphertextBytes": 1568,
        "sharedSecretBytes": 32,
    },
}


@ComponentBase.register_type(CipherSuiteBase, "Fips204CipherSuite")
class Fips204CipherSuite(CipherSuiteBase):
    """FIPS 204 compliant ML-KEM cipher suite surface."""

    def suite_id(self) -> str:
        return "fips-204"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {
            "wrap": _ALLOWED_KEM,
            "unwrap": _ALLOWED_KEM,
        }

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        if op in ("wrap", "unwrap"):
            return "ML-KEM-768"
        raise ValueError(f"{op=} not supported by the FIPS 204 cipher suite")

    def policy(self) -> Mapping[str, object]:
        return {
            "fips": True,
            "standard": "FIPS 204",
            "kem": {
                "family": "ML-KEM",
                "type": "module-lattice",
                "defaults": {
                    "wrap": "ML-KEM-768",
                    "unwrap": "ML-KEM-768",
                },
                "parameters": {
                    alg: dict(metadata) for alg, metadata in _KEM_METADATA.items()
                },
            },
        }

    def features(self) -> Features:
        return {
            "suite": "fips-204",
            "version": 1,
            "dialects": {"mlkem": list(_ALLOWED_KEM)},
            "ops": {
                "wrap": {"default": "ML-KEM-768", "allowed": list(_ALLOWED_KEM)},
                "unwrap": {"default": "ML-KEM-768", "allowed": list(_ALLOWED_KEM)},
            },
            "constraints": {
                "kemFamily": "ML-KEM",
                "kemType": "module-lattice",
                "securityLevels": {
                    alg: metadata["securityLevel"]
                    for alg, metadata in _KEM_METADATA.items()
                },
            },
            "compliance": {"fips": True, "postQuantum": True},
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
        supported = self.supports()
        if op not in supported:
            raise ValueError(f"{op=} not supported by the FIPS 204 cipher suite")

        allowed = set(supported[op])
        chosen = alg or self.default_alg(op, for_key=key)
        if chosen not in allowed:
            raise ValueError(f"{chosen=} not allowed for {op=}")

        metadata = dict(_KEM_METADATA[chosen])
        resolved = dict(params or {})
        resolved.setdefault("kemVersion", "ML-KEM")
        resolved.setdefault("securityLevel", metadata["securityLevel"])
        resolved.setdefault("ciphertextBytes", metadata["ciphertextBytes"])
        resolved.setdefault("sharedSecretBytes", metadata["sharedSecretBytes"])

        constraints = {
            **metadata,
            "kemFamily": "ML-KEM",
            "standard": "FIPS 204",
        }

        return {
            "op": op,
            "alg": chosen,
            "dialect": "mlkem" if dialect is None else dialect,
            "mapped": {"mlkem": chosen, "provider": chosen},
            "params": resolved,
            "constraints": constraints,
            "policy": self.policy(),
        }


__all__ = ["Fips204CipherSuite"]
