"""
peagen.gateway.services.base
============================

A minimal ABC that formalises the three-phase pattern used by gateway RPC
handlers:

    1. _pre_*   – transform JSON-RPC params  ➜  REST/CRUD payload
    2. _do_*    – perform Crouton REST calls
    3. _post_*  – transform REST/CRUD result ➜  JSON-RPC result

Sub-classes implement the *_pre_ / _do_ / _post_* hooks for the operations
they need (upload / fetch / delete, or any other verbs you invent).

The base class is *generic* over the Pydantic models you pass around in the
JSON-RPC layer, keeping full type hints.
"""

from __future__ import annotations

import abc
from typing import Any, Dict, Generic, TypeVar

from .crouton_factory import client as _crouton_sync

# --------------------------------------------------------------------------- #
# Type variables for strong typing                                            #
# --------------------------------------------------------------------------- #
UploadT = TypeVar("UploadT")   # JSON-RPC params  (e.g. UploadParams)
UploadR = TypeVar("UploadR")   # JSON-RPC result  (e.g. UploadResult)

FetchR  = TypeVar("FetchR")    # JSON-RPC result  (e.g. FetchResult)

DeleteT = TypeVar("DeleteT")   # JSON-RPC params  (e.g. DeleteParams)
DeleteR = TypeVar("DeleteR")   # JSON-RPC result  (e.g. DeleteResult)


# --------------------------------------------------------------------------- #
# Abstract service template                                                   #
# --------------------------------------------------------------------------- #
class ServiceBase(Generic[UploadT, UploadR, FetchR, DeleteT, DeleteR], metaclass=abc.ABCMeta):
    """
    ABC for gateway-side services that mediate between JSON-RPC and Crouton
    REST calls.  Override only the hooks you need.
    """

    # ----------- public façade --------------------------------------------
    def upload(self, params: UploadT) -> UploadR:
        payload = self._pre_u(params)
        raw     = self._do_u(_crouton_sync(), payload)
        return self._post_u(raw)

    def fetch(self) -> FetchR:
        raw = self._do_f(_crouton_sync())
        return self._post_f(raw)

    def delete(self, params: DeleteT) -> DeleteR:
        self._do_d(_crouton_sync(), params)
        return self._post_d()

    # ----------- hooks (override in subclass) -----------------------------
    # upload
    @abc.abstractmethod
    def _pre_u(self, params: UploadT) -> Dict[str, Any]: ...
    @abc.abstractmethod
    def _do_u(self, cli, payload: Dict[str, Any]) -> Dict[str, Any]: ...
    @abc.abstractmethod
    def _post_u(self, raw: Dict[str, Any]) -> UploadR: ...

    # fetch
    def _do_f(self, cli):                      # default implementation
        return cli.get(self._resource())
    @abc.abstractmethod
    def _post_f(self, raw: Any) -> FetchR: ...

    # delete
    @abc.abstractmethod
    def _do_d(self, cli, params: DeleteT) -> None: ...
    @abc.abstractmethod
    def _post_d(self) -> DeleteR: ...

    # resource helper
    @staticmethod
    @abc.abstractmethod
    def _resource() -> str:
        """Return the REST path segment for the underlying CRUD resource."""
