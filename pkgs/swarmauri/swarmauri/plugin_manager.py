# plugin_manager.py
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
    Fetch and group entry points based on their namespaces.

    This function retrieves all entry points declared in the environment and filters
    them by their group names, matching the specified `group_prefix`. The filtered
    entry points are then grouped by their namespace (i.e., the part of the group name
    following the `group_prefix`).

    Args:
        group_prefix (str): The prefix used to filter entry points by group names.
                           Default is 'swarmauri.'.

    Returns:
        dict: A dictionary mapping namespaces (str) to lists of entry points (EntryPoint).
              If no matching entry points are found or an error occurs, an empty dictionary is returned.
    """
    try:
        # Fetch all entry points grouped by their group names
        all_entry_points = importlib.metadata.entry_points()
        logger.debug(f"Raw entry points: {all_entry_points}")

        # Group entry points by namespace
        grouped_entry_points = {}

        # Iterate over the groups
        for group_name, entry_points in all_entry_points.items():
            logger.debug(f"Processing group: {group_name}")
            
            # Skip groups that do not match the prefix
            if not group_name.startswith(group_prefix):
                continue

            # Extract the namespace (e.g., 'chunkers' from 'swarmauri.chunkers')
            namespace = group_name[len(group_prefix):]
            logger.debug(f"Identified namespace: {namespace}")

            # Add entry points to the grouped dictionary
            grouped_entry_points[namespace] = list(entry_points)

        logger.debug(f"Grouped entry points: {grouped_entry_points}")
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
        logging.debug(F"Running First Class Validation on: {name}, {plugin_class}, {resource_kind}, {resource_interface}")
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
        logger.debug(
            f"Plugin '{name}' is already pre-registered as a first-class plugin. "
            "No additional registration is required."
        )


class SecondClassPluginManager(PluginManagerBase):
    """
    Manager for second-class plugins.
    """

    def validate(self, name, plugin_class, resource_kind, resource_interface):
        """
        Validate that the plugin implements the required interface and does not conflict with first-class citizens.
        """
        logging.debug(F"Running Second Class Validation on: {name}, {plugin_class}, {resource_kind}, {resource_interface}")
        if not resource_kind == 'utils':
            if not issubclass(plugin_class, resource_interface):
                raise TypeError(
                    f"Plugin '{name}' must implement the '{resource_interface.__name__}' interface."
                )

        # Check for conflicts with first-class citizens
        resource_path = f"swarmauri.{resource_kind}.{plugin_class.__name__}"
        first_class_entry = FIRST_CLASS_REGISTRY.get(resource_path)
        if first_class_entry:
            registered_module_path = first_class_entry["module_path"]
            incoming_module_path = plugin_class.__module__

            if registered_module_path != incoming_module_path:
                raise ValueError(
                    f"Conflict detected: Second-class plugin '{name}' (module: {incoming_module_path}) "
                    f"attempts to override first-class citizen (module: {registered_module_path})."
                )

    def register(self, entry_points):
        """
        Register second-class plugins, iterating over multiple entry points.

        :param entry_points: List of entry points associated with a namespace.
        """
        logger.debug(f"Attempting second class registration of entry points: '{entry_points}'")
        for entry_point in entry_points:
            name = entry_point.name
            namespace = entry_point.group
            resource_path = f"{namespace}.{name}"

            if read_entry(resource_path) or resource_path in SECOND_CLASS_REGISTRY:
                raise ValueError(f"Plugin '{name}' is already registered under '{resource_path}'.")

            # Dynamically load the plugin class
            plugin_class = entry_point.load()

            # Validate against first-class citizens
            resource_kind = namespace[len("swarmauri."):] if namespace.startswith("swarmauri.") else None
            resource_interface = get_interface_for_resource(resource_kind)
            self.validate(name, plugin_class, resource_kind, resource_interface)

            create_entry("second", resource_path, plugin_class.__module__)
            logger.debug(f"Registered second-class plugin: {plugin_class.__module__} -> {resource_path}")



class ThirdClassPluginManager(PluginManagerBase):
    """
    Manager for third-class plugins.
    """
    def validate(self, name, plugin_class, resource_kind, resource_interface):
        """
        No validation required for third-class plugins.
        """
        logging.debug(F"Passing through Third Class validation on: {name}, {plugin_class}, {resource_kind}, {resource_interface}")

    def register(self, name, plugin_class, resource_kind):
        """
        Register the plugin as a third-class citizen.
        """
        logger.debug(f"Attempting third class registration of entry points: '{entry_points}'")
        resource_path = f"swarmauri.plugins.{name}"
        if read_entry(resource_path) or resource_path in THIRD_CLASS_REGISTRY:
            raise ValueError(f"Plugin '{name}' is already registered as a third-class citizen.")

        create_entry("third", resource_path, plugin_class.__module__)
        logger.debug(f"Registered third-class citizen: {resource_path}")


def validate_and_register_plugin(entry_point, plugin_class, resource_interface):
    """
    Validates and registers a plugin using the appropriate manager.

    :param entry_point: The entry point object.
    :param plugin_class: The class implementing the plugin.
    :param resource_interface: The abstract base class/interface for validation.
    """
    logger.debug(f"Starting validation and registration attempt for: '{entry_point}' '{plugin_class}' '{resource_interface}'")
    resource_kind = entry_point.group[len("swarmauri."):] if "." in entry_point.group else None

    plugin_manager = determine_plugin_manager(entry_point)
    if not plugin_manager:
        logger.warning(f"Unrecognized entry point group: {entry_point.group}")
        return
 
    plugin_manager.validate(entry_point.name, plugin_class, resource_kind, resource_interface)
    plugin_manager.register(entry_point.name, plugin_class, resource_kind)


def process_plugin(entry_point):
    """
    Validates and registers a single plugin entry point.

    :param entry_point: The entry point object.
    """
    try:
        logger.debug(f"Processing plugin by entry_point: {entry_point}")
        plugin_class = entry_point.load()
        logger.debug(f"Plugin class detected: {plugin_class}")
        validate_and_register_plugin(entry_point, plugin_class, None)
        return True
    except Exception as e:
        logger.error(f"Failed to process plugin '{entry_point.name}': {e}")
        return False


def discover_and_register_plugins(group_prefix="swarmauri."):
    """
    Discover plugins via entry points and delegate validation/registration to appropriate managers.

    :param group_prefix: Prefix for entry points.
    """
    grouped_entry_points = get_entry_points(group_prefix)

    for namespace, entry_points in grouped_entry_points.items():
        for entry_point in entry_points:
            process_plugin(entry_point)


def determine_plugin_manager(entry_point):
    """
    Determines the plugin manager class based on entry point group.

    :param entry_point: The entry point object.
    :return: An instance of the appropriate PluginManagerBase subclass.
    """
    try:
        # Third-Class Plugins: Group is exactly "swarmauri.plugins"
        if entry_point.group == "swarmauri.plugins":
            logger.debug(f"Plugin '{entry_point.name}' recognized as a third-class plugin.")
            return ThirdClassPluginManager()

        # First-Class and Second-Class Plugins: Group starts with "swarmauri."
        elif entry_point.group.startswith("swarmauri."):
            resource_kind = entry_point.group if "." in entry_point.group else None
            resource_interface = get_interface_for_resource(resource_kind)
            logger.debug(f"Resource kind: '{resource_kind}'")
            logger.debug(f"Resource interface: '{resource_interface}'")

            # Attempt First-Class validation
            try:
                manager = FirstClassPluginManager()
                plugin_class = entry_point.load()
                manager.validate(entry_point.name, plugin_class, resource_kind, resource_interface)
                logger.debug(f"Plugin '{entry_point.name}' recognized as a first-class plugin.")
                return manager
            except (TypeError, ValueError):
                logger.debug(f"Plugin '{entry_point.name}' is not a first-class plugin. Trying second-class.")

            # Fallback to Second-Class validation
            try:
                manager = SecondClassPluginManager()
                plugin_class = entry_point.load()
                manager.validate(entry_point.name, plugin_class, resource_kind, resource_interface)
                logger.debug(f"Plugin '{entry_point.name}' recognized as a second-class plugin.")
                return manager
            except (TypeError, ValueError):
                logger.debug(f"Plugin '{entry_point.name}' is not a second-class plugin.")

        # If no match, log and return None
        logger.warning(f"Plugin '{entry_point.name}' does not match any recognized class.")
        return None

    except Exception as e:
        logger.error(f"Failed to determine plugin manager for '{entry_point.name}': {e}")
        return None
