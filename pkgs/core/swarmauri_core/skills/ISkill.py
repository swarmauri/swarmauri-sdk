from abc import ABC
from typing import Any, Dict, List, Optional


class ISkill(ABC):
    name: str
    description: str
    instructions: str
    license: Optional[str]
    compatibility: Optional[str]
    metadata: Dict[str, Any]
    allowed_tools: List[str]
    assets: List[str]
    # Legacy Swarmauri extension fields retained during the compatibility
    # window.
    agents: List[str]
    references: List[str]
    scripts: List[str]
    tools: List[str]
    validation: List[str]
