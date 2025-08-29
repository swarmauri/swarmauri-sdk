from __future__ import annotations

from typing import Type

from pydantic import BaseModel


def namely_model(model: Type[BaseModel], *, name: str, doc: str) -> Type[BaseModel]:
    """Assign a unique name and docstring to a Pydantic model class."""
    model.__name__ = name
    model.__qualname__ = name
    model.__doc__ = doc
    # Rebuild the model so Pydantic updates internal references (e.g., for OpenAPI titles).
    model.model_rebuild(force=True)
    return model


__all__ = ["namely_model"]
