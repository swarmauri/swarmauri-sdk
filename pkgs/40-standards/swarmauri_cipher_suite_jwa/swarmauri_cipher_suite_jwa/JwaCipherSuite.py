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

_JWA_TO_COSE = {
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


@ComponentBase.register_type(CipherSuiteBase, "JwaCipherSuite")
class JwaCipherSuite(CipherSuiteBase):
    """JSON Web Algorithm policy surface (RFC 7518)."""

    enable_x448: bool = False

    def suite_id(self) -> str:
        return "jwa"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {
            "sign": (
                "EdDSA",
                "PS256",
                "PS384",
                "PS512",
                "ES256",
                "ES384",
                "ES512",
            ),
            "verify": (
                "EdDSA",
                "PS256",
                "PS384",
                "PS512",
                "ES256",
                "ES384",
                "ES512",
            ),
            "encrypt": ("A128GCM", "A192GCM", "A256GCM"),
            "decrypt": ("A128GCM", "A192GCM", "A256GCM"),
            "wrap": ("RSA-OAEP", "RSA-OAEP-256", "A256KW"),
            "unwrap": ("RSA-OAEP", "RSA-OAEP-256", "A256KW"),
            **({"key_agreement": ("ECDH-ES",)} if self.enable_x448 else {}),
        }

    def default_alg(
        self, op: CipherOp, *, for_key: Optional[KeyRef] = None
    ) -> Alg:
        if op == "key_agreement" and not self.enable_x448:
            raise ValueError(
                "key_agreement is not supported without X448 opt-in."
            )
        defaults = {
            "sign": "EdDSA",
            "encrypt": "A256GCM",
            "wrap": "RSA-OAEP-256",
            "key_agreement": "ECDH-ES",
        }
        return defaults.get(op, "A256GCM")

    def features(self) -> Features:
        allowed = self.supports()
        flat = sorted({alg for values in allowed.values() for alg in values})
        return {
            "suite": "jwa",
            "version": 1,
            "dialects": {
                "jwa": flat,
                "cose": [
                    value
                    for value in {_JWA_TO_COSE.get(alg) for alg in flat}
                    if value is not None
                ],
            },
            "ops": {
                op: {"default": self.default_alg(op), "allowed": list(values)}
                for op, values in allowed.items()
                if values
            },
            "constraints": {
                "aead": {"tagBits": 128, "nonceLen": 12},
                **(
                    {
                        "key_agreement": {
                            "kty": "OKP",
                            "crv": "X448",
                            "enc": "A256GCM",
                        }
                    }
                    if self.enable_x448
                    else {}
                ),
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
        chosen = alg or self.default_alg(op, for_key=key)
        if chosen not in allowed:
            raise ValueError(f"{chosen=} not supported for {op=}")

        resolved = dict(params or {})
        if chosen == "ECDH-ES":
            if not key or (key.get("kty"), key.get("crv")) != ("OKP", "X448"):
                raise ValueError("ECDH-ES policy requires an OKP/X448 key.")
            if resolved.setdefault("enc", "A256GCM") != "A256GCM":
                raise ValueError("X448 requires A256GCM.")
            if resolved.setdefault("crv", "X448") != "X448":
                raise ValueError("ECDH-ES policy requires X448.")
        if chosen.endswith("GCM"):
            resolved.setdefault("tagBits", 128)
            resolved.setdefault("nonceLen", 12)
        if chosen.startswith("PS"):
            resolved.setdefault("saltBits", int(chosen[-3:]))
        mapped = {
            "jwa": chosen,
            "cose": _JWA_TO_COSE.get(chosen),
            "provider": chosen,
        }
        return {
            "op": op,
            "alg": chosen,
            "dialect": "jwa"
            if dialect is None
            else dialect,  # allow caller override
            "mapped": mapped,
            "params": resolved,
            "constraints": {"minKeyBits": 0},
            "policy": self.policy(),
        }
