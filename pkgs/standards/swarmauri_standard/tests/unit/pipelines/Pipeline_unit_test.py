import pytest
from swarmauri_standard.pipelines.Pipeline import Pipeline
from swarmauri_core.pipelines.IPipeline import PipelineStatus


@pytest.fixture
def mock_task():
    """Fixture for a sample task"""

    def task(x):
        return x * 2

    return task


@pytest.fixture
def pipeline():
    """Fixture for a basic pipeline"""
    return Pipeline()


@pytest.fixture
def error_handler():
    """Fixture for a custom error handler"""

    def custom_error_handler(e):
        return f"Error handled: {str(e)}"

    return custom_error_handler


@pytest.mark.unit
def test_ubc_resource(pipeline):
    assert pipeline.resource == "Pipeline"


@pytest.mark.unit
def test_ubc_type(pipeline):
    assert pipeline.type == "Pipeline"


@pytest.mark.unit
def test_serialization(pipeline):
    serialized = pipeline.model_dump_json()
    deserialized = Pipeline.model_validate_json(serialized)
    assert deserialized.id == pipeline.id


# Test inherited methods
def test_add_task(pipeline, mock_task):
    """Test adding a task to the pipeline"""
    pipeline.add_task(mock_task, 5)
    assert len(pipeline.tasks) == 1
    assert pipeline.tasks[0]["callable"] == mock_task
    assert pipeline.tasks[0]["args"] == (5,)


def test_sequential_execution(pipeline, mock_task):
    """Test sequential execution of tasks"""
    pipeline.add_task(mock_task, 5)
    pipeline.add_task(mock_task, 10)

    results = pipeline.execute()
    assert results == [10, 20]
    assert pipeline.get_status() == PipelineStatus.COMPLETED


def test_parallel_execution(mock_task):
    """Test parallel execution of tasks"""
    pipeline = Pipeline(parallel=True)
    pipeline.add_task(mock_task, 5)
    pipeline.add_task(mock_task, 10)

    results = pipeline.execute()
    assert sorted(results) == [10, 20]
    assert pipeline.get_status() == PipelineStatus.COMPLETED


def test_reset_pipeline(pipeline, mock_task):
    """Test resetting the pipeline"""
    pipeline.add_task(mock_task, 5)
    pipeline.execute()

    pipeline.reset()
    assert pipeline.get_status() == PipelineStatus.PENDING
    assert pipeline.get_results() == []


def test_get_results(pipeline, mock_task):
    """Test getting pipeline results"""
    pipeline.add_task(mock_task, 5)
    pipeline.execute()

    results = pipeline.get_results()
    assert results == [10]


# Test error handling methods
def test_pipeline_error_handling(pipeline, error_handler):
    """Test pipeline execution with error handler"""

    def failing_task():
        raise ValueError("Task failed")

    pipeline.add_task(failing_task)
    pipeline = pipeline.with_error_handler(error_handler)

    result = pipeline.execute()
    assert isinstance(result, list)
    assert "Error handled" in result[0]
    assert pipeline.get_status() == PipelineStatus.FAILED


def test_pipeline_without_error_handler(pipeline):
    """Test pipeline execution without error handler"""

    def failing_task():
        raise ValueError("Task failed")

    pipeline.add_task(failing_task)

    with pytest.raises(RuntimeError):
        pipeline.execute()
    assert pipeline.get_status() == PipelineStatus.FAILED
