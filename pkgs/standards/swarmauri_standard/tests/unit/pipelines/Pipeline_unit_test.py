import logging
import pytest
from swarmauri_standard.pipelines.Pipeline import Pipeline
from swarmauri_core.pipelines.IPipeline import PipelineStatus


@pytest.fixture(scope="module")
def simple_tasks():
    def task1():
        return "Task 1 completed"

    def task2(x):
        return f"Task 2 with {x}"

    def task3(x, y):
        return x + y

    return [task1, task2, task3]


@pytest.fixture(scope="module")
def pipeline(simple_tasks):
    pipeline = Pipeline()
    pipeline.add_task(simple_tasks[0])
    pipeline.add_task(simple_tasks[1], "parameter")
    pipeline.add_task(simple_tasks[2], 10, 20)
    return pipeline


@pytest.mark.unit
def test_ubc_resource(pipeline):
    assert pipeline.resource == "Pipeline"


@pytest.mark.unit
def test_ubc_type(pipeline):
    assert pipeline.type == "Pipeline"


@pytest.mark.unit
def test_serialization(pipeline):
    logging.info(pipeline)
    assert pipeline.id == Pipeline.model_validate_json(pipeline.model_dump_json()).id


@pytest.mark.unit
def test_pipeline_initial_status(pipeline):
    assert pipeline.get_status() == PipelineStatus.PENDING


@pytest.mark.unit
def test_pipeline_execution(pipeline):
    results = pipeline.execute()

    assert len(results) == 3
    assert results[0] == "Task 1 completed"
    assert results[1] == "Task 2 with parameter"
    assert results[2] == 30
    assert pipeline.get_status() == PipelineStatus.COMPLETED


@pytest.mark.unit
def test_pipeline_reset(pipeline):
    pipeline.reset()
    assert pipeline.get_status() == PipelineStatus.PENDING
    assert len(pipeline.get_results()) == 0


@pytest.mark.unit
def test_pipeline_add_task(simple_tasks):
    pipeline = Pipeline()
    initial_task_count = len(pipeline.tasks)

    pipeline.add_task(simple_tasks[0])
    assert len(pipeline.tasks) == initial_task_count + 1


@pytest.mark.unit
def test_pipeline_get_results(simple_tasks):
    pipeline = Pipeline()
    pipeline.add_task(simple_tasks[0])
    pipeline.execute()

    results = pipeline.get_results()
    assert len(results) == 1
    assert results[0] == "Task 1 completed"
