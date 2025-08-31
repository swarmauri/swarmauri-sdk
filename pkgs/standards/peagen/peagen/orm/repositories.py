# peagen/orm/repositories.py
from __future__ import annotations

from urllib.parse import urlparse
from typing import Any, Mapping, Optional, TYPE_CHECKING

from autoapi.v3.orm.tables import Base
from autoapi.v3.types import (
    String,
    UniqueConstraint,
    relationship,
    Mapped,
)
from autoapi.v3.orm.mixins import (
    GUIDPk,
    Timestamped,
    TenantBound,
    TenantPolicy,
    Ownable,
    OwnerPolicy,
    StatusMixin,
)
from autoapi.v3.runtime.errors import create_standardized_error
from autoapi.v3.specs import F, IO, S, acol, vcol
from autoapi.v3 import hook_ctx

if TYPE_CHECKING:  # pragma: no cover
    from .secrets import RepoSecret
    from .keys import DeployKey
    from .tasks import Task


class Repository(Base, GUIDPk, Timestamped, Ownable, TenantBound, StatusMixin):
    __tablename__ = "repositories"
    __table_args__ = (
        UniqueConstraint("url"),
        {"schema": "peagen", "extend_existing": True},
    )

    __autoapi_owner_policy__: OwnerPolicy = OwnerPolicy.STRICT_SERVER
    __autoapi_tenant_policy__: TenantPolicy = TenantPolicy.STRICT_SERVER

    name: Mapped[str] = acol(storage=S(String, nullable=False))
    url: Mapped[str] = acol(storage=S(String, unique=True, nullable=False))
    default_branch: Mapped[str] = acol(storage=S(String, default="main"))
    commit_sha: Mapped[str | None] = acol(storage=S(String(length=40), nullable=True))
    github_pat: str | None = vcol(
        field=F(
            py_type=str | None,
            constraints={
                "description": "GitHub PAT (write-only)",
                "exclude": True,
            },
            required_in=("create",),
        ),
        io=IO(in_verbs=("create", "update", "replace", "delete")),
    )

    secrets: Mapped[list["RepoSecret"]] = relationship(
        "RepoSecret", back_populates="repository", cascade="all, delete-orphan"
    )
    deploy_keys: Mapped[list["DeployKey"]] = relationship(
        "DeployKey", back_populates="repository", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="repository", cascade="all, delete-orphan"
    )

    # ─────────────── helpers ───────────────

    @staticmethod
    def _params(ctx) -> Mapping[str, Any]:
        params = ctx["env"].params if ctx.get("env") else {}
        if hasattr(params, "model_dump"):
            try:
                params = params.model_dump()
            except Exception:
                pass
        return params or {}

    @staticmethod
    def _slug_from_url(url: str) -> Optional[str]:
        if not url:
            return None
        if url.startswith("git@"):
            try:
                part = url.split(":", 1)[1]
                owner, name = part.split("/")[-2], part.split("/")[-1]
            except Exception:
                return None
        else:
            try:
                p = urlparse(url)
                segs = [s for s in (p.path or "").split("/") if s]
                if len(segs) < 2:
                    return None
                owner, name = segs[-2], segs[-1]
            except Exception:
                return None
        if name.endswith(".git"):
            name = name[:-4]
        return f"{owner}/{name}"

    # ─────────────── PRE_HANDLER (provision remotes) ───────────────

    @hook_ctx(ops="create", phase="PRE_HANDLER")
    async def _pre_handler_provision(cls, ctx):
        """
        Before DB create: ensure both remotes exist and are linked
        (GitHub via caller PAT, shadow mirror via server token).
        """
        from peagen.core import git_shadow_core as gsc

        p = cls._params(ctx)
        slug = cls._slug_from_url(p.get("url", ""))
        gh_pat = (p.get("github_pat") or "").strip()

        if not slug:
            http_exc, *_ = create_standardized_error(
                400, message="url must include owner/name"
            )
            raise http_exc
        if not gh_pat:
            http_exc, *_ = create_standardized_error(
                400, message="github_pat is required"
            )
            raise http_exc

        # Optional description from name
        desc = (p.get("name") or "").strip()

        try:
            result = await gsc.ensure_repo_and_mirror(
                slug=slug, github_pat=gh_pat, description=desc
            )
        except Exception as exc:
            # Map provisioning failure to 502 (bad upstream)
            http_exc, *_ = create_standardized_error(
                502, message=f"remote provisioning failed: {exc}"
            )
            raise http_exc
        finally:
            # scrub the PAT as soon as possible
            if isinstance(p, dict):
                p.pop("github_pat", None)
            ctx.get("env").params = p

        # park a tiny (redacted) summary; attached after handler
        ctx["__repo_init__"] = {
            "origin": result.get("origin"),
            "upstream": result.get("upstream"),
            "created": result.get("created"),
        }

    @hook_ctx(ops="create", phase="POST_RESPONSE")
    async def _post_response_attach(cls, ctx):
        summary = ctx.get("__repo_init__")
        if not summary:
            return
        if isinstance(ctx.get("result"), dict):
            ctx["result"].setdefault("_init", summary)
        if ctx.get("response") is not None and isinstance(ctx["response"].result, dict):
            ctx["response"].result.setdefault("_init", summary)

    # ─────────────── register hooks ───────────────

    # hooks registered via @hook_ctx


__all__ = ["Repository"]
