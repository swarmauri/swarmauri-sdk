from enum import Enum

from ..hooks import Phase
from ..jsonrpc_models import create_standardized_error
from ..info_schema import check as _info_check
from ..types import Column, ForeignKey, PgUUID, declared_attr


class OwnerPolicy(str, Enum):
    CLIENT_SET = "client"
    DEFAULT_TO_USER = "default"
    STRICT_SERVER = "strict"


class Ownable:
    """
    Mix-in that injects an `owner_id` FK plus policy-driven schema + hook logic.
    Down-stream models override `__autoapi_owner_policy__`.
    """

    __autoapi_owner_policy__: OwnerPolicy = OwnerPolicy.CLIENT_SET

    # ────────────────────────────────────────────────────────────────────
    # Column is produced per-subclass via @declared_attr, so the correct
    # `info["autoapi"]` is present *before* AutoAPI builds any schemas.
    # -------------------------------------------------------------------
    @declared_attr
    def owner_id(cls):
        pol = getattr(cls, "__autoapi_owner_policy__", OwnerPolicy.CLIENT_SET)

        autoapi_meta = {}
        if pol != OwnerPolicy.CLIENT_SET:
            # Hide on update/replace but allow server-side injection on create
            autoapi_meta["disable_on"] = [
                "update",
                "replace",
            ]  # add "create" if desired

        # Validate the metadata keys
        _info_check(autoapi_meta, "owner_id", cls.__name__)

        return Column(
            PgUUID,
            ForeignKey("users.id"),
            nullable=False,
            index=True,
            info={"autoapi": autoapi_meta} if autoapi_meta else {},
        )

    # ────────────────────────────────────────────────────────────────────
    # Runtime hooks – unchanged, still need the `api` instance.
    # -------------------------------------------------------------------
    @classmethod
    def __autoapi_register_hooks__(cls, api):
        pol = cls.__autoapi_owner_policy__

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

            if pol != OwnerPolicy.CLIENT_SET:
                _err(400, "owner_id is immutable.")

            new_val = ctx.params["owner_id"]
            if new_val != obj.owner_id and new_val != ctx.user_id and not ctx.is_admin:
                _err(403, "Cannot transfer ownership.")

        api.register_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="create")(
            _before_create
        )
        api.register_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="update")(
            _before_update
        )
