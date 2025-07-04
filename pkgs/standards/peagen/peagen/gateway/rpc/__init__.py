from __future__ import annotations

import uuid
from typing import Any, Dict

from autoapi.v2 import AutoAPI

from peagen.orm import (
    Base,
    DeployKeyModel,
    PoolModel,
    SecretModel,
    TaskModel,
    WorkerModel,
)
from peagen.transport.jsonrpc_schemas import Status

from ..db import get_db

# Initialize AutoAPI with our models
api = AutoAPI(
    base=Base,
    include={TaskModel, WorkerModel, PoolModel, SecretModel, DeployKeyModel},
    get_db=lambda: get_db(),
)

# Common ORM columns for TaskModel
_ORM_COLUMNS = {c.name for c in TaskModel.__table__.columns}

# Create or get router for the API
api_router = api.router

# Create a dispatcher proxy that will be populated in initialize()
dispatcher = None

# Export for inclusion in FastAPI app
__all__ = [
    "api_router",
    "initialize",
    "api",
    "_normalise_submit_payload",
    "_prepare_orm_task",
]


# ------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------


def _normalise_submit_payload(raw: dict) -> Dict[str, Any]:
    """
    Ensure required fields exist and assign sensible defaults.
    This is the only validation performed at the RPC layer.
    """
    tenant_id = raw.get("tenant_id") or "default"
    try:
        uuid.UUID(str(tenant_id))
        tenant_uuid = str(tenant_id)
    except (ValueError, TypeError):
        tenant_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, str(tenant_id)).hex

    blob: Dict[str, Any] = {
        "id": raw.get("id") or uuid.uuid4().hex,
        "tenant_id": tenant_uuid,
        "git_reference_id": raw.get("git_reference_id"),
        "pool": raw.get("pool", "default"),
        "payload": raw.get("payload", {}),
        "status": raw.get("status", Status.queued),
        "note": raw.get("note", ""),
        "labels": raw.get("labels", []),
        "spec_hash": raw.get("spec_hash") or "",
        "last_modified": raw.get("last_modified"),
    }
    return blob


def _prepare_orm_task(task_blob: Dict[str, Any]) -> TaskModel:
    """Convert a task blob to an ORM model for database operations."""
    orm_fields = {
        k: task_blob[k]
        for k in _ORM_COLUMNS
        if k in task_blob and task_blob[k] is not None
    }

    # Convert string IDs to UUID objects
    for col in ("id", "tenant_id", "git_reference_id"):
        if col in orm_fields and isinstance(orm_fields[col], str):
            try:
                orm_fields[col] = uuid.UUID(str(orm_fields[col]))
            except ValueError:
                pass

    # Convert timestamp fields
    for ts in ("date_created", "last_modified"):
        val = orm_fields.get(ts)
        if isinstance(val, (int, float)):
            from datetime import datetime, timezone

            orm_fields[ts] = datetime.fromtimestamp(val, tz=timezone.utc)

    return TaskModel(**orm_fields)


# ------------------------------------------------------------------------
# Initialization function that gets called after gateway is fully loaded
# ------------------------------------------------------------------------


def initialize():
    """Initialize RPC methods and import modules."""
    # Get dispatcher after gateway is fully loaded
    from .. import dispatcher as gateway_dispatcher
    from .. import log

    # Make the dispatcher available globally
    global dispatcher
    dispatcher = gateway_dispatcher

    # # Register RPC methods
    def _register_rpc_methods():
        """Register AutoAPI operations with the dispatcher using auto-generated method names."""
        from ..db import Session

        # Get all method names directly from AutoAPI
        for api_method in api.rpc:
            # Using a factory to create a unique wrapper for each method
            def create_wrapper(method_name):
                async def wrapper(params):
                    async with Session() as session:
                        try:
                            result = await api.rpc[method_name](params, session)
                            return result
                        except Exception as e:
                            raise e

                return wrapper

            # Register using the auto-generated method name
            wrapper_func = create_wrapper(api_method)
            dispatcher._methods[api_method] = wrapper_func
            log.info(f"Registered AutoAPI method: {api_method}")

    _register_rpc_methods()

    # Import modules to ensure their hooks are registered
    # These imports are done at runtime after dispatcher is available
    from . import keys, pool, secrets, tasks, workers

    return keys, pool, secrets, tasks, workers
