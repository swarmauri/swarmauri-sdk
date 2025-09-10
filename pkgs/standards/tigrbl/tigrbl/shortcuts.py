# tigrbl/tigrbl/v3/shortcuts.py
from __future__ import annotations

from .app import shortcuts as app_shortcuts
from .api import shortcuts as api_shortcuts
from .engine import shortcuts as engine_shortcuts
from .specs import shortcuts as specs_shortcuts
from .table import shortcuts as table_shortcuts

from .app.shortcuts import *  # noqa: F401,F403
from .api.shortcuts import *  # noqa: F401,F403
from .engine.shortcuts import *  # noqa: F401,F403
from .specs.shortcuts import *  # noqa: F401,F403
from .table.shortcuts import *  # noqa: F401,F403

__all__ = [
    *app_shortcuts.__all__,
    *api_shortcuts.__all__,
    *engine_shortcuts.__all__,
    *specs_shortcuts.__all__,
    *table_shortcuts.__all__,
]
