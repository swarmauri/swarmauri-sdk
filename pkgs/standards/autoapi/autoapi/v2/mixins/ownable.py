from enum import Enum

from ..hooks import Phase
from ..jsonrpc_models import create_standardized_error
from ..info_schema import check as _info_check
from ..types import Column, ForeignKey, PgUUID


class OwnerPolicy(str, Enum):
    CLIENT_SET      = "client"
    DEFAULT_TO_USER = "default"
    STRICT_SERVER   = "strict"


class Ownable:
    """
    Mix-in that adds an `owner_id` FK plus policy-driven schema + hook logic.
    Downstream models override `__autoapi_owner_policy__`.
    """

    owner_id = Column(
        PgUUID,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        info={},  # the autoapi sub-dict will be populated in __init_subclass__
    )
    __autoapi_owner_policy__: OwnerPolicy = OwnerPolicy.CLIENT_SET

    # ────────────────────────────────────────────────────────────────────
    # 1) Column-level metadata is applied IMMEDIATELY so the schema
    #    generator sees the correct flags before caching.
    # -------------------------------------------------------------------
    @classmethod
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)

        pol = getattr(cls, "__autoapi_owner_policy__", OwnerPolicy.CLIENT_SET)

        # Adjust Column.info["autoapi"] once the subclass is declared
        col = getattr(cls, "owner_id", None)
        if col is None:  # defensive: mix-in not used as intended
            return

        meta = col.info.setdefault("autoapi", {})
        if pol != OwnerPolicy.CLIENT_SET:
            # Hide the field on *all* write verbs
            disable = set(meta.get("disable_on", []))
            disable.update({"create", "update", "replace"})
            meta["disable_on"] = list(disable)
            # Make it read-only from the client's perspective
            meta.setdefault("read_only", True)

        # Validate keys against autoapi.info_schema.VALID_KEYS
        _info_check(meta, "owner_id", cls.__name__)

    # ────────────────────────────────────────────────────────────────────
    # 2) Runtime hooks need the `api` instance and therefore stay here.
    # -------------------------------------------------------------------
    @classmethod
    def __autoapi_register_hooks__(cls, api):
        """
        Called once per model during AutoAPI bootstrap.
        Registers lifecycle hooks that enforce the chosen policy.
        """
        pol = cls.__autoapi_owner_policy__

        # Helper to raise typed HTTP errors
        def _err(status: int, msg: str):
            http_exc, _, _ = create_standardized_error(status, detail=msg)
            raise http_exc

        # PRE-TX hooks ----------------------------------------------------
        def _before_create(ctx):
            if "owner_id" in ctx.params and pol == OwnerPolicy.STRICT_SERVER:
                _err(400, "owner_id cannot be set explicitly.")
            ctx.params.setdefault("owner_id", ctx.user_id)

        def _before_update(ctx, obj):
            if "owner_id" not in ctx.params:
                return

            # DEFAULT / STRICT: immutable
            if pol != OwnerPolicy.CLIENT_SET:
                _err(400, "owner_id is immutable.")

            # CLIENT_SET: only owner or admin may change it
            new_val = ctx.params["owner_id"]
            if new_val != obj.owner_id and new_val != ctx.user_id and not ctx.is_admin:
                _err(403, "Cannot transfer ownership.")

        # Register hooks with decorator-style helper
        api.register_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="create")(
            _before_create
        )
        api.register_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="update")(
            _before_update
        )
