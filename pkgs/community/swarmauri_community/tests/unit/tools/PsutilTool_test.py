import pytest
from swarmauri_community.tools.concrete.PsutilTool import PsutilTool as Tool


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "PsutilTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.parametrize(
    "info_type, expected_keys, should_raise",
    [
        (
            "cpu",
            [
                "cpu_times",
                "cpu_percent",
                "cpu_times_per_cpu",
                "cpu_count",
                "cpu_frequency",
                "cpu_stats",
            ],
            False,
        ),
        ("memory", ["virtual_memory", "swap_memory"], False),
        ("disk", ["disk_partitions", "disk_usage", "disk_io_counters"], False),
        (
            "network",
            ["network_io_counters", "network_connections", "network_interfaces"],
            False,
        ),
        ("sensors", ["battery", "temperatures", "fan_speeds"], False),
        ("invalid", [], True),  # This is the invalid case
    ],
)
@pytest.mark.unit
def test_call(info_type, expected_keys, should_raise):
    tool = Tool()
    if should_raise:
        with pytest.raises(ValueError, match=r"Invalid info_type 'invalid' specified"):
            tool(info_type=info_type)
    else:
        result = tool(info_type=info_type)
        assert isinstance(
            result, dict
        ), f"Expected result for {info_type} to be a dictionary"
        for key in expected_keys:
            assert key in result, f"Expected '{key}' in the result for {info_type}"
