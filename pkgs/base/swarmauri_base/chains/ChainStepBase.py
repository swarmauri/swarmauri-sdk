from typing import Any, Tuple, Dict, Optional, Union, Literal
from pydantic import Field, ConfigDict
from swarmauri_core.typing import SubclassUnion
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.chains.IChainStep import IChainStep

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