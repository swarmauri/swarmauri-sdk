from __future__ import annotations

from pathlib import Path

from swarmauri_core.skills.ISkillLoader import ISkillLoader


class SkillLoaderBase(ISkillLoader):
    """Shared provider-neutral loader helpers."""

    @staticmethod
    def resolve_root(path: str | Path) -> Path:
        root = Path(path).expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise FileNotFoundError(
                f"Skill path does not exist or is not a directory: {root}"
            )
        return root

    @staticmethod
    def ensure_contained(root: Path, candidate: Path) -> Path:
        resolved = candidate.expanduser().resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(
                f"Skill resource escapes skill root: {candidate}"
            ) from exc
        return resolved
