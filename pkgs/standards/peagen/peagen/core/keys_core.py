"""Utility helpers for key-pair management — refactored for AutoAPIClient."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, List

import httpx
from autoapi_client      import AutoAPIClient
from autoapi.v2          import AutoAPI
from peagen.orm          import PublicKey        # ORM resource

from peagen._utils.config_loader import load_peagen_toml
from peagen.plugins import PluginManager
from peagen.defaults import DEFAULT_GATEWAY


# ───────────────────────── secrets-driver glue (unchanged) ────────────
def _get_driver(key_dir: Path | None = None, passphrase: str | None = None) -> Any:
    cfg = load_peagen_toml()
    pm = PluginManager(cfg)
    try:
        drv = pm.get("secrets_drivers")
    except KeyError:
        from peagen.plugins.secret_drivers import AutoGpgDriver
        drv = AutoGpgDriver()

    if not hasattr(drv, "list_keys"):
        from peagen.plugins.secret_drivers import AutoGpgDriver
        drv = AutoGpgDriver()

    if key_dir is not None and hasattr(drv, "key_dir"):
        drv.key_dir   = Path(key_dir)
        drv.priv_path = drv.key_dir / "private.asc"
        drv.pub_path  = drv.key_dir / "public.asc"

    if passphrase is not None and hasattr(drv, "passphrase"):
        drv.passphrase = passphrase

    if hasattr(drv, "_ensure_keys"):
        drv._ensure_keys()

    return drv


# ─────────────────────────── local helpers (unchanged) ────────────────
def create_keypair(key_dir: Path | None = None, passphrase: Optional[str] = None) -> dict:
    drv = _get_driver(key_dir=key_dir, passphrase=passphrase)
    return {"private": str(drv.priv_path), "public": str(drv.pub_path)}


def list_local_keys(key_dir: Path | None = None) -> Dict[str, str]:
    return _get_driver(key_dir=key_dir).list_keys()


def export_public_key(
    fingerprint: str, *, key_dir: Path | None = None, fmt: str = "armor"
) -> str:
    return _get_driver(key_dir=key_dir).export_public_key(fingerprint, fmt=fmt)


def add_key(
    public_key: Path,
    *,
    private_key: Path | None = None,
    key_dir: Path | None = None,
    name: str | None = None,
) -> dict:
    drv = _get_driver(key_dir=key_dir)
    return drv.add_key(public_key, private_key=private_key, name=name)


# ─────────────────────────── RPC helpers (new stack) ───────────────────
def _rpc(gateway_url: str) -> AutoAPIClient:
    return AutoAPIClient(gateway_url, client=httpx.Client(timeout=30.0))


def _schema(tag: str):
    return AutoAPI.get_schema(PublicKey, tag)        # classmethod


def upload_public_key(
    key_dir: Path | None = None, gateway_url: str = DEFAULT_GATEWAY
) -> dict:
    drv     = _get_driver(key_dir=key_dir)
    pubkey  = drv.pub_path.read_text()
    SCreate = _schema("create")
    SRead   = _schema("read")

    params  = SCreate(public_key=pubkey)

    with _rpc(gateway_url) as rpc:
        res = rpc.call("PublicKeys.create", params=params, out_schema=SRead)

    return res.model_dump()


def remove_public_key(
    fingerprint: str, gateway_url: str = DEFAULT_GATEWAY
) -> dict:
    SDel = _schema("delete")
    params = SDel(fingerprint=fingerprint)

    with _rpc(gateway_url) as rpc:
        res: dict = rpc.call("PublicKeys.delete", params=params, out_schema=dict)

    return res


def fetch_server_keys(gateway_url: str = DEFAULT_GATEWAY) -> dict:
    SListIn = _schema("list")
    SRead   = _schema("read")

    with _rpc(gateway_url) as rpc:
        res = rpc.call("PublicKeys.list", params=SListIn(), out_schema=list[SRead])  # type: ignore

    return [k.model_dump() for k in res]
