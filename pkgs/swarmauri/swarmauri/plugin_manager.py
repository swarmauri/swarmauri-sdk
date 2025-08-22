# plugin_manager.py
import importlib
import importlib.metadata
import importlib.util
import inspect
import json
import logging
import sys
from importlib.metadata import EntryPoint
from typing import Any, Dict, Optional

# from swarmauri_base.ComponentBase import ComponentBase

from .interface_registry import InterfaceRegistry
from .plugin_citizenship_registry import PluginCitizenshipRegistry

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------
# 1. GLOBAL CACHE FOR ENTRY POINTS
# --------------------------------------------------------------------------------------
_cached_entry_points: Dict[str, list[EntryPoint]] | None = None


def _fetch_and_group_entry_points(
    group_prefix: str = "swarmauri.",
) -> Dict[str, list[EntryPoint]]:
    """Scan environment for relevant entry points grouped by namespace.

    The previous implementation skipped scanning once the
    :class:`PluginCitizenshipRegistry` contained any groups which effectively
    disabled discovery during development. This version always performs a
    targeted scan for only the groups we care about, dramatically reducing the
    overhead compared to scanning all entry points.
    """

    grouped_entry_points: Dict[str, list[EntryPoint]] = {}
    try:
        if PluginCitizenshipRegistry.known_groups():
            target_groups = {
                g
                for g in PluginCitizenshipRegistry.known_groups()
                if g.startswith(group_prefix)
            }
        else:
            target_groups = {
                g
                for g in InterfaceRegistry.list_registered_namespaces()
                if g.startswith(group_prefix)
            }

        all_eps = importlib.metadata.entry_points()
        for group in target_groups:
            selected = all_eps.select(group=group)
            if selected:
                namespace = group[len(group_prefix) :]
                grouped_entry_points[namespace] = list(selected)
        logger.debug("Grouped entry points (fresh scan): %s", grouped_entry_points)
    except Exception as e:
        logger.error("Failed to retrieve entry points: %s", e)
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
# 3. PLUGIN PROCESSING FUNCTIONS
# --------------------------------------------------------------------------------------
def process_plugin(entry_point: EntryPoint) -> bool:
    """
    Processes and registers a single plugin entry point based on its loading strategy and classification.

    :param entry_point: The entry point of the plugin.
    :return: True if processing is successful; False otherwise.
    """
    try:
        logger.debug(f"Processing plugin via entry_point: {entry_point}")

        # Load plugin metadata without triggering module load
        # Determine resource_kind from the entry point group
        resource_kind = entry_point.group.split(".")[
            -1
        ]  # e.g., 'agents' from 'swarmauri.agents'

        # Preliminary resource path using entry point name
        preliminary_path = f"swarmauri.{resource_kind}.{entry_point.name}"
        if PluginCitizenshipRegistry.resource_exists(preliminary_path):
            logger.debug(
                f"Resource path '{preliminary_path}' already registered; skipping."
            )
            return True

        metadata = _load_plugin_metadata(entry_point)
        loading_strategy = (
            metadata.get("loading_strategy", "eager").lower() if metadata else "eager"
        )
        logger.debug(
            f"Plugin '{entry_point.name}' loading_strategy: {loading_strategy}"
        )

        # Construct resource_path based on entry point and metadata
        type_name = metadata["type_name"] if metadata else entry_point.name
        resource_path = f"swarmauri.{resource_kind}.{type_name}"

        if loading_strategy == "lazy":
            # Register plugin based on classification (first, second)
            _register_lazy_plugin_from_metadata(entry_point, metadata)
            logger.info(f"Plugin '{entry_point.name}' registered for lazy loading.")
            return True
        else:
            # Eager loading: load the plugin module
            plugin_object = entry_point.load()
            logger.debug(
                f"Eagerly loaded plugin '{entry_point.name}' as {type(plugin_object)}"
            )

            # Determine plugin type based on entry point's object reference
            if is_plugin_class(entry_point):
                return _process_class_plugin(entry_point, resource_path, metadata)
            elif is_plugin_module(entry_point):
                return _process_module_plugin(entry_point, resource_path, metadata)
            else:
                return _process_generic_plugin(entry_point, resource_path, metadata)

    except (ImportError, ModuleNotFoundError) as e:
        msg = (
            f"Failed to import plugin '{entry_point.name}' from '{entry_point.value}'. "
            f"Check that it is installed and imports correctly. Error: {e}"
        )
        logger.error(msg)
        raise PluginLoadError(msg) from e
    except PluginValidationError as e:
        logger.error(f"Validation failed for plugin '{entry_point.name}': {e}")
        raise
    except Exception as e:
        logger.exception(
            f"Unexpected error processing plugin '{entry_point.name}': {e}"
        )
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
        package_name = module_path.rpartition(".")[0]  # 'swarmauri.agents'

        # Convert package name to path (replace dots with slashes)
        package_path = package_name.replace(".", "/")

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
                if (
                    file.name == "metadata.json"
                    and file.parent.as_posix() == package_path
                ):
                    metadata_path = file
                    break

        if metadata_path:
            # Read the metadata.json file
            with dist.locate_file(metadata_path).open("r", encoding="utf-8") as f:
                metadata = json.load(f)
                logger.debug(
                    f"Loaded metadata for plugin '{entry_point.name}': {metadata}"
                )
                return metadata
        else:
            logger.debug(f"No metadata.json found for plugin '{entry_point.name}'.")
    except importlib.metadata.PackageNotFoundError:
        logger.debug(f"Distribution not found for plugin '{entry_point.name}'.")
    except FileNotFoundError:
        logger.debug(f"metadata.json not found for plugin '{entry_point.name}'.")
    except json.JSONDecodeError as e:
        logger.error(
            f"Invalid JSON in metadata.json for plugin '{entry_point.name}': {e}"
        )
    except Exception as e:
        logger.exception(
            f"Error loading metadata.json for plugin '{entry_point.name}': {e}"
        )
    return None


def _register_lazy_plugin_from_metadata(
    entry_point: EntryPoint, metadata: Dict[str, Any]
) -> None:
    """
    Registers a lazy-loaded plugin's type and module in the registries based on metadata.
    Utilizes importlib.util.LazyLoader to defer module loading until accessed.

    :param entry_point: The entry point of the plugin.
    :param metadata: The metadata dictionary containing plugin details.
    """
    try:
        # Extract necessary fields from metadata
        type_name = metadata["type_name"]
        resource_kind = metadata["resource_kind"]
        metadata.get("interface")  # Optional field

        # Extract module_path and attribute_path from entry_point.value
        # Assumes 'module_path:attribute_path' format
        module_path, _, attr_path = entry_point.value.partition(":")
        if not module_path or not attr_path:
            msg = (
                f"Invalid entry point value '{entry_point.value}' for plugin '{entry_point.name}'. "
                f"Expected format 'module_path:attribute_path'."
            )
            logger.error(msg)
            raise PluginValidationError(msg)

        # Construct the resource path
        resource_path = f"swarmauri.{resource_kind}.{type_name}"

        # Retrieve the required interface class, if applicable
        # interface_class = InterfaceRegistry.get_interface_for_resource(
        #     f"swarmauri.{resource_kind}"
        # )

        # Determine classification: first or second class
        if PluginCitizenshipRegistry.is_first_class(entry_point):
            citizenship = "first"
            logger.debug(f"Plugin '{resource_path}' identified as first-class.")
        else:
            citizenship = "second"
            logger.debug(f"Plugin '{resource_path}' identified as second-class.")

        # Register in PluginCitizenshipRegistry with 'lazy' loading strategy
        module_path = (
            entry_point.value.split(":")[0]
            if ":" in entry_point.value
            else entry_point.value
        )
        PluginCitizenshipRegistry.add_to_registry(
            citizenship, resource_path, module_path
        )
        logger.info(
            f"Registered {citizenship}-class plugin '{type_name}' at '{resource_path}' [lazy]"
        )

        # Import Spec
        spec = importlib.util.find_spec(module_path)
        spec.loader = importlib.util.LazyLoader(spec.loader)
        if spec is None:
            raise ImportError(f"Cannot find module '{module_path}'")
        plugin_class = importlib.util.module_from_spec(spec)

        # Add LazyLoaded plugin
        sys.modules[spec.name] = plugin_class

        # type_name = resource_path.split(".")[-1]
        # ComponentBase.TYPE_REGISTRY.setdefault(interface_class, {})[type_name] = (
        #     plugin_class
        # )
        # logger.info(
        #     f"Registered class-based plugin '{plugin_class.__name__}' in ComponentBase.TYPE_REGISTRY under '{interface_class}'"
        # )

    except KeyError as e:
        logger.error(
            f"Missing required metadata field: {e} in plugin '{entry_point.name}'"
        )
        raise PluginValidationError(f"Missing required metadata field: {e}") from e
    except Exception as e:
        logger.exception(
            f"Failed to register lazy plugin '{entry_point.name}' from metadata: {e}"
        )
        raise PluginValidationError(
            f"Failed to register lazy plugin '{entry_point.name}' from metadata: {e}"
        ) from e


def is_plugin_class(entry_point: EntryPoint) -> bool:
    """
    Determines if the plugin is a class based on the entry point's object reference.

    :param entry_point: The entry point of the plugin.
    :return: True if the plugin is a class; False otherwise.
    """
    object_ref = entry_point.value
    return ":" in object_ref and object_ref.split(":")[1].isidentifier()


def is_plugin_module(entry_point: EntryPoint) -> bool:
    """
    Determines if the plugin is a module based on the entry point's object reference.

    :param entry_point: The entry point of the plugin.
    :return: True if the plugin is a module; False otherwise.
    """
    object_ref = entry_point.value
    return ":" not in object_ref


def is_plugin_generic(entry_point: EntryPoint) -> bool:
    """
    Determines if the plugin is generic (neither class nor module) based on the entry point's object reference.

    :param entry_point: The entry point of the plugin.
    :return: True if the plugin is generic; False otherwise.
    """
    object_ref = entry_point.value
    # Generic plugins may have attributes beyond class or module, e.g., functions
    # Here, we define generic as having multiple attributes or a specific pattern
    # Adjust the condition based on your specific criteria
    return ":" in object_ref and not object_ref.split(":")[1].isidentifier()


def _process_class_plugin(
    entry_point: EntryPoint,
    resource_path: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Processes and registers a class-based plugin.

    Steps:
        1. Load the plugin class.
        2. Determine the citizenship classification.
        3. If first or second-class, validate the plugin implements the required interface.
        4. Register the plugin in PluginCitizenshipRegistry with the external module path.
        5. Register the plugin class in ComponentBase.TYPE_REGISTRY.

    :param entry_point: The entry point of the plugin.
    :param resource_path: The resource path derived from the entry point.
    :param metadata: The metadata dictionary if available.
    :return: True if processing is successful; False otherwise.
    """
    try:
        # Step 1: Load the plugin class
        plugin_class = entry_point.load()
        logger.debug(
            f"Loaded plugin class '{plugin_class.__name__}' from '{entry_point.name}'"
        )

        # Step 2: Determine citizenship classification
        citizenship = determine_plugin_citizenship(entry_point)
        if citizenship:
            logger.info(
                f"Plugin '{entry_point.name}' is classified as {citizenship}-class."
            )
        else:
            logger.warning(
                f"Plugin '{entry_point.name}' has unrecognized citizenship and will not be registered."
            )
            return False

        # Step 3: If first or second-class, validate interface implementation
        if citizenship in ["first", "second"]:
            # Extract resource kind (e.g., 'agents' from 'swarmauri.agents.ExampleAgent')
            resource_kind = resource_path.split(".")[1]
            interface_class = InterfaceRegistry.get_interface_for_resource(
                f"swarmauri.{resource_kind}"
            )

            if not issubclass(plugin_class, interface_class):
                msg = f"Plugin '{entry_point.name}' must subclass '{interface_class.__name__}'."
                logger.error(msg)
                raise PluginValidationError(msg)

            logger.info(
                f"Validated class-based plugin '{plugin_class.__name__}' against interface '{interface_class.__name__}'"
            )

        # Step 4: Register the plugin in PluginCitizenshipRegistry
        # Extract module_path from entry_point.value (assumes 'module:attribute' format)
        module_path = (
            entry_point.value.split(":")[0]
            if ":" in entry_point.value
            else entry_point.value
        )
        PluginCitizenshipRegistry.add_to_registry(
            citizenship, resource_path, module_path
        )
        logger.info(
            f"Registered {citizenship}-class plugin '{plugin_class.__name__}' at '{resource_path}' in PluginCitizenshipRegistry"
        )

        # Step 5: Register the plugin class in ComponentBase.TYPE_REGISTRY
        # Extract type_name from resource_path (e.g., 'ExampleAgent' from 'swarmauri.agents.ExampleAgent')
        # type_name = resource_path.split(".")[-1]
        # ComponentBase.TYPE_REGISTRY.setdefault(interface_class, {})[type_name] = (
        #     plugin_class
        # )
        # logger.info(
        #     f"Registered class-based plugin '{plugin_class.__name__}' in ComponentBase.TYPE_REGISTRY under '{interface_class}'"
        # )

        return True

    except PluginValidationError as e:
        logger.error(
            f"Validation failed for class-based plugin '{entry_point.name}': {e}"
        )
        raise
    except Exception as e:
        logger.exception(
            f"Failed to process class-based plugin '{entry_point.name}': {e}"
        )
        raise PluginValidationError(
            f"Failed to process class-based plugin '{entry_point.name}': {e}"
        ) from e


def _process_module_plugin(
    entry_point: EntryPoint,
    resource_path: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Processes and registers a module-based plugin.

    :param entry_point: The entry point of the plugin.
    :param resource_path: The resource path derived from the entry point.
    :param metadata: The metadata dictionary if available.
    :return: True if processing is successful; False otherwise.
    """
    try:
        # Load the module
        plugin_module = entry_point.load()
        logger.debug(
            f"Loaded plugin module '{plugin_module.__name__}' from '{entry_point.name}'"
        )

        # Iterate through __all__ to process each attribute
        module_all = getattr(plugin_module, "__all__", [])
        if not module_all:
            logger.warning(
                f"Module '{plugin_module.__name__}' does not define __all__; skipping."
            )
            return False

        for attr_name in module_all:
            try:
                attr = getattr(plugin_module, attr_name)
                logger.debug(
                    f"Processing attribute '{attr_name}' in module '{plugin_module.__name__}'"
                )

                if inspect.isclass(attr):
                    # Construct resource_path for the class
                    class_resource_path = (
                        f"swarmauri.{resource_path.split('.')[1]}.{attr_name}"
                    )
                    # Determine citizenship
                    ep_class = EntryPoint(
                        name=attr_name,
                        value=f"{plugin_module.__name__}:{attr_name}",
                        group=entry_point.group,
                        dist=entry_point.dist,
                    )
                    citizenship = determine_plugin_citizenship(ep_class)
                    if citizenship in ["first", "second"]:
                        # Validate subclass
                        resource_kind = resource_path.split(".")[1]  # e.g., 'agents'
                        interface_class = InterfaceRegistry.get_interface_for_resource(
                            f"swarmauri.{resource_kind}"
                        )
                        if not issubclass(attr, interface_class):
                            msg = f"Plugin class '{attr_name}' must subclass '{interface_class.__name__}'."
                            logger.error(msg)
                            raise PluginValidationError(msg)

                        # Register in PluginCitizenshipRegistry
                        PluginCitizenshipRegistry.add_to_registry(
                            citizenship, class_resource_path, plugin_module.__name__
                        )
                        logger.info(
                            f"Registered {citizenship}-class plugin '{attr_name}' at '{class_resource_path}'"
                        )

                        # Register in TYPE_REGISTRY
                        # ComponentBase.TYPE_REGISTRY.setdefault(interface_class, {})[
                        #     attr_name
                        # ] = attr
                        # logger.info(
                        #     f"Registered class-based plugin '{attr_name}' in TYPE_REGISTRY under '{interface_class}'"
                        # )

                    elif citizenship is None:
                        logger.warning(
                            f"Plugin class '{attr_name}' has unrecognized citizenship and will not be registered."
                        )

                elif inspect.ismodule(attr):
                    # Recursively process the sub-module
                    sub_entry_point = EntryPoint(
                        name=attr_name,
                        value=f"{attr.__name__}",
                        group=entry_point.group,
                        dist=entry_point.dist,
                    )
                    logger.debug(f"Recursively processing sub-module '{attr.__name__}'")
                    process_plugin(sub_entry_point)

                else:
                    # Generic attribute; process as generic plugin
                    generic_resource_path = f"swarmauri.plugins.{attr_name}"
                    ep_generic = EntryPoint(
                        name=attr_name,
                        value=f"{plugin_module.__name__}:{attr_name}",
                        group="swarmauri.plugins",
                        dist=entry_point.dist,
                    )
                    citizenship = determine_plugin_citizenship(ep_generic)
                    if citizenship == "third":
                        # Register as third-class
                        PluginCitizenshipRegistry.add_to_registry(
                            "third", generic_resource_path, plugin_module.__name__
                        )
                        logger.info(
                            f"Registered third-class generic plugin '{attr_name}' at '{generic_resource_path}'"
                        )
                    else:
                        logger.warning(
                            f"Generic plugin '{attr_name}' in module '{plugin_module.__name__}' "
                            f"is not classified as third-class citizen and cannot be registered."
                        )
                        continue

            except PluginValidationError as ve:
                logger.error(
                    f"Validation failed for attribute '{attr_name}' in module '{plugin_module.__name__}': {ve}"
                )
                continue
            except Exception as e:
                logger.exception(
                    f"Failed to process attribute '{attr_name}' in module '{plugin_module.__name__}': {e}"
                )
                continue

        return True

    except Exception as e:
        logger.error(f"Failed to process module-based plugin '{entry_point.name}': {e}")
        raise PluginValidationError(
            f"Failed to process module-based plugin '{entry_point.name}': {e}"
        ) from e


def _process_generic_plugin(
    entry_point: EntryPoint,
    resource_path: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Processes and registers a generic plugin.

    :param entry_point: The entry point of the plugin.
    :param resource_path: The resource path derived from the entry point.
    :param metadata: The metadata dictionary if available.
    :return: True if processing is successful; False otherwise.
    """
    try:
        # Determine citizenship
        citizenship = determine_plugin_citizenship(entry_point)
        if citizenship != "third":
            logger.warning(
                f"Generic plugin '{entry_point.name}' is not classified as third-class citizen and cannot be registered under protected namespaces."
            )
            return False

        # Register in PluginCitizenshipRegistry
        PluginCitizenshipRegistry.add_to_registry(
            "third", resource_path, entry_point.value.split(":")[0]
        )
        logger.info(
            f"Registered generic plugin '{entry_point.name}' under '{resource_path}' for lazy loading."
        )

        # Register in TYPE_REGISTRY
        # 🚧ComponentBase.TYPE_REGISTRY.setdefault("plugins", {})[entry_point.name] = entry_point.load()
        # 🚧logger.info(f"Registered generic plugin '{entry_point.name}' in TYPE_REGISTRY under 'plugins'")

        return True

    except Exception as e:
        logger.error(f"Failed to process generic plugin '{entry_point.name}': {e}")
        raise PluginValidationError(
            f"Failed to process generic plugin '{entry_point.name}': {e}"
        ) from e


# --------------------------------------------------------------------------------------
# 4. HELPER FUNCTIONS
# --------------------------------------------------------------------------------------
def determine_plugin_citizenship(entry_point: EntryPoint) -> Optional[str]:
    """
    Determines the citizenship classification of a plugin based on its entry point.

    Citizenship Classification:
        - **First-Class Plugins**:
            - Pre-registered and have priority.
            - Mapped under specific namespaces like `swarmauri.agents`.
            - Must implement required interfaces.
        - **Second-Class Plugins**:
            - Community-contributed.
            - Not pre-registered but share the same namespace as first-class plugins.
            - Must implement required interfaces.
        - **Third-Class Plugins**:
            - Generic plugins not tied to specific resource kinds.
            - Mapped under `swarmauri.plugins`.
            - Do not require interface validation.

    Mappings:
        - **Resource Path to External Module Path**: The entry point's name (resource path) maps to an external module path.
          This mapping allows the importer to resolve the `swarmauri` namespace import to the actual external module,
          facilitating dynamic loading and validation of plugins based on their classification.

    Classification Logic:
        1. **Third-Class Plugins**:
            - If the entry point's group is exactly `'swarmauri.plugins'`, classify as `'third'`.
        2. **First-Class Plugins**:
            - If the entry point's group starts with any of the registered namespaces retrieved
              from the InterfaceRegistry and the plugin is pre-registered in PluginCitizenshipRegistry, classify as `'first'`.
        3. **Second-Class Plugins**:
            - If the entry point's group starts with any of the registered namespaces retrieved
              from the InterfaceRegistry but the plugin is not pre-registered in PluginCitizenshipRegistry, classify as `'second'`.
        4. **Unrecognized Plugins**:
            - If none of the above conditions are met, return `None`.

    :param entry_point: The entry point of the plugin.
    :param citizenship_registry: An instance of PluginCitizenshipRegistry.
    :return: A string indicating the plugin's citizenship ('first', 'second', 'third'), or None if unrecognized.
    """
    # Extract the group and name from the entry point
    group = entry_point.group
    name = entry_point.name

    # Debugging information
    logger.debug(f"Determining citizenship for plugin '{name}' with group '{group}'.")

    # Check for Third-Class Plugins
    if group == "swarmauri.plugins":
        logger.debug(
            f"Plugin '{name}' classified as third-class (mapped under 'swarmauri.plugins')."
        )
        return "third"

    # Check if the group starts with 'swarmauri.'
    if group.startswith("swarmauri."):
        # Retrieve the list of registered namespaces from InterfaceRegistry
        registered_namespaces = InterfaceRegistry.list_registered_namespaces()

        # Determine if the group starts with any registered namespace
        for namespace in registered_namespaces:
            if group.startswith(namespace):
                # Use PluginCitizenshipRegistry to check if it's first-class
                if PluginCitizenshipRegistry.is_first_class(entry_point):
                    logger.debug(
                        f"Plugin '{name}' classified as first-class (pre-registered)."
                    )
                    return "first"
                else:
                    logger.debug(
                        f"Plugin '{name}' classified as second-class (community-contributed)."
                    )
                    return "second"

    # If none of the conditions match, the plugin is unrecognized
    logger.warning(
        f"Plugin '{name}' does not match any recognized citizenship classification."
    )
    return None


def _extract_resource_kind_from_group(group: str) -> Optional[str]:
    """
    Extract the resource kind from something like 'swarmauri.chunkers'
    or 'swarmauri.utils'. E.g. 'swarmauri.utils' => 'utils'.
    """
    parts = group.split(".")
    return parts[1] if len(parts) > 1 else None


def discover_and_register_plugins(group_prefix="swarmauri."):
    """
    Discovers all plugins via entry points and processes them based on their classifications and loading strategies.

    :param group_prefix: The prefix to filter relevant entry point groups.
    """
    try:
        grouped_entry_points = get_entry_points(group_prefix)
        for eps in grouped_entry_points.values():
            for ep in eps:
                try:
                    process_plugin(ep)
                except PluginLoadError as e:
                    logger.error(f"Skipping plugin '{ep.name}' due to load error: {e}")
                except PluginValidationError as e:
                    logger.error(
                        f"Skipping plugin '{ep.name}' due to validation error: {e}"
                    )
    except Exception as e:
        logger.exception(f"Failed during plugin discovery and registration: {e}")


def get_plugin_type_info(resource_path: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves the plugin's type information from the registries without loading the module.

    :param resource_path: The resource path of the plugin (e.g., 'swarmauri.agents.QAAgent')
    :return: A dictionary with type information if available; otherwise, None
    """
    for registry in PluginCitizenshipRegistry.total_registry():
        if resource_path in registry:
            module_path = registry[resource_path]
            # Retrieve additional type info from type registries or maintain a separate mapping
            # For simplicity, assume type info is stored in TOTAL_REGISTRY as a dict
            # Alternatively, maintain a separate metadata registry
            # Here, we need to extend TOTAL_REGISTRY to hold type info
            # For this example, assume TOTAL_REGISTRY maps resource_path to module_path only
            # Thus, type info should be retrieved from metadata during registration
            # Therefore, consider maintaining a separate registry for type info
            return {
                "module_path": module_path,
                # Add other type info as needed
            }
    return None
