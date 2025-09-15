"""Pydantic dependencies re-exported for tigrbl_auth."""

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ValidationError,
    AnyHttpUrl,
    ConfigDict,
    field_validator,
    constr,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = [
    "BaseModel",
    "EmailStr",
    "Field",
    "ValidationError",
    "AnyHttpUrl",
    "ConfigDict",
    "field_validator",
    "constr",
    "BaseSettings",
    "SettingsConfigDict",
]
