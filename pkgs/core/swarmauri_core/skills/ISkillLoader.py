from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from swarmauri_core.skills.ISkill import ISkill


class ISkillLoader:
    """Interface for objects that discover and load skill bundles."""

    def discover(self, source: str | Path | Iterable[str | Path]):
        """Return lightweight metadata without activating instructions."""
        raise NotImplementedError

    def load(
        self, source: str | Path, skill_name: str | None = None
    ) -> "ISkill":
        """Activate one complete skill bundle."""
        raise NotImplementedError

    def activate(
        self, source: str | Path, skill_name: str | None = None
    ) -> "ISkill":
        """Explicit alias for loading/activating a selected skill bundle."""
        return self.load(source, skill_name=skill_name)

    def load_resource(self, skill: "ISkill", relative_path: str) -> bytes:
        """Read one resource from an activated skill bundle on demand."""
        raise NotImplementedError
