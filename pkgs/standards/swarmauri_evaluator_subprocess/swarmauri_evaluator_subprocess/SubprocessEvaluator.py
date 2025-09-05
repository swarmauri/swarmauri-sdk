import logging
import os
import resource
import shlex
import signal
import subprocess
import tempfile
import time
from typing import Any, Dict, List, Literal, Optional, Tuple

from pydantic import Field
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.programs.IProgram import IProgram as Program

logger = logging.getLogger(__name__)


# this is only good for python 3.13+
@ComponentBase.register_model()
class SubprocessEvaluator(EvaluatorBase):
    """
    Evaluator that runs programs in isolated subprocesses and measures their performance.

    This evaluator executes programs in sandboxed subprocesses, capturing stdout, stderr,
    exit code, and runtime metrics. It provides security through resource limits and
    timeout constraints to prevent malicious or poorly written code from affecting
    the host system.
    """

    type: Literal["SubprocessEvaluator"] = "SubprocessEvaluator"

    # Execution constraints
    timeout: float = Field(
        default=30.0, description="Maximum execution time in seconds"
    )
    max_memory_mb: int = Field(default=512, description="Maximum memory usage in MB")
    max_processes: int = Field(default=64, description="Maximum number of processes")
    max_file_size_mb: int = Field(default=10, description="Maximum file size in MB")
    working_dir: Optional[str] = Field(
        default=None, description="Working directory for execution"
    )
    env_vars: Dict[str, str] = Field(
        default_factory=dict, description="Environment variables for the subprocess"
    )

    # Scoring parameters
    success_exit_codes: List[int] = Field(
        default=[0], description="Exit codes considered successful"
    )
    score_on_timeout: float = Field(
        default=0.0, description="Score to assign on timeout"
    )
    score_on_error: float = Field(
        default=0.0, description="Score to assign on execution error"
    )

    def _compute_score(
        self, program: Program, **kwargs
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Execute the program in a subprocess and compute a score based on its performance.

        Args:
            program: The program to evaluate
            **kwargs: Additional parameters that may include:
                - args: List of command-line arguments to pass to the program
                - input_data: String to provide as stdin to the program
                - expected_output: Expected stdout for comparison
                - custom_timeout: Override the default timeout value

        Returns:
            A tuple containing:
                - float: A scalar fitness score (1.0 for success, lower for failures)
                - Dict[str, Any]: Metadata about the execution including stdout, stderr,
                  exit code, and runtime information
        """
        # Extract additional parameters
        args = kwargs.get("args", [])
        input_data = kwargs.get("input_data", "")
        expected_output = kwargs.get("expected_output", None)
        custom_timeout = kwargs.get("timeout", self.timeout)

        # Prepare command based on program type
        cmd = self._prepare_command(program, args)

        # Create a temporary working directory if none specified
        use_temp_dir = self.working_dir is None
        working_dir = self.working_dir

        if use_temp_dir:
            temp_dir = tempfile.TemporaryDirectory()
            working_dir = temp_dir.name
            logger.debug(f"Created temporary working directory: {working_dir}")

        try:
            # Execute the program in a subprocess with resource limits
            start_time = time.time()
            result = self._execute_subprocess(
                cmd,
                input_data=input_data,
                timeout=custom_timeout,
                working_dir=working_dir,
            )
            execution_time = time.time() - start_time

            # Calculate score based on execution results
            score, metadata = self._calculate_score(
                result, expected_output, execution_time
            )

            # Add program and execution details to metadata
            metadata.update(
                {
                    "command": cmd,
                    "args": args,
                    "working_dir": working_dir,
                }
            )

            return score, metadata

        except Exception as e:
            logger.error(f"Error during program execution: {str(e)}")
            return self.score_on_error, {
                "error": str(e),
                "command": cmd,
                "args": args,
                "working_dir": working_dir,
            }
        finally:
            # Clean up temporary directory if we created one
            if use_temp_dir:
                temp_dir.cleanup()
                logger.debug(f"Cleaned up temporary working directory: {working_dir}")

    def _prepare_command(self, program: Program, args: List[str]) -> List[str]:
        """
        Prepare the command to execute based on the program type.

        Args:
            program: The program to execute
            args: Additional command-line arguments

        Returns:
            List of command components ready for subprocess execution
        """
        # Get the program path
        program_path = program.get_path()

        if not program_path:
            raise ValueError("Program path is not available")

        if not os.path.exists(program_path):
            raise FileNotFoundError(f"Program file not found: {program_path}")

        # Make executable if needed
        if not os.access(program_path, os.X_OK) and program.is_executable():
            os.chmod(program_path, 0o755)
            logger.debug(f"Made program file executable: {program_path}")

        # Determine the appropriate command based on file type
        if program.is_executable():
            # Direct executable
            cmd = [program_path] + args
        elif program_path.endswith(".py"):
            # Python script
            cmd = ["python", program_path] + args
        elif program_path.endswith(".sh"):
            # Shell script
            cmd = ["bash", program_path] + args
        else:
            # Default to executing directly with arguments
            cmd = [program_path] + args

        logger.debug(f"Prepared command: {' '.join(cmd)}")
        return cmd

    def _execute_subprocess(
        self,
        cmd: List[str],
        input_data: str = "",
        timeout: float = None,
        working_dir: str = None,
    ) -> Dict[str, Any]:
        """
        Execute a command in a sandboxed subprocess with resource limits.

        Args:
            cmd: Command to execute as a list of strings
            input_data: Data to provide to the process via stdin
            timeout: Maximum execution time in seconds
            working_dir: Working directory for the subprocess

        Returns:
            Dictionary containing execution results including stdout, stderr, and exit code
        """

        # Set resource limits in a preexec function
        def limit_resources():
            # Set CPU time limit (slightly less than wall time)
            if timeout:
                resource.setrlimit(
                    resource.RLIMIT_CPU, (int(timeout * 0.9), int(timeout))
                )

            # Set memory limit
            memory_bytes = self.max_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

            # Set file size limit
            file_size_bytes = self.max_file_size_mb * 1024 * 1024
            resource.setrlimit(
                resource.RLIMIT_FSIZE, (file_size_bytes, file_size_bytes)
            )

            # Set process limit
            resource.setrlimit(
                resource.RLIMIT_NPROC, (self.max_processes, self.max_processes)
            )

            # Ignore keyboard interrupt in subprocess
            signal.signal(signal.SIGINT, signal.SIG_IGN)

        # Prepare environment
        env = os.environ.copy()
        env.update(self.env_vars)

        # Log execution attempt
        cmd_str = " ".join(shlex.quote(arg) for arg in cmd)
        logger.debug(f"Executing: {cmd_str}")
        logger.debug(f"Working directory: {working_dir}")

        # Execute the subprocess
        process = None
        stdout_data = ""
        stderr_data = ""
        exit_code = None
        timed_out = False

        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=working_dir,
                env=env,
                preexec_fn=limit_resources,
                text=True,
                bufsize=1,
            )

            # Communicate with the process, respecting timeout
            stdout_data, stderr_data = process.communicate(
                input=input_data, timeout=timeout
            )
            exit_code = process.returncode

        except subprocess.TimeoutExpired:
            if process:
                # Kill the process and all its children
                try:
                    process.kill()
                    # Attempt to collect any output that was produced before timeout
                    stdout_data, stderr_data = process.communicate()
                except Exception as e:
                    logger.warning(f"Error while killing timed-out process: {e}")

            timed_out = True
            exit_code = -1  # Use -1 to indicate timeout
            logger.warning(f"Process timed out after {timeout} seconds")

        except Exception as e:
            if process and process.poll() is None:
                try:
                    process.kill()
                except Exception:
                    pass

            logger.error(f"Error during subprocess execution: {str(e)}")
            exit_code = -2  # Use -2 to indicate execution error
            stderr_data = f"{stderr_data}\nExecution error: {str(e)}"

        return {
            "stdout": stdout_data,
            "stderr": stderr_data,
            "exit_code": exit_code,
            "timed_out": timed_out,
        }

    def _calculate_score(
        self,
        result: Dict[str, Any],
        expected_output: Optional[str],
        execution_time: float,
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate a score based on execution results.

        Args:
            result: Dictionary containing execution results
            expected_output: Expected output for comparison (if provided)
            execution_time: Time taken for execution in seconds

        Returns:
            A tuple containing:
                - float: Score between 0.0 and 1.0
                - Dict: Metadata with detailed evaluation metrics
        """
        metadata = {
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "exit_code": result["exit_code"],
            "execution_time": execution_time,
            "timed_out": result["timed_out"],
        }

        # Handle timeout case
        if result["timed_out"]:
            logger.warning("Program execution timed out")
            return self.score_on_timeout, {**metadata, "reason": "timeout"}

        # Check exit code
        exit_code = result["exit_code"]
        exit_code_success = exit_code in self.success_exit_codes

        if not exit_code_success:
            logger.debug(f"Program exited with non-success code: {exit_code}")
            return 0.5, {**metadata, "reason": f"exit_code_{exit_code}"}

        # If expected output is provided, compare with actual output
        if expected_output is not None:
            output_match = expected_output.strip() == result["stdout"].strip()
            metadata["output_match"] = output_match

            if not output_match:
                return 0.7, {**metadata, "reason": "output_mismatch"}

        # If we get here, the program executed successfully
        return 1.0, {**metadata, "reason": "success"}

    def aggregate_scores(
        self, scores: List[float], metadata_list: List[Dict[str, Any]]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Aggregate multiple evaluation scores and their metadata.

        This implementation extends the base aggregation with subprocess-specific metrics.

        Args:
            scores: List of individual scores to aggregate
            metadata_list: List of metadata dictionaries corresponding to each score

        Returns:
            A tuple containing:
                - float: The aggregated score
                - Dict[str, Any]: Aggregated metadata with execution statistics
        """
        # Use the base implementation for basic aggregation
        aggregated_score, aggregated_metadata = super().aggregate_scores(
            scores, metadata_list
        )

        # Add subprocess-specific aggregated metrics
        if metadata_list:
            # Count success/failure reasons
            reason_counts = {}
            for meta in metadata_list:
                reason = meta.get("reason", "unknown")
                reason_counts[reason] = reason_counts.get(reason, 0) + 1

            # Calculate timeout rate
            timeout_count = sum(
                1 for meta in metadata_list if meta.get("timed_out", False)
            )
            timeout_rate = timeout_count / len(metadata_list) if metadata_list else 0

            # Calculate exit code statistics
            exit_codes = [
                meta.get("exit_code") for meta in metadata_list if "exit_code" in meta
            ]
            success_exit_count = sum(
                1 for code in exit_codes if code in self.success_exit_codes
            )
            success_rate = success_exit_count / len(exit_codes) if exit_codes else 0

            # Add to aggregated metadata
            aggregated_metadata.update(
                {
                    "reason_counts": reason_counts,
                    "timeout_rate": timeout_rate,
                    "success_rate": success_rate,
                    "total_executions": len(metadata_list),
                }
            )

        return aggregated_score, aggregated_metadata
