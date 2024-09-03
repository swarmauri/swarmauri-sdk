import pytest
from unittest.mock import MagicMock, patch
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
    "info_type, mock_data",
    [
        ('cpu', mock_cpu_data),
        ('memory', mock_memory_data),
        ('disk', mock_disk_data),
        ('network', mock_network_data),
        ('sensors', mock_sensors_data),
    ]
)
@pytest.mark.unit
def test_call(info_type, mock_data):
    tool = Tool()

    with patch('psutil.cpu_times', return_value=MagicMock(**mock_data.get('cpu_times', {}))):
        with patch('psutil.cpu_percent', return_value=mock_data.get('cpu_percent', 0.0)):
            with patch('psutil.cpu_times_percpu', return_value=[MagicMock(**cpu) for cpu in mock_data.get('cpu_times_per_cpu', [])]):
                with patch('psutil.cpu_count', return_value=mock_data.get('cpu_count', 0)):
                    with patch('psutil.cpu_freq', return_value=MagicMock(**mock_data.get('cpu_frequency', {}))):
                        with patch('psutil.cpu_stats', return_value=MagicMock(**mock_data.get('cpu_stats', {}))):
                            with patch('psutil.virtual_memory', return_value=MagicMock(**mock_data.get('virtual_memory', {}))):
                                with patch('psutil.swap_memory', return_value=MagicMock(**mock_data.get('swap_memory', {}))):
                                    with patch('psutil.disk_partitions', return_value=[MagicMock(**partition) for partition in mock_data.get('disk_partitions', [])]):
                                        with patch('psutil.disk_usage', return_value=MagicMock(**mock_data.get('disk_usage', {}))):
                                            with patch('psutil.disk_io_counters', return_value=MagicMock(**mock_data.get('disk_io_counters', {}))):
                                                with patch('psutil.net_io_counters', return_value=MagicMock(**mock_data.get('network_io_counters', {}))):
                                                    with patch('psutil.net_connections', return_value=[MagicMock(**conn) for conn in mock_data.get('network_connections', [])]):
                                                        with patch('psutil.net_if_addrs', return_value={iface: [MagicMock(**addr) for addr in addrs] for iface, addrs in mock_data.get('network_interfaces', {}).items()}):
                                                            with patch('psutil.sensors_battery', return_value=MagicMock(**mock_data.get('battery', {}))):
                                                                with patch('psutil.sensors_temperatures', return_value={name: [MagicMock(**temp) for temp in temps] for name, temps in mock_data.get('temperatures', {}).items()}):
                                                                    with patch('psutil.sensors_fans', return_value={name: [MagicMock(**fan) for fan in fans] for name, fans in mock_data.get('fan_speeds', {}).items()}):
                                                                        result = tool(info_type)
                                                                        expected_key = next(iter(mock_data.keys()))
                                                                        assert expected_key in result
                                                                        assert isinstance(result[expected_key], dict)
