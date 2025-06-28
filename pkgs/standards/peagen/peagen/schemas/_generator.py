from __future__ import annotations

import inspect
from datetime import datetime
from typing import Any, Optional

from pydantic import create_model

from peagen.orm import __all__ as model_names
from peagen.orm import base as base_module

__all__ = []


def _python_type(column: Any) -> type:
    try:
        return column.type.python_type
    except Exception:  # fallback for custom/complex types
        return Any


for _name in model_names:
    model_cls = getattr(base_module, _name, None)
    if model_cls is None:
        try:
            mod = __import__("peagen.orm", fromlist=[_name])
            model_cls = getattr(mod, _name)
        except Exception:
            continue

    if not inspect.isclass(model_cls) or not issubclass(
        model_cls, base_module.BaseModel
    ):
        continue

    columns = {c.name: c for c in model_cls.__table__.columns}
    id_col = columns.get("id", None)
    if id_col is None:
        continue
    id_type = _python_type(id_col)

    # CREATE: all required fields except 'date_created'
    create_fields = {
        c_name: (_python_type(c), ...)
        for c_name, c in columns.items()
        if c_name != "date_created"
    }
    root_name = _name[:-5] if _name.endswith("Model") else _name
    create_cls = create_model(f"{root_name}Create", **create_fields)

    # UPDATE: all optional fields except 'id' and 'date_created'
    update_fields = {
        c_name: (Optional[_python_type(c)], None)
        for c_name, c in columns.items()
        if c_name not in ["id", "date_created"]
    }
    update_cls = create_model(f"{root_name}Update", **update_fields)

    # READ: all required, including id and date_created
    read_fields = {"id": (id_type, ...)}
    for c_name, c in columns.items():
        read_fields[c_name] = (_python_type(c), ...)
    if "date_created" not in read_fields and "date_created" in columns:
        read_fields["date_created"] = (datetime, ...)
    read_cls = create_model(f"{root_name}Read", **read_fields)

    # CHILD: id only
    child_cls = create_model(f"{root_name}Child", id=(id_type, ...))

    # Register in global scope and __all__
    globals()[create_cls.__name__] = create_cls
    globals()[update_cls.__name__] = update_cls
    globals()[read_cls.__name__] = read_cls
    globals()[child_cls.__name__] = child_cls
    __all__ += [
        create_cls.__name__,
        update_cls.__name__,
        read_cls.__name__,
        child_cls.__name__,
    ]

# Explicit exports for common task schemas
if "TaskRead" in globals():
    __all__.extend(["TaskRead", "TaskCreate", "TaskUpdate"])
