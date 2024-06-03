from abc import ABC, abstractmethod
from typing import Optional, List, Any
from swarmauri.core.BaseComponent import BaseComponent
from swarmauri.core.tools.IParameter import IParameter

@dataclass
class ParameterBase(IParameter, BaseComponent, ABC):
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
        if type(self.required) == property:
            self.required = None
        if type(self.enum) == property:
            self.enum = None
            
            

        # Assuming BaseComponent initialization if needed
        BaseComponent.__init__(self, 
                               id=self.id, 
                               owner=self.owner, 
                               name=self.name, 
                               host=self.host, 
                               members=self.members, 
                               resource=ResourceTypes.PARAMETER.value)
        
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def required(self) -> bool:
        return self._required

    @required.setter
    def required(self, value: bool):
        self._required = value

    @property
    def enum(self) -> List[str]:
        return self._enum

    @enum.setter
    def enum(self, value: List[str]):
        self._enum = value