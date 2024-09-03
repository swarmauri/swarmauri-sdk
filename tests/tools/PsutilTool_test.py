from unittest.mock import patch, MagicMock
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

@pytest.mark.parametrize("action, kwargs, expected", [
    ("cpu_times", {}, "CPU times data"),
    ("cpu_percent", {}, "CPU percent data"),
    ("cpu_stats", {}, "CPU stats data"),
    ("cpu_count", {}, 4),
    ("cpu_freq", {}, "CPU frequency data"),
    ("virtual_memory", {}, "Virtual memory data"),
    ("swap_memory", {}, "Swap memory data"),
    ("disk_partitions", {}, ["partition1", "partition2"]),
    ("disk_usage", {"path": "/"}, "Disk usage data"),
    ("disk_io_counters", {}, "Disk I/O counters data"),
    ("network_io_counters", {}, "Network I/O counters data"),
    ("sensors_battery", {}, "Battery status data"),
    ("sensors_temperatures", {}, "Temperature data"),
    ("sensors_fans", {}, "Fan speed data"),
])
@pytest.mark.unit
def test_call(action, kwargs, expected):
    tool = Tool()

    with patch.object(tool.psutil, 'cpu_times') as mock_cpu_times, \
         patch.object(tool.psutil, 'cpu_percent') as mock_cpu_percent, \
         patch.object(tool.psutil, 'cpu_stats') as mock_cpu_stats, \
         patch.object(tool.psutil, 'cpu_count') as mock_cpu_count, \
         patch.object(tool.psutil, 'cpu_freq') as mock_cpu_freq, \
         patch.object(tool.psutil, 'virtual_memory') as mock_virtual_memory, \
         patch.object(tool.psutil, 'swap_memory') as mock_swap_memory, \
         patch.object(tool.psutil, 'disk_partitions') as mock_disk_partitions, \
         patch.object(tool.psutil, 'disk_usage') as mock_disk_usage, \
         patch.object(tool.psutil, 'disk_io_counters') as mock_disk_io_counters, \
         patch.object(tool.psutil, 'network_io_counters') as mock_network_io_counters, \
         patch.object(tool.psutil, 'sensors_battery') as mock_sensors_battery, \
         patch.object(tool.psutil, 'sensors_temperatures') as mock_sensors_temperatures, \
         patch.object(tool.psutil, 'sensors_fans') as mock_sensors_fans:

        # Set mock return values
        mock_cpu_times.return_value = "CPU times data"
        mock_cpu_percent.return_value = "CPU percent data"
        mock_cpu_stats.return_value = "CPU stats data"
        mock_cpu_count.return_value = 4
        mock_cpu_freq.return_value = "CPU frequency data"
        mock_virtual_memory.return_value = "Virtual memory data"
        mock_swap_memory.return_value = "Swap memory data"
        mock_disk_partitions.return_value = ["partition1", "partition2"]
        mock_disk_usage.return_value = "Disk usage data"
        mock_disk_io_counters.return_value = "Disk I/O counters data"
        mock_network_io_counters.return_value = "Network I/O counters data"
        mock_sensors_battery.return_value = "Battery status data"
        mock_sensors_temperatures.return_value = "Temperature data"
        mock_sensors_fans.return_value = "Fan speed data"

        result = tool(action, **kwargs)

        assert result == expected
