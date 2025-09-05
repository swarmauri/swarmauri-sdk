import ast
import logging
import os
import re
from typing import Any, Dict, List, Literal, Tuple

from pydantic import Field
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.programs.IProgram import IProgram as Program

logger = logging.getLogger(__name__)


@ComponentBase.register_type(EvaluatorBase, "AnyTypeUsageEvaluator")
class AnyTypeUsageEvaluator(EvaluatorBase, ComponentBase):
    """
    Evaluator that detects and penalizes usage of the `Any` type in Python code.

    This evaluator parses Python source files to identify imports and usages of
    the `typing.Any` type. It counts occurrences and generates a penalty score
    proportional to the number of `Any` usages found in the code.
    """

    type: Literal["AnyTypeUsageEvaluator"] = "AnyTypeUsageEvaluator"
    penalty_per_occurrence: float = Field(
        default=0.1, description="Penalty score per Any occurrence"
    )
    max_penalty: float = Field(
        default=1.0, description="Maximum penalty that can be applied"
    )

    def _compute_score(
        self, program: Program, **kwargs
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Compute a score based on the usage of `Any` type in the program's files.

        Args:
            program: The program to evaluate
            **kwargs: Additional parameters for the evaluation process

        Returns:
            A tuple containing:
                - float: A scalar fitness score (1.0 = no Any usage, lower scores indicate Any usage)
                - Dict[str, Any]: Metadata about the evaluation, including file paths and line numbers
                  where Any is used
        """
        logger.info(f"Evaluating Any type usage in program: {program.name}")

        # Initialize result data
        any_occurrences = []
        total_occurrences = 0

        # Get all Python files in the program
        python_files = self._get_python_files(program)
        logger.debug(f"Found {len(python_files)} Python files to analyze")

        # Analyze each file for Any usage
        for file_path in python_files:
            file_occurrences = self._analyze_file_for_any(file_path)
            if file_occurrences:
                total_occurrences += len(file_occurrences)
                any_occurrences.append(
                    {"file": file_path, "occurrences": file_occurrences}
                )

        # Calculate penalty score (1.0 is best, lower is worse)
        penalty = min(self.max_penalty, total_occurrences * self.penalty_per_occurrence)
        score = 1.0 - penalty

        metadata = {
            "total_any_occurrences": total_occurrences,
            "detailed_occurrences": any_occurrences,
            "penalty_applied": penalty,
            "files_analyzed": len(python_files),
        }

        logger.info(
            f"Found {total_occurrences} Any type usages across {len(any_occurrences)} files"
        )
        return score, metadata

    def _get_python_files(self, program: Program) -> List[str]:
        """
        Get all Python files from the program's directory.

        Args:
            program: The program to evaluate

        Returns:
            A list of paths to Python files in the program
        """
        python_files = []

        # Get the program's root directory
        if hasattr(program, "path") and program.path:
            root_dir = program.path
        else:
            # Fallback to current directory if path is not available
            root_dir = os.getcwd()
            logger.warning(
                f"Program path not available, using current directory: {root_dir}"
            )

        # Walk through the directory and collect Python files
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith(".py"):
                    python_files.append(os.path.join(dirpath, filename))

        return python_files

    def _analyze_file_for_any(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Analyze a Python file for Any type usage.

        This method parses the file and looks for:
        1. Import statements like 'from typing import Any'
        2. Direct usage of 'Any' in type annotations

        Args:
            file_path: Path to the Python file to analyze

        Returns:
            A list of dictionaries containing line numbers and context for each Any occurrence
        """
        occurrences = []

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Parse the file with AST
            try:
                tree = ast.parse(content, filename=file_path)

                # Use a visitor to find Any usages in the AST
                visitor = AnyTypeVisitor()
                visitor.visit(tree)

                # Add AST-detected occurrences
                for line_no, context in visitor.any_occurrences:
                    occurrences.append({"line": line_no, "context": context})

                # Also perform regex search for cases the AST parser might miss
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    # Look for Any that's not part of a word (like "Anything")
                    # This regex looks for Any as a standalone word or in type annotations
                    matches = re.finditer(r"\bAny\b|\[Any\]|: Any|-> Any", line)
                    for match in matches:
                        # Check if this line is already recorded from AST parsing
                        if not any(occ["line"] == i + 1 for occ in occurrences):
                            occurrences.append({"line": i + 1, "context": line.strip()})

            except SyntaxError as e:
                logger.warning(f"Syntax error in file {file_path}: {str(e)}")
                # Even with syntax errors, try to find Any with regex
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if "Any" in line:
                        # Simple pattern matching for files with syntax errors
                        if re.search(r"\bAny\b", line):
                            occurrences.append({"line": i + 1, "context": line.strip()})

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")

        return occurrences


class AnyTypeVisitor(ast.NodeVisitor):
    """
    AST visitor that finds usages of the Any type in Python code.
    """

    def __init__(self):
        self.any_occurrences = []  # List of (line_number, context) tuples
        self.importing_any = False

    def visit_ImportFrom(self, node):
        """Visit import from statements to detect 'from typing import Any'."""
        if node.module == "typing":
            for name in node.names:
                if name.name == "Any":
                    self.any_occurrences.append(
                        (node.lineno, f"from typing import {name.name}")
                    )
                    self.importing_any = True
        self.generic_visit(node)

    def visit_Name(self, node):
        """Visit name nodes to find Any identifiers."""
        if node.id == "Any" and not isinstance(node.ctx, ast.Store):
            # Get the line of code for context
            context = "Any used as identifier"
            self.any_occurrences.append((node.lineno, context))
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        """Visit annotated assignments to find Any in type annotations."""
        # Check if the annotation contains Any
        if isinstance(node.annotation, ast.Name) and node.annotation.id == "Any":
            context = "variable: Any annotation"
            self.any_occurrences.append((node.lineno, context))
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Visit function definitions to find Any in return annotations."""
        if (
            node.returns
            and isinstance(node.returns, ast.Name)
            and node.returns.id == "Any"
        ):
            context = f"def {node.name}(...) -> Any"
            self.any_occurrences.append((node.lineno, context))
        self.generic_visit(node)

    def visit_arg(self, node):
        """Visit function arguments to find Any in parameter annotations."""
        if (
            node.annotation
            and isinstance(node.annotation, ast.Name)
            and node.annotation.id == "Any"
        ):
            context = f"parameter: {node.arg}: Any"
            self.any_occurrences.append((node.lineno, context))
        self.generic_visit(node)

    def visit_Subscript(self, node):
        """Visit subscripts to find Any in complex type annotations like List[Any]."""
        # Check for Any in subscripts like List[Any]
        if (
            isinstance(node.value, ast.Name)
            and isinstance(node.slice, ast.Name)
            and node.slice.id == "Any"
        ):
            context = f"Complex type with Any: {node.value.id}[Any]"
            self.any_occurrences.append((node.lineno, context))
        self.generic_visit(node)
