from typing import List, Literal, Optional

import numpy as np
from pydantic import Field
from swarmauri_core.vectors.IVector import IVector

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class VectorBase(IVector, ComponentBase):
    value: List[float]
    resource: Optional[str] = Field(default=ResourceTypes.VECTOR.value, frozen=True)
    type: Literal["VectorBase"] = "VectorBase"
    # model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    def to_numpy(self) -> np.ndarray:
        """
        Converts the vector into a numpy array.

        Returns:
            np.ndarray: The numpy array representation of the vector.
        """
        return np.array(self.value)

    @property
    def shape(self):
        return self.to_numpy().shape

    def dot(self, other: IVector) -> float:
        """
        Computes the dot product with another vector.

        Args:
            other (IVector): The other vector to compute the dot product with.

        Returns:
            float: The result of the dot product.
        """
        return np.dot(self.to_numpy(), other.to_numpy())

    def __len__(self):
        return len(self.value)
