"""Utility helpers for managing encrypted secrets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import uuid
import httpx
from pydantic import TypeAdapter
from peagen.protocols import Request, Response
from peagen.protocols.methods.worker import WORKER_LIST, ListParams, ListResult
from peagen.protocols.methods.secrets import (
    AddParams,
    AddResult,
    GetParams,
    GetResult,
    DeleteParams,
    DeleteResult,
    SECRETS_ADD,
    SECRETS_GET,
    SECRETS_DELETE,
)

from peagen.plugins.secret_drivers import AutoGpgDriver

DEFAULT_GATEWAY = "http://localhost:8000/rpc"
STORE_FILE = Path.home() / ".peagen" / "secret_store.json"


def _rpc_post(
    url: str, method: str, params: dict, *, timeout: float = 10.0, result_model=None
):
    """Send a JSON-RPC request and return a typed ``Response``."""
    envelope = Request(id=str(uuid.uuid4()), method=method, params=params)
    resp = httpx.post(url, json=envelope.model_dump(), timeout=timeout)
    resp.raise_for_status()
    if result_model is not None:
        adapter = TypeAdapter(Response[result_model])  # type: ignore[index]
    else:
        adapter = TypeAdapter(Response[dict])
    return adapter.validate_python(resp.json())


def _pool_worker_pubs(pool: str, gateway_url: str) -> list[str]:
    envelope = ListParams(pool=pool).model_dump()
    try:
        res = _rpc_post(
            gateway_url,
            WORKER_LIST,
            envelope,
            timeout=10.0,
            result_model=ListResult,
        )
        workers = res.result or []
    except Exception:
        return []
    keys = []
    for w in workers:
        advert = w.get("advertises") or {}
        if isinstance(advert, str):  # gateway may return JSON string
            try:
                advert = json.loads(advert)
            except Exception:  # pragma: no cover - invalid JSON
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
    params = AddParams(
        name=secret_id,
        cipher=cipher,
        tenant_id=pool,
        version=version,
    ).model_dump()
    res = _rpc_post(
        gateway_url,
        SECRETS_ADD,
        params,
        timeout=10.0,
        result_model=AddResult,
    )
    return res.model_dump()


def get_remote_secret(
    secret_id: str,
    gateway_url: str = DEFAULT_GATEWAY,
    *,
    pool: str = "default",
) -> str:
    """Retrieve and decrypt a secret from the gateway."""
    drv = AutoGpgDriver()
    params = GetParams(name=secret_id, tenant_id=pool).model_dump()
    res = _rpc_post(
        gateway_url,
        SECRETS_GET,
        params,
        timeout=10.0,
        result_model=GetResult,
    )
    cipher = res.result.secret.encode()
    return drv.decrypt(cipher).decode()


def remove_remote_secret(
    secret_id: str,
    gateway_url: str = DEFAULT_GATEWAY,
    version: Optional[int] = None,
    *,
    pool: str = "default",
) -> dict:
    """Delete a secret stored on the gateway."""
    params = DeleteParams(
        name=secret_id,
        tenant_id=pool,
        version=version,
    ).model_dump()
    res = _rpc_post(
        gateway_url,
        SECRETS_DELETE,
        params,
        timeout=10.0,
        result_model=DeleteResult,
    )
    return res.model_dump()
