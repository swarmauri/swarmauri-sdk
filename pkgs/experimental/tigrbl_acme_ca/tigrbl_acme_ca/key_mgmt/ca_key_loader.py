from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from tigrbl_acme_ca.key_mgmt.providers import (
    FileKeyProvider,
    KmsKeyProvider,
    Pkcs11KeyProvider,
    KeyProvider,
)


@dataclass
class CaKeyLoader:
    provider: KeyProvider

    @classmethod
    def from_config(cls, config: dict) -> "CaKeyLoader":
        km_cfg = (config or {}).get("acme.ca", {})
        source = (km_cfg.get("key_source") or "file").lower()
        if source == "file":
            prov = FileKeyProvider(
                path=km_cfg.get("key_path", "ca.key.pem"),
                password=km_cfg.get("key_password"),
            )
        elif source == "kms":
            prov = KmsKeyProvider(
                key_id=km_cfg.get("kms_key_id"), region=km_cfg.get("kms_region")
            )
        elif source == "pkcs11":
            prov = Pkcs11KeyProvider(
                slot=int(km_cfg.get("slot", 0)), label=km_cfg.get("label")
            )
        else:
            raise ValueError(f"Unsupported key_source: {source}")
        return cls(provider=prov)

    async def load_issuer_key(self) -> Any:
        return self.provider.private_key()
