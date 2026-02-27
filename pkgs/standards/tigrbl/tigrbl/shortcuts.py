# tigrbl/tigrbl/v3/shortcuts.py
from __future__ import annotations

from .app import shortcuts as app_shortcuts
from .shortcuts import router as router_shortcuts
from .shortcuts import engine as engine_shortcuts
from .specs import shortcuts as specs_shortcuts
from .shortcuts import table as table_shortcuts

from .app.shortcuts import *  # noqa: F401,F403
from .shortcuts.router import *  # noqa: F401,F403
from .shortcuts.engine import *  # noqa: F401,F403
from .specs.shortcuts import *  # noqa: F401,F403
from .shortcuts.table import *  # noqa: F401,F403

__all__ = [
    *app_shortcuts.__all__,
    *router_shortcuts.__all__,
    *engine_shortcuts.__all__,
    *specs_shortcuts.__all__,
    *table_shortcuts.__all__,
]
