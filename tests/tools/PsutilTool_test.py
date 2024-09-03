from unittest.mock import MagicMock, patch
import pytest
import psutil
from swarmauri.community.tools.concrete.PsutilTool import PsutilTool as Tool

# Mock data
mock_cpu_data = {
    'cpu_times': {
        'user': 1.23,
        'system': 0.45,
        'idle': 2.34,
        'interrupt': 0.01,
        'dpc': 0.02
    },
    'cpu_percent': 55.0,
    'cpu_times_per_cpu': [
        {'user': 1.23, 'system': 0.45, 'idle': 2.34},
        {'user': 1.30, 'system': 0.50, 'idle': 2.40}
    ],
    'cpu_count': 4,
    'cpu_frequency': {'current': 2.5, 'min': 1.2, 'max': 3.5},
    'cpu_stats': {'ctx_switches': 12345, 'interrupts': 67890, 'soft_interrupts': 23456}
}

mock_memory_data = {
    'virtual_memory': {'total': 8_000_000_000, 'available': 4_000_000_000, 'used': 3_000_000_000},
    'swap_memory': {'total': 2_000_000_000, 'used': 500_000_000, 'free': 1_500_000_000}
}

mock_disk_data = {
    'disk_partitions': [
        {'device': '/dev/sda1', 'mountpoint': '/', 'fstype': 'ext4', 'opts': 'rw,relatime'},
        {'device': '/dev/sdb1', 'mountpoint': '/data', 'fstype': 'xfs', 'opts': 'rw,relatime'}
    ],
    'disk_usage': {
        '/': {'total': 100_000_000_000, 'used': 30_000_000_000, 'free': 70_000_000_000},
        '/data': {'total': 50_000_000_000, 'used': 10_000_000_000, 'free': 40_000_000_000}
    },
    'disk_io_counters': {'read_count': 1000, 'write_count': 500, 'read_bytes': 500_000_000, 'write_bytes': 250_000_000}
}

mock_network_data = {
    'network_io_counters': {'bytes_sent': 1_000_000, 'bytes_recv': 2_000_000, 'packets_sent': 1000, 'packets_recv': 2000},
    'network_connections': [{'fd': 3, 'family': 2, 'type': 1, 'laddr': {'ip': '192.168.0.1', 'port': 12345}, 'raddr': {'ip': '93.184.216.34', 'port': 80}}],
    'network_interfaces': {
        'lo': [{'address': '127.0.0.1', 'netmask': '255.0.0.0'}],
        'eth0': [{'address': '192.168.0.100', 'netmask': '255.255.255.0'}]
    }
}

mock_sensors_data = {
    'battery': {'percent': 85, 'plugged_in': True},
    'temperatures': {'coretemp': [{'label': 'Core 0', 'temperature': 45.0}, {'label': 'Core 1', 'temperature': 50.0}]},
    'fan_speeds': {'fan1': [{'speed': 1200}]}
}

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
        ('cpu', 'get_all_cpu_values', 'cpu_times'),
        ('memory', 'get_all_memory_values', 'virtual_memory'),
        ('disk', 'get_all_disk_values', 'disk_partitions'),
        ('network', 'get_all_network_values', 'network_io_counters'),
        ('sensors', 'get_all_sensors_values', 'battery'),
    ]
)
@pytest.mark.unit
def test_call(info_type, psutil_method, expected_key):
    tool = Tool()

    with patch.object(tool, psutil_method, return_value=globals()[f"mock_{info_type}_data"]) as mock_method:
        result = tool(info_type)

        assert expected_key in result
        assert isinstance(result[expected_key], dict)

        # Additional specific checks based on `info_type`
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
