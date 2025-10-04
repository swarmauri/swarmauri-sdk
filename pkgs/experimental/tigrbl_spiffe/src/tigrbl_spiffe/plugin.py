from __future__ import annotations

from typing import Any, Iterable

from .tables.svid import Svid
from .tables.registrar import Registrar
from .tables.bundle import Bundle
from .tables.workload import Workload

from .identity.svid_validator import SvidValidator
from .identity.rotation_policy import RotationPolicy
from .tls.context import TlsHelper
from .middleware.identity import InjectSpiffeExtras
from .middleware.authn import SpiffeAuthn
from .middleware.tls import AttachTlsContexts
from .adapters import Endpoint, TigrblClientAdapter

from tigrbl import include_model

class TigrblSpiffePlugin:
    def __init__(self, *, workload_endpoint: Endpoint, server_endpoint: Endpoint|None=None):
        self._cfg = {
            "workload_endpoint": workload_endpoint,
            "server_endpoint": server_endpoint or workload_endpoint,
        }
        self._adapter = TigrblClientAdapter()
        self._validator = SvidValidator()
        self._rotation = RotationPolicy()
        self._tls_helper = TlsHelper(self._adapter, self._cfg)

    def supports(self) -> set[str]:
        from .supports import CAPABILITIES
        return CAPABILITIES

    def install(self, app: Any) -> None:
        include_model(Svid)
        include_model(Registrar)
        include_model(Bundle)
        include_model(Workload)
        # Wire middleware (order: identity extras -> authn -> tls)
        app.use(InjectSpiffeExtras(self._adapter, type("Cfg",(object,),self._cfg)))
        app.use(SpiffeAuthn(self._validator))
        app.use(AttachTlsContexts(self._tls_helper))

    # convenience for ops/hooks expecting ctx extras
    def ctx_extras(self) -> dict[str, Any]:
        return {
            "spiffe_adapter": self._adapter,
            "spiffe_config": type("Cfg",(object,),self._cfg),
            "rotation_policy": self._rotation,
            "svid_validator": self._validator,
            "tls_helper": self._tls_helper,
        }
