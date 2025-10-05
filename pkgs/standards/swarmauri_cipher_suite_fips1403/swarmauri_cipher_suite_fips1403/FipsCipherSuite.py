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

_ALLOWED_SIGN = ("PS256", "PS384", "ES256", "ES384")
_ALLOWED_ENC = ("A256GCM",)
_ALLOWED_WRAP = ("RSA-OAEP-256", "A256KW")


@ComponentBase.register_type(CipherSuiteBase, "FipsCipherSuite")
class FipsCipherSuite(CipherSuiteBase):
    """FIPS 140-3 compliant algorithm surface."""

    def suite_id(self) -> str:
        return "fips140-3"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {
            "sign": _ALLOWED_SIGN,
            "verify": _ALLOWED_SIGN,
            "encrypt": _ALLOWED_ENC,
            "decrypt": _ALLOWED_ENC,
            "wrap": _ALLOWED_WRAP,
            "unwrap": _ALLOWED_WRAP,
        }

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return {
            "sign": "PS256",
            "encrypt": "A256GCM",
            "wrap": "RSA-OAEP-256",
        }.get(op, "A256GCM")

    def policy(self) -> Mapping[str, object]:
        return {
            "fips": True,
            "min_rsa_bits": 2048,
            "allowed_curves": ("P-256", "P-384"),
            "hashes": ("SHA256", "SHA384"),
            "aead_tag_bits": 128,
        }

    def features(self) -> Features:
        return {
            "suite": "fips140-3",
            "version": 1,
            "dialects": {
                "jwa": list(
                    {
                        *self.supports()["sign"],
                        *self.supports()["encrypt"],
                        *self.supports()["wrap"],
                    }
                ),
            },
            "ops": {
                "sign": {"default": "PS256", "allowed": list(_ALLOWED_SIGN)},
                "encrypt": {"default": "A256GCM", "allowed": list(_ALLOWED_ENC)},
                "wrap": {"default": "RSA-OAEP-256", "allowed": list(_ALLOWED_WRAP)},
            },
            "constraints": {
                "min_rsa_bits": 2048,
                "allowed_curves": ["P-256", "P-384"],
                "aead": {"tagBits": 128, "nonceLen": 12},
            },
            "compliance": {"fips": True},
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
        chosen = alg or self.default_alg(op, for_key=key)
        if chosen not in allowed:
            raise ValueError(f"{chosen=} not allowed by FIPS 140-3 for {op=}")

        resolved = dict(params or {})
        if chosen.endswith("GCM"):
            resolved.setdefault("tagBits", self.policy()["aead_tag_bits"])
            resolved.setdefault("nonceLen", 12)
        if chosen.startswith("PS"):
            resolved.setdefault("saltBits", int(chosen[-3:]))
            resolved.setdefault("hash", "SHA" + chosen[-3:])
        if chosen.startswith("ES"):
            resolved.setdefault("hash", "SHA" + chosen[-3:])

        return {
            "op": op,
            "alg": chosen,
            "dialect": "jwa" if dialect is None else dialect,
            "mapped": {"jwa": chosen, "provider": chosen},
            "params": resolved,
            "constraints": {
                "minKeyBits": self.policy()["min_rsa_bits"],
                "curves": self.policy()["allowed_curves"],
                "hashes": self.policy()["hashes"],
            },
            "policy": self.policy(),
        }
