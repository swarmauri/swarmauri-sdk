import logging
from typing import Any, Sequence, List, Literal, Optional
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.mutators.IMutator import IMutator

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class MutatorBase(IMutator, ComponentBase):
    """Base class for data mutators."""

    resource: Optional[str] = Field(default=ResourceTypes.MUTATOR.value)
    type: Literal["MutatorBase"] = "MutatorBase"

    def mutate(self, item: Any) -> Any:
        """Mutate a single item and return the result."""
        logger.debug("MutatorBase mutate called with %s", type(item))
        raise NotImplementedError("mutate method must be implemented by subclasses")

    def mutates(self, items: Sequence[Any]) -> List[Any]:
        """Mutate multiple items by applying :py:meth:`mutate` to each."""
        logger.debug("MutatorBase mutates called with %d items", len(items))
        return [self.mutate(item) for item in items]
