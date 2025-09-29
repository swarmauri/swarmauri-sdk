from __future__ import annotations

from typing import Dict, Iterable, Mapping, Optional

from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_base.cipher_suites import CipherSuiteBase

_COSE_ALGS: Dict[str, tuple[int, ...]] = {
    "sign": (-8, -7, -35, -36, -37, -38, -39),
    "verify": (-8, -7, -35, -36, -37, -38, -39),
    "encrypt": (1, 2, 3),
    "decrypt": (1, 2, 3),
    "wrap": (1, 2, 3),
    "unwrap": (1, 2, 3),
}

_COSE_TO_JWA: Dict[int, str] = {
    -8: "EdDSA",
    -7: "ES256",
    -35: "ES384",
    -36: "ES512",
    -37: "PS256",
    -38: "PS384",
    -39: "PS512",
    1: "A128GCM",
    2: "A192GCM",
    3: "A256GCM",
}


class CoseCipherSuite(CipherSuiteBase):
    """COSE dialect cipher suite."""

    type = "CoseCipherSuite"

    def suite_id(self) -> str:
        return "cose"

    def supports(self) -> Mapping[str, Iterable[Alg]]:
        return {op: tuple(str(v) for v in values) for op, values in _COSE_ALGS.items()}

    def default_alg(self, op: str, *, for_key: Optional[KeyRef] = None) -> Alg:
        defaults = {
            "sign": "-8",
            "verify": "-8",
            "encrypt": "3",
            "decrypt": "3",
            "wrap": "3",
            "unwrap": "3",
        }
        return defaults.get(op, "3")

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
            operation: {str(v) for v in values}
            for operation, values in self.supports().items()
        }
        chosen = alg if alg is not None else self.default_alg(op, for_key=key)
        chosen_str = str(chosen)
        if chosen_str not in supported.get(op, set()):
            raise ValueError(
                f"Unsupported algorithm '{chosen_str}' for operation '{op}'"
            )

        resolved_params: Dict[str, object] = dict(params or {})
        if int(chosen_str) in (1, 2, 3):
            resolved_params.setdefault("tagBits", 128)

        cose_int = int(chosen_str)
        mapped = {
            "cose": cose_int,
            "jwa": _COSE_TO_JWA.get(cose_int),
            "provider": chosen_str,
        }
        descriptor: Dict[str, object] = {
            "op": op,
            "alg": chosen_str,
            "dialect": dialect or "cose",
            "mapped": mapped,
            "params": resolved_params,
            "constraints": {},
        }
        return descriptor
