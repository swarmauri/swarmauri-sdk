from __future__ import annotations

from typing import Dict, Iterable, Mapping, Optional

from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_base.cipher_suites import CipherSuiteBase

_ALLOWED_SIGN = ("PS256", "PS384", "PS512", "ES256", "ES384")
_ALLOWED_ENC = ("A256GCM",)
_ALLOWED_WRAP = ("RSA-OAEP-256", "AES-KW")


class FipsCipherSuite(CipherSuiteBase):
    """FIPS 140-3 policy enforcing cipher suite."""

    type = "FipsCipherSuite"

    def suite_id(self) -> str:
        return "fips140-3"

    def supports(self) -> Mapping[str, Iterable[Alg]]:
        return {
            "sign": _ALLOWED_SIGN,
            "verify": _ALLOWED_SIGN,
            "encrypt": _ALLOWED_ENC,
            "decrypt": _ALLOWED_ENC,
            "wrap": _ALLOWED_WRAP,
            "unwrap": _ALLOWED_WRAP,
        }

    def default_alg(self, op: str, *, for_key: Optional[KeyRef] = None) -> Alg:
        defaults = {
            "sign": "PS256",
            "verify": "PS256",
            "encrypt": "A256GCM",
            "decrypt": "A256GCM",
            "wrap": "RSA-OAEP-256",
            "unwrap": "RSA-OAEP-256",
        }
        return defaults.get(op, "A256GCM")

    def policy(self) -> Mapping[str, object]:
        return {
            "fips": True,
            "min_rsa_bits": 2048,
            "allowed_curves": ("P-256", "P-384"),
            "hashes": ("SHA256", "SHA384"),
            "aead_tag_bits": 128,
        }

    def normalize(
        self,
        *,
        op: str,
        alg: Optional[Alg] = None,
        key: Optional[KeyRef] = None,
        params: Optional[Mapping[str, object]] = None,
        dialect: Optional[str] = None,
    ) -> Mapping[str, object]:
        supported = {
            operation: {str(v) for v in values}
            for operation, values in self.supports().items()
        }
        chosen = str(alg or self.default_alg(op, for_key=key))
        if chosen not in supported.get(op, set()):
            raise ValueError(
                f"Algorithm '{chosen}' is not approved for '{op}' in FIPS mode"
            )

        resolved_params: Dict[str, object] = dict(params or {})
        if chosen.startswith("PS"):
            resolved_params.setdefault("saltBits", int(chosen[-3:]))
            resolved_params.setdefault("hash", "SHA" + chosen[-3:])
        if chosen.endswith("GCM"):
            resolved_params.setdefault("tagBits", self.policy()["aead_tag_bits"])
        if chosen.startswith("ES"):
            resolved_params.setdefault("hash", "SHA" + chosen[-3:])

        mapped = {
            "jwa": chosen,
            "cose": None,
            "provider": chosen,
        }
        constraints = {
            "minKeyBits": self.policy()["min_rsa_bits"],
            "curves": self.policy()["allowed_curves"],
            "hashes": self.policy()["hashes"],
        }
        descriptor: Dict[str, object] = {
            "op": op,
            "alg": chosen,
            "dialect": dialect or "jwa",
            "mapped": mapped,
            "params": resolved_params,
            "constraints": constraints,
        }
        return descriptor
