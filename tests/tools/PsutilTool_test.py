from unittest.mock import MagicMock, patch

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


mock_cpu_data = {
    "cpu_times": {'user': 1000.0, 'system': 500.0, 'idle': 10000.0},
    "cpu_percent": 10.0,
    "cpu_times_per_cpu": [{'user': 500.0, 'system': 250.0, 'idle': 5000.0}],
    "cpu_count": 4,
    "cpu_frequency": {'current': 2400.0, 'min': 800.0, 'max': 4000.0},
    "cpu_stats": {'ctx_switches': 1000, 'interrupts': 500, 'soft_interrupts': 300, 'syscalls': 200},
}

mock_memory_data = {
    "virtual_memory": {'total': 8589934592, 'available': 4294967296, 'percent': 50.0, 'used': 4294967296,
                       'free': 2147483648},
    "swap_memory": {'total': 4294967296, 'used': 2147483648, 'free': 2147483648, 'percent': 50.0},
}

mock_disk_data = {
    "disk_partitions": [{'device': '/dev/sda1', 'mountpoint': '/', 'fstype': 'ext4', 'opts': 'rw,relatime'}],
    "disk_usage": {'/dev/sda1': {'total': 1000000000, 'used': 500000000, 'free': 500000000, 'percent': 50.0}},
    "disk_io_counters": {'read_count': 1000, 'write_count': 500, 'read_bytes': 1000000, 'write_bytes': 500000},
}

mock_network_data = {
    "network_io_counters": {'bytes_sent': 1000000, 'bytes_recv': 1000000, 'packets_sent': 1000, 'packets_recv': 1000},
    "network_connections": [
        {'fd': 10, 'family': 2, 'type': 1, 'laddr': ('127.0.0.1', 8080), 'raddr': ('127.0.0.1', 8081),
         'status': 'ESTABLISHED'}],
    "network_interfaces": {'lo': [{'family': 2, 'address': '127.0.0.1', 'netmask': '255.0.0.0', 'broadcast': None}]},
    "interface_addresses": {'lo': [{'family': 2, 'address': '127.0.0.1', 'netmask': '255.0.0.0', 'broadcast': None}]},
}

mock_sensors_data = {
    "battery": {'percent': 80, 'secsleft': 1000, 'power_plugged': False},
    "temperatures": {'coretemp': [{'label': 'Core 0', 'current': 42.0, 'high': 80.0, 'critical': 100.0}]},
    "fan_speeds": {'fan1': [{'label': 'Fan1', 'current': 1200}]},
}


@pytest.mark.parametrize(
    "info_type, expected_output",
    [
        ('cpu', mock_cpu_data),
        ('memory', mock_memory_data),
        ('disk', mock_disk_data),
        ('network', mock_network_data),
        ('sensors', mock_sensors_data),
    ]
)
@pytest.mark.unit
def test_call(info_type, expected_output):
    tool = Tool()

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
