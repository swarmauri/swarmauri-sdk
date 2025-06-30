"""Utility helpers for managing encrypted secrets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from peagen.plugins.secret_drivers import AutoGpgDriver
from peagen.transport.client import (
    RPCResponseError,
    RPCTransportError,
    send_jsonrpc_request,
)
from peagen.transport.jsonrpc_schemas.secrets import (
    SECRETS_ADD,
    SECRETS_DELETE,
    SECRETS_GET,
    AddParams,
    AddResult,
    DeleteParams,
    DeleteResult,
    GetParams,
    GetResult,
)
from peagen.transport.jsonrpc_schemas.worker import WORKER_LIST, ListParams, ListResult

DEFAULT_GATEWAY = "http://localhost:8000/rpc"
STORE_FILE = Path.home() / ".peagen" / "secret_store.json"


def _pool_worker_pubs(pool: str, gateway_url: str) -> list[str]:
    """Return public keys advertised by workers in ``pool``."""
    params = ListParams(pool=pool)
    try:
        result = send_jsonrpc_request(
            gateway_url, WORKER_LIST, params, expect=ListResult
        )
        workers = result.root if hasattr(result, "root") else result
    except (RPCTransportError, RPCResponseError):
        return []

    keys = []
    for w in workers:
        if isinstance(w, dict):
            advert = w.get("advertises") or {}
        else:
            advert = w.advertises or {}
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
    pubkeys.append(drv.pub_path.read_text())
    cipher = drv.encrypt(value.encode(), list(set(pubkeys))).decode()
    data = _load()
    data[name] = cipher
    _save(data)


def get_local_secret(name: str) -> str:
    """Decrypt and return a locally stored secret."""
    drv = AutoGpgDriver()
    val = _load().get(name)
    if val is None:
        raise KeyError(f"Secret '{name}' not found in local store.")
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
    pubs.append(drv.pub_path.read_text())
    pubs.extend(_pool_worker_pubs(pool, gateway_url))

    encrypted_value = drv.encrypt(value.encode(), list(set(pubs))).decode()

    params = AddParams(name=secret_id, cipher=encrypted_value, version=version)
    result = send_jsonrpc_request(
        gateway_url, SECRETS_ADD, params, expect=AddResult, sign=True
    )
    return result.model_dump()


def get_remote_secret(
    secret_id: str,
    gateway_url: str = DEFAULT_GATEWAY,
) -> str:
    """Retrieve and decrypt a secret from the gateway."""
    drv = AutoGpgDriver()
    params = GetParams(name=secret_id)
    result = send_jsonrpc_request(
        gateway_url, SECRETS_GET, params, expect=GetResult, sign=True
    )
    if not result.cipher:
        raise ValueError("Secret not found or is empty.")
    return drv.decrypt(result.cipher.encode()).decode()


def remove_remote_secret(
    secret_id: str,
    gateway_url: str = DEFAULT_GATEWAY,
    version: Optional[int] = None,
) -> dict:
    """Delete a secret stored on the gateway."""
    params = DeleteParams(name=secret_id, version=version)
    result = send_jsonrpc_request(
        gateway_url, SECRETS_DELETE, params, expect=DeleteResult, sign=True
    )
    return result.model_dump()
