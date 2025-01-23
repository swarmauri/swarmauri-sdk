from math import acos, isclose
from pydantic import BaseModel, ConfigDict
from swarmauri.vectors.IVector import IVector
from swarmauri.innerproducts.base.InnerProductBase import InnerProductBase
from swarmauri_core.typing import SubclassUnion

class NormInnerProductMixin(IUseInnerProduct, BaseModel):
    inner_product: SubclassUnion[InnerProductBase]
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

    def angle_between_vectors(self, x: IVector, y: IVector) -> float:
        dot_product = self.inner_product.compute(x, y)
        norm_x = self.compute(x)
        norm_y = self.compute(y)
        return acos(dot_product / (norm_x * norm_y))

    def verify_orthogonality(self, x: IVector, y: IVector) -> bool:
        return isclose(self.inner_product.compute(x, y), 0.0)

    def project(self, x: IVector, y: IVector) -> IVector:
        scalar = self.inner_product.compute(x, y) / self.inner_product.compute(y, y)
        return scalar * y

    def verify_parallelogram_law(self, x: IVector, y: IVector):
        norm_x_y = self.compute(x + y) ** 2
        norm_x_minus_y = self.compute(x - y) ** 2
        norm_x = self.compute(x) ** 2
        norm_y = self.compute(y) ** 2
        if not isclose(norm_x_y + norm_x_minus_y, 2 * (norm_x + norm_y)):
            raise ValueError("Parallelogram law violated.")
