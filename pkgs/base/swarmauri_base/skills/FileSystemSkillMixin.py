from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic import BaseModel, ConfigDict

from swarmauri_base.skills.SkillBase import SkillBase
from swarmauri_base.skills.SkillLoaderBase import SkillLoaderBase
from swarmauri_base.skills.SkillMetadata import SkillMetadata


class FileSystemSkillMixin(BaseModel, SkillLoaderBase):
    """Load Agent Skills packages from a filesystem root."""

    root_path: str | None = None
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @classmethod
    def discover(cls, source: str | Path) -> List[SkillMetadata]:
        root = cls.resolve_root(source)
        skill_md = root / "SKILL.md"
        if not skill_md.is_file():
            raise FileNotFoundError(
                f"Skill package requires SKILL.md: {skill_md}"
            )
        frontmatter, _ = SkillBase.split_frontmatter(
            skill_md.read_text(encoding="utf-8-sig")
        )
        records = [
            SkillMetadata(
                name=frontmatter.get("name", ""),
                description=frontmatter.get("description", ""),
                license=frontmatter.get("license"),
                compatibility=frontmatter.get("compatibility"),
                metadata=frontmatter.get("metadata") or {},
                source="filesystem",
                location=str(root),
            )
        ]
        if records[0].name != root.name:
            raise ValueError(
                f"Skill name '{records[0].name}' must match "
                f"directory '{root.name}'"
            )
        return records

    @classmethod
    def load(
        cls,
        source: str | Path,
        skill_name: str | None = None,
        **overrides: Any,
    ):
        root = cls.resolve_root(source)
        skill_md = root / "SKILL.md"
        if not skill_md.is_file():
            raise FileNotFoundError(
                f"Skill package requires SKILL.md: {skill_md}"
            )

        manifest = cls._read_manifest(root / "skill.yaml")
        if not manifest:
            manifest = cls._read_manifest(root / "skill.yml")
        markdown = skill_md.read_text(encoding="utf-8-sig")
        data = cls._data_from_markdown(markdown, manifest, overrides)
        data.setdefault("root_path", str(root))
        cls._add_discovered_resources(root, data)
        skill = cls(**data)
        if skill.name != root.name:
            raise ValueError(
                f"Skill name '{skill.name}' must match directory '{root.name}'"
            )
        if skill_name is not None and skill.name != skill_name:
            raise ValueError(
                f"Loaded skill name '{skill.name}' does not match "
                f"'{skill_name}'"
            )
        return skill

    @classmethod
    def from_path(cls, path: str | Path, **overrides: Any):
        """Compatibility alias for activating a filesystem skill."""
        return cls.load(path, **overrides)

    @classmethod
    def load_resource(cls, skill: Any, relative_path: str) -> bytes:
        root_path = getattr(skill, "root_path", None)
        if not root_path:
            raise ValueError(f"Skill '{skill.name}' does not define root_path")
        root = cls.resolve_root(root_path)
        candidate = cls.ensure_contained(root, root / relative_path)
        if not candidate.is_file():
            raise FileNotFoundError(
                f"Skill resource does not exist: {relative_path}"
            )
        return candidate.read_bytes()

    def read_resource(self, relative_path: str) -> bytes:
        """Read one resource lazily from this skill's root."""
        return type(self).load_resource(self, relative_path)

    @classmethod
    def _data_from_markdown(
        cls,
        markdown: str,
        manifest: Dict[str, Any],
        overrides: Dict[str, Any],
    ) -> Dict[str, Any]:
        frontmatter, instructions = SkillBase.split_frontmatter(markdown)
        data = cls.merge_skill_data(frontmatter, manifest, overrides)
        data.setdefault("instructions", instructions.strip())
        return data

    @classmethod
    def _read_manifest(cls, path: Path) -> Dict[str, Any]:
        if not path.is_file():
            return {}
        parsed = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        if parsed is None:
            return {}
        if not isinstance(parsed, dict):
            raise ValueError(f"Skill manifest must be a YAML mapping: {path}")
        return parsed

    @classmethod
    def _add_discovered_resources(
        cls, root: Path, data: Dict[str, Any]
    ) -> None:
        resource_fields = tuple(getattr(cls, "_RESOURCE_FIELDS", ()))
        for field_name in resource_fields:
            current = list(data.get(field_name) or [])
            seen = set(current)
            folder = root / field_name
            if folder.is_dir():
                for child in sorted(
                    p for p in folder.rglob("*") if p.is_file()
                ):
                    rel = child.relative_to(root).as_posix()
                    if rel not in seen:
                        current.append(rel)
                        seen.add(rel)
            data[field_name] = current
