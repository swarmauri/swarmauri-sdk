from dataclasses import dataclass, field
from typing import Optional, List, Any
import json

from swarmauri.standard.tools.base.ParameterBase import ParameterBase

@dataclass
class Parameter(ParameterBase, BaseComponent):
    name: str
    type: str
    description: str
    required: bool = False
    enum: Optional[List[str]] = None

    id: Optional[str] = None
    owner: Optional[str] = None
    host: Optional[str] = None
    members: List[str] = field(default_factory=list)
    #resource = None

    def __post_init__(self):
        print(self.name, type(self.name))
        if type(self.name) == property:
            raise ValueError('Name parameter is required.')
        if type(self.type) == property:
            raise ValueError('Type parameter is required.')
        if type(self.description) == property:
            raise ValueError('Description parameter is required.')

        # Assuming BaseComponent initialization if needed
        BaseComponent.__init__(self, 
                               id=self.id, 
                               owner=self.owner, 
                               name=self.name, 
                               host=self.host, 
                               members=self.members, 
                               resource=ResourceTypes.PARAMETER.value)