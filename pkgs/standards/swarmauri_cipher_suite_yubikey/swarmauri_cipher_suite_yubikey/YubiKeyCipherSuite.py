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

_SIGN: tuple[Alg, ...] = ("PS256", "PS384", "PS512", "ES256", "ES384", "EdDSA")
_WRAP: tuple[Alg, ...] = ("RSA-OAEP-256",)


class YubiKeyCipherSuite(CipherSuiteBase):
    type = "YubiKeyCipherSuite"

    def suite_id(self) -> str:
        return "yubikey"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {
            "sign": _SIGN,
            "verify": _SIGN,
            "wrap": _WRAP,
            "unwrap": _WRAP,
        }

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return {"sign": "ES256", "wrap": "RSA-OAEP-256"}.get(op, "ES256")

    def policy(self) -> Mapping[str, object]:
        return {
            "fips": False,
            "min_rsa_bits": 2048,
            "allowed_curves": ("P-256", "P-384"),
            "hashes": ("SHA256", "SHA384", "SHA512"),
            "attestation_required": False,
            "piv_slots": ("9a", "9c", "9d", "9e"),
        }

    def features(self) -> Features:
        sup = self.supports()
        return {
            "suite": "yubikey",
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
                "rsa_pss": {"mgf1": "hash-match", "saltLen": "hashLen"},
            },
            "compliance": {"fips": False},
            "notes": [
                "PIV-backed signing/unwrap; EdDSA allowed on non-FIPS models/firmware.",
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
            raise ValueError(f"{chosen_alg=} not supported for {op=} in YubiKey suite")

        normalized_params = dict(params or {})
        if chosen_alg.startswith("PS"):
            if "saltLen" not in normalized_params:
                normalized_params["saltLen"] = {"PS256": 32, "PS384": 48, "PS512": 64}[
                    chosen_alg
                ]
            normalized_params.setdefault(
                "mgf1Hash",
                {"PS256": "SHA256", "PS384": "SHA384", "PS512": "SHA512"}[chosen_alg],
            )
        if chosen_alg in ("ES256", "ES384"):
            normalized_params.setdefault(
                "hash", {"ES256": "SHA256", "ES384": "SHA384"}[chosen_alg]
            )

        mapped = {
            "jwa": chosen_alg,
            "provider": f"piv:{chosen_alg}",
        }
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
