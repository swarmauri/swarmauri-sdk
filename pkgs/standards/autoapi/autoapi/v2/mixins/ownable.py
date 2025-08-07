from enum import Enum

from ..hooks import Phase
from ..jsonrpc_models import create_standardized_error   # <── built-in helper
from ..types import Column, ForeignKey, PgUUID

class OwnerPolicy(str, Enum):
    CLIENT_SET      = "client"
    DEFAULT_TO_USER = "default"
    STRICT_SERVER   = "strict"

class Ownable:
    """
    Mix-in for an `owner_id` column with three selectable behaviours.
    Each table sets `__autoapi_owner_policy__`.
    """

    owner_id = Column(
        PgUUID,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        info={},                    # schema flags will be inserted here
    )
    __autoapi_owner_policy__: OwnerPolicy = OwnerPolicy.CLIENT_SET

    # ────────────────────────────────────────────────────────────────────
    @classmethod
    def __autoapi_register_hooks__(cls, api):
        """
        Runs once during AutoAPI bootstrap.
        Tweaks schema flags and registers lifecycle hooks.
        """
        pol = cls.__autoapi_owner_policy__

        # 1️⃣  Schema flags so Pydantic ignores owner_id when appropriate
        col_info = cls.__table__.c.owner_id.info
        if pol != OwnerPolicy.CLIENT_SET:
            col_info.setdefault("no_create", True)
            col_info.setdefault("no_update", True)

        # 2️⃣  Helper to raise typed HTTP errors
        def _err(status: int, msg: str):
            http_exc, _, _ = create_standardized_error(status, detail=msg)
            raise http_exc

        # 3️⃣  Hooks ----------------------------------------------------------
        def _before_create(ctx):
            if "owner_id" in ctx.params and pol == OwnerPolicy.STRICT_SERVER:
                _err(400, "owner_id cannot be set explicitly.")
            ctx.params.setdefault("owner_id", ctx.user_id)

        def _before_update(ctx, obj):
            if "owner_id" in ctx.params:
                if pol != OwnerPolicy.CLIENT_SET:
                    _err(400, "owner_id is immutable.")
                new_val = ctx.params["owner_id"]
                if new_val != obj.owner_id and new_val != ctx.user_id and not ctx.is_admin:
                    _err(403, "Cannot transfer ownership.")

        api.add_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="create", fn=_before_create)
        api.add_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="update", fn=_before_update)
