from typing import Any, Tuple, Dict, Optional, Union, Callable
from pydantic import Field, ConfigDict, ImportString
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.chains.IChainStep import IChainStep

class ChainStepBase(IChainStep, ComponentBase):
    """
    Represents a single step within an execution chain.
    """
    key: str
    method: Union[ImportString, Callable[..., Any]] = Field(kw_only=True)
    args: Tuple = Field(default_factory=tuple)
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    ref: Optional[str] =  Field(default=None)
    resource: Optional[str] =  Field(default=ResourceTypes.CHAINSTEP.value)