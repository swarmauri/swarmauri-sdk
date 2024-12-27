import importlib.metadata
import logging
from .registry import (
    create_entry,
    read_entry,
    FIRST_CLASS_REGISTRY,
    SECOND_CLASS_REGISTRY,
    THIRD_CLASS_REGISTRY,
)
from .interface_registry import get_interface_for_resource

logger = logging.getLogger(__name__)


def get_entry_points(group_prefix="swarmauri."):
    """
    Fetch and group entry points based on their namespaces from pyproject.toml.

    :param group_prefix: Prefix to filter entry points (default: 'swarmauri.').
    :return: A dictionary mapping namespaces to entry points.
    """
    try:
        all_entry_points = importlib.metadata.entry_points()
        grouped_entry_points = {}

        for ep in all_entry_points:
            if ep.group.startswith(group_prefix):
                namespace = ep.group[len(group_prefix):]  # Extract namespace (e.g., 'toolkits' or 'tools')
                if namespace not in grouped_entry_points:
                    grouped_entry_points[namespace] = []
                grouped_entry_points[namespace].append(ep)

        return grouped_entry_points
    except Exception as e:
        logger.error(f"Failed to retrieve entry points: {e}")
        return {}


class PluginManagerBase:
    """
    Base class for all plugin types.
    """
    def validate(self, name, plugin_class, resource_kind, resource_interface):
        """
        Validate the plugin. Must be implemented by subclasses.
        """
        raise NotImplementedError("Validation logic must be implemented in subclass.")

    def register(self, name, plugin_class, resource_kind):
        """
        Register the plugin. Must be implemented by subclasses.
        """
        raise NotImplementedError("Registration logic must be implemented in subclass.")


class FirstClassPluginManager(PluginManagerBase):
    """
    Manager for first-class plugins.
    """
    def validate(self, name, plugin_class, resource_kind, resource_interface):
        """
        Validate that the plugin is:
        1. A subclass of the required resource interface.
        2. Already pre-registered as a first-class plugin.
        """
        if not issubclass(plugin_class, resource_interface):
            raise TypeError(
                f"Plugin '{name}' must implement the '{resource_interface.__name__}' interface."
            )

        resource_path = f"swarmauri.{resource_kind}.{plugin_class.__name__}"
        if resource_path not in FIRST_CLASS_REGISTRY:
            raise ValueError(
                f"Plugin '{name}' is not pre-registered as a first-class plugin. "
                "First-class plugins must be explicitly pre-registered in the registry."
            )

    def register(self, name, plugin_class, resource_kind):
        """
        Pass-through method for first-class plugins, as they are pre-registered.
        """
        logger.info(
            f"Plugin '{name}' is already pre-registered as a first-class plugin. "
            "No additional registration is required."
        )


class SecondClassPluginManager(PluginManagerBase):
    """
    Manager for second-class plugins.
    """
    def validate(self, name, plugin_class, resource_kind, resource_interface):
        """
        Validate that the plugin implements the required interface.
        """
        if not issubclass(plugin_class, resource_interface):
            raise TypeError(
                f"Plugin '{name}' must implement the '{resource_interface.__name__}' interface."
            )

    def register(self, entry_points):
        """
        Register second-class plugins, iterating over multiple entry points.

        :param entry_points: List of entry points associated with a namespace.
        """
        for entry_point in entry_points:
            name = entry_point.name
            namespace = entry_point.group
            resource_path = f"{namespace}.{name}"

            if read_entry(resource_path) or resource_path in SECOND_CLASS_REGISTRY:
                raise ValueError(f"Plugin '{name}' is already registered under '{resource_path}'.")

            # Dynamically load the plugin class
            plugin_class = entry_point.load()
            create_entry("second", resource_path, plugin_class.__module__)
            logger.info(f"Registered second-class plugin: {plugin_class.__module__} -> {resource_path}")


class ThirdClassPluginManager(PluginManagerBase):
    """
    Manager for third-class plugins.
    """
    def validate(self, name, plugin_class, resource_kind, resource_interface):
        """
        No validation required for third-class plugins.
        """
        pass

    def register(self, name, plugin_class, resource_kind):
        """
        Register the plugin as a third-class citizen.
        """
        resource_path = f"swarmauri.plugins.{name}"
        if read_entry(resource_path) or resource_path in THIRD_CLASS_REGISTRY:
            raise ValueError(f"Plugin '{name}' is already registered as a third-class citizen.")
        create_entry("third", resource_path, plugin_class.__module__)
        logger.info(f"Registered third-class citizen: {resource_path}")


def validate_and_register_plugin(entry_point, plugin_class, resource_interface):
    """
    Validates and registers a plugin using the appropriate manager.

    :param entry_point: The entry point object.
    :param plugin_class: The class implementing the plugin.
    :param resource_interface: The abstract base class/interface for validation.
    """
    resource_kind = entry_point.group[len("swarmauri."):] if "." in entry_point.group else None

    plugin_manager = determine_plugin_manager(entry_point)
    if not plugin_manager:
        logger.warning(f"Unrecognized entry point group: {entry_point.group}")
        return

    plugin_manager.validate(entry_point.name, plugin_class, resource_kind, resource_interface)
    plugin_manager.register([entry_point])  # Register as a list for uniformity


def discover_and_register_plugins():
    """
    Discover plugins via entry points, validate them, and register them using the appropriate manager.
    """
    grouped_entry_points = get_entry_points()

    for namespace, entry_points in grouped_entry_points.items():
        manager = SecondClassPluginManager()  # Assume second-class plugins for simplicity
        manager.register(entry_points)
        logger.info(f"Successfully registered plugins in namespace '{namespace}'.")
