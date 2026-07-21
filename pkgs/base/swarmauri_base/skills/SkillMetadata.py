from __future__ import annotations

import re
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SkillMetadata(BaseModel):
    """Catalog-level metadata for a skill before full activation."""

    name: str
    description: str
    license: Optional[str] = None
    compatibility: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: str
    location: str
    model_config = ConfigDict(extra="forbid")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not 1 <= len(value) <= 64 or not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", value
        ):
            raise ValueError("Invalid Agent Skills name")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        if not value.strip() or len(value) > 1024:
            raise ValueError("Skill description must be 1-1024 characters")
        return value

    @field_validator("compatibility")
    @classmethod
    def validate_compatibility(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not 1 <= len(value) <= 500:
            raise ValueError("Skill compatibility must be 1-500 characters")
        return value
