"""Cipher suite describing the PEP 458 signing policy surface."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional

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

_PEP458_ALGS: tuple[Alg, ...] = ("Ed25519", "RSA-PSS-SHA256")
_DEFAULT_CANON = "tuf-json"


def _infer_alg_from_key(key: Optional[KeyRef]) -> Optional[Alg]:
    if not key:
        return None
    kty = key.get("kty")
    if not kty:
        return None
    lowered = str(kty).lower()
    if lowered in {"rsa"}:
        return "RSA-PSS-SHA256"
    if lowered in {"ed25519", "okp"}:
        return "Ed25519"
    return None


@ComponentBase.register_type(CipherSuiteBase, "Pep458CipherSuite")
class Pep458CipherSuite(CipherSuiteBase):
    """Metadata policy and algorithm registry for PEP 458 repositories."""

    def suite_id(self) -> str:
        return "pep458"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {"sign": _PEP458_ALGS, "verify": _PEP458_ALGS}

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        inferred = _infer_alg_from_key(for_key)
        if inferred:
            return inferred
        return "Ed25519"

    def features(self) -> Features:
        return {
            "suite": "pep458",
            "version": 1,
            "dialects": {"provider": ["pep458"], "sigstore": []},
            "ops": {
                "sign": {"default": "Ed25519", "allowed": list(_PEP458_ALGS)},
                "verify": {"default": "Ed25519", "allowed": list(_PEP458_ALGS)},
            },
            "constraints": {
                "canonicalization": _DEFAULT_CANON,
                "signature_format": "detached",
                "min_threshold": 1,
            },
            "compliance": {"pep458": True, "tuf": "1.x"},
            "notes": [
                "Implements offline root and online timestamp role separation per PEP 458.",
                "Pair with swarmauri_signing_pep458.Pep458Signer for signature production.",
            ],
        }

    def policy(self) -> Mapping[str, Any]:
        return {
            "canonicalization": _DEFAULT_CANON,
            "signature": {
                "format": "tuf/pep458",
                "allowed_algs": list(_PEP458_ALGS),
                "detached": True,
                "keyid_hash": "sha256",
            },
            "roles": {
                "root": {"threshold": 2, "expires": "P365D", "alg": "RSA-PSS-SHA256"},
                "targets": {"threshold": 1, "expires": "P90D", "alg": "Ed25519"},
                "snapshot": {"threshold": 1, "expires": "P14D", "alg": "Ed25519"},
                "timestamp": {"threshold": 1, "expires": "P1D", "alg": "Ed25519"},
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
        chosen_alg = alg or self.default_alg(op, for_key=key)
        if chosen_alg not in allowed:
            raise ValueError(f"{chosen_alg} not supported for operation {op}")

        resolved_params: Dict[str, Any] = dict(params or {})
        canon = resolved_params.pop("canon", _DEFAULT_CANON)
        role = resolved_params.pop("role", resolved_params.pop("tuf_role", "generic"))
        threshold = int(resolved_params.pop("threshold", 1))

        mapped = {
            "provider": {
                "suite": "pep458",
                "signer": "swarmauri_signing_pep458.Pep458Signer",
                "alg": chosen_alg,
                "canon": canon,
                "role": role,
            }
        }

        params_out = {
            "canon": canon,
            "role": role,
            "threshold": threshold,
        }
        if resolved_params:
            params_out.update(resolved_params)

        constraints = {
            "threshold": threshold,
            "detached": True,
        }

        return {
            "op": op,
            "alg": chosen_alg,
            "dialect": "provider" if dialect is None else dialect,
            "mapped": mapped,
            "params": params_out,
            "constraints": constraints,
            "policy": self.policy(),
        }


__all__ = ["Pep458CipherSuite"]
