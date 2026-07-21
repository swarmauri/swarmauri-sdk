from __future__ import annotations

import re
from pathlib import PurePath
from typing import Any, ClassVar, Dict, List, Literal, Optional, Tuple

import yaml
from pydantic import (
    AliasChoices,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.skills.ISkill import ISkill


@ComponentBase.register_model()
class SkillBase(ISkill, ComponentBase):
    """Portable Agent Skills model with Swarmauri compatibility extensions."""

    name: str
    description: str
    instructions: str
    license: Optional[str] = None
    compatibility: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    allowed_tools: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("allowed-tools", "allowed_tools"),
    )
    assets: List[str] = Field(default_factory=list)
    # Legacy Swarmauri extension fields retained during migration.
    agents: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    scripts: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    validation: List[str] = Field(default_factory=list)
    resource: Optional[str] = Field(default=ResourceTypes.SKILL.value)
    type: Literal["SkillBase"] = "SkillBase"
    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    _RESOURCE_FIELDS: ClassVar[tuple[str, ...]] = (
        "agents",
        "references",
        "scripts",
        "tools",
        "validation",
        "assets",
    )
    _NAME_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    )

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        if not 1 <= len(value) <= 64 or not cls._NAME_PATTERN.fullmatch(value):
            raise ValueError(
                "Skill name must be 1-64 characters of lowercase letters, "
                "numbers, and single hyphens, without leading/trailing hyphens"
            )
        return value

    @field_validator("description")
    @classmethod
    def _validate_description(cls, value: str) -> str:
        if not value.strip() or len(value) > 1024:
            raise ValueError("Skill description must be 1-1024 characters")
        return value

    @field_validator("compatibility")
    @classmethod
    def _validate_compatibility(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not 1 <= len(value) <= 500:
            raise ValueError("Skill compatibility must be 1-500 characters")
        return value

    @model_validator(mode="before")
    @classmethod
    def _normalize_legacy_fields(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        data = dict(value)
        if "allowed-tools" not in data and "allowed_tools" in data:
            data["allowed-tools"] = data.pop("allowed_tools")
        if isinstance(data.get("allowed-tools"), str):
            data["allowed-tools"] = data["allowed-tools"].split()
        # Legacy `tools` was historically used as a manifest. Treat it as an
        # allowed-tools alias only when no standard field was provided.
        if "allowed-tools" not in data and "tools" in data:
            data["allowed-tools"] = data["tools"]
        return data

    @model_validator(mode="after")
    def _validate_resource_paths(self) -> "SkillBase":
        for field_name in self._RESOURCE_FIELDS:
            for value in getattr(self, field_name):
                if not isinstance(value, str) or not value:
                    raise ValueError(f"{field_name} entries must be strings")
                path = PurePath(value.replace("\\", "/"))
                if path.is_absolute() or ".." in path.parts:
                    raise ValueError(
                        f"Skill resource path must stay relative: {value}"
                    )
        return self

    @classmethod
    def from_markdown(
        cls,
        markdown: str,
        manifest: Optional[Dict[str, Any]] = None,
        **overrides: Any,
    ) -> "SkillBase":
        frontmatter, instructions = cls.split_frontmatter(markdown)
        data = cls.merge_skill_data(frontmatter, manifest or {}, overrides)
        data.setdefault("instructions", instructions.strip())
        return cls(**data)

    @classmethod
    def split_frontmatter(cls, markdown: str) -> Tuple[Dict[str, Any], str]:
        normalized = markdown.lstrip("\ufeff")
        if not normalized.startswith("---"):
            return {}, markdown

        lines = normalized.splitlines()
        if not lines or lines[0].strip() != "---":
            return {}, markdown

        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                raw_frontmatter = "\n".join(lines[1:index])
                body = "\n".join(lines[index + 1 :])
                parsed = (
                    yaml.safe_load(raw_frontmatter)
                    if raw_frontmatter.strip()
                    else {}
                )
                if parsed is None:
                    parsed = {}
                if not isinstance(parsed, dict):
                    raise ValueError(
                        "SKILL.md frontmatter must be a YAML mapping"
                    )
                return parsed, body
        return {}, normalized

    @classmethod
    def merge_skill_data(
        cls,
        frontmatter: Dict[str, Any],
        manifest: Dict[str, Any],
        overrides: Dict[str, Any],
    ) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        data.update(frontmatter or {})
        data.update(manifest or {})
        data.update(
            {
                key: value
                for key, value in overrides.items()
                if value is not None
            }
        )
        return data
