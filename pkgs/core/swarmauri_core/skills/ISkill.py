from abc import ABC
from typing import Dict, List, Optional


class ISkill(ABC):
    """Portable Agent Skills contract for one complete skill bundle."""

    name: str
    description: str
    instructions: str
    license: str | None
    compatibility: str | None
    metadata: dict[str, str]
    allowed_tools: list[str]
    references: list[str]
    scripts: list[str]
    assets: list[str]
