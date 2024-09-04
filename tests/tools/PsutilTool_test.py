from unittest.mock import patch, MagicMock
import pytest
import psutil
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

@pytest.mark.parametrize("action, kwargs, expected", [
    ("cpu", {}, {'cpu_count': 4, 'cpu_frequency': 'CPU frequency data', 'cpu_percent': 'CPU percent data', 'cpu_stats': 'CPU stats data', 'cpu_times': {'cpu_times': 'CPU times data', 'cpu_times_per_cpu': ['CPU times per CPU data']}, 'cpu_times_per_cpu': []}),
    ("memory", {}, {"virtual_memory": "Virtual memory data", "swap_memory": "Swap memory data"}),
    ("disk", {}, {
        'disk_partitions': [{'device': 'sda1', 'mountpoint': '/', 'fstype': 'ext4', 'opts': 'rw'}],
        'disk_usage': {'sda1': {'disk_usage_data': 'Disk usage data'}},
        'disk_io_counters': 'Disk I/O counters data'
    }),
    ("network", {}, {"network_io_counters": "Network I/O counters data", "network_connections": ["Network connection data"], "network_interfaces": {"iface1": ["Address data"], "iface2": ["Address data"]}}),
    ("sensors", {}, {"battery": "Battery status data", "temperatures": {"temp1": ["Temperature data"]}, "fan_speeds": {"fan1": ["Fan speed data"]}})
])

@pytest.mark.unit
def test_call(action, kwargs, expected):
    with patch('psutil.cpu_times') as mock_cpu_times, \
         patch('psutil.cpu_percent') as mock_cpu_percent, \
         patch('psutil.cpu_stats') as mock_cpu_stats, \
         patch('psutil.cpu_count') as mock_cpu_count, \
         patch('psutil.cpu_freq') as mock_cpu_freq, \
         patch('psutil.virtual_memory') as mock_virtual_memory, \
         patch('psutil.swap_memory') as mock_swap_memory, \
         patch('psutil.disk_partitions') as mock_disk_partitions, \
         patch('psutil.disk_usage') as mock_disk_usage, \
         patch('psutil.disk_io_counters') as mock_disk_io_counters, \
         patch('psutil.net_io_counters') as mock_network_io_counters, \
         patch('psutil.net_connections') as mock_network_connections, \
         patch('psutil.net_if_addrs') as mock_network_if_addrs, \
         patch('psutil.sensors_battery') as mock_sensors_battery, \
         patch('psutil.sensors_temperatures') as mock_sensors_temperatures, \
         patch('psutil.sensors_fans') as mock_sensors_fans:

        # Set mock return values
        mock_cpu_times.return_value = MagicMock(_asdict=lambda: {"cpu_times": "CPU times data", "cpu_times_per_cpu": ["CPU times per CPU data"]})
        mock_cpu_percent.return_value = "CPU percent data"
        mock_cpu_stats.return_value = MagicMock(_asdict=lambda: "CPU stats data")
        mock_cpu_count.return_value = 4
        mock_cpu_freq.return_value = MagicMock(_asdict=lambda: "CPU frequency data")
        mock_virtual_memory.return_value = MagicMock(_asdict=lambda: "Virtual memory data")
        mock_swap_memory.return_value = MagicMock(_asdict=lambda: "Swap memory data")

        mock_partition1 = MagicMock(_asdict=lambda: {
            'device': 'sda1',
            'mountpoint': '/',
            'fstype': 'ext4',
            'opts': 'rw'
        })
        mock_disk_partitions.return_value = [mock_partition1]

        mock_disk_usage.return_value = MagicMock(_asdict=lambda: {"disk_usage_data": "Disk usage data"})
        mock_disk_io_counters.return_value = MagicMock(_asdict=lambda: "Disk I/O counters data")
        mock_network_io_counters.return_value = MagicMock(_asdict=lambda: "Network I/O counters data")
        mock_network_connections.return_value = [MagicMock(_asdict=lambda: "Network connection data")]
        mock_network_if_addrs.return_value = {
            "iface1": [MagicMock(_asdict=lambda: "Address data")],
            "iface2": [MagicMock(_asdict=lambda: "Address data")]
        }
        mock_sensors_battery.return_value = MagicMock(_asdict=lambda: "Battery status data")
        mock_sensors_temperatures.return_value = {
            "temp1": [MagicMock(_asdict=lambda: "Temperature data")]
        }
        mock_sensors_fans.return_value = {
            "fan1": [MagicMock(_asdict=lambda: "Fan speed data")]
        }

        tool = Tool()
        result = tool.call(action, **kwargs)
        assert result == expected
