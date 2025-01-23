from typing import List
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.metrics.IMetric import IMetric
from pydantic import Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes

class MetricBase(IMetric, ComponentBase):
    """
    Base class providing default implementations for metric properties.
    Concrete classes should implement the `distance`, `distances`, `similarity`, 
    and `similarities` methods.
    """
    resource: Optional[str] =  Field(default=ResourceTypes.METRIC.value, frozen=True)
    type: Literal['MetricBase'] = 'MetricBase'

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        raise NotImplementedError("Concrete classes must implement the `distance` method.")

    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        """
        Computes distances from one vector to a list of vectors.

        Args:
            vector_a (IVector): The reference vector.
            vectors_b (List[IVector]): A list of vectors to compute distances to.

        Returns:
            List[float]: A list of distances.
        """
        return [self.distance(vector_a, vector_b) for vector_b in vectors_b]

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes a similarity score derived from the distance.
        Default implementation assumes similarity is inversely proportional to distance.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            float: A similarity score (0 to 1).
        """
        raise NotImplementedError("Concrete classes must implement the `similarity` method.")

    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        """
        Computes similarities from one vector to a list of vectors.

        Args:
            vector_a (IVector): The reference vector.
            vectors_b (List[IVector]): A list of vectors to compute similarities to.

        Returns:
            List[float]: A list of similarity scores.
        """
        return [self.similarity(vector_a, vector_b) for vector_b in vectors_b]

    def check_triangle_inequality(self, vector_a: IVector, vector_b: IVector, vector_c: IVector) -> bool:
        """
        Checks the triangle inequality property: d(a, c) <= d(a, b) + d(b, c).

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.
            vector_c (IVector): The third vector.

        Returns:
            bool: True if the triangle inequality holds, False otherwise.
        """
        dist_ab = self.distance(vector_a, vector_b)
        dist_bc = self.distance(vector_b, vector_c)
        dist_ac = self.distance(vector_a, vector_c)

        return dist_ac <= dist_ab + dist_bc

    def check_non_negativity(self, vector_a: IVector, vector_b: IVector) -> bool:
        """
        Checks the non-negativity property: d(a, b) >= 0.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            bool: True if the non-negativity property holds, False otherwise.
        """
        return self.distance(vector_a, vector_b) >= 0

    def check_identity_of_indiscernibles(self, vector_a: IVector, vector_b: IVector) -> bool:
        """
        Checks the identity of indiscernibles property: d(a, b) = 0 if and only if a = b.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            bool: True if the identity of indiscernibles property holds, False otherwise.
        """
        dist = self.distance(vector_a, vector_b)
        if vector_a.value == vector_b.value:
            return dist == 0
        else:
            return dist > 0

    def check_symmetry(self, vector_a: IVector, vector_b: IVector) -> bool:
        """
        Checks the symmetry property: d(a, b) = d(b, a).

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            bool: True if the symmetry property holds, False otherwise.
        """
        return self.distance(vector_a, vector_b) == self.distance(vector_b, vector_a)

    def check_positivity(self, vector_a: IVector, vector_b: IVector) -> bool:
        """
        Checks the positivity property: d(a, b) > 0 for all a != b.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            bool: True if the positivity property holds (i.e., d(a, b) > 0 for a != b), 
                  False otherwise.
        """
        return vector_a.value != vector_b.value and self.distance(vector_a, vector_b) > 0