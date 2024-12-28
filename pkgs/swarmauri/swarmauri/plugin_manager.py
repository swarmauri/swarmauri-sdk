# plugin_manager.py

import importlib.metadata
import inspect
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

# --------------------------------------------------------------------------------------
# 1. GLOBAL CACHE FOR ENTRY POINTS
# --------------------------------------------------------------------------------------
_cached_entry_points = None

def _fetch_and_group_entry_points(group_prefix="swarmauri."):
    """
    Internal function that scans the environment for entry points and groups them
    by namespace (e.g., 'chunkers' for 'swarmauri.chunkers').
    """
    grouped_entry_points = {}
    try:
        all_entry_points = importlib.metadata.entry_points()
        logger.debug(f"Raw entry points from environment: {all_entry_points}")

        for group_name, entry_points in all_entry_points.items():
            if group_name.startswith(group_prefix):
                namespace = group_name[len(group_prefix):]  # e.g. 'chunkers'
                grouped_entry_points[namespace] = list(entry_points)

        logger.debug(f"Grouped entry points (fresh scan): {grouped_entry_points}")
    except Exception as e:
        logger.error(f"Failed to retrieve entry points: {e}")
        return {}
    return grouped_entry_points

def get_cached_entry_points(group_prefix="swarmauri."):
    """
    Returns cached entry points if available; otherwise performs a fresh scan.
    """
    global _cached_entry_points
    if _cached_entry_points is None:
        logger.debug("Entry points cache is empty; fetching now...")
        _cached_entry_points = _fetch_and_group_entry_points(group_prefix)
    return _cached_entry_points

def invalidate_entry_point_cache():
    """
    Call this if your environment changes (e.g., plugin is installed/removed at runtime).
    """
    global _cached_entry_points
    logger.debug("Invalidating entry points cache...")
    _cached_entry_points = None

def get_entry_points(group_prefix="swarmauri."):
    """
    Public-facing function returning grouped entry points, using a global cache.
    """
    return get_cached_entry_points(group_prefix)

# --------------------------------------------------------------------------------------
# 2. CUSTOM EXCEPTIONS FOR ENHANCED ERROR DIAGNOSTICS
# --------------------------------------------------------------------------------------
class PluginLoadError(Exception):
    """Raised when a plugin fails to load or import."""

class PluginValidationError(Exception):
    """Raised when a plugin fails validation against an interface or registry."""

# --------------------------------------------------------------------------------------
# 3. PLUGIN MANAGERS
# --------------------------------------------------------------------------------------
class PluginManagerBase:
    """
    Base class for all plugin types.
    """
    def validate(self, name, plugin_object, resource_kind, resource_interface):
        """Validate the plugin. Must be implemented by subclasses."""
        raise NotImplementedError("Validation logic must be implemented in subclass.")

    def register(self, entry_point):
        """Register the plugin. Must be implemented by subclasses."""
        raise NotImplementedError("Registration logic must be implemented in subclass.")


class FirstClassPluginManager(PluginManagerBase):
    """
    Manager for first-class plugins.
    - Must be pre-registered in FIRST_CLASS_REGISTRY.
    - Must implement the interface if resource_kind != 'utils'.
    """

    def validate(self, name, plugin_class, resource_kind, resource_interface):
        logger.debug(
            f"Running First-Class validation on: {name}, {plugin_class}, {resource_kind}, {resource_interface}"
        )

        # 1) For 'utils', skip base-class validation:
        if resource_kind != "utils":
            if not issubclass(plugin_class, resource_interface):
                raise TypeError(
                    f"Plugin '{name}' must implement the '{resource_interface.__name__}' interface."
                )

        # 2) Must be pre-registered in FIRST_CLASS_REGISTRY
        resource_path = f"swarmauri.{resource_kind}.{plugin_class.__name__}"
        if resource_path not in FIRST_CLASS_REGISTRY:
            raise ValueError(
                f"Plugin '{name}' is not pre-registered as a first-class plugin. "
                "First-class plugins must be explicitly pre-registered in the registry."
            )

    def register(self, entry_point):
        logger.debug(
            f"Plugin '{entry_point.name}' is already pre-registered as a first-class plugin. "
            "No additional registration is required."
        )


class SecondClassPluginManager(PluginManagerBase):
    """
    Manager for second-class plugins.
    - If resource_kind != 'utils', must implement the interface.
    - Checks for conflicts with first-class citizens.
    """

    def validate(self, name, plugin_class, resource_kind, resource_interface):
        logger.debug(f"Running Second-Class validation on: {name}, {plugin_class}, {resource_kind}, {resource_interface}")

        # 1) For 'utils', skip base-class validation:
        if resource_kind != "utils":
            if not issubclass(plugin_class, resource_interface):
                raise TypeError(
                    f"Plugin '{name}' must implement the '{resource_interface.__name__}' interface."
                )

        # 2) Check conflicts with first-class citizens
        resource_path = f"swarmauri.{resource_kind}.{plugin_class.__name__}"
        first_class_entry = FIRST_CLASS_REGISTRY.get(resource_path)
        if first_class_entry:
            registered_module_path = first_class_entry
            incoming_module_path = plugin_class.__module__
            if registered_module_path != incoming_module_path:
                raise ValueError(
                    f"Conflict detected: Second-class plugin '{name}' (module: {incoming_module_path}) "
                    f"attempts to override first-class citizen (module: {registered_module_path})."
                )

    def register(self, entry_point):
        """
        Register second-class plugins under the specified resource_path.
        """
        logger.debug(f"Attempting second-class registration of entry point: '{entry_point}'")
        name = entry_point.name
        namespace = entry_point.group  # e.g. 'swarmauri.utils'
        resource_path = f"{namespace}.{name}"

        if read_entry(resource_path) or resource_path in SECOND_CLASS_REGISTRY:
            raise ValueError(f"Plugin '{name}' is already registered under '{resource_path}'.")

        plugin_class = entry_point.load()
        create_entry("second", resource_path, plugin_class.__module__)
        logger.debug(f"Registered second-class plugin: {plugin_class.__module__} -> {resource_path}")


class ThirdClassPluginManager(PluginManagerBase):
    """
    Manager for third-class plugins.
    - Minimal validation, typically no interface requirement.
    """

    def validate(self, name, plugin_object, resource_kind, resource_interface):
        logger.debug(f"Passing through Third-Class validation on: {name}, {plugin_object}, {resource_kind}, {resource_interface}")
        # Minimal or no checks

    def register(self, entry_point):
        logger.debug(f"Attempting third-class registration of entry point: '{entry_point}'")

        name = entry_point.name
        resource_path = f"swarmauri.plugins.{name}"
        plugin_object = entry_point.load()

        if read_entry(resource_path) or resource_path in THIRD_CLASS_REGISTRY:
            raise ValueError(f"Plugin '{name}' is already registered as a third-class citizen.")

        create_entry("third", resource_path, plugin_object.__module__)
        logger.debug(f"Registered third-class citizen: {resource_path}")

# --------------------------------------------------------------------------------------
# 4. ENTRY POINT PROCESSING (Classes, Modules, Generic Objects)
# --------------------------------------------------------------------------------------
def process_plugin(entry_point):
    """
    Loads, inspects, and registers a single plugin entry point.
    """
    try:
        logger.debug(f"Processing plugin via entry_point: {entry_point}")
        plugin_object = entry_point.load()

        if inspect.isclass(plugin_object):
            logger.debug(f"'{entry_point.name}' loaded as a class: {plugin_object}")
            return _process_class_plugin(entry_point, plugin_object)

        elif inspect.ismodule(plugin_object):
            logger.debug(f"'{entry_point.name}' loaded as a module: {plugin_object}")
            return _process_module_plugin(entry_point, plugin_object)

        else:
            logger.debug(
                f"'{entry_point.name}' loaded as an object of type {type(plugin_object)}. "
                "Handling with generic plugin logic..."
            )
            return _process_generic_plugin(entry_point, plugin_object)

    except (ImportError, ModuleNotFoundError) as e:
        msg = (
            f"Failed to import plugin '{entry_point.name}' from '{entry_point.value}'. "
            f"Check that it is installed and imports correctly. Error: {e}"
        )
        logger.error(msg)
        raise PluginLoadError(msg) from e
    except PluginValidationError:
        # Already logged or raised. Let the caller handle.
        raise
    except Exception as e:
        logger.exception(f"Unexpected error processing plugin '{entry_point.name}': {e}")
        return False


def _process_class_plugin(entry_point, plugin_class):
    """
    Validate & register a plugin loaded as a class.
    """
    resource_kind = _extract_resource_kind_from_group(entry_point.group)
    resource_interface = _safe_get_interface_for_resource(resource_kind)

    plugin_manager = determine_plugin_manager_for_class(entry_point, plugin_class, resource_kind, resource_interface)
    if not plugin_manager:
        msg = f"Unrecognized plugin manager for class-based plugin '{entry_point.name}'."
        raise PluginValidationError(msg)

    # Validate & register
    plugin_manager.validate(entry_point.name, plugin_class, resource_kind, resource_interface)
    plugin_manager.register(entry_point)
    logger.info(f"Class-based plugin '{entry_point.name}' registered successfully.")
    return True


def _process_module_plugin(entry_point, plugin_module):
    """
    Validate & register a plugin loaded as a module.
    """
    logger.debug(
        f"Validating module-based plugin '{entry_point.name}' at module: {plugin_module.__name__}"
    )
    # Example: call a setup function if present
    if hasattr(plugin_module, "setup_plugin"):
        logger.debug(f"Detected 'setup_plugin' in module '{plugin_module.__name__}'. Invoking...")
        plugin_module.setup_plugin()

    # Register the entire module as third-class, or adapt as needed
    resource_path = f"swarmauri.modules.{plugin_module.__name__}"
    if read_entry(resource_path) or resource_path in THIRD_CLASS_REGISTRY:
        raise PluginValidationError(
            f"Module '{plugin_module.__name__}' is already registered as third-class at '{resource_path}'."
        )

    create_entry("third", resource_path, plugin_module.__name__)
    logger.info(f"Module-based plugin '{entry_point.name}' registered under '{resource_path}'.")
    return True


def _process_generic_plugin(entry_point, plugin_object):
    """
    Fallback for plugins that are neither classes nor modules (could be a function, etc.).
    """
    logger.warning(
        f"Entry point '{entry_point.name}' is neither a class nor a module. "
        f"Loaded object type: {type(plugin_object)}."
    )
    # For example, treat them as third-class 'misc' plugins
    resource_path = f"swarmauri.misc.{entry_point.name}"
    if read_entry(resource_path):
        raise PluginValidationError(f"Plugin '{entry_point.name}' already registered under '{resource_path}'.")

    create_entry("third", resource_path, plugin_object.__module__)
    logger.info(f"Generic plugin '{entry_point.name}' registered under '{resource_path}'.")
    return True

# --------------------------------------------------------------------------------------
# 5. HELPER FUNCTIONS
# --------------------------------------------------------------------------------------
def determine_plugin_manager_for_class(entry_point, plugin_class, resource_kind, resource_interface):
    """
    Determines whether a class-based plugin is first-class, second-class, or third-class,
    then returns the appropriate PluginManager instance (or None if not recognized).
    """
    # If group is exactly 'swarmauri.plugins', treat it as third-class
    if entry_point.group == "swarmauri.plugins":
        logger.debug(f"Plugin '{entry_point.name}' recognized as a third-class plugin (module-level).")
        return ThirdClassPluginManager()

    # Otherwise, if it starts with 'swarmauri.' we can try first/second
    if entry_point.group.startswith("swarmauri."):
        # Attempt first-class
        try:
            manager = FirstClassPluginManager()
            manager.validate(entry_point.name, plugin_class, resource_kind, resource_interface)
            logger.debug(f"Plugin '{entry_point.name}' recognized as first-class.")
            return manager
        except (TypeError, ValueError):
            logger.debug(f"Plugin '{entry_point.name}' is not first-class; trying second-class.")

        # Attempt second-class
        try:
            manager = SecondClassPluginManager()
            manager.validate(entry_point.name, plugin_class, resource_kind, resource_interface)
            logger.debug(f"Plugin '{entry_point.name}' recognized as second-class.")
            return manager
        except (TypeError, ValueError):
            logger.debug(f"Plugin '{entry_point.name}' is not second-class either.")

    # If no match
    logger.warning(f"Plugin '{entry_point.name}' does not match any recognized manager.")
    return None

def _extract_resource_kind_from_group(group):
    """
    Extract the resource kind from something like 'swarmauri.chunkers'
    or 'swarmauri.utils'. E.g. 'swarmauri.utils' => 'utils'.
    """
    parts = group.split(".")
    return parts[1] if len(parts) > 1 else None

def _safe_get_interface_for_resource(resource_kind):
    """
    Safely retrieve the interface for a resource kind, or return None if resource_kind is 'utils'
    or doesn't exist in interface_registry.
    """
    if resource_kind is None or resource_kind == "utils":
        # Skip interface requirement for utils
        return None

    try:
        return get_interface_for_resource(f"swarmauri.{resource_kind}")
    except KeyError as ke:
        msg = f"No interface found for resource kind '{resource_kind}'."
        raise PluginValidationError(msg) from ke

def discover_and_register_plugins(group_prefix="swarmauri."):
    """
    Discover all plugins via entry points and process them.
    """
    grouped_entry_points = get_entry_points(group_prefix)
    for namespace, entry_points in grouped_entry_points.items():
        for entry_point in entry_points:
            try:
                process_plugin(entry_point)
            except PluginLoadError as e:
                logger.error(f"Skipping plugin '{entry_point.name}' due to load error: {e}")
            except PluginValidationError as e:
                logger.error(f"Skipping plugin '{entry_point.name}' due to validation error: {e}")
