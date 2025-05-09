from typing import Union, List, Literal
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.metrics.IMetric import IMetric
import logging

logger = logging.getLogger(__name__)

@ComponentBase.register_model()
class MetricBase(IMetric, ComponentBase):
    """
    Base implementation for metric spaces. This class provides a foundation for 
    implementing specific metric spaces by implementing the required methods 
    while enforcing the metric axioms.

    Implementations must provide concrete implementations for the abstract methods 
    while adhering to the following properties:
    1. Non-negativity: d(x, y) ≥ 0
    2. Identity: d(x, y) = 0 if and only if x = y
    3. Symmetry: d(x, y) = d(y, x)
    4. Triangle inequality: d(x, z) ≤ d(x, y) + d(y, z)
    """
    resource: Optional[str] = Field(default=ResourceTypes.METRIC.value)
    
    def distance(
        self, 
        x: Union[IVector, IMatrix, List, str, callable], 
        y: Union[IVector, IMatrix, List, str, callable]
    ) -> float:
        """
        Compute the distance between two points.

        Args:
            x: The first point. Can be a vector, matrix, list, string, or callable.
            y: The second point. Can be a vector, matrix, list, string, or callable.

        Returns:
            float: The computed distance between x and y.

        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        """
        logger.warning("distance method called on base class - must be implemented in subclass")
        raise NotImplementedError("distance method must be implemented in subclass")

    def distances(
        self, 
        x: Union[IVector, IMatrix, List, str, callable], 
        ys: List[Union[IVector, IMatrix, List, str, callable]]
    ) -> List[float]:
        """
        Compute distances from a single point to multiple points.

        Args:
            x: The reference point. Can be a vector, matrix, list, string, or callable.
            ys: List of points to compute distances to. Each can be a vector, 
                matrix, list, string, or callable.

        Returns:
            List[float]: List of distances from x to each point in ys.

        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        """
        logger.warning("distances method called on base class - must be implemented in subclass")
        raise NotImplementedError("distances method must be implemented in subclass")

    def check_non_negativity(
        self, 
        x: Union[IVector, IMatrix, List, str, callable], 
        y: Union[IVector, IMatrix, List, str, callable]
    ) -> Literal[True]:
        """
        Verify the non-negativity property: d(x, y) ≥ 0.

        Args:
            x: The first point. Can be a vector, matrix, list, string, or callable.
            y: The second point. Can be a vector, matrix, list, string, or callable.

        Returns:
            Literal[True]: True if the non-negativity property holds.

        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        """
        logger.warning("check_non_negativity method called on base class - must be implemented in subclass")
        raise NotImplementedError("check_non_negativity method must be implemented in subclass")

    def check_identity(
        self, 
        x: Union[IVector, IMatrix, List, str, callable], 
        y: Union[IVector, IMatrix, List, str, callable]
    ) -> Literal[True]:
        """
        Verify the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.

        Args:
            x: The first point. Can be a vector, matrix, list, string, or callable.
            y: The second point. Can be a vector, matrix, list, string, or callable.

        Returns:
            Literal[True]: True if the identity property holds.

        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        """
        logger.warning("check_identity method called on base class - must be implemented in subclass")
        raise NotImplementedError("check_identity method must be implemented in subclass")

    def check_symmetry(
        self, 
        x: Union[IVector, IMatrix, List, str, callable], 
        y: Union[IVector, IMatrix, List, str, callable]
    ) -> Literal[True]:
        """
        Verify the symmetry property: d(x, y) = d(y, x).

        Args:
            x: The first point. Can be a vector, matrix, list, string, or callable.
            y: The second point. Can be a vector, matrix, list, string, or callable.

        Returns:
            Literal[True]: True if the symmetry property holds.

        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        """
        logger.warning("check_symmetry method called on base class - must be implemented in subclass")
        raise NotImplementedError("check_symmetry method must be implemented in subclass")

    def check_triangle_inequality(
        self, 
        x: Union[IVector, IMatrix, List, str, callable], 
        y: Union[IVector, IMatrix, List, str, callable], 
        z: Union[IVector, IMatrix, List, str, callable]
    ) -> Literal[True]:
        """
        Verify the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: The first point. Can be a vector, matrix, list, string, or callable.
            y: The second point. Can be a vector, matrix, list, string, or callable.
            z: The third point. Can be a vector, matrix, list, string, or callable.

        Returns:
            Literal[True]: True if the triangle inequality property holds.

        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        """
        logger.warning("check_triangle_inequality method called on base class - must be implemented in subclass")
        raise NotImplementedError("check_triangle_inequality method must be implemented in subclass")