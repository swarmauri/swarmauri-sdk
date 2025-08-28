"""Utility helpers for managing encrypted secrets – AutoAPI edition."""

from __future__ import annotations

import json
import httpx
from pathlib import Path
from typing import List, Optional

from autoapi_client import AutoAPIClient
from autoapi.v3 import get_schema
from peagen.orm import RepoSecret, Worker

from peagen.plugins import PluginManager
from peagen._utils.config_loader import resolve_cfg
from peagen.defaults import DEFAULT_GATEWAY

STORE_FILE = Path.home() / ".peagen" / "secret_store.json"


# ─────────────────────── internal helpers ────────────────────────────
def _schema(model, tag: str):
    return get_schema(model, tag)


def _rpc(url: str, *, timeout: float = 30.0) -> AutoAPIClient:
    return AutoAPIClient(url, client=httpx.Client(timeout=timeout))


def _pool_worker_pubs(pool: str, gateway_url: str) -> list[str]:
    """Return public keys advertised by workers in ``pool``."""
    SListIn = _schema(Worker, "list")
    SRead = _schema(Worker, "read")

    try:
        with _rpc(gateway_url) as rpc:
            workers = rpc.call(
                "Worker.list",
                params=SListIn(pool=pool),
                out_schema=list[SRead],  # type: ignore[arg-type]
            )
    except (httpx.HTTPError, RuntimeError):
        return []

    keys: list[str] = []
    for w in workers:
        advert = w.advertises or {} if hasattr(w, "advertises") else {}
        if isinstance(advert, str):
            try:
                advert = json.loads(advert)
            except Exception:
                advert = {}
        key = advert.get("public_key") or advert.get("pubkey")
        if key:
            keys.append(key)
    return keys


def _load() -> dict:
    return json.loads(STORE_FILE.read_text()) if STORE_FILE.exists() else {}


def _save(data: dict) -> None:
    STORE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STORE_FILE.write_text(json.dumps(data, indent=2))


def _get_crypto():
    """Return a cryptography plugin instance.

    Falls back to ``PGPCrypto`` when no plugin is configured.
    """
    cfg = resolve_cfg()
    pm = PluginManager(cfg)
    try:
        return pm.get("cryptos")
    except KeyError:
        from peagen.plugins.cryptos import PGPCrypto

        return PGPCrypto()


# ─────────────────────── local-only secrets ***************************
def add_local_secret(
    name: str, value: str, recipients: List[Path] | None = None
) -> None:
    crypto = _get_crypto()
    pubkeys = [p.read_text() for p in recipients or []]
    pubkeys.append(crypto.public_key_str())
    cipher = crypto.encrypt_for_text(list(set(pubkeys)), value).decode()
    data = _load()
    data[name] = cipher
    _save(data)


def get_local_secret(name: str) -> str:
    crypto = _get_crypto()
    val = _load().get(name)
    if val is None:
        raise KeyError(f"Secret '{name}' not found in local store.")
    return crypto.decrypt_text(val.encode())


def remove_local_secret(name: str) -> None:
    data = _load()
    data.pop(name, None)
    _save(data)


# ─────────────────────── gateway-backed secrets ***********************
def add_remote_secret(
    secret_id: str,
    value: str,
    gateway_url: str = DEFAULT_GATEWAY,
    *,
    version: int = 0,
    recipients: List[Path] | None = None,
    pool: str = "default",
) -> dict:
    crypto = _get_crypto()
    pubs = [p.read_text() for p in recipients or []]
    pubs.append(crypto.public_key_str())
    pubs.extend(_pool_worker_pubs(pool, gateway_url))

    cipher = crypto.encrypt_for_text(list(set(pubs)), value).decode()
    SCreate = _schema(RepoSecret, "create")
    SRead = _schema(RepoSecret, "read")

    params = SCreate(name=secret_id, cipher=cipher, version=version)

    with _rpc(gateway_url) as rpc:
        res = rpc.call("RepoSecret.create", params=params, out_schema=SRead)
    return res.model_dump()


def get_remote_secret(
    secret_id: str,
    gateway_url: str = DEFAULT_GATEWAY,
) -> str:
    crypto = _get_crypto()
    SDel = _schema(RepoSecret, "delete")  # only primary key (name)
    SRead = _schema(RepoSecret, "read")

    with _rpc(gateway_url) as rpc:
        res = rpc.call("RepoSecret.read", params=SDel(name=secret_id), out_schema=SRead)

    if not res.cipher:
        raise ValueError("RepoSecret not found or is empty.")

    return crypto.decrypt_text(res.cipher.encode())


def remove_remote_secret(
    secret_id: str,
    gateway_url: str = DEFAULT_GATEWAY,
    version: Optional[int] = None,
) -> dict:
    SDel = _schema(RepoSecret, "delete")  # pk-only schema

    params = SDel(name=secret_id, version=version)

    with _rpc(gateway_url) as rpc:
        res: dict = rpc.call("RepoSecret.delete", params=params, out_schema=dict)
    return res
