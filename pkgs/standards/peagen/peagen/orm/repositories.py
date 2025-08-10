# peagen/orm/repositories.py
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, Mapping

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

    # ─────────────────────── init-core integration ───────────────────────

    @staticmethod
    def _slug_from_url(url: str | None) -> str | None:
        """Return 'owner/repo' from common Git URLs or None if it can't be derived."""
        if not url:
            return None
        u = url.strip()

        # git@github.com:owner/repo.git
        if u.startswith("git@"):
            try:
                _, tail = u.split(":", 1)
                if tail.endswith(".git"):
                    tail = tail[:-4]
                parts = tail.strip("/").split("/")
                if len(parts) >= 2:
                    return "/".join(parts[-2:])
            except Exception:
                return None

        # https://github.com/owner/repo(.git)?  or  github.com/owner/repo
        for prefix in ("https://", "http://"):
            if u.startswith(prefix):
                u = u[len(prefix):]
        if u.startswith("github.com/"):
            u = u[len("github.com/"):]
        if u.endswith(".git"):
            u = u[:-4]
        parts = u.strip("/").split("/")
        if len(parts) >= 2:
            return "/".join(parts[-2:])
        return None

    @classmethod
    async def _pre_create_capture_init(cls, ctx):
        """
        Capture an optional init spec from the request params and stash it on ctx.
        Accepted payloads:
          { ..., "init": { "repo": "owner/name", "pat": "...", "deploy_key": "...",
                           "path": "...", "remotes": {...}, "description": "..." } }
        Legacy (Task-style):
          { ..., "args": { "kind": "repo", "repo": "...", "pat": "...", ... } }
        """
        from peagen.gateway import log

        params = ctx["env"].params if ctx.get("env") else {}
        if hasattr(params, "model_dump"):
            params = params.model_dump()

        if not isinstance(params, Mapping):
            return

        init_raw: Dict[str, Any] | None = None

        # Preferred: "init": {...}
        maybe_init = params.get("init")
        if isinstance(maybe_init, dict):
            init_raw = dict(maybe_init)

        # Legacy: "args": {"kind":"repo", ...}
        if init_raw is None:
            args = params.get("args")
            if isinstance(args, dict) and (args.get("kind") == "repo" or "repo" in args):
                init_raw = dict(args)

        if init_raw is None:
            return  # nothing to do

        # Derive repo slug if not provided explicitly
        repo_slug = init_raw.get("repo") or cls._slug_from_url(params.get("url"))
        if not repo_slug:
            log.info("Repository.init: no repo slug derivable; skipping init")
            return

        # PAT can come from init, or env (fallback), or you can later extend to fetch from secrets.
        pat = init_raw.get("pat") or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

        init_spec = {
            "repo": repo_slug,
            "pat": pat,
            "description": init_raw.get("description") or params.get("name") or "",
            "deploy_key": init_raw.get("deploy_key"),
            "path": Path(init_raw["path"]).expanduser() if init_raw.get("path") else None,
            "remotes": init_raw.get("remotes") or {},
        }

        # Stash for POST_COMMIT
        ctx["__repo_init__"] = init_spec
        log.info("Repository.init: captured init spec for %s (path=%s, remotes=%s)",
                 repo_slug, init_spec["path"], bool(init_spec["remotes"]))

    @classmethod
    async def _post_create_init_repo(cls, ctx):
        """
        After the repository row is committed, run init_core.init_repo in the background.
        """
        from peagen.gateway import log
        from peagen.core import init_core

        spec = ctx.get("__repo_init__")
        if not spec:
            return  # no init requested/captured

        created = cls._SRead.model_validate(ctx["result"], from_attributes=True)
        log.info("Repository.init: starting init_repo for %s (%s)", created.name, created.url)

        # Run blocking work off the event loop
        async def _run():
            try:
                # Decide between full init_repo or a lightweight configure_repo
                if spec.get("pat"):
                    res = await asyncio.to_thread(
                        init_core.init_repo,
                        repo=spec["repo"],
                        pat=spec["pat"],
                        description=spec.get("description", "") or "",
                        deploy_key=Path(spec["deploy_key"]).expanduser()
                                   if spec.get("deploy_key") else None,
                        path=spec.get("path"),
                        remotes=spec.get("remotes") or None,
                    )
                else:
                    # No PAT → just local configuration if we have enough info
                    if spec.get("path") and spec.get("remotes"):
                        res = await asyncio.to_thread(
                            init_core.configure_repo,
                            path=spec["path"],
                            remotes=spec["remotes"],
                        )
                    else:
                        log.info("Repository.init: missing PAT and insufficient local info; skipping")
                        return
                log.info("Repository.init: completed with result: %s", res)
            except Exception as exc:  # noqa: BLE001
                log.error("Repository.init: init failed for %s – %s", spec["repo"], exc)

        await _run()  # fire and wait; switch to `asyncio.create_task(_run())` if you prefer fire-and-forget

    # ───────────────────────── existing hooks ─────────────────────────

    @classmethod
    async def _post_create(cls, ctx):
        from peagen.gateway import log

        log.info("entering post_repository_create")
        created = cls._SRead.model_validate(ctx["result"], from_attributes=True)
        log.info("repository created: %s (%s)", created.name, created.url)
        ctx["result"] = created.model_dump()

    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        from autoapi.v2 import AutoAPI, Phase

        cls._SRead = AutoAPI.get_schema(cls, "read")
        # New hooks for init-core integration
        api.register_hook(Phase.PRE_TX_BEGIN, model=cls, op="create")(cls._pre_create_capture_init)
        api.register_hook(Phase.POST_COMMIT,   model=cls, op="create")(cls._post_create_init_repo)

        # Keep your existing post-create logging
        api.register_hook(Phase.POST_COMMIT, model=cls, op="create")(cls._post_create)


__all__ = ["Repository"]
