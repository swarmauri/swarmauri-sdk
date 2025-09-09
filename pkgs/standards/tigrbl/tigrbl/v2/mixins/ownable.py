from enum import Enum
import logging
from uuid import UUID

from ..hooks import Phase
from ..jsonrpc_models import create_standardized_error
from ..info_schema import check as _info_check
from ..types import Column, ForeignKey, PgUUID, declared_attr
from ..cfgs import AUTH_CONTEXT_KEY, INJECTED_FIELDS_KEY, USER_ID_KEY

log = logging.getLogger(__name__)


class OwnerPolicy(str, Enum):
    CLIENT_SET = "client"
    DEFAULT_TO_USER = "default"
    STRICT_SERVER = "strict"


def _infer_schema(cls, default: str = "public") -> str:
    args = getattr(cls, "__table_args__", None)
    if not args:
        return default
    if isinstance(args, dict):
        return args.get("schema", default)
    if isinstance(args, (tuple, list)):
        for elem in args:
            if isinstance(elem, dict) and "schema" in elem:
                return elem["schema"]
    return default


def _is_missing(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def _normalize_uuid(v):
    if isinstance(v, UUID):
        return v
    if isinstance(v, str):
        try:
            return UUID(v)
        except ValueError:
            return v
    return v


class Ownable:
    __tigrbl_owner_policy__: OwnerPolicy = OwnerPolicy.CLIENT_SET

    @declared_attr
    def owner_id(cls):
        pol = getattr(cls, "__tigrbl_owner_policy__", OwnerPolicy.CLIENT_SET)
        schema = _infer_schema(cls, default="public")

        tigrbl_meta = {}
        if pol != OwnerPolicy.CLIENT_SET:
            tigrbl_meta["disable_on"] = ["update", "replace"]
            tigrbl_meta["read_only"] = True

        _info_check(tigrbl_meta, "owner_id", cls.__name__)

        return Column(
            PgUUID(as_uuid=True),
            ForeignKey(f"{schema}.users.id"),
            nullable=False,
            index=True,
            info={"tigrbl": tigrbl_meta} if tigrbl_meta else {},
        )

    @classmethod
    def __tigrbl_register_hooks__(cls, api):
        pol = cls.__tigrbl_owner_policy__

        def _err(status: int, msg: str):
            http_exc, _, _ = create_standardized_error(status, message=msg)
            raise http_exc

        def _ownable_before_create(ctx):
            params = ctx["env"].params if ctx.get("env") else {}
            if hasattr(params, "model_dump"):
                # keep None so we can treat it as "missing" explicitly
                params = params.model_dump()

            auto_fields = ctx.get(AUTH_CONTEXT_KEY, {})
            user_id = auto_fields.get(USER_ID_KEY)
            provided = params.get("owner_id")
            missing = _is_missing(provided)

            log.info(
                "Ownable before_create policy=%s params=%s auto_fields=%s",
                pol,
                params,
                auto_fields,
            )

            if pol == OwnerPolicy.STRICT_SERVER:
                if user_id is None:
                    _err(400, "owner_id is required.")
                if not missing and _normalize_uuid(provided) != _normalize_uuid(
                    user_id
                ):
                    _err(400, "owner_id mismatch.")
                params["owner_id"] = user_id  # always enforce server value
            else:
                if missing:
                    params["owner_id"] = user_id
                else:
                    params["owner_id"] = _normalize_uuid(provided)

            ctx["env"].params = params
            print(f"\n🚧 ownable params: {ctx['env'].params}")

        def _ownable_before_update(ctx, obj):
            params = getattr(ctx.get("env"), "params", None)
            if not params or "owner_id" not in params:
                return

            if _is_missing(params.get("owner_id")):
                # treat None/"" as not provided → drop it
                params.pop("owner_id", None)
                ctx["env"].params = params
                return

            if pol != OwnerPolicy.CLIENT_SET:
                _err(400, "owner_id is immutable.")

            new_val = _normalize_uuid(params["owner_id"])
            auto_fields = ctx.get(INJECTED_FIELDS_KEY, {})
            user_id = _normalize_uuid(auto_fields.get(USER_ID_KEY))

            log.info(
                "Ownable before_update new_val=%s obj_owner=%s injected=%s",
                new_val,
                getattr(obj, "owner_id", None),
                user_id,
            )
            if (
                new_val != obj.owner_id
                and new_val != user_id
                and not ctx.get("is_admin")
            ):
                _err(403, "Cannot transfer ownership.")

        api.register_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="create")(
            _ownable_before_create
        )
        api.register_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="update")(
            _ownable_before_update
        )
