from __future__ import annotations

from typing import Dict, Iterable, Mapping, Optional

from swarmauri_core.crypto.types import Alg, JWAAlg, KeyRef
from swarmauri_base.cipher_suites import CipherSuiteBase

_JWA_TO_COSE: Dict[str, int] = {
    "ES256": -7,
    "ES384": -35,
    "ES512": -36,
    "PS256": -37,
    "PS384": -38,
    "PS512": -39,
    "EdDSA": -8,
    "A128GCM": 1,
    "A192GCM": 2,
    "A256GCM": 3,
}


class JwaCipherSuite(CipherSuiteBase):
    """JWA dialect cipher suite."""

    type = "JwaCipherSuite"

    def suite_id(self) -> str:
        return "jwa"

    def supports(self) -> Mapping[str, Iterable[Alg]]:
        return {
            "sign": (
                JWAAlg.EDDSA.value,
                JWAAlg.PS256.value,
                JWAAlg.PS384.value,
                JWAAlg.PS512.value,
                JWAAlg.ES256.value,
                JWAAlg.ES384.value,
                JWAAlg.ES512.value,
            ),
            "verify": (
                JWAAlg.EDDSA.value,
                JWAAlg.PS256.value,
                JWAAlg.PS384.value,
                JWAAlg.PS512.value,
                JWAAlg.ES256.value,
                JWAAlg.ES384.value,
                JWAAlg.ES512.value,
            ),
            "encrypt": (
                JWAAlg.A128GCM.value,
                JWAAlg.A192GCM.value,
                JWAAlg.A256GCM.value,
            ),
            "decrypt": (
                JWAAlg.A128GCM.value,
                JWAAlg.A192GCM.value,
                JWAAlg.A256GCM.value,
            ),
            "wrap": (
                JWAAlg.RSA_OAEP.value,
                JWAAlg.RSA_OAEP_256.value,
                "AES-KW",
            ),
            "unwrap": (
                JWAAlg.RSA_OAEP.value,
                JWAAlg.RSA_OAEP_256.value,
                "AES-KW",
            ),
        }

    def default_alg(self, op: str, *, for_key: Optional[KeyRef] = None) -> Alg:
        defaults = {
            "sign": JWAAlg.EDDSA.value,
            "verify": JWAAlg.EDDSA.value,
            "encrypt": JWAAlg.A256GCM.value,
            "decrypt": JWAAlg.A256GCM.value,
            "wrap": JWAAlg.RSA_OAEP_256.value,
            "unwrap": JWAAlg.RSA_OAEP_256.value,
        }
        return defaults.get(op, JWAAlg.A256GCM.value)

    def policy(self) -> Mapping[str, object]:
        return {"fips": False}

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
            operation: {str(value) for value in values}
            for operation, values in self.supports().items()
        }
        chosen = str(alg or self.default_alg(op, for_key=key))
        if chosen not in supported.get(op, set()):
            raise ValueError(f"Unsupported algorithm '{chosen}' for operation '{op}'")

        resolved_params: Dict[str, object] = dict(params or {})
        if chosen.startswith("PS") and "saltBits" not in resolved_params:
            resolved_params["saltBits"] = int(chosen[-3:])
        if chosen.endswith("GCM"):
            resolved_params.setdefault("tagBits", 128)
        if chosen == JWAAlg.EDDSA.value:
            resolved_params.setdefault("hash", "SHA-512")

        mapped = {
            "jwa": chosen,
            "cose": _JWA_TO_COSE.get(chosen),
            "provider": chosen,
        }
        descriptor: Dict[str, object] = {
            "op": op,
            "alg": chosen,
            "dialect": dialect or "jwa",
            "mapped": mapped,
            "params": resolved_params,
            "constraints": {},
        }
        return descriptor
