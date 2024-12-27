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

import importlib.metadata
import logging

logger = logging.getLogger(__name__)

def get_entry_points(group_prefix="swarmauri."):
    """
    Fetch and group entry points based on their namespaces.

    This function retrieves all entry points declared in the environment and filters
    them by their group names, matching the specified `group_prefix`. The filtered
    entry points are then grouped by their namespace (i.e., the part of the group name
    following the `group_prefix`).

    Example:
        Given the following entry points in `pyproject.toml`:
        [tool.poetry.plugins."swarmauri.chunkers"]
        "SentenceChunker" = "swarmauri.chunkers.sentence_chunker:SentenceChunker"
        "OtherChunker" = "swarmauri.chunkers.other_chunker:OtherChunker"

        Calling `get_entry_points(group_prefix="swarmauri.")` will return:
        {
            "chunkers": [
                <EntryPoint name='SentenceChunker' group='swarmauri.chunkers' value='swarmauri.chunkers.sentence_chunker:SentenceChunker'>,
                <EntryPoint name='OtherChunker' group='swarmauri.chunkers' value='swarmauri.chunkers.other_chunker:OtherChunker'>
            ]
        }

    Args:
        group_prefix (str): The prefix used to filter entry points by group names.
                           Default is 'swarmauri.'.

    Returns:
        dict: A dictionary mapping namespaces (str) to lists of entry points (EntryPoint).
              If no matching entry points are found or an error occurs, an empty dictionary is returned.

    Logs:
        - Logs errors or exceptions encountered during entry point retrieval.
        - Logs raw entry points and processing details for debugging purposes.
    """
    try:
        # Fetch all entry points as a list
        all_entry_points = importlib.metadata.entry_points()

        # Group entry points by their group name
        grouped_entry_points = {}
        for ep in all_entry_points:
            # Ensure the group attribute exists and matches the prefix
            if hasattr(ep, "group") and ep.group.startswith(group_prefix):
                namespace = ep.group[len(group_prefix):]
                grouped_entry_points.setdefault(namespace, []).append(ep)

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
        Validate that the plugin implements the required interface and does not conflict with first-class citizens.
        """

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
    plugin_manager.register(entry_point.name, plugin_class, resource_kind)


def process_plugin(entry_point):
    """
    Validates and registers a single plugin entry point.

    :param entry_point: The entry point object.
    """
    try:
        plugin_class = entry_point.load()
        validate_and_register_plugin(entry_point, plugin_class, None)
    except Exception as e:
        logger.error(f"Failed to process plugin '{entry_point.name}': {e}")


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
            logger.info(f"Plugin '{entry_point.name}' recognized as a third-class plugin.")
            return ThirdClassPluginManager()

        # First-Class and Second-Class Plugins: Group starts with "swarmauri."
        elif entry_point.group.startswith("swarmauri."):
            resource_kind = entry_point.group[len("swarmauri."):] if "." in entry_point.group else None
            resource_interface = get_interface_for_resource(resource_kind)

            # Attempt First-Class validation
            try:
                manager = FirstClassPluginManager()
                plugin_class = entry_point.load()
                manager.validate(entry_point.name, plugin_class, resource_kind, resource_interface)
                logger.info(f"Plugin '{entry_point.name}' recognized as a first-class plugin.")
                return manager
            except (TypeError, ValueError):
                logger.debug(f"Plugin '{entry_point.name}' is not a first-class plugin. Trying second-class.")

            # Fallback to Second-Class validation
            try:
                manager = SecondClassPluginManager()
                plugin_class = entry_point.load()
                manager.validate(entry_point.name, plugin_class, resource_kind, resource_interface)
                logger.info(f"Plugin '{entry_point.name}' recognized as a second-class plugin.")
                return manager
            except (TypeError, ValueError):
                logger.debug(f"Plugin '{entry_point.name}' is not a second-class plugin.")

        # If no match, log and return None
        logger.warning(f"Plugin '{entry_point.name}' does not match any recognized class.")
        return None

    except Exception as e:
        logger.error(f"Failed to determine plugin manager for '{entry_point.name}': {e}")
        return None
