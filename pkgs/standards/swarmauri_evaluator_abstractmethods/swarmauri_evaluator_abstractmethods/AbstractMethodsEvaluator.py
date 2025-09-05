import ast
import logging
from typing import Any, Dict, List, Literal, Tuple

from pydantic import Field
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.programs.IProgram import IProgram as Program

logger = logging.getLogger(__name__)


@ComponentBase.register_type(EvaluatorBase, "AbstractMethodsEvaluator")
class AbstractMethodsEvaluator(EvaluatorBase, ComponentBase):
    """
    Evaluator that verifies all methods in abstract base classes are properly marked as abstract.

    This evaluator parses Python source code to identify classes that inherit from ABC
    (Abstract Base Class) and verifies that all methods defined in these classes are
    decorated with @abstractmethod. It helps enforce proper interface design by ensuring
    that abstract classes properly declare their contract.
    """

    type: Literal["AbstractMethodsEvaluator"] = "AbstractMethodsEvaluator"

    # Configuration fields
    ignore_private: bool = Field(
        default=True, description="Whether to ignore private methods (starting with _)"
    )

    ignore_dunder: bool = Field(
        default=True,
        description="Whether to ignore dunder methods (starting and ending with __)",
    )

    abc_base_classes: List[str] = Field(
        default=["ABC", "abc.ABC"],
        description="List of base class names that indicate an abstract class",
    )

    def _compute_score(
        self, program: Program, **kwargs
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Computes a score based on proper use of @abstractmethod in abstract base classes.

        The score is calculated as the ratio of properly decorated abstract methods
        to the total number of methods that should be abstract. A score of 1.0 means
        all methods in abstract classes are properly decorated.

        Args:
            program: The program to evaluate
            **kwargs: Additional parameters for the evaluation process

        Returns:
            A tuple containing:
                - float: A scalar fitness score (1.0 for perfect compliance)
                - Dict[str, Any]: Metadata about the evaluation including issues found
        """
        # Get source code from the program
        source_files = program.get_source_files()

        # Track issues found
        issues = []
        total_abstract_classes = 0
        total_methods = 0
        total_abstract_methods = 0
        total_missing_decorators = 0

        # Process each source file
        for file_path, source_code in source_files.items():
            file_issues = self._check_file(file_path, source_code)

            if file_issues:
                issues.extend(file_issues)
                total_abstract_classes += len(
                    {issue["class_name"] for issue in file_issues}
                )
                total_methods += len(file_issues)
                total_missing_decorators += len(
                    [i for i in file_issues if not i["has_abstractmethod"]]
                )

        total_abstract_methods = total_methods - total_missing_decorators

        # Calculate score (1.0 is perfect, 0.0 is worst)
        score = 1.0
        if total_methods > 0:
            score = total_abstract_methods / total_methods

        # Prepare metadata
        metadata = {
            "issues": issues,
            "total_abstract_classes": total_abstract_classes,
            "total_methods": total_methods,
            "total_abstract_methods": total_abstract_methods,
            "total_missing_decorators": total_missing_decorators,
            "percentage_compliant": score * 100,
        }

        return score, metadata

    def _check_file(self, file_path: str, source_code: str) -> List[Dict[str, Any]]:
        """
        Analyzes a Python source file for abstract method compliance.

        Parses the abstract syntax tree of the source code to identify classes
        inheriting from ABC and checks if their methods are properly decorated.

        Args:
            file_path: Path to the source file
            source_code: Source code content as string

        Returns:
            List of dictionaries describing issues found in the file
        """
        issues = []

        try:
            # Parse the source code into an AST
            tree = ast.parse(source_code)

            # Find all class definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if this class inherits from ABC
                    if self._is_abstract_class(node):
                        # Check all methods in the class
                        for method_node in [
                            n for n in node.body if isinstance(n, ast.FunctionDef)
                        ]:
                            # Skip methods based on configuration
                            method_name = method_node.name
                            if (
                                self.ignore_dunder
                                and method_name.startswith("__")
                                and method_name.endswith("__")
                            ) or (
                                self.ignore_private
                                and method_name.startswith("_")
                                and not method_name.startswith("__")
                            ):
                                continue

                            # Check if the method has @abstractmethod decorator
                            has_abstractmethod = self._has_abstractmethod_decorator(
                                method_node
                            )

                            # If not abstract, add to issues
                            if not has_abstractmethod:
                                issues.append(
                                    {
                                        "file": file_path,
                                        "line": method_node.lineno,
                                        "class_name": node.name,
                                        "method_name": method_name,
                                        "has_abstractmethod": has_abstractmethod,
                                        "message": f"Method '{method_name}' in abstract class '{node.name}' should be decorated with @abstractmethod",
                                    }
                                )
                            else:
                                # Include properly decorated methods for completeness
                                issues.append(
                                    {
                                        "file": file_path,
                                        "line": method_node.lineno,
                                        "class_name": node.name,
                                        "method_name": method_name,
                                        "has_abstractmethod": has_abstractmethod,
                                        "message": f"Method '{method_name}' in abstract class '{node.name}' is properly decorated",
                                    }
                                )

        except SyntaxError as e:
            logger.error(f"Syntax error in file {file_path}: {str(e)}")
            issues.append(
                {
                    "file": file_path,
                    "line": getattr(e, "lineno", 0),
                    "class_name": "",
                    "method_name": "",
                    "has_abstractmethod": False,
                    "message": f"Syntax error: {str(e)}",
                }
            )
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            issues.append(
                {
                    "file": file_path,
                    "line": 0,
                    "class_name": "",
                    "method_name": "",
                    "has_abstractmethod": False,
                    "message": f"Error analyzing file: {str(e)}",
                }
            )

        return issues

    def _is_abstract_class(self, class_node: ast.ClassDef) -> bool:
        """
        Determines if a class is an abstract base class.

        Checks if the class inherits from ABC or any other configured abstract base classes.

        Args:
            class_node: AST node representing a class definition

        Returns:
            True if the class is an abstract base class, False otherwise
        """
        for base in class_node.bases:
            # Check direct inheritance from ABC
            if isinstance(base, ast.Name) and base.id in self.abc_base_classes:
                return True

            # Check for qualified names like abc.ABC
            if isinstance(base, ast.Attribute):
                full_name = self._get_full_name(base)
                if full_name in self.abc_base_classes:
                    return True

        return False

    def _get_full_name(self, node: ast.Attribute) -> str:
        """
        Constructs the full qualified name from an attribute node.

        For example, converts an AST representation of 'abc.ABC' into the string 'abc.ABC'.

        Args:
            node: AST attribute node

        Returns:
            String representation of the qualified name
        """
        parts = []
        current = node

        # Traverse up the attribute chain
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            parts.append(current.id)

        # Reverse and join with dots
        return ".".join(reversed(parts))

    def _has_abstractmethod_decorator(self, method_node: ast.FunctionDef) -> bool:
        """
        Checks if a method has the @abstractmethod decorator.

        Examines the decorators of a method to determine if it's marked as abstract.

        Args:
            method_node: AST node representing a function definition

        Returns:
            True if the method has @abstractmethod decorator, False otherwise
        """
        for decorator in method_node.decorator_list:
            # Simple decorator: @abstractmethod
            if isinstance(decorator, ast.Name) and decorator.id == "abstractmethod":
                return True

            # Qualified decorator: @abc.abstractmethod
            if isinstance(decorator, ast.Attribute):
                full_name = self._get_full_name(decorator)
                if full_name == "abc.abstractmethod":
                    return True

        return False

    def aggregate_scores(
        self, scores: List[float], metadata_list: List[Dict[str, Any]]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Aggregates multiple evaluation scores and their metadata.

        Combines scores from multiple evaluations and aggregates their metadata
        to provide a comprehensive overview of abstract method compliance.

        Args:
            scores: List of individual scores to aggregate
            metadata_list: List of metadata dictionaries corresponding to each score

        Returns:
            A tuple containing:
                - float: The aggregated score (average)
                - Dict[str, Any]: Aggregated metadata
        """
        if not scores:
            return 0.0, {"error": "No scores to aggregate"}

        # Default aggregation is to average the scores
        aggregated_score = sum(scores) / len(scores)

        # Combine all issues from all evaluations
        all_issues = []
        total_abstract_classes = 0
        total_methods = 0
        total_abstract_methods = 0
        total_missing_decorators = 0

        for metadata in metadata_list:
            all_issues.extend(metadata.get("issues", []))
            total_abstract_classes += metadata.get("total_abstract_classes", 0)
            total_methods += metadata.get("total_methods", 0)
            total_abstract_methods += metadata.get("total_abstract_methods", 0)
            total_missing_decorators += metadata.get("total_missing_decorators", 0)

        # Create aggregated metadata
        aggregated_metadata = {
            "individual_scores": scores,
            "aggregation_method": "average",
            "score_count": len(scores),
            "issues": all_issues,
            "total_abstract_classes": total_abstract_classes,
            "total_methods": total_methods,
            "total_abstract_methods": total_abstract_methods,
            "total_missing_decorators": total_missing_decorators,
            "percentage_compliant": aggregated_score * 100,
        }

        return aggregated_score, aggregated_metadata
