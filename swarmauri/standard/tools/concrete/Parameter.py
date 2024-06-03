from dataclasses import dataclass, field, asdict
from typing import Optional, List, Any

import json
from swarmauri.core.BaseComponent import BaseComponent
from swarmauri.core.tools.IParameter import IParameter

@dataclass
class Parameter(IParameter, BaseComponent):
    name: str = ""
    type: str = ""
    description: str = ""
    required: bool = False
    enum: Optional[List[str]] = None
    id: Optional[str] = None
    owner: Optional[str] = None
    name: Optional[str] = None
    host: Optional[str] = None
    members: List[str] = field(default_factory=list)
    #resource = None

    def __post_init__(self):
        # Assuming BaseComponent initialization if needed
        BaseComponent.__init__(self, 
                               id=self.id, 
                               owner=self.owner, 
                               name=self.name, 
                               host=self.host, 
                               members=self.members, 
                               resource=ResourceTypes.PARAMETER.value)