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

_FIDO_COSE = ("-7", "-8", "-257")


class WebAuthnCipherSuite(CipherSuiteBase):
    """COSE subset tailored for WebAuthn / FIDO2."""

    type: str = "WebAuthnCipherSuite"

    def suite_id(self) -> str:
        return "webauthn"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {"sign": _FIDO_COSE, "verify": _FIDO_COSE}

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return "-7"

    def features(self) -> Features:
        return {
            "suite": "webauthn",
            "version": 1,
            "dialects": {"cose": list(_FIDO_COSE), "fido2": list(_FIDO_COSE)},
            "ops": {"sign": {"default": "-7", "allowed": list(_FIDO_COSE)}},
            "constraints": {
                "attestation_formats": ["packed", "tpm", "android-safetynet", "apple"]
            },
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
        chosen = str(alg or self.default_alg(op))
        if chosen not in allowed:
            raise ValueError(f"{chosen=} not allowed for {op=} in WebAuthn")

        return {
            "op": op,
            "alg": chosen,
            "dialect": "cose" if dialect is None else dialect,
            "mapped": {"cose": int(chosen), "fido2": chosen, "provider": chosen},
            "params": dict(params or {}),
            "constraints": {},
            "policy": self.policy(),
        }
