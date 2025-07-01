"""
peagen.gateway.rpc.keys
-----------------------

JSON-RPC ⇆ Crouton bridge for managing trusted public keys.

Public contract (unchanged)
~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Params  : UploadParams · FetchParams · DeleteParams
* Results : UploadResult · FetchResult · DeleteResult
"""

from __future__ import annotations

import os
import uuid
from typing import Any, Dict, List

from pgpy import PGPKey

from .. import dispatcher, log, TRUSTED_USERS                      # gateway globals
from peagen.transport.jsonrpc_schemas.keys import (                # JSON-RPC IO
    KEYS_UPLOAD, KEYS_FETCH, KEYS_DELETE,
    UploadParams, UploadResult,
    FetchResult,
    DeleteParams, DeleteResult,
)

# ──────────────────────────  shared helpers  ──────────────────────────────
from peagen.gateway.services.base import ServiceBase
from peagen.gateway.services.crouton_factory import client as _crouton

# REST resource segment (generated CRUD router exposes /deploy_keys)
_RESOURCE = "deploy_keys"


# ──────────────────────────  concrete service  ────────────────────────────
class _KeyService(
    ServiceBase[
        UploadParams, UploadResult,
        FetchResult,
        DeleteParams, DeleteResult
    ]
):
    """
    Implements the three-phase pattern for *Keys* operations.
    """

    # --- upload ----------------------------------------------------------
    def _pre_u(self, params: UploadParams) -> Dict[str, Any]:
        """JSON-RPC ➜ DeployKeyCreate payload."""
        pgp = PGPKey(); pgp.parse(params.public_key)

        return {
            # ORM columns
            "id":          str(uuid.uuid4()),
            "user_id":     None,                     # server will resolve to caller
            "name":        f"{pgp.fingerprint[:16]}-key",
            "public_key":  params.public_key,
            "secret_id":   None,
            "read_only":   True,
            # helper field retained for _post_u
            "_fp":         pgp.fingerprint,
        }

    def _do_u(self, cli, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Persist via REST.  Duplicate keys are idempotent."""
        try:
            return cli.post(_RESOURCE, payload)
        except ValueError as err:                     # 409 Conflict handled as idempotent
            # fall-back: locate existing row by public_key
            rows: List[Dict[str, Any]] = cli.get(_RESOURCE, filters={"public_key": payload["public_key"]})
            if rows:
                return rows[0]
            raise err

    def _post_u(self, raw: Dict[str, Any]) -> UploadResult:
        fp = PGPKey().parse(raw["public_key"]).fingerprint
        TRUSTED_USERS[fp] = raw["public_key"]
        log.info("key persisted (fingerprint = %s)", fp)
        return UploadResult(fingerprint=fp)

    # --- fetch -----------------------------------------------------------
    def _post_f(self, raw: Any) -> FetchResult:
        """Convert list[DeployKeyRead] ➜ {fingerprint: public_key}."""
        mapping = {
            PGPKey().parse(row["public_key"]).fingerprint: row["public_key"]
            for row in raw
        }
        TRUSTED_USERS.clear(); TRUSTED_USERS.update(mapping)
        return FetchResult(keys=mapping)

    # --- delete ----------------------------------------------------------
    def _do_d(self, cli, params: DeleteParams) -> None:
        # locate key by fingerprint
        rows = cli.get(_RESOURCE)                     # minimal dataset; could add pagination
        for row in rows:
            if PGPKey().parse(row["public_key"]).fingerprint == params.fingerprint:
                cli.delete(_RESOURCE, item_id=row["id"])
                return
        raise ValueError(f"fingerprint {params.fingerprint} not found")

    def _post_d(self) -> DeleteResult:
        return DeleteResult(ok=True)

    # helper
    @staticmethod
    def _resource() -> str:
        return _RESOURCE


# ──────────────────────────  RPC bindings  ────────────────────────────────
_srv = _KeyService()

@dispatcher.method(KEYS_UPLOAD)
async def keys_upload(params: UploadParams) -> dict:
    return _srv.upload(params).model_dump()


@dispatcher.method(KEYS_FETCH)
async def keys_fetch() -> dict:
    return _srv.fetch().model_dump()


@dispatcher.method(KEYS_DELETE)
async def keys_delete(params: DeleteParams) -> dict:
    return _srv.delete(params).model_dump()
