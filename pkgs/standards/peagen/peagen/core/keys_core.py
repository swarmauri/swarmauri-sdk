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

import httpx
from autoapi_client import AutoAPIClient
from autoapi.v2 import AutoAPI
from peagen._utils.config_loader import (
    load_peagen_toml,
    resolve_cfg,
)
from peagen.defaults import DEFAULT_GATEWAY
from peagen.orm import DeployKey
from peagen.plugins import PluginManager

# ───────────────────────── cryptography layer ───────────────────────────
from peagen.plugins.cryptos import ParamikoCrypto, CryptoBase


# -----------------------------------------------------------------------#
# Internal helpers
# -----------------------------------------------------------------------#
def _get_crypto(
    key_dir: str | Path | None = None,
    passphrase: str | None = None,
) -> CryptoBase:
    """
    Resolve a `CryptoBase` provider through the plugin manager.
    Fallback ➜ `ParamikoCrypto` when no plugin is configured.
    """
    cfg = resolve_cfg()  # helper loads ~/.peagen.toml
    pm = PluginManager(cfg)
    try:
        crypto_cls = pm.get("cryptos")  # user-supplied plugin
    except KeyError:
        crypto_cls = ParamikoCrypto  # built-in default
    return crypto_cls(key_dir=key_dir, passphrase=passphrase)


@contextmanager
def _rpc(gateway: str = DEFAULT_GATEWAY, timeout: float = 30.0):
    with AutoAPIClient(gateway, timeout=httpx.Timeout(timeout)) as client:
        yield client


def _schema(verb: str):
    """Helper for DeployKey schema look-ups (create/read/delete/list)."""
    return AutoAPI.get_schema(DeployKey, verb)  # type: ignore[arg-type]


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
    drv = _get_crypto(key_dir, passphrase)
    return {"fingerprint": drv.fingerprint(), "public_key": drv.public_key_str()}


def upload_public_key(
    key_dir: str | Path | None = None,
    passphrase: str | None = None,
    gateway_url: str = DEFAULT_GATEWAY,
) -> dict:
    drv = _get_crypto(key_dir, passphrase)
    SCreateIn = _schema("create")
    SRead = _schema("read")

    with _rpc(gateway_url) as rpc:
        res = rpc.call(
            "DeployKeys.create",
            params=SCreateIn(key=drv.public_key_str()),
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
