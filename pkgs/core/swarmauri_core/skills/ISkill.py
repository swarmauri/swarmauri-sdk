from abc import ABC
from typing import Any, Dict, List


class ISkill(ABC):
    name: str
    description: str
    instructions: str
    metadata: Dict[str, Any]
    agents: List[str]
    references: List[str]
    scripts: List[str]
    tools: List[str]
    validation: List[str]
