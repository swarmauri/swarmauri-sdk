"""Reusable model-catalog behavior."""

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Literal, Optional

from pydantic import Field, PrivateAttr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.model_providers.IModelCatalog import IModelCatalog


class ModelCatalogBase(IModelCatalog, ComponentBase):
    models: Dict[str, Any] = Field(default_factory=dict)
    type: Literal["ModelCatalogBase"] = "ModelCatalogBase"
    _refreshed_at: Optional[datetime] = PrivateAttr(default=None)

    def list_models(self) -> Iterable[Any]:
        return list(self.models.values())

    def get_model(self, name: str) -> Optional[Any]:
        return self.models.get(name)

    def refresh(self) -> Iterable[Any]:
        self._refreshed_at = datetime.now(timezone.utc)
        return self.list_models()

    async def arefresh(self) -> Iterable[Any]:
        return self.refresh()

    def replace(self, models: Iterable[Any], *, key: str = "name") -> None:
        self.models = {str(getattr(model, key)): model for model in models}
        self._refreshed_at = datetime.now(timezone.utc)

    @property
    def refreshed_at(self) -> Optional[datetime]:
        return self._refreshed_at
