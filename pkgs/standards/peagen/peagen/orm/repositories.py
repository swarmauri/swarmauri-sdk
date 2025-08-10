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
    """
    A code or data repository that lives under a tenant.
    – parent of Secrets & DeployKeys
    """

    __tablename__ = "repositories"
    __table_args__ = (
        UniqueConstraint("url"),
        {"schema": "peagen"},
    )

    # Add request extras to all verbs via "*" wildcard
    __autoapi_request_extras__ = {
        "*": {
            "github_pat": (str | None, Field(default=None, exclude=True, description="GitHub PAT (write-only)")),
        }
    }


    # The request must not contain owner_id. The server injects the caller’s user_id automatically.
    __autoapi_owner_policy__: OwnerPolicy = OwnerPolicy.STRICT_SERVER
    # The request must not contain tenant_id. The server injects the caller’s tenant_id automatically.
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
        """
        Extract `<owner>/<name>` from a Git URL or HTTPS URL.
        Handles: https://github.com/owner/name(.git), git@github.com:owner/name(.git)
        """
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
        Accept either:
          • params["init"] = {repo, pat, description?, deploy_key?, path?, remotes?}
          • legacy: params["args"] with args["kind"] == "repo", carrying same keys
        Derive `repo` from `url` if missing. Pull `pat` from env if absent.
        """
        init_spec = None

        if isinstance(params.get("init"), dict):
            init_spec = dict(params["init"])
        else:
            args = params.get("args")
            if isinstance(args, dict) and args.get("kind") == "repo":
                init_spec = dict(args)

        if not init_spec:
            return None

        # Normalize keys
        repo = init_spec.get("repo") or cls._slug_from_url(params.get("url", ""))
        pat = init_spec.get("pat") or os.getenv("PEAGEN_GH_PAT") or os.getenv("GITHUB_PAT")
        description = init_spec.get("description", "")
        deploy_key = init_spec.get("deploy_key")
        path = init_spec.get("path")  # may be None on “remote” usage
        remotes = init_spec.get("remotes")

        if not repo:
            # Without a repo slug we can’t do remote init; silently skip
            return None

        out = {
            "repo": repo,
            "pat": pat,
            "description": description,
            "deploy_key": deploy_key,
            "path": path,
            "remotes": remotes,
        }
        # Drop Nones except pat (we want to detect “no PAT” later)
        return {k: v for k, v in out.items() if v is not None or k == "pat"}

    # ────────────────────────────────────────────────────────────────────
    # Hooks for remote init
    # -------------------------------------------------------------------
    @classmethod
    async def _pre_create_collect_init(cls, ctx):
        """
        Capture and normalize any init payload from the RPC request and stash it
        on the context. This runs before validation drops unknown fields.
        """
        from peagen.gateway import log

        params = cls._get_params_map(ctx)
        spec = cls._normalize_init_spec(params)
        if not spec:
            return
        ctx["__repo_init__"] = spec
        log.info("Repository.init spec captured: %s", {k: ('***' if k == 'pat' else v) for k, v in spec.items()})

    @classmethod
    async def _post_commit_maybe_init(cls, ctx):
        """
        If an init spec was captured, run repo init after the DB row is created.
        - If PAT provided: init_repo (creates GH repo, key, optional push)
        - Else if remotes provided: configure_repo
        """
        from peagen.gateway import log
        from peagen.core import init_core

        spec = ctx.get("__repo_init__")
        if not spec:
            return

        # Defensive copy; keep PAT masked in logs
        log.info("Repository.init begin for repo=%s", spec.get("repo"))

        async def _run():
            if spec.get("pat"):
                return await asyncio.to_thread(init_core.init_repo, **spec)
            # Fallback path: just configure remotes (server-side)
            remotes = spec.get("remotes") or {}
            path = spec.get("path")
            if not path:
                # Nothing to configure without a working directory
                return {"skipped": "no path/remotes for configure_repo"}
            return await asyncio.to_thread(init_core.configure_repo, path=path, remotes=remotes)

        try:
            init_result = await _run()
            log.info("Repository.init done: %s", init_result)
            # Attach a lightweight summary onto the response
            result = ctx.get("result")
            if result and isinstance(result, dict):
                result.setdefault("_init", init_result)
                ctx["result"] = result
            resp = ctx.get("response")
            if resp is not None and isinstance(resp.result, dict):
                resp.result.setdefault("_init", init_result)
        except Exception as exc:  # don’t fail the main RPC
            log.error("Repository.init failed: %s", exc)

    # ────────────────────────────────────────────────────────────────────
    # Existing post-create (kept intact, now attaches after commit too)
    # -------------------------------------------------------------------
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

        # Capture init payload early (before RPC adapter validation strips it)
        api.register_hook(Phase.PRE_TX_BEGIN, model=cls, op="create")(cls._pre_create_collect_init)
        # Do the heavy work only after commit
        api.register_hook(Phase.POST_COMMIT,   model=cls, op="create")(cls._post_commit_maybe_init)
        # Keep your existing post-create logging/normalization
        api.register_hook(Phase.POST_COMMIT,   model=cls, op="create")(cls._post_create)

__all__ = ["Repository"]
