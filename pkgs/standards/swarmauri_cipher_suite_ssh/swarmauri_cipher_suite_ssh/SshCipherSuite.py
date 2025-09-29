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

_SSH_KEX = ("curve25519-sha256", "ecdh-sha2-nistp256")
_SSH_HOST = ("ssh-ed25519", "rsa-sha2-256")
_SSH_CIPHER = ("chacha20-poly1305@openssh.com", "aes256-gcm@openssh.com")
_SSH_MAC = ("hmac-sha2-256",)


class SshCipherSuite(CipherSuiteBase):
    """Skeleton suite for OpenSSH policy."""

    type = "SshCipherSuite"

    def suite_id(self) -> str:
        return "ssh"

    def supports(self) -> Mapping[CipherOp, Iterable[Alg]]:
        return {"encrypt": _SSH_CIPHER, "decrypt": _SSH_CIPHER}

    def default_alg(self, op: CipherOp, *, for_key: Optional[KeyRef] = None) -> Alg:
        return "chacha20-poly1305@openssh.com"

    def features(self) -> Features:
        return {
            "suite": "ssh",
            "version": 1,
            "dialects": {"ssh": list(_SSH_CIPHER)},
            "constraints": {
                "kex": _SSH_KEX,
                "host_key": _SSH_HOST,
                "mac": _SSH_MAC,
            },
            "ops": {
                "encrypt": {
                    "default": self.default_alg("encrypt"),
                    "allowed": list(_SSH_CIPHER),
                }
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
        chosen = alg or self.default_alg(op)
        if chosen not in allowed:
            raise ValueError(f"{chosen=} not supported for {op=}")

        return {
            "op": op,
            "alg": chosen,
            "dialect": "ssh" if dialect is None else dialect,
            "mapped": {"ssh": chosen, "provider": chosen},
            "params": dict(params or {}),
            "constraints": {},
            "policy": self.policy(),
        }
