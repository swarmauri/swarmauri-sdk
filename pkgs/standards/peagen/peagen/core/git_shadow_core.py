"""Idempotent helpers for shadow repo management."""
from __future__ import annotations
import os, httpx, asyncio

BASE = os.getenv("PEAGEN_GIT_SHADOW_URL", "https://git.peagen.com")
TOKEN = os.environ["PEAGEN_GIT_SHADOW_PAT"]          # service account PAT

async def _req(method: str, path: str, **kw):
    hdr = {"Authorization": f"token {TOKEN}"}
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.request(method, f"{BASE}{path}", headers=hdr, **kw)
        if r.status_code == 404:
            raise FileNotFoundError(path)
        r.raise_for_status()
        return r.json()

async def ensure_org(slug: str):
    try:
        await _req("GET", f"/api/v1/orgs/{slug}")
    except FileNotFoundError:
        await _req("POST", "/api/v1/orgs",
                   json={"username": slug, "visibility": "private"})

async def ensure_mirror(slug: str, repo: str, upstream: str):
    try:
        await _req("GET", f"/api/v1/repos/{slug}/{repo}")
    except FileNotFoundError:
        body = {"name": repo, "private": True, "mirror": True,
                "mirror_interval": "1m", "clone_addr": upstream}
        await _req("POST", f"/api/v1/orgs/{slug}/repos", json=body)

async def attach_deploy_key(slug: str, repo: str, pub_key: str, rw=True) -> int:
    keys = await _req("GET", f"/api/v1/repos/{slug}/{repo}/keys")
    for k in keys:
        if k["key"] == pub_key and k["read_only"] == (not rw):
            return k["id"]
    body = {"key": pub_key, "read_only": not rw, "title": "peagen-auto"}
    k = await _req("POST", f"/api/v1/repos/{slug}/{repo}/keys", json=body)
    return k["id"]
