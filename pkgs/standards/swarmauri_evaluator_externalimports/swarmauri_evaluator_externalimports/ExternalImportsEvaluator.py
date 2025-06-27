import ast
import logging
import os
import pkgutil
import sys
from typing import Any, Dict, List, Literal, Set, Tuple

from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.programs.IProgram import IProgram as Program

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class ExternalImportsEvaluator(EvaluatorBase):
    """
    Evaluator that detects and penalizes non-built-in Python imports in source files.

    This evaluator analyzes import statements to identify modules that are not part of
    the Python standard library. It helps to assess the external dependencies of a program.

    Attributes:
        type: The literal type identifier for this evaluator.
        standard_modules: A set of module names that are part of the Python standard library.
    """

    type: Literal["ExternalImportsEvaluator"] = "ExternalImportsEvaluator"
    standard_modules: Set[str] = set()

    def __init__(self, **data):
        """
        Initialize the ExternalImportsEvaluator.

        Args:
            **data: Additional initialization parameters.
        """
        super().__init__(**data)
        # Initialize the standard library modules set
        self._initialize_standard_modules()

    def _initialize_standard_modules(self) -> None:
        """
        Initialize the set of standard library modules.

        This method populates the standard_modules set with names of all modules
        from the Python standard library.
        """
        # Get all standard library modules
        self.standard_modules = {
            module.name for module in pkgutil.iter_modules(sys.stdlib_module_names)
        }

        # Add built-in modules
        self.standard_modules.update(sys.builtin_module_names)

        # Add some common standard library packages that might not be detected
        additional_std_libs = {
            "abc",
            "argparse",
            "ast",
            "asyncio",
            "collections",
            "concurrent",
            "contextlib",
            "copy",
            "csv",
            "datetime",
            "decimal",
            "email",
            "enum",
            "functools",
            "gzip",
            "hashlib",
            "http",
            "importlib",
            "inspect",
            "io",
            "itertools",
            "json",
            "logging",
            "math",
            "multiprocessing",
            "os",
            "pathlib",
            "pickle",
            "re",
            "shutil",
            "signal",
            "socket",
            "sqlite3",
            "string",
            "subprocess",
            "sys",
            "tempfile",
            "threading",
            "time",
            "traceback",
            "types",
            "typing",
            "unittest",
            "urllib",
            "uuid",
            "warnings",
            "xml",
            "zipfile",
        }
        self.standard_modules.update(additional_std_libs)

        logger.debug(
            f"Initialized with {len(self.standard_modules)} standard library modules"
        )

    def _is_standard_module(self, module_name: str) -> bool:
        """
        Check if a module is part of the Python standard library.

        Args:
            module_name: The name of the module to check.

        Returns:
            True if the module is part of the standard library, False otherwise.
        """
        # Check if the base module name is in standard modules
        base_module = module_name.split(".")[0]
        return base_module in self.standard_modules

    def _extract_imports(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract all import statements from a Python file.

        Args:
            file_path: Path to the Python file to analyze.

        Returns:
            A list of dictionaries containing information about each import.
        """
        imports = []

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                file_content = file.read()

            try:
                tree = ast.parse(file_content)

                for node in ast.walk(tree):
                    # Handle 'import module' statements
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports.append(
                                {
                                    "module": name.name,
                                    "alias": name.asname,
                                    "line": node.lineno,
                                    "is_standard": self._is_standard_module(name.name),
                                    "type": "import",
                                }
                            )

                    # Handle 'from module import name' statements
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module if node.module else ""
                        for name in node.names:
                            imports.append(
                                {
                                    "module": f"{module}.{name.name}"
                                    if module
                                    else name.name,
                                    "parent_module": module,
                                    "name": name.name,
                                    "alias": name.asname,
                                    "line": node.lineno,
                                    "is_standard": self._is_standard_module(module),
                                    "type": "importfrom",
                                }
                            )

            except SyntaxError as e:
                logger.warning(f"Syntax error in {file_path}: {str(e)}")
                imports.append({"error": str(e), "file": file_path})

        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            imports.append({"error": str(e), "file": file_path})

        return imports

    def _compute_score(
        self, program: Program, **kwargs
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Analyze a program's source files for external imports and compute a score.

        The score is inversely proportional to the number of external dependencies.
        A program with no external dependencies receives a perfect score of 1.0.

        Args:
            program: The program to evaluate.
            **kwargs: Additional parameters for the evaluation process.

        Returns:
            A tuple containing:
                - float: A scalar fitness score (1.0 is best, lower for more external imports)
                - Dict[str, Any]: Metadata about the evaluation, including detected imports
        """
        # Get all Python files in the program
        python_files = []
        for root, _, files in os.walk(program.path):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))

        logger.info(f"Analyzing {len(python_files)} Python files for external imports")

        # Extract imports from all files
        all_imports = []
        external_imports = []

        for file_path in python_files:
            relative_path = os.path.relpath(file_path, program.path)
            file_imports = self._extract_imports(file_path)

            for imp in file_imports:
                imp["file"] = relative_path
                all_imports.append(imp)

                # Collect external imports for detailed reporting
                if (
                    "is_standard" in imp
                    and not imp["is_standard"]
                    and "error" not in imp
                ):
                    external_imports.append(imp)

        # Count unique external modules
        unique_external_modules = set()
        for imp in external_imports:
            if imp["type"] == "import":
                # Extract the base module name for "import" statements
                module_name = imp["module"].split(".")[0]
                unique_external_modules.add(module_name)
            elif imp["type"] == "importfrom":
                # Extract the base module name for "from" statements
                module_name = (
                    imp["parent_module"].split(".")[0] if imp["parent_module"] else ""
                )
                if module_name:
                    unique_external_modules.add(module_name)

        # Calculate score - penalize for each unique external module
        # Base score is 1.0, subtract penalty for each external module
        num_external = len(unique_external_modules)
        base_score = 1.0
        penalty_per_module = 0.1  # Adjust this value to control severity

        # Ensure score doesn't go below 0
        score = max(0.0, base_score - (num_external * penalty_per_module))

        # Prepare metadata
        metadata = {
            "total_imports": len(all_imports),
            "external_imports_count": len(external_imports),
            "unique_external_modules": len(unique_external_modules),
            "external_modules": list(unique_external_modules),
            "external_imports_details": external_imports,
            "files_analyzed": len(python_files),
            "python_files": python_files,
        }

        logger.info(
            f"Found {len(external_imports)} external imports from {len(unique_external_modules)} unique modules"
        )

        return score, metadata
