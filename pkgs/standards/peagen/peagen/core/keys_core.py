"""
Key-pair helpers driven by `peagen.plugins.cryptography`.

Exports
-------
create_keypair()      – ensure local key-pair, return fingerprint + pubkey
upload_public_key()   – POST DeployKey.create → dict
remove_public_key()   – DELETE DeployKey.delete → dict
fetch_server_keys()   – GET   DeployKey.list   → [dict]
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import os
import anyio
import httpx
from tigrbl_client import TigrblClient
from tigrbl import get_schema
from peagen._utils.config_loader import (
    load_peagen_toml,
    resolve_cfg,
)
from peagen.defaults import DEFAULT_GATEWAY
from peagen.orm import DeployKey
from peagen.plugins import PluginManager

from swarmauri_core.key_providers.types import KeyAlg, KeyClass, KeySpec, ExportPolicy
from swarmauri_core.crypto.types import KeyUse


def _get_key_provider():
    """Return a key provider plugin instance.

    Falls back to ``SshKeyProvider`` when no plugin is configured.
    """
    cfg = resolve_cfg()
    pm = PluginManager(cfg)
    try:
        return pm.get("key_providers")
    except KeyError:
        from swarmauri_keyprovider_ssh import SshKeyProvider

        return SshKeyProvider()


@contextmanager
def _rpc(gateway: str = DEFAULT_GATEWAY, timeout: float = 30.0):
    with TigrblClient(gateway, timeout=httpx.Timeout(timeout)) as client:
        yield client


def _schema(verb: str):
    """Helper for DeployKey schema look-ups (create/read/delete/list)."""
    return get_schema(DeployKey, verb)  # type: ignore[arg-type]


# -----------------------------------------------------------------------#
# Public helpers
# -----------------------------------------------------------------------#
def create_keypair(
    key_dir: str | Path | None = None,
    passphrase: str | None = None,
) -> dict:
    """
    Idempotent local key-pair provisioning.

    Returns
    -------
    dict  { "fingerprint": str, "public_key": str }
    """
    key_dir = Path(key_dir or Path.home() / ".peagen" / "keys")
    kp = _get_key_provider()

    priv_path = key_dir / "ssh-private"
    pub_path = key_dir / "ssh-public"
    key_dir.mkdir(parents=True, exist_ok=True)

    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label="peagen",
    )

    if priv_path.exists() and pub_path.exists():
        material = priv_path.read_bytes()
        public = pub_path.read_bytes()
        ref = anyio.run(kp.import_key, spec, material, public=public)
    else:
        ref = anyio.run(kp.create_key, spec)
        if ref.material:
            priv_path.write_bytes(ref.material)
            os.chmod(priv_path, 0o600)
        if ref.public:
            pub_path.write_bytes(ref.public)

    fingerprint = ref.tags.get("ssh_fingerprint", getattr(ref, "fingerprint", ""))
    public_key = (ref.public or b"").decode().strip()
    return {"fingerprint": fingerprint, "public_key": public_key}


def upload_public_key(
    key_dir: str | Path | None = None,
    passphrase: str | None = None,
    gateway_url: str = DEFAULT_GATEWAY,
) -> dict:
    info = create_keypair(key_dir, passphrase)
    SCreateIn = _schema("create")
    SRead = _schema("read")

    with _rpc(gateway_url) as rpc:
        res = rpc.call(
            "DeployKeys.create",
            params=SCreateIn(key=info["public_key"]),
            out_schema=SRead,
        )
    return res.model_dump()


def remove_public_key(
    fingerprint: str,
    gateway_url: str = DEFAULT_GATEWAY,
) -> dict:
    SDeleteIn = _schema("delete")

    with _rpc(gateway_url) as rpc:
        res: dict = rpc.call(
            "DeployKeys.delete",
            params=SDeleteIn(fingerprint=fingerprint),
            out_schema=dict,
        )
    return res


def fetch_server_keys(gateway_url: str = DEFAULT_GATEWAY) -> list[dict]:
    SListIn = _schema("list")
    SRead = _schema("read")

    with _rpc(gateway_url) as rpc:
        res = rpc.call(
            "DeployKeys.list",
            params=SListIn(),  # no filters
            out_schema=list[SRead],  # type: ignore[arg-type]
        )
    return [k.model_dump() for k in res]


__all__ = [
    "create_keypair",
    "upload_public_key",
    "remove_public_key",
    "fetch_server_keys",
    "load_peagen_toml",
]
