from unittest.mock import MagicMock, patch

import psutil
import pytest
from swarmauri.community.tools.concrete.PsutilTool import PsutilTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'PsutilTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.parametrize(
    "info_type, psutil_method, expected_key",
    [
        ('cpu', psutil.cpu_times, 'cpu_times'),
        ('memory', psutil.virtual_memory, 'virtual_memory'),
        ('disk', psutil.disk_partitions, 'disk_partitions'),
        ('network', psutil.net_io_counters, 'network_io_counters'),
        ('sensors', psutil.sensors_battery, 'battery'),
    ]
)
@pytest.mark.unit
def test_call(info_type, psutil_method, expected_key):
    tool = Tool()
    result = tool(info_type)

    if info_type == 'cpu':
        assert 'cpu_times' in result
        assert isinstance(result['cpu_times'], dict)
        assert 'cpu_percent' in result
        assert isinstance(result['cpu_percent'], float)
        assert 'cpu_count' in result
        assert isinstance(result['cpu_count'], int)
    elif info_type == 'memory':
        assert 'virtual_memory' in result
        assert isinstance(result['virtual_memory'], dict)
    elif info_type == 'disk':
        assert 'disk_partitions' in result
        assert isinstance(result['disk_partitions'], list)
    elif info_type == 'network':
        assert 'network_io_counters' in result
        assert isinstance(result['network_io_counters'], dict)
    elif info_type == 'sensors':
        assert 'battery' in result
        assert isinstance(result['battery'], dict)