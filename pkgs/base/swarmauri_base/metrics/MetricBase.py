from abc import ABC
from typing import Any, Callable, Optional, Sequence, TypeVar, Union
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.metrics.IMetric import IMetric

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T', IVector, IMatrix, Sequence, str, Callable)
S = TypeVar('S', int, float, bool, str)

@ComponentBase.register_model()
class MetricBase(IMetric, ComponentBase):
    """
    Provides a base implementation for the IMetric interface, implementing the core
    functionality required for metric spaces. This class ensures compliance with
    the four main metric axioms and provides boilerplate code for distance
    calculations.

    Inherits From:
        IMetric (ABC): The interface for metric spaces.
        ComponentBase: Base class for components in the system.

    Provides:
        - Abstract method implementations that raise NotImplementedError
        - Logging functionality
        - Type hints and docstrings
        - Compliance with PEP 8 and PEP 484 guidelines
    """
    resource: Optional[str] = Field(default=ResourceTypes.METRIC.value)

    def __init__(self):
        """
        Initialize the MetricBase instance.

        Initializes the base class and sets up logging.
        """
        super().__init__()
        logger.debug("MetricBase instance initialized")

    def distance(self, x: T, y: T) -> float:
        """
        Compute the distance between two points.

        Args:
            x: T
                The first point to compare
            y: T
                The second point to compare

        Returns:
            float:
                The computed distance between x and y

        Raises:
            NotImplementedError:
                This method must be implemented by a subclass
            ValueError:
                If the input types are not supported
            TypeError:
                If the input types are incompatible
        """
        raise NotImplementedError("distance must be implemented by subclass")

    def distances(self, x: T, y_list: Union[T, Sequence[T]]) -> Union[float, Sequence[float]]:
        """
        Compute the distance(s) between a point and one or more points.

        Args:
            x: T
                The reference point
            y_list: Union[T, Sequence[T]]
                Either a single point or a sequence of points

        Returns:
            Union[float, Sequence[float]]:
                - If y_list is a single point: Returns the distance as a float
                - If y_list is a sequence: Returns a sequence of distances

        Raises:
            NotImplementedError:
                This method must be implemented by subclass
            ValueError:
                If the input types are not supported
            TypeError:
                If the input types are incompatible
        """
        raise NotImplementedError("distances must be implemented by subclass")

    def check_non_negativity(self, x: T, y: T) -> bool:
        """
        Verify the non-negativity axiom: d(x, y) ≥ 0.

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if the non-negativity condition holds, False otherwise

        Raises:
            NotImplementedError:
                This method must be implemented by subclass
            ValueError:
                If the distance computation fails
        """
        raise NotImplementedError("check_non_negativity must be implemented by subclass")

    def check_identity(self, x: T, y: T) -> bool:
        """
        Verify the identity of indiscernibles axiom: d(x, y) = 0 if and only if x = y.

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if the identity condition holds, False otherwise

        Raises:
            NotImplementedError:
                This method must be implemented by subclass
            ValueError:
                If the distance computation fails
        """
        raise NotImplementedError("check_identity must be implemented by subclass")

    def check_symmetry(self, x: T, y: T) -> bool:
        """
        Verify the symmetry axiom: d(x, y) = d(y, x).

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if the symmetry condition holds, False otherwise

        Raises:
            NotImplementedError:
                This method must be implemented by subclass
            ValueError:
                If the distance computation fails
        """
        raise NotImplementedError("check_symmetry must be implemented by subclass")

    def check_triangle_inequality(self, x: T, y: T, z: T) -> bool:
        """
        Verify the triangle inequality axiom: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: T
                The first point
            y: T
                The second point
            z: T
                The third point

        Returns:
            bool:
                True if the triangle inequality condition holds, False otherwise

        Raises:
            NotImplementedError:
                This method must be implemented by subclass
            ValueError:
                If the distance computation fails
        """
        raise NotImplementedError("check_triangle_inequality must be implemented by subclass")