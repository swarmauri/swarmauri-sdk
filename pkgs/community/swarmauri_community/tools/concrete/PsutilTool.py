# standard/tools/concrete/PsutilTool.py
import psutil
from typing import Dict, Any, Literal, List, Callable
from pydantic import Field
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter


class PsutilTool(ToolBase):
    type: Literal["PsutilTool"] = "PsutilTool"
    name: str = Field(
        "PsutilTool", description="Tool to gather system information using psutil."
    )
    description: str = Field(
        "This tool gathers system information like CPU, memory, disk, network, and sensors using the psutil library.",
        description="Description of the PsutilTool",
    )

    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="info_type",
                type="string",
                description="Type of system information to retrieve (cpu, memory, disk, network, sensors).",
                required=True,
            )
        ]
    )

    def get_all_cpu_values(self) -> Dict[str, Any]:
        return {
            "cpu_times": psutil.cpu_times()._asdict(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_times_per_cpu": [
                cpu._asdict() for cpu in psutil.cpu_times(percpu=True)
            ],
            "cpu_count": psutil.cpu_count(logical=True),
            "cpu_frequency": psutil.cpu_freq()._asdict(),
            "cpu_stats": psutil.cpu_stats()._asdict(),
        }

    def get_all_memory_values(self) -> Dict[str, Any]:
        return {
            "virtual_memory": psutil.virtual_memory()._asdict(),
            "swap_memory": psutil.swap_memory()._asdict(),
        }

    def get_all_disk_values(self) -> Dict[str, Any]:
        partitions = psutil.disk_partitions()
        disk_usage = {
            partition.device: psutil.disk_usage(partition.mountpoint)._asdict()
            for partition in partitions
        }
        return {
            "disk_partitions": [partition._asdict() for partition in partitions],
            "disk_usage": disk_usage,
            "disk_io_counters": psutil.disk_io_counters()._asdict(),
        }

    def get_all_network_values(self) -> Dict[str, Any]:
        return {
            "network_io_counters": psutil.net_io_counters()._asdict(),
            "network_connections": [
                conn._asdict() for conn in psutil.net_connections()
            ],
            "network_interfaces": {
                iface: [addr._asdict() for addr in addrs]
                for iface, addrs in psutil.net_if_addrs().items()
            },
        }

    def get_all_sensors_values(self) -> Dict[str, Any]:
        battery = psutil.sensors_battery()
        temperatures = psutil.sensors_temperatures()
        fans = psutil.sensors_fans()

        return {
            "battery": battery._asdict() if battery else None,
            "temperatures": {
                name: [temp._asdict() for temp in temps]
                for name, temps in (temperatures or {}).items()
            },
            "fan_speeds": {
                name: [fan._asdict() for fan in fans]
                for name, fans in (fans or {}).items()
            },
        }

    def __call__(self, info_type: str) -> Dict[str, Any]:
        """
        Call the appropriate method based on the provided info_type and return the corresponding system information.

        Parameters:
        info_type (str): The type of system information requested. Valid options are 'cpu', 'memory', 'disk',
                         'network', or 'sensors'.

        Returns:
        Dict[str, Any]: A dictionary where the key is the `info_type` and the value is the result of the corresponding
                        system information retrieval method.

        Raises:
        ValueError: If an invalid `info_type` is provided.

        Example:
        >>> tool = YourToolClass()
        >>> result = tool("cpu")
        >>> print(result)
        {'cpu': {...}}
        """

        # Mapping info_type values to the corresponding methods
        info_methods: Dict[str, Callable[[], Any]] = {
            "cpu": self.get_all_cpu_values,
            "memory": self.get_all_memory_values,
            "disk": self.get_all_disk_values,
            "network": self.get_all_network_values,
            "sensors": self.get_all_sensors_values,
        }

        # Retrieve the appropriate method or raise an error if invalid info_type is provided
        if info_type not in info_methods:
            raise ValueError(
                f"Invalid info_type '{info_type}' specified. Valid options are: {list(info_methods.keys())}."
            )

        # Execute the corresponding method and return the result
        result = info_methods[info_type]()
        return result
