"""ORM model re-exports.

This module provides a backward compatibility layer for the old
``peagen.models`` package. All ORM classes are imported from
:mod:`peagen.models` and re-exported under :mod:`peagen.orm`.
"""

from .. import models as _models
import pkgutil
import importlib
import sys

for _name in dir(_models):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_models, _name)

# Map submodules of peagen.models to peagen.orm
for _info in pkgutil.walk_packages(_models.__path__, _models.__name__ + "."):
    _mod = importlib.import_module(_info.name)
    _alias = _info.name.replace("peagen.models", __name__)
    sys.modules[_alias] = _mod

__all__ = [n for n in dir(_models) if not n.startswith("_")]
