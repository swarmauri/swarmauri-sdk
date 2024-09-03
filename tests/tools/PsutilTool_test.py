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

    with patch('psutil.cpu_times', return_value=MagicMock(_asdict=lambda: mock_cpu_data['cpu_times'])), \
            patch('psutil.cpu_percent', return_value=mock_cpu_data['cpu_percent']), \
            patch('psutil.cpu_times',
                  return_value=[MagicMock(_asdict=lambda: cpu) for cpu in mock_cpu_data['cpu_times_per_cpu']]), \
            patch('psutil.cpu_count', return_value=mock_cpu_data['cpu_count']), \
            patch('psutil.cpu_freq', return_value=MagicMock(_asdict=lambda: mock_cpu_data['cpu_frequency'])), \
            patch('psutil.cpu_stats', return_value=MagicMock(_asdict=lambda: mock_cpu_data['cpu_stats'])), \
            patch('psutil.virtual_memory', return_value=MagicMock(_asdict=lambda: mock_memory_data['virtual_memory'])), \
            patch('psutil.swap_memory', return_value=MagicMock(_asdict=lambda: mock_memory_data['swap_memory'])), \
            patch('psutil.disk_partitions', return_value=[MagicMock(_asdict=lambda: partition) for partition in
                                                          mock_disk_data['disk_partitions']]), \
            patch('psutil.disk_usage',
                  return_value=MagicMock(_asdict=lambda: list(mock_disk_data['disk_usage'].values())[0])), \
            patch('psutil.disk_io_counters',
                  return_value=MagicMock(_asdict=lambda: mock_disk_data['disk_io_counters'])), \
            patch('psutil.net_io_counters',
                  return_value=MagicMock(_asdict=lambda: mock_network_data['network_io_counters'])), \
            patch('psutil.net_connections',
                  return_value=[MagicMock(_asdict=lambda: conn) for conn in mock_network_data['network_connections']]), \
            patch('psutil.net_if_addrs', return_value={
                'lo': [MagicMock(_asdict=lambda: addr) for addr in mock_network_data['network_interfaces']['lo']]}), \
            patch('psutil.sensors_battery', return_value=MagicMock(_asdict=lambda: mock_sensors_data['battery'])), \
            patch('psutil.sensors_temperatures', return_value={'coretemp': [MagicMock(_asdict=lambda: temp) for temp in
                                                                            mock_sensors_data['temperatures'][
                                                                                'coretemp']]}), \
            patch('psutil.sensors_fans', return_value={
                'fan1': [MagicMock(_asdict=lambda: fan) for fan in mock_sensors_data['fan_speeds']['fan1']]}):
        result = tool(info_type)
        assert result == expected_output, f"Expected {expected_output}, but got {result}"
