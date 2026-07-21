from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, List


class ISkillLoader:
    """Provider-neutral contract for discovering and loading skills."""

    def discover(self, source: str | Path | Iterable[str | Path]) -> List[Any]:
        """Return metadata records without activating skill instructions."""
        raise NotImplementedError

    def load(self, source: str | Path, skill_name: str | None = None) -> Any:
        """Activate a skill from a source."""
        raise NotImplementedError

    def load_resource(self, skill: Any, relative_path: str) -> bytes:
        """Load one skill resource on demand."""
        raise NotImplementedError
