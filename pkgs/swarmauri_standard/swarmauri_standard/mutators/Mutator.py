from typing import Any, Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.mutators.MutatorBase import MutatorBase


@ComponentBase.register_type(MutatorBase, "Mutator")
class Mutator(MutatorBase):
    """Generic mutator that returns items unchanged."""

    type: Literal["Mutator"] = "Mutator"

    def mutate(self, item: Any) -> Any:
        return item
