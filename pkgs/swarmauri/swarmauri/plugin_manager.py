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
    Fetch and filter entry points based on a group prefix.

    :param group_prefix: Prefix to filter entry points (default: 'swarmauri.').
    :return: A list of matching entry points.
    """
    try:
        all_entry_points = importlib.metadata.entry_points()
        return [
            ep for ep in all_entry_points
            if ep.group.startswith(group_prefix)
        ]
    except Exception as e:
        logger.error(f"Failed to retrieve entry points: {e}")
        return []


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
        Validate that the plugin implements the required interface.
        """
        if not issubclass(plugin_class, resource_interface):
            raise TypeError(f"Plugin '{name}' must implement the '{resource_interface.__name__}' interface.")

    def register(self, name, plugin_class, resource_kind):
        """
        Register the plugin as a first-class citizen.
        """
        resource_path = f"swarmauri.{resource_kind}.{plugin_class.__name__}"
        if read_entry(resource_path) or resource_path in FIRST_CLASS_REGISTRY:
            raise ValueError(f"Plugin '{name}' is already registered as a first-class citizen.")
        create_entry('first', resource_path, plugin_class.__module__)
        logger.info(f"Registered first-class citizen: {resource_path}")


class SecondClassPluginManager(PluginManagerBase):
    """
    Manager for second-class plugins.
    """
    def validate(self, name, plugin_class, resource_kind, resource_interface):
        """
        Validate that the plugin implements the required interface.
        """
        if not issubclass(plugin_class, resource_interface):
            raise TypeError(f"Plugin '{name}' must implement the '{resource_interface.__name__}' interface.")

    def register(self, name, plugin_class, resource_kind):
        """
        Register the plugin as a second-class citizen.
        """
        resource_path = f"swarmauri.{resource_kind}.{plugin_class.__name__}"
        if read_entry(resource_path) or resource_path in SECOND_CLASS_REGISTRY:
            raise ValueError(f"Plugin '{name}' is already registered as a second-class citizen.")
        create_entry('second', resource_path, plugin_class.__module__)
        logger.info(f"Registered second-class citizen: {resource_path}")


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
        create_entry('third', resource_path, plugin_class.__module__)
        logger.info(f"Registered third-class citizen: {resource_path}")


def determine_plugin_manager(entry_point):
    """
    Determines the plugin manager class based on entry point group.

    :param entry_point: The entry point object.
    :return: Instance of the appropriate PluginManagerBase subclass.
    """
    if entry_point.group.startswith("swarmauri."):
        if entry_point.group == "swarmauri.plugins":
            return ThirdClassPluginManager()
        elif entry_point.group.count(".") == 1:
            return FirstClassPluginManager()
        else:
            return SecondClassPluginManager()
    return None


def validate_and_register_plugin(entry_point, plugin_class, resource_interface):
    """
    Validates and registers a plugin using the appropriate manager.

    :param entry_point: The entry point object.
    :param plugin_class: The class implementing the plugin.
    :param resource_interface: The abstract base class/interface for validation.
    """
    plugin_manager = determine_plugin_manager(entry_point)
    if not plugin_manager:
        logger.warning(f"Unrecognized entry point group: {entry_point.group}")
        return

    resource_kind = entry_point.group[len("swarmauri."):] if "." in entry_point.group else None
    plugin_manager.validate(entry_point.name, plugin_class, resource_kind, resource_interface)
    plugin_manager.register(entry_point.name, plugin_class, resource_kind)


def discover_and_register_plugins():
    """
    Discover plugins via entry points, validate them, and register them using the appropriate manager.
    """
    entry_points = get_entry_points()

    for entry_point in entry_points:
        try:
            plugin_class = entry_point.load()
            resource_kind = entry_point.group[len("swarmauri."):] if "." in entry_point.group else None
            resource_interface = get_interface_for_resource(resource_kind)
            validate_and_register_plugin(entry_point, plugin_class, resource_interface)
            logger.info(f"Successfully processed plugin: {entry_point.name}")
        except Exception as e:
            logger.error(f"Failed to process plugin '{entry_point.name}': {e}")
