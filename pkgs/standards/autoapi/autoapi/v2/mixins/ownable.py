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
            # Hide on write verbs (create/update/replace) and mark read-only
            autoapi_meta["disable_on"] = [
                "update",
                "replace",
            ]  # add "create" if desired
            autoapi_meta["read_only"] = True

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
            http_exc, _, _ = create_standardized_error(status, message=msg)
            raise http_exc

        # PRE-TX hooks ----------------------------------------------------
        def _ownable_before_create(ctx):
            try:
                params = ctx.params
            except KeyError:
                params = {}
                ctx.params = params
            user_id = ctx.user_id
            auto_fields = ctx.get("__autoapi_injected_fields__", set())
            if pol == OwnerPolicy.STRICT_SERVER:
                if user_id is None:
                    _err(400, "owner_id is required.")
                if "owner_id" in params and params["owner_id"] not in (
                    None,
                    user_id,
                ):
                    _err(400, "owner_id mismatch.")
                if "owner_id" in auto_fields or "owner_id" not in params:
                    params["owner_id"] = user_id
            else:
                params.setdefault("owner_id", user_id)

        def _ownable_before_update(ctx, obj):
            try:
                params = ctx.params
            except KeyError:
                return
            if "owner_id" not in params:
                return

            if pol != OwnerPolicy.CLIENT_SET:
                _err(400, "owner_id is immutable.")

            new_val = params["owner_id"]
            if new_val != obj.owner_id and new_val != ctx.user_id and not ctx.is_admin:
                _err(403, "Cannot transfer ownership.")

        api.register_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="create")(
            _ownable_before_create
        )
        api.register_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="update")(
            _ownable_before_update
        )
