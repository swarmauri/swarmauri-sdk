import importlib.metadata
import logging
from .registry import REGISTRY

logger = logging.getLogger(__name__)


def validate_and_register_first_class(name, plugin_class, resource_kind, resource_interface):
    """
    Validates and registers a plugin as a first-class citizen.

    :param name: The name of the plugin (e.g., "example_plugin").
    :param plugin_class: The class implementing the plugin.
    :param resource_kind: The resource namespace (e.g., "conversations").
    :param resource_interface: The abstract base class/interface for validation.
    :raises TypeError: If the plugin does not conform to the required interface.
    :raises ValueError: If the plugin is already registered.
    """
    # Validate the plugin
    if not issubclass(plugin_class, resource_interface):
        raise TypeError(f"Plugin '{name}' must implement the '{resource_interface.__name__}' interface.")

    # Construct the resource path
    resource_path = f"swarmauri.{resource_kind}.{plugin_class.__name__}"

    # Ensure it's not already registered
    if resource_path in REGISTRY:
        raise ValueError(f"Plugin '{name}' is already registered as a first-class citizen.")

    # Register in the REGISTRY
    REGISTRY[resource_path] = plugin_class
    logger.info(f"Registered first-class citizen: {resource_path}")


def register_second_class(name, plugin_class):
    """
    Register a plugin as a second-class citizen in the swarmauri.plugins namespace.

    :param name: The name of the plugin (e.g., "example_plugin").
    :param plugin_class: The class implementing the plugin.
    :raises ValueError: If a module with the same name already exists.
    """
    import sys
    from types import ModuleType

    # Construct the namespace path
    namespace_path = f"swarmauri.plugins.{name}"

    # Check if the module is already registered
    if namespace_path in sys.modules:
        raise ValueError(
            f"A module with the name '{namespace_path}' already exists. "
            "Overwriting is not allowed."
        )

    # Dynamically create a module for the plugin
    module = ModuleType(namespace_path)
    setattr(module, name, plugin_class)
    sys.modules[namespace_path] = module

    logger.info(f"Registered second-class citizen: {namespace_path}")



def determine_plugin_type(entry_point):
    """
    Determines whether a plugin is a first-class or second-class citizen based on its entry point path.

    :param entry_point: The entry point object.
    :return: "first-class" or "second-class" based on the entry point path.
    """
    if entry_point.group.startswith("swarmauri."):
        if entry_point.group == "swarmauri.plugins":
            return "second-class"
        else:
            return "first-class"
    return None


def validate_and_register_plugin(entry_point, plugin_class, resource_interface):
    """
    Validates and registers a plugin based on its entry point path.

    :param entry_point: The entry point object.
    :param plugin_class: The class implementing the plugin.
    :param resource_interface: The abstract base class/interface for validation.
    """
    plugin_type = determine_plugin_type(entry_point)

    if plugin_type == "first-class":
        resource_kind = entry_point.group[len("swarmauri.") :]
        validate_and_register_first_class(entry_point.name, plugin_class, resource_kind, resource_interface)
    elif plugin_type == "second-class":
        register_second_class(entry_point.name, plugin_class)
    else:
        logger.warning(f"Unrecognized entry point group: {entry_point.group}")


def discover_and_register_plugins(resource_interface):
    """
    Discover plugins via entry points, validate them, and register them as first or second-class citizens.

    :param resource_interface: The abstract base class/interface for validation.
    """
    entry_points = importlib.metadata.entry_points()

    for entry_point in entry_points:
        try:
            plugin_class = entry_point.load()
            validate_and_register_plugin(entry_point, plugin_class, resource_interface)
            logger.info(f"Successfully processed plugin: {entry_point.name}")
        except Exception as e:
            logger.error(f"Failed to process plugin '{entry_point.name}': {e}")
