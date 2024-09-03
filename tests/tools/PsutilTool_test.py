import pytest
from unittest.mock import MagicMock, patch
from swarmauri.community.tools.concrete.PsutilTool import PsutilTool as Tool
from collections import namedtuple

# Define namedtuples for various psutil structures
CPUTimes = namedtuple('CPUTimes', 'user system idle interrupt dpc')
MemoryInfo = namedtuple('MemoryInfo', 'total available percent used free')
DiskUsage = namedtuple('DiskUsage', 'total used free percent')
NetIO = namedtuple('NetIO', 'bytes_sent bytes_recv packets_sent packets_recv')
Battery = namedtuple('Battery', 'percent secsleft power_plugged')

# Mock data for each psutil type
mock_cpu_times = CPUTimes(user=1.23, system=0.45, idle=2.34, interrupt=0.01, dpc=0.02)
mock_memory_data = {
    'virtual_memory': MemoryInfo(total=8000, available=4000, percent=50.0, used=3000, free=1000)._asdict(),
    'swap_memory': MemoryInfo(total=2000, available=1000, percent=50.0, used=800, free=200)._asdict()
}
mock_disk_data = {
    'disk_partitions': [{'device': '/dev/sda1', 'mountpoint': '/', 'fstype': 'ext4', 'opts': 'rw'}],
    'disk_usage': {'/dev/sda1': DiskUsage(total=500000, used=300000, free=200000, percent=60.0)._asdict()},
    'disk_io_counters': {'read_count': 1234, 'write_count': 5678, 'read_bytes': 1024, 'write_bytes': 2048}
}
mock_network_data = {
    'network_io_counters': NetIO(bytes_sent=1234567, bytes_recv=2345678, packets_sent=3456, packets_recv=4567)._asdict(),
    'network_connections': [{'fd': 3, 'family': 2, 'type': 1, 'laddr': ('127.0.0.1', 8080), 'raddr': (), 'status': 'LISTEN'}],
    'network_interfaces': {
        'eth0': [
            {'family': 2, 'address': '192.168.1.2', 'netmask': '255.255.255.0', 'broadcast': '192.168.1.255'}
        ]
    }
}
mock_sensors_data = {
    'battery': Battery(percent=85, secsleft=1200, power_plugged=True)._asdict(),
    'temperatures': {
        'coretemp': [{'label': 'Core 0', 'current': 42.0, 'high': 80.0, 'critical': 100.0}]
    },
    'fan_speeds': {
        'fan1': [{'label': 'Fan 1', 'current': 1500}]
    }
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
        ('cpu', {'cpu_times': mock_cpu_times._asdict(),
                 'cpu_percent': 55.0,
                 'cpu_times_per_cpu': [mock_cpu_times._asdict()],
                 'cpu_count': 4,
                 'cpu_frequency': {'current': 2.5, 'min': 1.2, 'max': 3.5},
                 'cpu_stats': {'ctx_switches': 12345, 'interrupts': 67890, 'soft_interrupts': 23456}
        }),
        ('memory', mock_memory_data),
        ('disk', mock_disk_data),
        ('network', mock_network_data),
        ('sensors', mock_sensors_data),
    ]
)
@pytest.mark.unit
def test_call(info_type, mock_data):
    tool = Tool()

    # Patch based on the info_type provided
    with patch('psutil.cpu_times', return_value=mock_cpu_times), \
         patch('psutil.cpu_percent', return_value=mock_data.get('cpu_percent', 0.0)), \
         patch('psutil.cpu_times', return_value=[mock_cpu_times for _ in mock_data.get('cpu_times_per_cpu', [])]), \
         patch('psutil.cpu_count', return_value=mock_data.get('cpu_count', 0)), \
         patch('psutil.cpu_freq', return_value=MagicMock(**mock_data.get('cpu_frequency', {}))), \
         patch('psutil.cpu_stats', return_value=MagicMock(**mock_data.get('cpu_stats', {}))), \
         patch('psutil.virtual_memory', return_value=MagicMock(**mock_data.get('virtual_memory', {}))), \
         patch('psutil.swap_memory', return_value=MagicMock(**mock_data.get('swap_memory', {}))), \
         patch('psutil.disk_partitions', return_value=[MagicMock(**partition) for partition in mock_data.get('disk_partitions', [])]), \
         patch('psutil.disk_usage', side_effect=lambda p: MagicMock(**mock_data['disk_usage'][p])), \
         patch('psutil.disk_io_counters', return_value=MagicMock(**mock_data.get('disk_io_counters', {}))), \
         patch('psutil.net_io_counters', return_value=MagicMock(**mock_data.get('network_io_counters', {}))), \
         patch('psutil.net_connections', return_value=[MagicMock(**conn) for conn in mock_data.get('network_connections', [])]), \
         patch('psutil.net_if_addrs', return_value={iface: [MagicMock(**addr) for addr in addrs] for iface, addrs in mock_data.get('network_interfaces', {}).items()}), \
         patch('psutil.sensors_battery', return_value=MagicMock(**mock_data.get('battery', {}))), \
         patch('psutil.sensors_temperatures', return_value={name: [MagicMock(**temp) for temp in temps] for name, temps in mock_data.get('temperatures', {}).items()}), \
         patch('psutil.sensors_fans', return_value={name: [MagicMock(**fan) for fan in fans] for name, fans in mock_data.get('fan_speeds', {}).items()}):
        
        result = tool(info_type)
        expected_key = next(iter(mock_data.keys()))
        assert expected_key in result
        assert isinstance(result[expected_key], dict)
