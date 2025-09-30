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

_SIG_ALGS = ("ES256", "EdDSA", "PS256")


class SigstoreCipherSuite(CipherSuiteBase):
    """Sigstore / Cosign policy bundle."""

    type: str = "SigstoreCipherSuite"

    def suite_id(self) -> str:
        return "sigstore"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {"sign": _SIG_ALGS, "verify": _SIG_ALGS}

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return "ES256"

    def features(self) -> Features:
        return {
            "suite": "sigstore",
            "version": 1,
            "dialects": {"jwa": list(_SIG_ALGS), "sigstore": ["rekor", "tsa:rfc3161"]},
            "ops": {"sign": {"default": "ES256", "allowed": list(_SIG_ALGS)}},
            "constraints": {"tsa": {"required": False}},
            "compliance": {"fips": False},
            "notes": ["Cosign-style transparency log + optional TSA"],
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
            raise ValueError(f"{chosen=} not supported in Sigstore suite")

        mapped = {"jwa": chosen, "sigstore": chosen, "provider": chosen}
        return {
            "op": op,
            "alg": chosen,
            "dialect": "jwa" if dialect is None else dialect,
            "mapped": mapped,
            "params": dict(params or {}),
            "constraints": {},
            "policy": self.policy(),
        }
