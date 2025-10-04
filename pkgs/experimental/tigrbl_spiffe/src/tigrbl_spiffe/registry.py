from __future__ import annotations
from typing import Any
from tigrbl import include_model
from .tables.svid import Svid
from .tables.registrar import Registrar
from .tables.bundle import Bundle
from .tables.workload import Workload

def register(app: Any) -> None:
    include_model(Svid)
    include_model(Registrar)
    include_model(Bundle)
    include_model(Workload)
