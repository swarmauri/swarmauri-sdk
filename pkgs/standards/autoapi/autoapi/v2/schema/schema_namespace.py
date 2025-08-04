from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - forward ref
    from .. import AutoAPI


# ────────────────────────────────────────────────────────────────────
class _SchemaNS(SimpleNamespace):
    """
    Attribute-style access to generated Pydantic schemas.

        api.schemas.UserCreate          → <class 'UserCreate'>
        api.schemas.UserCreate(name=…)  → instance of that model
    """

    def __init__(self, api: "AutoAPI"):
        super().__init__()
        self._api = api  # back-reference to parent

    def __getattr__(self, item: str):  # lazy lookup / build
        # already cached on the namespace?
        try:
            return self.__dict__[item]
        except KeyError:
            pass

        # check AutoAPI's registry
        if item in self._api._schemas:
            mdl = self._api._schemas[item]
            setattr(self, item, mdl)  # cache on first use
            return mdl

        # try to *derive* model  verb from the camel-cased key, e.g. "GroupCreate"
        import re

        m = re.match(r"([A-Z]\w?)(Create|Read|Update|Replace|Delete|List)$", item)
        if not m:
            raise AttributeError(item) from None

        model_name, verb = m.groups()
        orm_cls = self._api._model_registry.get(model_name)
        if orm_cls is None:
            raise AttributeError(item) from None

        mdl = self._api.schema(orm_cls, verb=verb.lower())
        self._api._schemas[item] = mdl
        setattr(self, item, mdl)
        return mdl
