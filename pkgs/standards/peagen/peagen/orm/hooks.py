# peagen/orm/__init__.py  (add near the bottom of the file)
from autoapi.v2.hooks import Phase, _Hook
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from . import Task, Secret, DeployKey, Repository   # ← your ORM classes

_TARGET_MODELS = {Task, Secret, DeployKey}
# _ALLOWED_VERBS = {"create", "update"}               # ignore read/list/delete


class _ResolveRepositoryHook(_Hook):
    """
    Slug-or-ID repository resolver / consistency guard
    for Task, Secret, and DeployKey submissions.
    """
    phase = Phase.PRE_TX_BEGIN
    model = None          # make it globally visible; we'll filter manually

    def __call__(self, ctx):
        # ── 1. apply only to our tables & verbs ─────────────────────────
        if ctx.model not in _TARGET_MODELS:
            return
        # if ctx.op.verb not in _ALLOWED_VERBS:
        #     return

        data = ctx.in_.model_dump()
        db   = ctx.db

        # ── 2. slug-only submission: resolve repository_id ──────────────
        if data.get("repository_id") is None:
            try:
                repo_id = (
                    db.query(Repository.id)
                      .filter_by(tenant_id=data["tenant_id"], slug=data["repo"])
                      .one()[0]
                )
            except NoResultFound:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"Unknown repository slug '{data['repo']}' "
                        f"for tenant {data['tenant_id']}"
                    ),
                )
            ctx.in_.repository_id = repo_id  # mutate inbound Pydantic model

        # ── 3. both fields supplied → verify they match ─────────────────
        else:
            repo = db.get(Repository, data["repository_id"])
            if repo is None or repo.slug != data["repo"]:
                raise HTTPException(
                    status_code=422,
                    detail="repository_id does not match repo slug",
                )
