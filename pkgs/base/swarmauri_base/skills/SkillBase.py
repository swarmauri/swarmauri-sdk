from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Literal, Optional, Tuple

import yaml
from pydantic import ConfigDict, Field, model_validator

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.skills.ISkill import ISkill


@ComponentBase.register_model()
class SkillBase(ISkill, ComponentBase):
    name: str
    description: str
    instructions: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    agents: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    scripts: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    validation: List[str] = Field(default_factory=list)
    resource: Optional[str] = Field(default=ResourceTypes.SKILL.value)
    type: Literal["SkillBase"] = "SkillBase"
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    _RESOURCE_FIELDS: ClassVar[tuple[str, ...]] = (
        "agents",
        "references",
        "scripts",
        "tools",
        "validation",
    )
    _SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {".md", ".yaml", ".yml", ".py"}

    @model_validator(mode="after")
    def _validate_resource_extensions(self) -> "SkillBase":
        for field_name in self._RESOURCE_FIELDS:
            for value in getattr(self, field_name):
                suffix = self._suffix(value)
                if suffix and suffix not in self._SUPPORTED_EXTENSIONS:
                    raise ValueError(
                        (
                            f"Unsupported skill resource extension for "
                            f"{field_name}: "
                            f"{value}"
                        )
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
        normalized = markdown.lstrip("﻿")
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
        return {}, markdown

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

    @staticmethod
    def _suffix(value: str) -> str:
        name = value.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        if "." not in name:
            return ""
        return "." + name.rsplit(".", 1)[1].lower()
