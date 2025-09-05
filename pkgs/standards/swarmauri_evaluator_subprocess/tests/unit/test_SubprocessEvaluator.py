import logging
import subprocess
from unittest.mock import ANY, MagicMock, patch

import pytest
from swarmauri_core.programs.IProgram import IProgram
from swarmauri_evaluator_subprocess.SubprocessEvaluator import SubprocessEvaluator

# Configure logger for tests
logger = logging.getLogger(__name__)


@pytest.fixture
def evaluator():
    """
    Fixture that provides a SubprocessEvaluator instance with default settings.

    Returns:
        SubprocessEvaluator: A configured evaluator instance
    """
    return SubprocessEvaluator()


@pytest.fixture
def mock_program():
    """
    Fixture that provides a mock Program object.

    Returns:
        MagicMock: A mock program object with the necessary methods
    """
    program = MagicMock(spec=IProgram)
    program.get_path = MagicMock()
    program.is_executable = MagicMock()
    return program


@pytest.mark.unit
def test_initialization():
    """Test that the evaluator initializes with default values."""
    evaluator = SubprocessEvaluator()

    assert evaluator.type == "SubprocessEvaluator"
    assert evaluator.timeout == 30.0
    assert evaluator.max_memory_mb == 512
    assert evaluator.max_processes == 64
    assert evaluator.max_file_size_mb == 10
    assert evaluator.working_dir is None
    assert evaluator.env_vars == {}
    assert evaluator.success_exit_codes == [0]
    assert evaluator.score_on_timeout == 0.0
    assert evaluator.score_on_error == 0.0


@pytest.mark.unit
def test_initialization_with_custom_values():
    """Test that the evaluator initializes with custom values."""
    evaluator = SubprocessEvaluator(
        timeout=10.0,
        max_memory_mb=256,
        max_processes=32,
        max_file_size_mb=5,
        working_dir="/tmp",
        env_vars={"TEST": "VALUE"},
        success_exit_codes=[0, 1],
        score_on_timeout=0.1,
        score_on_error=0.2,
    )

    assert evaluator.timeout == 10.0
    assert evaluator.max_memory_mb == 256
    assert evaluator.max_processes == 32
    assert evaluator.max_file_size_mb == 5
    assert evaluator.working_dir == "/tmp"
    assert evaluator.env_vars == {"TEST": "VALUE"}
    assert evaluator.success_exit_codes == [0, 1]
    assert evaluator.score_on_timeout == 0.1
    assert evaluator.score_on_error == 0.2


@pytest.mark.unit
def test_prepare_command_executable(mock_program, evaluator):
    """Test preparing command for an executable program."""
    # Configure mock for this specific test
    mock_program.get_path.return_value = "/path/to/program"
    mock_program.is_executable.return_value = True

    with (
        patch("os.path.exists", return_value=True),
        patch("os.access", return_value=True),
    ):
        cmd = evaluator._prepare_command(mock_program, ["arg1", "arg2"])

    assert cmd == ["/path/to/program", "arg1", "arg2"]


@pytest.mark.unit
def test_prepare_command_python_script(mock_program, evaluator):
    """Test preparing command for a Python script."""

    mock_program.get_path.return_value = "/path/to/script.py"
    mock_program.is_executable.return_value = False

    with patch("os.path.exists", return_value=True):
        cmd = evaluator._prepare_command(mock_program, ["arg1", "arg2"])

    assert cmd == ["python", "/path/to/script.py", "arg1", "arg2"]


@pytest.mark.unit
def test_prepare_command_shell_script(mock_program, evaluator):
    """Test preparing command for a shell script."""

    mock_program.get_path.return_value = "/path/to/script.sh"
    mock_program.is_executable.return_value = False

    with patch("os.path.exists", return_value=True):
        cmd = evaluator._prepare_command(mock_program, ["arg1", "arg2"])

    assert cmd == ["bash", "/path/to/script.sh", "arg1", "arg2"]


@pytest.mark.unit
def test_prepare_command_missing_program(mock_program):
    """Test preparing command for a non-existent program."""
    evaluator = SubprocessEvaluator()

    with patch("os.path.exists", return_value=False), pytest.raises(FileNotFoundError):
        evaluator._prepare_command(mock_program, [])


@pytest.mark.unit
def test_prepare_command_make_executable(mock_program, evaluator):
    """Test making a program executable if needed."""
    mock_program.get_path.return_value = "/path/to/program"
    mock_program.is_executable.return_value = True

    with (
        patch("os.path.exists", return_value=True),
        patch("os.access", return_value=False),
        patch("os.chmod") as mock_chmod,
    ):
        evaluator._prepare_command(mock_program, [])

        mock_chmod.assert_called_once_with("/path/to/program", 0o755)


@pytest.mark.unit
def test_calculate_score_success(evaluator):
    """Test score calculation for successful execution."""
    result = {"stdout": "output", "stderr": "", "exit_code": 0, "timed_out": False}

    score, metadata = evaluator._calculate_score(result, None, 1.5)

    assert score == 1.0
    assert metadata["reason"] == "success"
    assert metadata["execution_time"] == 1.5
    assert metadata["exit_code"] == 0


@pytest.mark.unit
def test_calculate_score_timeout():
    """Test score calculation for timed out execution."""
    evaluator = SubprocessEvaluator(score_on_timeout=0.1)
    result = {
        "stdout": "partial output",
        "stderr": "error",
        "exit_code": -1,
        "timed_out": True,
    }

    score, metadata = evaluator._calculate_score(result, None, 30.0)

    assert score == 0.1
    assert metadata["reason"] == "timeout"
    assert metadata["timed_out"] is True


@pytest.mark.unit
def test_calculate_score_exit_code_failure(evaluator):
    """Test score calculation for execution with non-success exit code."""
    result = {
        "stdout": "output",
        "stderr": "error message",
        "exit_code": 1,
        "timed_out": False,
    }

    score, metadata = evaluator._calculate_score(result, None, 1.0)

    assert score == 0.5
    assert metadata["reason"] == "exit_code_1"


@pytest.mark.unit
def test_calculate_score_output_mismatch(evaluator):
    """Test score calculation for execution with output mismatch."""
    result = {
        "stdout": "actual output",
        "stderr": "",
        "exit_code": 0,
        "timed_out": False,
    }

    score, metadata = evaluator._calculate_score(result, "expected output", 1.0)

    assert score == 0.7
    assert metadata["reason"] == "output_mismatch"
    assert metadata["output_match"] is False


@pytest.mark.unit
def test_calculate_score_output_match(evaluator):
    """Test score calculation for execution with matching output."""
    result = {
        "stdout": "expected output",
        "stderr": "",
        "exit_code": 0,
        "timed_out": False,
    }

    score, metadata = evaluator._calculate_score(result, "expected output", 1.0)

    assert score == 1.0
    assert metadata["reason"] == "success"
    assert metadata["output_match"] is True


@pytest.mark.unit
@patch("subprocess.Popen")
def test_execute_subprocess_success(mock_popen, evaluator):
    """Test successful subprocess execution."""
    mock_process = MagicMock()
    mock_process.communicate.return_value = ("stdout data", "stderr data")
    mock_process.returncode = 0
    mock_popen.return_value = mock_process

    result = evaluator._execute_subprocess(["echo", "test"], "input", 10.0, "/tmp")

    assert result["stdout"] == "stdout data"
    assert result["stderr"] == "stderr data"
    assert result["exit_code"] == 0
    assert result["timed_out"] is False
    mock_popen.assert_called_once()


@pytest.mark.unit
@patch("subprocess.Popen")
def test_execute_subprocess_timeout(mock_popen, evaluator):
    """Test subprocess execution with timeout."""
    mock_process = MagicMock()
    mock_process.communicate.side_effect = subprocess.TimeoutExpired(
        cmd="test", timeout=10
    )
    mock_process.returncode = None
    mock_popen.return_value = mock_process

    result = evaluator._execute_subprocess(["sleep", "100"], "", 10.0, "/tmp")

    assert result["exit_code"] == -1
    assert result["timed_out"] is True
    mock_process.kill.assert_called_once()


@pytest.mark.unit
@patch("subprocess.Popen")
def test_execute_subprocess_error(mock_popen, evaluator):
    """Test subprocess execution with error."""
    mock_popen.side_effect = Exception("Test error")

    result = evaluator._execute_subprocess(["invalid", "command"], "", 10.0, "/tmp")

    assert result["exit_code"] == -2
    assert "Execution error: Test error" in result["stderr"]


@pytest.mark.unit
@patch("tempfile.TemporaryDirectory")
@patch.object(SubprocessEvaluator, "_prepare_command")
@patch.object(SubprocessEvaluator, "_execute_subprocess")
@patch.object(SubprocessEvaluator, "_calculate_score")
def test_compute_score_success(
    mock_calculate, mock_execute, mock_prepare, mock_temp_dir, evaluator, mock_program
):
    """Test successful score computation."""
    mock_temp_dir.return_value.name = "/tmp/test_dir"
    mock_prepare.return_value = ["cmd", "arg"]
    mock_execute.return_value = {
        "stdout": "out",
        "stderr": "err",
        "exit_code": 0,
        "timed_out": False,
    }
    mock_calculate.return_value = (1.0, {"reason": "success"})

    score, metadata = evaluator._compute_score(
        mock_program, args=["arg"], input_data="input"
    )

    assert score == 1.0
    assert "command" in metadata
    assert metadata["command"] == ["cmd", "arg"]
    mock_prepare.assert_called_once_with(mock_program, ["arg"])
    mock_execute.assert_called_once()
    mock_calculate.assert_called_once()


@pytest.mark.unit
def test_compute_score_with_working_dir(evaluator, mock_program):
    """Test score computation with specified working directory."""
    evaluator.working_dir = "/custom/dir"

    with (
        patch.object(SubprocessEvaluator, "_prepare_command") as mock_prepare,
        patch.object(SubprocessEvaluator, "_execute_subprocess") as mock_execute,
        patch.object(SubprocessEvaluator, "_calculate_score") as mock_calculate,
    ):
        mock_prepare.return_value = ["cmd"]
        mock_execute.return_value = {
            "stdout": "",
            "stderr": "",
            "exit_code": 0,
            "timed_out": False,
        }
        mock_calculate.return_value = (1.0, {})

        evaluator._compute_score(mock_program)

        mock_execute.assert_called_once_with(
            ANY, input_data="", timeout=30.0, working_dir="/custom/dir"
        )


@pytest.mark.unit
def test_aggregate_scores(evaluator):
    """Test aggregation of multiple scores and metadata."""
    scores = [1.0, 0.5, 0.0]
    metadata_list = [
        {"reason": "success", "exit_code": 0, "timed_out": False},
        {"reason": "exit_code_1", "exit_code": 1, "timed_out": False},
        {"reason": "timeout", "exit_code": -1, "timed_out": True},
    ]

    score, metadata = evaluator.aggregate_scores(scores, metadata_list)

    assert score == 0.5  # Default is average
    assert metadata["reason_counts"] == {"success": 1, "exit_code_1": 1, "timeout": 1}
    assert metadata["timeout_rate"] == 1 / 3
    assert metadata["success_rate"] == 1 / 3
    assert metadata["total_executions"] == 3


@pytest.mark.unit
def test_aggregate_scores_empty(evaluator):
    """Test aggregation with empty inputs."""
    score, metadata = evaluator.aggregate_scores([], [])

    # Should use the base implementation which typically returns 0 for empty input
    assert isinstance(score, float)
    assert isinstance(metadata, dict)


@pytest.mark.unit
@pytest.mark.parametrize("custom_timeout", [10.0, 20.0, None])
def test_compute_score_custom_timeout(custom_timeout, evaluator, mock_program):
    """Test score computation with custom timeout."""
    with (
        patch.object(SubprocessEvaluator, "_prepare_command") as mock_prepare,
        patch.object(SubprocessEvaluator, "_execute_subprocess") as mock_execute,
        patch.object(SubprocessEvaluator, "_calculate_score") as mock_calculate,
        patch("tempfile.TemporaryDirectory") as mock_temp_dir,
    ):
        mock_temp_dir.return_value.name = "/tmp/test_dir"
        mock_prepare.return_value = ["cmd"]
        mock_execute.return_value = {
            "stdout": "",
            "stderr": "",
            "exit_code": 0,
            "timed_out": False,
        }
        mock_calculate.return_value = (1.0, {})

        kwargs = {}
        if custom_timeout is not None:
            kwargs["timeout"] = custom_timeout

        evaluator._compute_score(mock_program, **kwargs)

        expected_timeout = (
            custom_timeout if custom_timeout is not None else evaluator.timeout
        )
        mock_execute.assert_called_once_with(
            ANY, input_data="", timeout=expected_timeout, working_dir=ANY
        )


@pytest.mark.unit
def test_evaluator_serialization():
    """Test that the evaluator can be serialized and deserialized correctly."""
    evaluator = SubprocessEvaluator(
        timeout=15.0, max_memory_mb=256, env_vars={"TEST": "VALUE"}
    )

    # Serialize to JSON
    json_data = evaluator.model_dump_json()

    # Deserialize from JSON
    deserialized = SubprocessEvaluator.model_validate_json(json_data)

    # Check that the deserialized object has the same properties
    assert deserialized.timeout == 15.0
    assert deserialized.max_memory_mb == 256
    assert deserialized.env_vars == {"TEST": "VALUE"}
    assert deserialized.type == "SubprocessEvaluator"
