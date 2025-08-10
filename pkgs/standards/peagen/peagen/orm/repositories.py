# peagen/orm/repositories.py
from __future__ import annotations

import os
import asyncio
from urllib.parse import urlparse
from typing import Any, Dict, Mapping, Optional

from autoapi.v2.tables import Base
from autoapi.v2.types import (
    Column, String, UniqueConstraint, relationship, HookProvider, Field,
)
from autoapi.v2.mixins import (
    GUIDPk, Timestamped, TenantBound, TenantPolicy, Ownable, OwnerPolicy, StatusMixin,
)
from autoapi.v2.hooks import Phase
from autoapi.v2.jsonrpc_models import create_standardized_error


class Repository(
    Base, GUIDPk, Timestamped, Ownable, TenantBound, StatusMixin, HookProvider
):
    __tablename__ = "repositories"
    __table_args__ = (UniqueConstraint("url"), {"schema": "peagen"})

    # Request-only extras: accepted on all verbs, never persisted or returned
    __autoapi_request_extras__ = {
        "*": {
            "github_pat":  (str | None, Field(default=None, exclude=True, description="GitHub PAT (write-only)")),
            "repo":        (str | None, Field(default=None, exclude=True, description="owner/name slug")),
            "description": (str | None, Field(default=None, exclude=True)),
            "deploy_key":  (str | None, Field(default=None, exclude=True, description="Path to deploy key")),
            "path":        (str | None, Field(default=None, exclude=True, description="Local path for server-side git")),
            "remotes":     (dict[str, str] | None, Field(default=None, exclude=True)),
        }
    }

    __autoapi_owner_policy__: OwnerPolicy = OwnerPolicy.STRICT_SERVER
    __autoapi_tenant_policy__ = TenantPolicy.STRICT_SERVER

    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    default_branch = Column(String, default="main")
    commit_sha = Column(String(length=40), nullable=True)

    secrets = relationship("RepoSecret", back_populates="repository", cascade="all, delete-orphan")
    deploy_keys = relationship("DeployKey", back_populates="repository", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="repository", cascade="all, delete-orphan")

    # ───────────────────────── helpers ─────────────────────────
    @staticmethod
    def _slug_from_url(url: str) -> Optional[str]:
        if not url:
            return None
        if url.startswith("git@"):
            try:
                host_and_path = url.split(":", 1)[1]
                parts = host_and_path.split("/")
            except Exception:
                return None
        else:
            try:
                p = urlparse(url)
                parts = [seg for seg in (p.path or "").split("/") if seg]
            except Exception:
                return None
        if len(parts) < 2:
            return None
        owner, name = parts[-2], parts[-1]
        if name.endswith(".git"):
            name = name[:-4]
        return f"{owner}/{name}"

    @staticmethod
    def _params_map(ctx) -> Mapping[str, Any]:
        params = ctx["env"].params if ctx.get("env") else {}
        if hasattr(params, "model_dump"):
            try:
                params = params.model_dump()
            except Exception:
                pass
        return params or {}

    @staticmethod
    def _shadow_remote(repo: str) -> str:
        # Prefer runtime settings; fallback to env
        try:
            from peagen.gateway import settings  # configured in gateway
            base = getattr(settings, "git_shadow_ssh_base", None)
        except Exception:
            base = None
        base = base or os.getenv("GIT_SHADOW_SSH_BASE")  # e.g. "git@git-shadow.example.com:"
        if not base:
            raise RuntimeError("git shadow base not configured (git_shadow_ssh_base / GIT_SHADOW_SSH_BASE).")
        return f"{base}{repo}.git" if base.endswith(":") else f"{base.rstrip('/')}/{repo}.git"

    # ─────────────── PRE_HANDLER #1: validate/normalize ───────────────
    @classmethod
    async def _pre_handler_validate_init(cls, ctx):
        from peagen.gateway import log
        params = cls._params_map(ctx)

        repo = params.get("repo") or cls._slug_from_url(params.get("url", ""))
        gh_pat_raw = params.get("github_pat")
        path = params.get("path")

        # Require both steps for this flow: GitHub + shadow (needs both PAT and path)
        if not repo:
            http_exc, *_ = create_standardized_error(400, message="repo (or derivable url) is required")
            raise http_exc
        if not gh_pat_raw or not str(gh_pat_raw).strip():
            http_exc, *_ = create_standardized_error(400, message="github_pat is required for remote init")
            raise http_exc
        if not path or not str(path).strip():
            http_exc, *_ = create_standardized_error(400, message="path is required to configure local repository")
            raise http_exc

        gh_pat = str(gh_pat_raw).strip()
        try:
            origin = cls._shadow_remote(repo)
        except Exception as exc:
            http_exc, *_ = create_standardized_error(500, message=f"git shadow misconfigured: {exc}")
            raise http_exc

        upstream = f"git@github.com:{repo}.git"

        # Persist only a sanitized, working spec on the ctx (never to DB/response)
        ctx["__repo_init_spec__"] = {
            "repo": repo,
            "pat": gh_pat,                        # transient only
            "description": params.get("description", "") or "",
            "deploy_key": params.get("deploy_key"),
            "path": path,
            "remotes": {"origin": origin, "upstream": upstream},
        }
        log.info("Repository.init spec (sanitized) prepared for %s", repo)

    # ─────────────── PRE_HANDLER #2: perform remote init ───────────────
    @classmethod
    async def _pre_handler_run_init(cls, ctx):
        from peagen.gateway import log
        from peagen.core import init_core

        spec = ctx.get("__repo_init_spec__")
        if not spec:
            return  # nothing to do

        log.info("Repository.init running for repo=%s", spec["repo"])

        # Heavy I/O off the event loop
        try:
            result = await asyncio.to_thread(init_core.init_repo, **spec)
        except Exception as exc:
            http_exc, *_ = create_standardized_error(502, message=f"remote init failed: {exc}")
            raise http_exc

        # Stash a redacted summary for the response
        redacted = {
            "created": result.get("created"),
            "configured": result.get("configured"),
            "remotes": result.get("remotes"),
            "next": result.get("next"),
        }
        ctx["__repo_init_result__"] = redacted
        log.info("Repository.init completed for %s: %s", spec["repo"], redacted)

    # ─────────────── POST_RESPONSE: attach tiny summary ────────────────
    @classmethod
    async def _post_response_attach_init(cls, ctx):
        res = ctx.get("__repo_init_result__")
        if not res:
            return
        # attach under `_init` without secrets
        if isinstance(ctx.get("result"), dict):
            ctx["result"].setdefault("_init", res)
        if ctx.get("response") is not None and isinstance(ctx["response"].result, dict):
            ctx["response"].result.setdefault("_init", res)

    # ─────────────── register hooks ────────────────────────────────────
    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        from autoapi.v2 import AutoAPI

        cls._SRead = AutoAPI.get_schema(cls, "read")

        # PRE_HANDLER: validate+normalize, then perform remote init; aborts on failure
        api.register_hook(Phase.PRE_HANDLER, model=cls, op="create")(cls._pre_handler_validate_init)
        api.register_hook(Phase.PRE_HANDLER, model=cls, op="create")(cls._pre_handler_run_init)

        # Optional: keep your existing post-create normalization if desired
        # (now happens after commit as before)
        # api.register_hook(Phase.POST_COMMIT, model=cls, op="create")(cls._post_create)

        # Attach small summary to the response (non-fatal if missing)
        api.register_hook(Phase.POST_RESPONSE, model=cls, op="create")(cls._post_response_attach_init)


__all__ = ["Repository"]
