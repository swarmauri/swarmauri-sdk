import numpy as np
from typing import List
from pydantic import BaseModel
from swarmauri_core.vectors.IVectorProduct import IVectorProduct
from swarmauri.vectors.concrete.Vector import Vector

class VectorProductMixin(IVectorProduct, BaseModel):
    def dot_product(self, vector_a: Vector, vector_b: Vector) -> float:
        a = np.array(vector_a.value).flatten()
        b = np.array(vector_b.value).flatten()
        return np.dot(a, b)
    
    def cross_product(self, vector_a: Vector, vector_b: Vector) -> Vector:
        if len(vector_a.value) != 3 or len(vector_b.value) != 3:
            raise ValueError("Cross product is only defined for 3-dimensional vectors")
        a = np.array(vector_a.value)
        b = np.array(vector_b.value)
        cross = np.cross(a, b)
        return Vector(value=cross.tolist())
    
    def vector_triple_product(self, vector_a: Vector, vector_b: Vector, vector_c: Vector) -> Vector:
        a = np.array(vector_a.value)
        b = np.array(vector_b.value)
        c = np.array(vector_c.value)
        result = np.cross(a, np.cross(b, c))
        return Vector(value=result.tolist())
    
    def scalar_triple_product(self, vector_a: Vector, vector_b: Vector, vector_c: Vector) -> float:
        a = np.array(vector_a.value)
        b = np.array(vector_b.value)
        c = np.array(vector_c.value)
        return np.dot(a, np.cross(b, c))