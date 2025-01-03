# plugin_manager.py
from typing import Any, Optional, Type, Dict
from importlib.metadata import EntryPoint, entry_points
import importlib.metadata
import inspect
import logging
import json
from importlib.util import LazyLoader, spec_from_loader
from importlib.resources import read_binary
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
        all_entry_points = entry_points()
        logger.debug(f"Raw entry points from environment: {all_entry_points}")

        for ep in all_entry_points:
            if ep.group.startswith(group_prefix):
                namespace = ep.group[len(group_prefix):]  # e.g., 'chunkers'
                grouped_entry_points.setdefault(namespace, []).append(ep)

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

    def validate(
        self, 
        name: str, 
        plugin_object: Any, 
        resource_kind: str, 
        resource_interface: Optional[Type[Any]]
    ) -> bool:
        """
        Validate the plugin. Must be implemented by subclasses.

        :param name: Entry point name (e.g. "my_plugin")
        :param plugin_object: The loaded plugin (could be a class, module, or something else)
        :param resource_kind: The extracted sub-namespace (e.g. "utils", "agents", etc.)
        :param resource_interface: The interface class or None if not required
        :return: True if validation succeeds; otherwise raise an exception
        """
        raise NotImplementedError("Validation logic must be implemented in subclass.")

    def register(self, entry_point: EntryPoint) -> None:
        """
        Register the plugin. Must be implemented by subclasses.

        :param entry_point: The discovered entry point
        :return: None
        """
        raise NotImplementedError("Registration logic must be implemented in subclass.")

class FirstClassPluginManager(PluginManagerBase):
    """
    Manager for first-class plugins.
    """

    def validate(
        self,
        name: str,
        plugin_class: Type[Any],
        resource_kind: str,
        resource_interface: Optional[Type[Any]]
    ) -> bool:
        logger.debug(
            f"Running First-Class validation on: {name}, {plugin_class}, "
            f"{resource_kind}, {resource_interface}"
        )

        if resource_interface is not None:
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

        return True  # Validation succeeded

    def register(self, entry_point: EntryPoint) -> None:
        logger.debug(
            f"Plugin '{entry_point.name}' is already pre-registered as a first-class plugin. "
            "No additional registration is required."
        )

class SecondClassPluginManager(PluginManagerBase):
    """
    Manager for second-class plugins.
    """

    def validate(
        self,
        name: str,
        plugin_class: Type[Any],
        resource_kind: str,
        resource_interface: Optional[Type[Any]]
    ) -> bool:
        logger.debug(
            f"Running Second-Class validation on: {name}, {plugin_class}, "
            f"{resource_kind}, {resource_interface}"
        )

        if resource_interface is not None:
            if not issubclass(plugin_class, resource_interface):
                raise TypeError(
                    f"Plugin '{name}' must implement the '{resource_interface.__name__}' interface."
                )

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

        return True  # Validation succeeded

    def register(self, entry_point: EntryPoint) -> None:
        logger.debug(f"Attempting second-class registration of entry point: '{entry_point}'")
        name = entry_point.name
        namespace = entry_point.group
        resource_path = f"{namespace}.{name}"

        if read_entry(resource_path) or resource_path in SECOND_CLASS_REGISTRY:
            raise ValueError(f"Plugin '{name}' is already registered under '{resource_path}'.")

        plugin_class = entry_point.load()
        create_entry("second", resource_path, plugin_class.__module__)
        logger.debug(f"Registered second-class plugin: {plugin_class.__module__} -> {resource_path}")

class ThirdClassPluginManager(PluginManagerBase):
    """
    Manager for third-class plugins.
    """

    def validate(
        self,
        name: str,
        plugin_object: Any,
        resource_kind: str,
        resource_interface: Optional[Type[Any]]
    ) -> bool:
        logger.debug(
            f"Passing through Third-Class validation on: {name}, {plugin_object}, "
            f"{resource_kind}, {resource_interface}"
        )
        # Minimal or no checks
        return True

    def register(self, entry_point: EntryPoint) -> None:
        logger.debug(f"Attempting third-class registration of entry point: '{entry_point}'")

        name = entry_point.name
        resource_path = f"swarmauri.plugins.{name}"
        plugin_object = entry_point.load()

        if read_entry(resource_path) or resource_path in THIRD_CLASS_REGISTRY:
            raise PluginValidationError(f"Plugin '{name}' is already registered as a third-class citizen.")

        create_entry("third", resource_path, plugin_object.__module__)
        logger.debug(f"Registered third-class citizen: {resource_path}")

# --------------------------------------------------------------------------------------
# 4. PLUGIN PROCESSING FUNCTIONS
# --------------------------------------------------------------------------------------
def process_plugin(entry_point: EntryPoint) -> bool:
    """
    Loads, inspects, and registers a single plugin entry point based on its loading strategy.
    """
    try:
        logger.debug(f"Processing plugin via entry_point: {entry_point}")
        
        # Attempt to load plugin metadata
        metadata = _load_plugin_metadata(entry_point)
        loading_strategy = metadata.get("loading_strategy", "eager") if metadata else "eager"
        logger.debug(f"Plugin '{entry_point.name}' loading_strategy: {loading_strategy}")

        # Decide loading strategy
        if loading_strategy == "lazy":
            logger.debug(f"Applying lazy loading for plugin '{entry_point.name}'")
            plugin_object = _lazy_load_plugin(entry_point)
        else:
            logger.debug(f"Applying eager loading for plugin '{entry_point.name}'")
            plugin_object = entry_point.load()

        # Proceed with processing based on plugin type
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

def _load_plugin_metadata(entry_point: EntryPoint) -> Optional[Dict[str, Any]]:
    """
    Attempts to load metadata.json from the plugin's distribution without loading the module.
    """
    try:
        # Get the distribution that provides the entry point
        dist = importlib.metadata.distribution(entry_point.dist.name)
        
        # Assume metadata.json is located in the same package as the module
        # Extract the package name from module_path
        module_path = entry_point.value  # e.g., 'swarmauri.agents.QAAgent'
        package_name = module_path.rpartition('.')[0]  # 'swarmauri.agents'
        
        # Convert package name to path (replace dots with slashes)
        package_path = package_name.replace('.', '/')
        
        # Construct the relative path to metadata.json
        metadata_file = f"{package_path}/metadata.json"
        
        # Access the files in the distribution
        dist_files = dist.files or []
        
        # Search for metadata.json in the specified package
        metadata_path = None
        for file in dist_files:
            if file.as_posix() == metadata_file:
                metadata_path = file
                break
        
        # If not found, attempt to find metadata.json at the root of the package
        if not metadata_path:
            for file in dist_files:
                if file.name == 'metadata.json' and file.parent.as_posix() == package_path:
                    metadata_path = file
                    break
        
        if metadata_path:
            # Read the metadata.json file
            with dist.locate_file(metadata_path).open('r', encoding='utf-8') as f:
                metadata = json.load(f)
                logger.debug(f"Loaded metadata for plugin '{entry_point.name}': {metadata}")
                return metadata
        else:
            logger.debug(f"No metadata.json found for plugin '{entry_point.name}'.")
    except importlib.metadata.PackageNotFoundError:
        logger.debug(f"Distribution not found for plugin '{entry_point.name}'.")
    except FileNotFoundError:
        logger.debug(f"metadata.json not found for plugin '{entry_point.name}'.")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in metadata.json for plugin '{entry_point.name}': {e}")
    except Exception as e:
        logger.exception(f"Error loading metadata.json for plugin '{entry_point.name}': {e}")
    return None
    
def _lazy_load_plugin(entry_point: EntryPoint) -> Any:
    """
    Lazily loads the plugin using importlib's LazyLoader.
    """
    try:
        spec = importlib.util.find_spec(entry_point.value)
        if spec is None:
            raise ImportError(f"Cannot find spec for '{entry_point.value}'")
        loader = LazyLoader(spec.loader, module_name=spec.name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[spec.name] = module
        logger.debug(f"Lazily loaded plugin module '{spec.name}'")
        return getattr(module, entry_point.name, module)
    except Exception as e:
        logger.error(f"Failed to lazily load plugin '{entry_point.name}': {e}")
        raise PluginLoadError(f"Failed to lazily load plugin '{entry_point.name}': {e}") from e

def _process_class_plugin(entry_point: EntryPoint, plugin_class: Type[Any]) -> bool:
    """
    Processes a plugin loaded as a class.
    """
    resource_kind: Optional[str] = _extract_resource_kind_from_group(entry_point.group)
    resource_interface: Optional[Type[Any]] = _safe_get_interface_for_resource(resource_kind)

    plugin_manager: Optional[PluginManagerBase] = determine_plugin_manager_for_class(
        entry_point, plugin_class, resource_kind, resource_interface
    )
    if not plugin_manager:
        msg = f"Unrecognized plugin manager for class-based plugin '{entry_point.name}'."
        raise PluginValidationError(msg)

    is_valid: bool = plugin_manager.validate(entry_point.name, plugin_class, resource_kind, resource_interface)
    if not is_valid:
        # Handle scenarios where validate returns False without raising an exception
        msg  = f"Validation returned False for plugin '{entry_point.name}'."
        raise PluginValidationError(msg)

    # Automatic Type Registration
    if inspect.isclass(plugin_class) and hasattr(plugin_class, 'register_type'):
        # If the class has a register_type decorator, it should have already been registered
        logger.debug(f"Plugin class '{plugin_class.__name__}' has a register_type decorator.")
    else:
        # Alternatively, handle type registration based on metadata
        logger.debug(f"Automatically registering type for plugin class '{plugin_class.__name__}'")
        # Assuming metadata registration is handled elsewhere

    plugin_manager.register(entry_point)
    logger.info(f"Class-based plugin '{entry_point.name}' registered successfully.")
    return True

def _process_module_plugin(entry_point: EntryPoint, plugin_module: Any) -> bool:
    """
    Processes a plugin loaded as a module.
    """
    logger.debug(
        f"Validating module-based plugin '{entry_point.name}' at module: {plugin_module.__name__}"
    )
    # Example: call a setup function if present
    if hasattr(plugin_module, "setup_plugin"):
        logger.debug(f"Detected 'setup_plugin' in module '{plugin_module.__name__}'. Invoking...")
        plugin_module.setup_plugin()

    resource_path = f"swarmauri.modules.{plugin_module.__name__}"
    if read_entry(resource_path) or resource_path in THIRD_CLASS_REGISTRY:
        raise PluginValidationError(
            f"Module '{plugin_module.__name__}' is already registered as third-class at '{resource_path}'."
        )

    create_entry("third", resource_path, plugin_module.__name__)
    logger.info(f"Module-based plugin '{entry_point.name}' registered under '{resource_path}'.")
    return True

def _process_generic_plugin(entry_point: EntryPoint, plugin_object: Any) -> bool:
    """
    Fallback for plugins that are neither classes nor modules (could be a function, etc.).
    """
    logger.warning(
        f"Entry point '{entry_point.name}' is neither a class nor a module. "
        f"Loaded object type: {type(plugin_object)}."
    )
    # Treat them as third-class 'misc' plugins
    resource_path = f"swarmauri.misc.{entry_point.name}"
    if read_entry(resource_path):
        raise PluginValidationError(f"Plugin '{entry_point.name}' already registered under '{resource_path}'.")

    create_entry("third", resource_path, plugin_object.__module__)
    logger.info(f"Generic plugin '{entry_point.name}' registered under '{resource_path}'.")
    return True

# --------------------------------------------------------------------------------------
# 5. HELPER FUNCTIONS
# --------------------------------------------------------------------------------------
def determine_plugin_manager_for_class(entry_point: EntryPoint, plugin_class: Type[Any], resource_kind: Optional[str], resource_interface: Optional[Type[Any]]) -> Optional[PluginManagerBase]:
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

def _extract_resource_kind_from_group(group: str) -> Optional[str]:
    """
    Extract the resource kind from something like 'swarmauri.chunkers'
    or 'swarmauri.utils'. E.g. 'swarmauri.utils' => 'utils'.
    """
    parts = group.split(".")
    return parts[1] if len(parts) > 1 else None

def _safe_get_interface_for_resource(resource_kind: Optional[str]) -> Optional[Type[Any]]:
    """
    Safely retrieve the interface for a resource kind, or return None if
    the interface registry mapping is None or if resource_kind is None.
    """
    if resource_kind is None:
        return None

    try:
        interface = get_interface_for_resource(f"swarmauri.{resource_kind}")
        # If interface is None in the registry, that means "no validation needed."
        return interface
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
