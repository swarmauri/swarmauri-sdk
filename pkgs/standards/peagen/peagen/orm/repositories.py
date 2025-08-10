# peagen/orm/repositories.py
from __future__ import annotations

import os
import asyncio
from urllib.parse import urlparse
from typing import Any, Dict, Mapping, Optional

from autoapi.v2.tables import Base
from autoapi.v2.types import (
    Column,
    String,
    UniqueConstraint,
    relationship,
    HookProvider,
    Field,
)
from autoapi.v2.mixins import (
    GUIDPk,
    Timestamped,
    TenantBound,
    TenantPolicy,
    Ownable,
    OwnerPolicy,
    StatusMixin,
)
from autoapi.v2.hooks import Phase


class Repository(
    Base, GUIDPk, Timestamped, Ownable, TenantBound, StatusMixin, HookProvider
):
    __tablename__ = "repositories"
    __table_args__ = (
        UniqueConstraint("url"),
        {"schema": "peagen"},
    )

    # Request-only extras, flattened; accepted on all verbs, never persisted or returned
    __autoapi_request_extras__ = {
        "*": {
            # auth / remote-control inputs
            "github_pat":   (str | None, Field(default=None, exclude=True, description="GitHub PAT (write-only)")),
            "repo":         (str | None, Field(default=None, exclude=True, description="owner/name slug")),
            "description":  (str | None, Field(default=None, exclude=True)),
            "deploy_key":   (str | None, Field(default=None, exclude=True, description="Path to deploy key")),
            "path":         (str | None, Field(default=None, exclude=True, description="Local path (server-side)")),
            "remotes":      (dict[str, str] | None, Field(default=None, exclude=True)),
        }
    }

    __autoapi_owner_policy__: OwnerPolicy = OwnerPolicy.STRICT_SERVER
    __autoapi_tenant_policy__ = TenantPolicy.STRICT_SERVER

    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    default_branch = Column(String, default="main")
    commit_sha = Column(String(length=40), nullable=True)

    secrets = relationship(
        "RepoSecret", back_populates="repository", cascade="all, delete-orphan"
    )
    deploy_keys = relationship(
        "DeployKey", back_populates="repository", cascade="all, delete-orphan"
    )
    tasks = relationship(
        "Task",
        back_populates="repository",
        cascade="all, delete-orphan",
    )

    # ────────────────────────────────────────────────────────────────────
    # Helpers
    # -------------------------------------------------------------------
    @staticmethod
    def _slug_from_url(url: str) -> Optional[str]:
        if not url:
            return None
        if url.startswith("git@"):
            # git@github.com:owner/name.git
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
    def _get_params_map(ctx) -> Mapping[str, Any]:
        params = ctx["env"].params if ctx.get("env") else {}
        if hasattr(params, "model_dump"):
            try:
                params = params.model_dump()
            except Exception:
                pass
        return params or {}

    @classmethod
    def _normalize_init_spec(cls, params: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        """
        FLAT KEYS ONLY (no 'init' or legacy 'args'):
          - repo, github_pat, description, deploy_key, path, remotes
          - derive repo from url if not supplied
          - fallback PAT from env if not supplied
        """
        # accept flattened inputs
        repo = params.get("repo") or cls._slug_from_url(params.get("url", ""))
        if not repo:
            return None  # nothing to do

        spec: Dict[str, Any] = {
            "repo": repo,
            "pat": params.get("github_pat"),  # init_core expects 'pat'
            "description": params.get("description", ""),
            "deploy_key": params.get("deploy_key"),
            "path": params.get("path"),
            "remotes": params.get("remotes"),
        }
        # Keep PAT (may be None) so we can branch later; drop other Nones
        spec = {k: v for k, v in spec.items() if v is not None or k == "pat"}
        return spec

    # ────────────────────────────────────────────────────────────────────
    # Hooks for remote init
    # -------------------------------------------------------------------
    @classmethod
    async def _pre_create_collect_init(cls, ctx):
        """Capture and normalize any flat init payload before validation."""
        from peagen.gateway import log

        params = cls._get_params_map(ctx)
        spec = cls._normalize_init_spec(params)
        if not spec:
            return
        ctx["__repo_init__"] = spec
        log.info(
            "Repository.init(spec) captured: %s",
            {k: ("***" if k == "pat" else v) for k, v in spec.items()},
        )

    @classmethod
    async def _post_commit_maybe_init(cls, ctx):
        """Run remote init after commit, non-fatal to the main RPC."""
        from peagen.gateway import log
        from peagen.core import init_core

        spec = ctx.get("__repo_init__")
        if not spec:
            return

        log.info("Repository.init begin for repo=%s", spec.get("repo"))

        async def _run():
            if spec.get("pat"):
                # full remote init (GH repo + deploy key, optional local config)
                return await asyncio.to_thread(init_core.init_repo, **spec)1
            # no PAT: optionally just configure local remotes if provided
            remotes = spec.get("remotes") or {}
            path = spec.get("path")
            if not path or not remotes:
                return {"skipped": "no PAT and no local config provided"}
            return await asyncio.to_thread(init_core.configure_repo, path=path, remotes=remotes)

        try:
            init_result = await _run()
            log.info("Repository.init done: %s", init_result)
            # Attach a small summary to response (doesn't leak secrets)
            result = ctx.get("result")
            if isinstance(result, dict):
                result.setdefault("_init", init_result)
                ctx["result"] = result
            resp = ctx.get("response")
            if resp is not None and isinstance(resp.result, dict):
                resp.result.setdefault("_init", init_result)
        except Exception as exc:  # never fail the main transaction
            log.error("Repository.init failed: %s", exc)

    @classmethod
    async def _post_create(cls, ctx):
        from peagen.gateway import log
        created = cls._SRead.model_validate(ctx["result"], from_attributes=True)
        log.info("repository created: %s (%s)", created.name, created.url)
        ctx["result"] = created.model_dump()

    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        from autoapi.v2 import AutoAPI, Phase

        cls._SRead = AutoAPI.get_schema(cls, "read")

        # capture flat init params early; run remote work after commit
        api.register_hook(Phase.PRE_TX_BEGIN, model=cls, op="create")(cls._pre_create_collect_init)
        api.register_hook(Phase.POST_COMMIT,   model=cls, op="create")(cls._post_commit_maybe_init)
        api.register_hook(Phase.POST_COMMIT,   model=cls, op="create")(cls._post_create)


__all__ = ["Repository"]
