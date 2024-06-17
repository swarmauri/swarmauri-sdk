from typing import Any, Callable, List, Dict, Optional
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.chains.IChainStep import IChainStep

class ChainStepBase(IChainStep, ComponentBase):
    """
    Represents a single step within an execution chain.
    """
    key: str = Field(kw_only=True)
    method: Callable = Field(kw_only=True)
    args: List[Any] = Field(kw_only=True, default_factory=list)
    kwargs: Dict[str, Any] = Field(kw_only=True, default_factory=dict)
    ref: Optional[str] =  Field(kw_only=True, default=None)
    resource: Optional[str] =  Field(default=ResourceTypes.CHAINSTEP.value)