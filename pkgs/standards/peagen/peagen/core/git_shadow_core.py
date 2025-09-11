# peagen/core/git_shadow_core.py
"""Idempotent helpers for provisioning shadow (origin) and GitHub (mirror)."""

from __future__ import annotations

from typing import Any, Optional, Tuple
from urllib.parse import urlparse

import httpx

from peagen.defaults import (
    GIT_SHADOW_BASE,
    GIT_SHADOW_TOKEN,
)

# ───────────────────────────── helpers ─────────────────────────────


def _slug_from_url(url: str) -> Tuple[str, str]:
    """
    Accepts HTTPS or SSH GitHub URL and returns (owner, repo).
      https://github.com/<owner>/<repo>.git
      git@github.com:<owner>/<repo>.git
    """
    if not url:
        raise ValueError("url is required")
    if url.startswith("git@"):
        # git@github.com:owner/name(.git)
        part = url.split(":", 1)[1]
        owner, name = part.split("/")[-2], part.split("/")[-1]
    else:
        p = urlparse(url)
        segs = [s for s in (p.path or "").split("/") if s]
        if len(segs) < 2:
            raise ValueError("url must include owner/name")
        owner, name = segs[-2], segs[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return owner, name


async def _shadow_req(
    method: str,
    path: str,
    *,
    base: Optional[str] = None,
    token: Optional[str] = None,
    **kw,
) -> httpx.Response:
    """
    Low-level request to the shadow (Gitea-like) API.
    Raises for non-2xx/404. Lets caller decide 404 flow.
    """
    base = (base or GIT_SHADOW_BASE or "").rstrip("/")
    tok = (token or GIT_SHADOW_TOKEN or "").strip()
    if not base or not tok:
        raise RuntimeError(
            "git-shadow not configured (GIT_SHADOW_BASE / GIT_SHADOW_TOKEN)."
        )

    headers = kw.pop("headers", {})
    headers.setdefault("Authorization", f"token {tok}")
    headers.setdefault("Accept", "application/json")
    async with httpx.AsyncClient(base_url=base, timeout=30.0) as cli:
        r = await cli.request(method, path, headers=headers, **kw)
        return r


async def _gh_req(method: str, path: str, *, pat: str, **kw) -> httpx.Response:
    """
    Low-level request to GitHub REST v3.
    """
    if not pat:
        raise ValueError("github PAT required")
    headers = kw.pop("headers", {})
    headers.setdefault("Authorization", f"token {pat}")
    headers.setdefault("Accept", "application/vnd.github+json")
    async with httpx.AsyncClient(
        base_url="https://api.github.com", timeout=30.0
    ) as cli:
        r = await cli.request(method, path, headers=headers, **kw)
        return r


# ───────────────────────────── GitHub side ─────────────────────────


async def _gh_repo_exists(owner: str, repo: str, *, pat: str) -> bool:
    r = await _gh_req("GET", f"/repos/{owner}/{repo}", pat=pat)
    if r.status_code == 200:
        return True
    if r.status_code == 404:
        return False
    r.raise_for_status()
    return False  # unreachable


async def _gh_authed_login(*, pat: str) -> str:
    r = await _gh_req("GET", "/user", pat=pat)
    r.raise_for_status()
    return r.json()["login"]


async def _gh_ensure_repo(
    owner: str, repo: str, *, pat: str, description: str = ""
) -> None:
    if await _gh_repo_exists(owner, repo, pat=pat):
        return
    me = await _gh_authed_login(pat=pat)
    body = {"name": repo, "private": True, "description": description}
    if owner.lower() == me.lower():
        r = await _gh_req("POST", "/user/repos", pat=pat, json=body)
    else:
        r = await _gh_req("POST", f"/orgs/{owner}/repos", pat=pat, json=body)
    if r.status_code not in (201, 202):
        # 422 "name already exists" etc becomes a no-op
        if r.status_code == 422:
            return
        r.raise_for_status()


# ───────────────────────────── shadow side ─────────────────────────


async def _shadow_org_exists(owner: str) -> bool:
    r = await _shadow_req("GET", f"/api/v1/orgs/{owner}")
    if r.status_code == 200:
        return True
    if r.status_code == 404:
        return False
    r.raise_for_status()
    return False


async def _shadow_ensure_org(owner: str) -> None:
    if await _shadow_org_exists(owner):
        return
    # Create org – requires server token with permission.
    body = {"username": owner, "full_name": owner}
    r = await _shadow_req("POST", "/api/v1/orgs", json=body)
    if r.status_code not in (200, 201):
        # If already exists or not allowed, a 422/409 → treat as no-op
        if r.status_code in (409, 422):
            return
        r.raise_for_status()


async def _shadow_repo_exists(owner: str, repo: str) -> bool:
    r = await _shadow_req("GET", f"/api/v1/repos/{owner}/{repo}")
    if r.status_code == 200:
        return True
    if r.status_code == 404:
        return False
    r.raise_for_status()
    return False


async def _shadow_migrate_mirror(
    owner: str, repo: str, *, upstream_https: str, upstream_pat: str
) -> None:
    """
    Use the Gitea 'migrate' endpoint with mirror=True so shadow tracks GitHub.
    Safe to call if repo already exists: we'll skip earlier.
    """
    exists = await _shadow_repo_exists(owner, repo)
    if exists:
        return
    body = {
        "clone_addr": upstream_https,
        "repo_owner": owner,
        "repo_name": repo,
        "mirror": True,
        "private": True,
        # For private upstreams:
        "auth_token": upstream_pat,
        # optional: "mirror_interval": "1m"
    }
    r = await _shadow_req("POST", "/api/v1/repos/migrate", json=body)
    if r.status_code not in (201, 200):
        # If something else created it mid-flight, 409 → ok
        if r.status_code == 409:
            return
        r.raise_for_status()


# ───────────────────────────── orchestration ────────────────────────


async def ensure_repo_and_mirror(
    *, slug: str, github_pat: str, description: str = ""
) -> dict[str, Any]:
    """
    Idempotently ensure:
      • GitHub repo {slug}
      • Shadow mirror that tracks the GitHub repo
    Returns a tiny summary with both SSH remotes.
    """
    if not slug or "/" not in slug:
        raise ValueError("slug must be 'owner/repo'")
    owner, repo = slug.split("/", 1)

    # 1) Ensure GitHub side
    await _gh_ensure_repo(owner, repo, pat=github_pat, description=description)

    # 2) Ensure shadow org + mirror from GitHub (uses server token)
    await _shadow_ensure_org(owner)
    upstream_https = f"https://github.com/{owner}/{repo}.git"
    await _shadow_migrate_mirror(
        owner, repo, upstream_https=upstream_https, upstream_pat=github_pat
    )

    # 3) Build SSH remotes
    # Shadow SSH base derived from shadow HTTP base hostname (or configurable)
    host = urlparse(GIT_SHADOW_BASE).hostname or "git.peagen.com"
    origin = f"git@{host}:{slug}.git"
    upstream = f"git@github.com:{slug}.git"

    return {
        "origin": origin,
        "upstream": upstream,
        "created": slug,
    }
