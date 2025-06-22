"""Utility helpers for managing encrypted secrets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import httpx

from peagen.plugins.secret_drivers import AutoGpgDriver

DEFAULT_GATEWAY = "http://localhost:8000/rpc"
STORE_FILE = Path.home() / ".peagen" / "secret_store.json"


def _pool_worker_pubs(pool: str, gateway_url: str) -> list[str]:
    envelope = {
        "jsonrpc": "2.0",
        "method": "Worker.list",
        "params": {"pool": pool},
    }
    try:
        res = httpx.post(gateway_url, json=envelope, timeout=10.0)
        res.raise_for_status()
    except Exception:
        return []
    workers = res.json().get("result", [])
    keys = []
    for w in workers:
        advert = w.get("advertises") or {}
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
    if STORE_FILE.exists():
        return json.loads(STORE_FILE.read_text())
    return {}


def _save(data: dict) -> None:
    STORE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STORE_FILE.write_text(json.dumps(data, indent=2))


def add_local_secret(
    name: str, value: str, recipients: List[Path] | None = None
) -> None:
    """Encrypt and store a secret locally."""
    drv = AutoGpgDriver()
    pubkeys = [p.read_text() for p in recipients or []]
    cipher = drv.encrypt(value.encode(), pubkeys).decode()
    data = _load()
    data[name] = cipher
    _save(data)


def get_local_secret(name: str) -> str:
    """Decrypt and return a locally stored secret."""
    drv = AutoGpgDriver()
    val = _load().get(name)
    if val is None:
        raise KeyError("Unknown secret")
    return drv.decrypt(val.encode()).decode()


def remove_local_secret(name: str) -> None:
    """Remove a secret from the local store."""
    data = _load()
    data.pop(name, None)
    _save(data)


def add_remote_secret(
    secret_id: str,
    value: str,
    gateway_url: str = DEFAULT_GATEWAY,
    *,
    version: int = 0,
    recipients: List[Path] | None = None,
    pool: str = "default",
) -> dict:
    """Upload an encrypted secret to the gateway."""
    drv = AutoGpgDriver()
    pubs = [p.read_text() for p in recipients or []]
    pubs.extend(_pool_worker_pubs(pool, gateway_url))
    cipher = drv.encrypt(value.encode(), pubs).decode()
    envelope = {
        "jsonrpc": "2.0",
        "method": "Secrets.add",
        "params": {"id": secret_id, "secret": cipher, "version": version},
    }
    res = httpx.post(gateway_url, json=envelope, timeout=10.0)
    res.raise_for_status()
    return res.json()


def get_remote_secret(secret_id: str, gateway_url: str = DEFAULT_GATEWAY) -> str:
    """Retrieve and decrypt a secret from the gateway."""
    drv = AutoGpgDriver()
    envelope = {
        "jsonrpc": "2.0",
        "method": "Secrets.get",
        "params": {"id": secret_id},
    }
    res = httpx.post(gateway_url, json=envelope, timeout=10.0)
    res.raise_for_status()
    cipher = res.json()["result"]["secret"].encode()
    return drv.decrypt(cipher).decode()


def remove_remote_secret(
    secret_id: str,
    gateway_url: str = DEFAULT_GATEWAY,
    version: Optional[int] = None,
) -> dict:
    """Delete a secret stored on the gateway."""
    envelope = {
        "jsonrpc": "2.0",
        "method": "Secrets.delete",
        "params": {"id": secret_id, "version": version},
    }
    res = httpx.post(gateway_url, json=envelope, timeout=10.0)
    res.raise_for_status()
    return res.json()
