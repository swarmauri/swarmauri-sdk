from abc import ABC
from typing import Dict, List, Optional


class ISkill(ABC):
    """Portable Agent Skills contract for one complete skill bundle."""

    name: str
    description: str
    instructions: str
    license: Optional[str]
    compatibility: Optional[str]
    metadata: Dict[str, str]
    allowed_tools: List[str]
    references: List[str]
    scripts: List[str]
    assets: List[str]
