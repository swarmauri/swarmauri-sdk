from __future__ import annotations

from typing import Any, Iterable


class TableRegistryBase(dict[str, Any]):
    """Dict-like registry used for table/model lookups."""

    def __init__(self, tables: Iterable[Any] = ()) -> None:
        resolved_tables = tuple(tables or ())
        dict.__init__(self)
        self.tables = resolved_tables
        self.register_many(resolved_tables)

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "tables" or name.startswith("_"):
            super().__setattr__(name, value)
            return
        self[name] = value

    def register(self, entry: Any) -> None:
        if isinstance(entry, tuple) and len(entry) == 2 and isinstance(entry[0], str):
            alias, model = entry
            self[alias] = model
            model_name = getattr(model, "__name__", alias)
            self.setdefault(model_name, model)
            return

        model = entry
        model_name = getattr(model, "__name__", None)
        if model_name is None:
            model_name = str(model)
        self[model_name] = model

    def register_many(self, tables: Iterable[Any]) -> None:
        for entry in tables:
            self.register(entry)


__all__ = ["TableRegistryBase"]
