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

_SIGN = ("ES384", "PS384")
_ENC = ("A256GCM",)


class Cnsa20CipherSuite(CipherSuiteBase):
    """Skeleton suite for CNSA 2.0 policy."""

    type = "Cnsa20CipherSuite"

    def suite_id(self) -> str:
        return "cnsa-2.0"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {
            "sign": _SIGN,
            "verify": _SIGN,
            "encrypt": _ENC,
            "decrypt": _ENC,
        }

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return {"sign": "ES384", "encrypt": "A256GCM"}.get(op, "A256GCM")

    def features(self) -> Features:
        return {
            "suite": "cnsa-2.0",
            "version": 1,
            "dialects": {"jwa": list({*_SIGN, *_ENC})},
            "constraints": {
                "min_rsa_bits": 3072,
                "allowed_curves": ["P-384"],
                "hash": "SHA384",
                "aead": {"tagBits": 128, "nonceLen": 12},
            },
            "compliance": {"cnsa": True},
            "ops": {
                "sign": {"default": "ES384", "allowed": list(_SIGN)},
                "encrypt": {"default": "A256GCM", "allowed": list(_ENC)},
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
            raise ValueError(f"{chosen=} not supported for {op=}")

        resolved = dict(params or {})
        if chosen.endswith("GCM"):
            resolved.setdefault("tagBits", 128)
            resolved.setdefault("nonceLen", 12)

        return {
            "op": op,
            "alg": chosen,
            "dialect": "jwa" if dialect is None else dialect,
            "mapped": {"jwa": chosen, "provider": chosen},
            "params": resolved,
            "constraints": {"minKeyBits": 3072},
            "policy": self.policy(),
        }
