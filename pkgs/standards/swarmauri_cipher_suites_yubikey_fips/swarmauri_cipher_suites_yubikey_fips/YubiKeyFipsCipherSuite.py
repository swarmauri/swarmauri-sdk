from __future__ import annotations

from typing import Iterable, Mapping, Optional

from swarmauri_base.cipher_suites.CipherSuiteBase import CipherSuiteBase
from swarmauri_core.cipher_suites.types import (
    Alg,
    CipherOp,
    Features,
    KeyRef,
    NormalizedDescriptor,
    ParamMapping,
)

_SIGN: tuple[Alg, ...] = ("PS256", "PS384", "ES256", "ES384")
_WRAP: tuple[Alg, ...] = ("RSA-OAEP-256",)


class YubiKeyFipsCipherSuite(CipherSuiteBase):
    type = "YubiKeyFipsCipherSuite"

    def suite_id(self) -> str:
        return "yubikey-fips"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {"sign": _SIGN, "verify": _SIGN, "wrap": _WRAP, "unwrap": _WRAP}

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return {"sign": "PS256", "wrap": "RSA-OAEP-256"}.get(op, "PS256")

    def policy(self) -> Mapping[str, object]:
        return {
            "fips": True,
            "min_rsa_bits": 2048,
            "allowed_curves": ("P-256", "P-384"),
            "hashes": ("SHA256", "SHA384"),
            "attestation_required": True,
            "piv_slots": ("9a", "9c", "9d", "9e"),
        }

    def features(self) -> Features:
        sup = self.supports()
        return {
            "suite": "yubikey-fips",
            "version": 1,
            "dialects": {
                "jwa": list({*sup["sign"], *sup["wrap"]}),
                "provider": ["piv"],
            },
            "ops": {
                "sign": {
                    "default": self.default_alg("sign"),
                    "allowed": list(sup["sign"]),
                },
                "wrap": {
                    "default": self.default_alg("wrap"),
                    "allowed": list(sup["wrap"]),
                },
            },
            "constraints": {
                "min_rsa_bits": 2048,
                "allowed_curves": ["P-256", "P-384"],
                "hashes": ["SHA256", "SHA384"],
                "rsa_pss": {"mgf1": "hash-match", "saltLen": "hashLen"},
            },
            "compliance": {"fips": True},
            "notes": [
                "EdDSA excluded; require attestation; hash & curve policy enforced."
            ],
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
            raise ValueError(
                f"{chosen_alg=} not allowed for {op=} in YubiKey FIPS suite"
            )

        normalized_params = dict(params or {})
        if chosen_alg.startswith("PS"):
            if "saltLen" not in normalized_params:
                normalized_params["saltLen"] = {"PS256": 32, "PS384": 48}[chosen_alg]
            normalized_params.setdefault(
                "mgf1Hash",
                {"PS256": "SHA256", "PS384": "SHA384"}[chosen_alg],
            )
        if chosen_alg in ("ES256", "ES384"):
            normalized_params.setdefault(
                "hash", {"ES256": "SHA256", "ES384": "SHA384"}[chosen_alg]
            )

        mapped = {"jwa": chosen_alg, "provider": f"piv:{chosen_alg}"}
        if key and "slot" in key:
            mapped["provider"] += f":slot={key['slot']}"

        return {
            "op": op,
            "alg": chosen_alg,
            "dialect": "jwa",
            "mapped": mapped,
            "params": normalized_params,
            "constraints": {
                "minKeyBits": 2048,
                "curves": ("P-256", "P-384"),
            },
            "policy": self.policy(),
        }
