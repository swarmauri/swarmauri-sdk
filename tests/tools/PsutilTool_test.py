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

@pytest.mark.unit
def test_call_cpu():
    tool = Tool()
    result = tool('cpu')
    assert 'cpu_times' in result
    assert 'cpu_percent' in result

@pytest.mark.unit
def test_call_memory():
    tool = Tool()
    result = tool('memory')
    assert 'virtual_memory' in result
    assert 'swap_memory' in result

@pytest.mark.unit
def test_call_disk():
    tool = Tool()
    result = tool('disk')
    assert 'disk_partitions' in result
    assert 'disk_usage' in result

@pytest.mark.unit
def test_call_network():
    tool = Tool()
    result = tool('network')
    assert 'network_io_counters' in result
    assert 'network_connections' in result

@pytest.mark.unit
def test_call_sensors():
    tool = Tool()
    result = tool('sensors')
    assert 'battery' in result
    assert 'temperatures' in result
    assert 'fan_speeds' in result
