from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseModel, ConfigDict


class FileSystemSkillMixin(BaseModel):
    root_path: str | None = None
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @classmethod
    def from_path(cls, path: str | Path, **overrides: Any):
        root = Path(path).expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise FileNotFoundError(
                f"Skill path does not exist or is not a directory: {root}"
            )

        skill_md = root / "SKILL.md"
        if not skill_md.is_file():
            raise FileNotFoundError(
                f"Skill package requires SKILL.md: {skill_md}"
            )

        manifest = cls._read_manifest(root / "skill.yaml")
        if not manifest:
            manifest = cls._read_manifest(root / "skill.yml")

        markdown = skill_md.read_text(encoding="utf-8")
        data = cls._data_from_markdown(markdown, manifest, overrides)
        data.setdefault("root_path", str(root))
        cls._add_discovered_resources(root, data)
        return cls(**data)

    @classmethod
    def _data_from_markdown(
        cls,
        markdown: str,
        manifest: Dict[str, Any],
        overrides: Dict[str, Any],
    ) -> Dict[str, Any]:
        frontmatter, instructions = cls.split_frontmatter(markdown)
        data = cls.merge_skill_data(frontmatter, manifest, overrides)
        data.setdefault("instructions", instructions.strip())
        return data

    @classmethod
    def _read_manifest(cls, path: Path) -> Dict[str, Any]:
        if not path.is_file():
            return {}
        parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
        if parsed is None:
            return {}
        if not isinstance(parsed, dict):
            raise ValueError(f"Skill manifest must be a YAML mapping: {path}")
        return parsed

    @classmethod
    def _add_discovered_resources(
        cls, root: Path, data: Dict[str, Any]
    ) -> None:
        for field_name in cls._RESOURCE_FIELDS:
            current = list(data.get(field_name) or [])
            seen = set(current)
            folder = root / field_name
            if folder.is_dir():
                for child in sorted(
                    p for p in folder.rglob("*") if p.is_file()
                ):
                    rel = child.relative_to(root).as_posix()
                    if child.suffix.lower() not in cls._SUPPORTED_EXTENSIONS:
                        raise ValueError(
                            (
                                f"Unsupported skill resource extension for "
                                f"{field_name}: "
                                f"{rel}"
                            )
                        )
                    if rel not in seen:
                        current.append(rel)
                        seen.add(rel)
            data[field_name] = current
