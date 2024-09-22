from typing import Any, Tuple, Dict, Optional, Union, Literal
from pydantic import Field, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.chains.IChainStep import IChainStep

class ChainStepBase(IChainStep, ComponentBase):
    """
    Represents a single step within an execution chain.
    """
    key: str
    method: SubclassUnion[ToolBase]
    args: Tuple = Field(default_factory=tuple)
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    ref: Optional[str] =  Field(default=None)
    resource: Optional[str] =  Field(default=ResourceTypes.CHAINSTEP.value)
    type: Literal['ChainStepBase'] = 'ChainStepBase'