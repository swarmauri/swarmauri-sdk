import logging
import typing
from typing import Callable, Sequence, Optional, Union, List
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.pseudometrics.IPseudometric import IPseudometric

logger = logging.getLogger(__name__)

TypeVarT = TypeVar('T', bound=Union[Callable, Sequence, str])

@ComponentBase.register_type(PseudometricBase, "FunctionDifferencePseudometric")
class FunctionDifferencePseudometric(PseudometricBase):
    """
    A concrete implementation of PseudometricBase that measures the output difference of functions.

    This class provides a pseudometric that evaluates the distance between two functions
    based on their value differences at specific evaluation points. The evaluation points
    can be either provided explicitly or generated using a Halton sequence sampler.

    Attributes:
        evaluation_points: Sequence of points at which to evaluate the functions
        num_evaluation_points: Number of points to generate if no explicit points are provided
    """
    type: Literal["FunctionDifferencePseudometric"] = "FunctionDifferencePseudometric"
    resource: str = ResourceTypes.PSEUDOMETRIC.value
    
    def __init__(self, evaluation_points: Optional[Sequence] = None, num_evaluation_points: int = 10):
        """
        Initializes the FunctionDifferencePseudometric instance.

        Args:
            evaluation_points: Optional[Sequence], optional
                Specific points to evaluate the functions at. If not provided,
                num_evaluation_points points will be generated using a Halton sequence
            num_evaluation_points: int, optional
                Number of points to generate if evaluation_points is None. Defaults to 10

        Raises:
            ValueError: If both evaluation_points and num_evaluation_points are None
        """
        super().__init__()
        self.evaluation_points = evaluation_points
        self.num_evaluation_points = num_evaluation_points
        
        if evaluation_points is None and num_evaluation_points is None:
            raise ValueError("Either evaluation_points or num_evaluation_points must be specified")
            
        logger.info(f"Initialized FunctionDifferencePseudometric with evaluation points: {self.evaluation_points}")
        
    def distance(self, x: Callable, y: Callable) -> float:
        """
        Computes the pseudometric distance between two functions.

        The distance is computed as the average absolute difference between the
        function outputs at the specified evaluation points.

        Args:
            x: Callable
                The first function to evaluate
            y: Callable
                The second function to evaluate

        Returns:
            float
                The computed pseudometric distance between the functions

        Raises:
            ValueError: If evaluation points are invalid for the function domain
        """
        logger.debug("Computing function difference pseudometric distance")
        
        # Generate evaluation points if not provided
        if self.evaluation_points is None:
            logger.info("Generating evaluation points using Halton sequence")
            # Simple Halton sequence implementation for demonstration purposes
            import itertools
            points = list(itertools.islice(itertools.accumulate(itertools.count(1), lambda a, _: a / (a + 1)), 
                                         self.num_evaluation_points))
            self.evaluation_points = points
        
        total_difference = 0.0
        
        for point in self.evaluation_points:
            try:
                x_value = x(point)
                y_value = y(point)
                difference = abs(x_value - y_value)
                total_difference += difference
            except Exception as e:
                logger.error(f"Error evaluating functions at point {point}: {str(e)}")
                raise ValueError(f"Failed to evaluate functions at point {point}: {str(e)}")
        
        average_difference = total_difference / len(self.evaluation_points)
        logger.info(f"Computed average difference: {average_difference}")
        
        return average_difference

    def distances(self, xs: Sequence[Callable], ys: Sequence[Callable]) -> List[float]:
        """
        Computes pairwise pseudometric distances between two sequences of functions.

        Args:
            xs: Sequence[Callable]
                The first sequence of functions
            ys: Sequence[Callable]
                The second sequence of functions

        Returns:
            List[float]
                A list of computed pseudometric distances for each pair
        """
        logger.debug("Computing pairwise function distances")
        
        distances = []
        for x, y in zip(xs, ys):
            distances.append(self.distance(x, y))
            
        logger.info(f"Computed pairwise distances: {distances}")
        return distances

    def __str__(self) -> str:
        return f"FunctionDifferencePseudometric(evaluation_points={self.evaluation_points})"