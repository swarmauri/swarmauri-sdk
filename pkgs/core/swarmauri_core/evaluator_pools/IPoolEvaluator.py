from abc import ABC, abstractmethod
import logging
from typing import Sequence, Dict, Any, List, Callable, Optional

from swarmauri_core.evaluators.IEvaluate import IEvaluate
from swarmauri_core.programs.IProgram import IProgram
from swarmauri_core.evaluator_results.IEvalResult import IEvalResult

logger = logging.getLogger(__name__)


class EvaluationResult:
    """
    Container for evaluation results from a pool of evaluators.
    
    This class holds the results of evaluating a program with multiple evaluators,
    including the program, scores, and metadata from each evaluator.
    """
    
    def __init__(self, program: IProgram, scores: Dict[str, float], metadata: Dict[str, Dict[str, Any]]):
        """
        Initialize an evaluation result.
        
        Args:
            program: The program that was evaluated
            scores: Dictionary mapping evaluator names to their scores
            metadata: Dictionary mapping evaluator names to their metadata
        """
        self.program = program
        self.scores = scores
        self.metadata = metadata
        self.aggregate_score: Optional[float] = None


class IPoolEvaluator(ABC):
    """
    Interface for evaluator pools that manage sets of evaluators.
    
    This abstract class defines the contract for evaluator pools, providing methods
    for dynamic registration, execution, and aggregation of evaluators. Pools are
    responsible for coordinating the evaluation of programs across multiple evaluators
    and aggregating their results.
    """
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the evaluator pool and its resources.
        
        This method should be called before using the pool to set up any
        necessary resources, connections, or state.
        
        Raises:
            RuntimeError: If initialization fails
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """
        Shut down the evaluator pool and release its resources.
        
        This method should be called when the pool is no longer needed to
        clean up resources and ensure proper termination.
        
        Raises:
            RuntimeError: If shutdown fails
        """
        pass
    
    @abstractmethod
    def add_evaluator(self, evaluator: IEvaluate, name: Optional[str] = None) -> str:
        """
        Add an evaluator to the pool.
        
        Args:
            evaluator: The evaluator to add to the pool
            name: Optional name for the evaluator, if not provided a name will be generated
            
        Returns:
            The name assigned to the evaluator
            
        Raises:
            ValueError: If an evaluator with the same name already exists
            TypeError: If the evaluator doesn't implement IEvaluate
        """
        pass
    
    @abstractmethod
    def remove_evaluator(self, name: str) -> bool:
        """
        Remove an evaluator from the pool by name.
        
        Args:
            name: The name of the evaluator to remove
            
        Returns:
            True if the evaluator was removed, False if it wasn't found
        """
        pass
    
    @abstractmethod
    def evaluate_all(self, programs: Sequence[IProgram], **kwargs) -> Sequence[EvaluationResult]:
        """
        Evaluate all programs with all registered evaluators.
        
        This method runs each program through each evaluator and collects the results.
        
        Args:
            programs: The programs to evaluate
            **kwargs: Additional parameters to pass to evaluators
            
        Returns:
            A sequence of evaluation results, one for each program
            
        Raises:
            RuntimeError: If evaluation fails
        """
        pass
    
    @abstractmethod
    async def evaluate_async(self, programs: Sequence[IProgram], **kwargs) -> Sequence[EvaluationResult]:
        """
        Asynchronously evaluate all programs with all registered evaluators.
        
        This method runs each program through each evaluator concurrently and collects the results.
        
        Args:
            programs: The programs to evaluate
            **kwargs: Additional parameters to pass to evaluators
            
        Returns:
            A sequence of evaluation results, one for each program
            
        Raises:
            RuntimeError: If evaluation fails
        """
        pass
    
    @abstractmethod
    def aggregate(self, scores: Sequence[float]) -> float:
        """
        Aggregate multiple scores into a single score.
        
        This method combines multiple evaluation scores into a single scalar value
        according to the pool's aggregation strategy.
        
        Args:
            scores: The scores to aggregate
            
        Returns:
            The aggregated score
            
        Raises:
            ValueError: If scores is empty or contains invalid values
        """
        pass
    
    @abstractmethod
    def set_aggregation_function(self, func: Callable[[Sequence[float]], float]) -> None:
        """
        Set the function used to aggregate scores.
        
        Args:
            func: A function that takes a sequence of scores and returns an aggregated score
            
        Raises:
            TypeError: If func is not callable or has an invalid signature
        """
        pass
    
    @abstractmethod
    def get_evaluator(self, name: str) -> Optional[IEvaluate]:
        """
        Get an evaluator by name.
        
        Args:
            name: The name of the evaluator to retrieve
            
        Returns:
            The evaluator if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_evaluator_names(self) -> List[str]:
        """
        Get the names of all registered evaluators.
        
        Returns:
            A list of evaluator names
        """
        pass
    
    @abstractmethod
    def get_evaluator_count(self) -> int:
        """
        Get the number of registered evaluators.
        
        Returns:
            The count of evaluators in the pool
        """
        pass