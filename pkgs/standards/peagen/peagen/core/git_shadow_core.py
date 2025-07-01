"""Idempotent helpers for shadow repo management."""

from __future__ import annotations
from urllib.parse import urlparse

import httpx

from peagen.defaults import (
    GIT_SHADOW_BASE,
    GIT_SHADOW_TOKEN,
)


def _split_github(url: str) -> tuple[str, str]:
    """
    https://github.com/<org>/<repo>.git -> ('org', 'repo')
    """
    parts = urlparse(url)
    path = parts.path.lstrip("/").removesuffix(".git")
    return tuple(path.split("/", 1))  # type: ignore[misc]


async def _req(method: str, path: str, **kw):
    hdr = {"Authorization": f"token {GIT_SHADOW_TOKEN}"}
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.request(method, f"{GIT_SHADOW_BASE}{path}", headers=hdr, **kw)
        if r.status_code == 404:
            raise FileNotFoundError(path)
        r.raise_for_status()
        return r.json()


async def ensure_org(slug: str):
    try:
        await _req("GET", f"/api/v1/orgs/{slug}")
    except FileNotFoundError:
        await _req(
            "POST", "/api/v1/orgs", json={"username": slug, "visibility": "private"}
        )


async def ensure_mirror(slug: str, repo: str, upstream: str):
    try:
        await _req("GET", f"/api/v1/repos/{slug}/{repo}")
    except FileNotFoundError:
        body = {
            "name": repo,
            "private": True,
            "mirror": True,
            "mirror_interval": "1m",
            "clone_addr": upstream,
        }
        await _req("POST", f"/api/v1/orgs/{slug}/repos", json=body)


async def attach_deploy_key(slug: str, repo: str, pub_key: str, rw=True) -> int:
    keys = await _req("GET", f"/api/v1/repos/{slug}/{repo}/keys")
    for k in keys:
        if k["key"] == pub_key and k["read_only"] == (not rw):
            return k["id"]
    body = {"key": pub_key, "read_only": not rw, "title": "peagen-auto"}
    k = await _req("POST", f"/api/v1/repos/{slug}/{repo}/keys", json=body)
    return k["id"]
