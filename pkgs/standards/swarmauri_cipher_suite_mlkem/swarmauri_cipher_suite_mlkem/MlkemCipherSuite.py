from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.cipher_suites import CipherSuiteBase
from swarmauri_core.cipher_suites import (
    Alg,
    CipherOp,
    Features,
    KeyRef,
    NormalizedDescriptor,
    OpSupports,
    ParamMapping,
)

_VARIANTS: dict[str, dict[str, Any]] = {
    "mlkem512": {
        "aliases": {
            "ml-kem-512",
            "mlkem-512",
            "mlkem512",
            "mlkem 512",
            "kyber512",
            "kyber-512",
            "mlkem_512",
            "mlkemfips512",
            "fips203-mlkem512",
        },
        "jwa": "ML-KEM-512",
        "tls": {"group": "MLKEM512", "iana": 512, "hex": "0x0200"},
        "provider": "MLKEM512",
        "params": {
            "ciphertextLen": 768,
            "publicKeyLen": 800,
            "secretKeyLen": 1632,
            "sharedSecretLen": 32,
            "securityLevel": 128,
        },
    },
    "mlkem768": {
        "aliases": {
            "ml-kem-768",
            "mlkem-768",
            "mlkem768",
            "mlkem 768",
            "kyber768",
            "kyber-768",
            "mlkem_768",
            "mlkemfips768",
            "fips203-mlkem768",
        },
        "jwa": "ML-KEM-768",
        "tls": {"group": "MLKEM768", "iana": 513, "hex": "0x0201"},
        "provider": "MLKEM768",
        "params": {
            "ciphertextLen": 1088,
            "publicKeyLen": 1184,
            "secretKeyLen": 2400,
            "sharedSecretLen": 32,
            "securityLevel": 192,
        },
    },
    "mlkem1024": {
        "aliases": {
            "ml-kem-1024",
            "mlkem-1024",
            "mlkem1024",
            "mlkem 1024",
            "kyber1024",
            "kyber-1024",
            "mlkem_1024",
            "mlkemfips1024",
            "fips203-mlkem1024",
        },
        "jwa": "ML-KEM-1024",
        "tls": {"group": "MLKEM1024", "iana": 514, "hex": "0x0202"},
        "provider": "MLKEM1024",
        "params": {
            "ciphertextLen": 1568,
            "publicKeyLen": 1568,
            "secretKeyLen": 3168,
            "sharedSecretLen": 32,
            "securityLevel": 256,
        },
    },
}

_ALIAS_INDEX: dict[str, str] = {}


def _normalize_alias(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())


for _canonical, _meta in _VARIANTS.items():
    _ALIAS_INDEX[_normalize_alias(_canonical)] = _canonical
    for _alias in _meta.get("aliases", ()):  # type: ignore[arg-type]
        _ALIAS_INDEX[_normalize_alias(str(_alias))] = _canonical


_ALLOWED_OPS: tuple[CipherOp, ...] = ("wrap", "unwrap", "seal", "unseal")


@ComponentBase.register_type(CipherSuiteBase, "MlkemCipherSuite")
class MlkemCipherSuite(CipherSuiteBase):
    """Cipher suite policy surface for ML-KEM key encapsulation mechanisms."""

    def suite_id(self) -> str:
        return "mlkem"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        algorithms = tuple(_VARIANTS.keys())
        return {op: algorithms for op in _ALLOWED_OPS}

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        if op not in _ALLOWED_OPS:
            raise ValueError(f"Unsupported operation: {op}")
        return "mlkem768"

    def features(self) -> Features:
        algorithms = list(_VARIANTS.keys())
        ops: dict[CipherOp, OpSupports] = {
            op: {"default": self.default_alg(op), "allowed": algorithms}
            for op in _ALLOWED_OPS
        }
        return {
            "suite": self.suite_id(),
            "version": 1,
            "dialects": {
                "tls": [meta["tls"]["group"] for meta in _VARIANTS.values()],
                "jwa": [meta["jwa"] for meta in _VARIANTS.values()],
                "provider": [meta["provider"] for meta in _VARIANTS.values()],
            },
            "ops": ops,
            "constraints": {
                "kem": {
                    "variants": {
                        name: meta["params"] for name, meta in _VARIANTS.items()
                    }
                }
            },
            "compliance": {"fips203": True},
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
        supported = self.supports().get(op)
        if supported is None:
            raise ValueError(f"Unsupported operation: {op}")

        chosen = self._coerce_alg(alg) if alg is not None else None
        if chosen is None:
            chosen = self.default_alg(op, for_key=key)
        if chosen not in set(supported):
            raise ValueError(f"{chosen=} not supported for {op=}")

        meta = _VARIANTS[chosen]
        mapped = {
            "tls": meta["tls"],
            "jwa": meta["jwa"],
            "provider": meta["provider"],
        }

        selected_dialect = dialect if dialect is not None else "tls"
        if selected_dialect not in mapped:
            raise ValueError(
                f"Dialect {selected_dialect!r} is unavailable for ML-KEM descriptors"
            )

        resolved = dict(params or {})
        for key_name, value in meta["params"].items():
            resolved.setdefault(key_name, value)

        return {
            "op": op,
            "alg": chosen,
            "dialect": selected_dialect,
            "mapped": mapped,
            "params": resolved,
            "constraints": {},
            "policy": self.policy(),
        }

    @staticmethod
    def _coerce_alg(alg: Optional[Alg]) -> Optional[Alg]:
        if alg is None:
            return None
        token = _normalize_alias(str(alg))
        return _ALIAS_INDEX.get(token)
