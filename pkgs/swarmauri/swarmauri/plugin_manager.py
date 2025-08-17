# plugin_manager.py
from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
import inspect
import json
import logging
import sys
import time
from importlib.metadata import EntryPoint, entry_points
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .interface_registry import InterfaceRegistry
from .plugin_citizenship_registry import PluginCitizenshipRegistry

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------
# Types / Constants
# --------------------------------------------------------------------------------------
GroupedEntryPoints = Dict[str, List[EntryPoint]]
_SWARMAURI_PREFIX = "swarmauri."

# --------------------------------------------------------------------------------------
# 1. GLOBAL CACHE FOR ENTRY POINTS
# --------------------------------------------------------------------------------------
_cached_entry_points: Optional[GroupedEntryPoints] = None


def _target_groups(group_prefix: str = _SWARMAURI_PREFIX) -> List[str]:
    """
    Return fully-qualified entry point groups to scan, e.g.:
    ['swarmauri.agents', 'swarmauri.tools', ..., 'swarmauri.plugins']
    """
    namespaces = InterfaceRegistry.list_registered_namespaces()  # e.g., ['swarmauri.agents', ...]
    groups = [ns for ns in namespaces if ns.startswith(group_prefix)]
    if "swarmauri.plugins" not in groups:
        groups.append("swarmauri.plugins")
    return groups


def _fetch_and_group_entry_points(group_prefix: str = _SWARMAURI_PREFIX) -> GroupedEntryPoints:
    """
    Scan environment for entry points in the swarmauri namespace, grouped by short
    namespace key (e.g., 'agents' from 'swarmauri.agents').
    """
    grouped: GroupedEntryPoints = {}
    try:
        ep_obj = entry_points()
        groups = _target_groups(group_prefix)

        # Prefer the modern .select(group=...) path for performance.
        select = getattr(ep_obj, "select", None)
        if callable(select):
            for group in groups:
                eps = list(ep_obj.select(group=group))
                if not eps:
                    continue
                namespace_key = group[len(group_prefix) :]  # 'agents'
                grouped[namespace_key] = eps
        else:
            # Fallback: single pass filter (no "compat shim", just direct iteration).
            for ep in ep_obj:
                if ep.group in groups:
                    namespace_key = ep.group[len(group_prefix) :]
                    grouped.setdefault(namespace_key, []).append(ep)

        logger.debug("Grouped entry points (fresh scan): %s", {k: len(v) for k, v in grouped.items()})
        return grouped
    except Exception as e:
        logger.exception("Failed to retrieve entry points: %s", e)
        return {}


def get_cached_entry_points(group_prefix: str = _SWARMAURI_PREFIX) -> GroupedEntryPoints:
    """
    Returns cached entry points if available; otherwise performs a fresh scan.
    """
    global _cached_entry_points
    if _cached_entry_points is None:
        logger.debug("Entry points cache is empty; fetching now...")
        _cached_entry_points = _fetch_and_group_entry_points(group_prefix)
    return _cached_entry_points


def invalidate_entry_point_cache() -> None:
    """
    Call this if your environment changes (e.g., plugin is installed/removed at runtime).
    """
    global _cached_entry_points
    logger.debug("Invalidating entry points cache...")
    _cached_entry_points = None


def get_entry_points(group_prefix: str = _SWARMAURI_PREFIX) -> GroupedEntryPoints:
    """
    Public-facing function returning grouped entry points, using a global cache.
    """
    return get_cached_entry_points(group_prefix)


def unload_modules(prefixes: Iterable[str]) -> None:
    """
    Remove modules by package prefix (idempotent), then invalidate import caches.
    Useful for perf tests to force cold imports/discovery.
    """
    to_delete = []
    for mod in list(sys.modules):
        for p in prefixes:
            if mod == p or mod.startswith(p + "."):
                to_delete.append(mod)
                break
    for mod in to_delete:
        sys.modules.pop(mod, None)
    importlib.invalidate_caches()
    logger.debug("Unloaded %d modules matching prefixes: %s", len(to_delete), list(prefixes))


def reset_plugin_environment(*, unload_prefixes: Iterable[str] = ()) -> None:
    """
    Hard-reset the plugin system for testing:
      - clear dynamic registries (2nd/3rd-class)
      - invalidate entry-point cache
      - unload modules by prefix (optional)
    """
    try:
        PluginCitizenshipRegistry.reset_all()
    except Exception:
        # Keep reset best-effort; tests should still proceed
        logger.exception("PluginCitizenshipRegistry.reset_all() failed")
    invalidate_entry_point_cache()
    if unload_prefixes:
        unload_modules(unload_prefixes)

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
        logger.debug("Processing plugin via entry_point: %s", entry_point)

        # Load plugin metadata (if available) without importing module
        metadata = _load_plugin_metadata(entry_point)
        loading_strategy = (metadata.get("loading_strategy", "eager").lower() if metadata else "eager")
        logger.debug("Plugin '%s' loading_strategy: %s", entry_point.name, loading_strategy)

        # Determine resource_kind from the entry point group
        resource_kind = entry_point.group.split(".")[-1]  # e.g., 'agents' from 'swarmauri.agents'

        # Construct resource_path based on entry point and metadata
        type_name = metadata["type_name"] if metadata else entry_point.name
        resource_path = f"swarmauri.{resource_kind}.{type_name}"

        if loading_strategy == "lazy":
            _register_lazy_plugin_from_metadata(entry_point, metadata or {})
            logger.info("Plugin '%s' registered for lazy loading.", entry_point.name)
            return True

        # Eager path: decide by signature BEFORE loading to avoid unnecessary imports
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
    except PluginValidationError:
        # Already logged upstream; re-raise to let caller handle
        raise
    except Exception as e:
        logger.exception("Unexpected error processing plugin '%s': %s", entry_point.name, e)
        return False


def _load_plugin_metadata(entry_point: EntryPoint) -> Optional[Dict[str, Any]]:
    """
    Attempts to load metadata.json from the plugin's distribution without loading the module.
    """
    try:
        # Get the distribution that provides the entry point (may not exist for synthetic EPs in tests)
        dist = getattr(entry_point, "dist", None)
        if dist is None:
            logger.debug("Entry point '%s' has no 'dist'; skipping metadata.json lookup.", entry_point.name)
            return None

        distribution = importlib.metadata.distribution(dist.name)
        module_path = entry_point.value  # e.g., 'package.module:ClassName' or 'package.module'
        package_name = module_path.partition(":")[0].rpartition(".")[0]  # 'package.module' -> 'package'
        if not package_name:
            return None

        package_path = package_name.replace(".", "/")
        metadata_file = f"{package_path}/metadata.json"

        dist_files = distribution.files or []
        metadata_path = None

        for file in dist_files:
            if file.as_posix() == metadata_file:
                metadata_path = file
                break

        if not metadata_path:
            for file in dist_files:
                if file.name == "metadata.json" and file.parent.as_posix() == package_path:
                    metadata_path = file
                    break

        if metadata_path:
            with distribution.locate_file(metadata_path).open("r", encoding="utf-8") as f:
                metadata = json.load(f)
                logger.debug("Loaded metadata for plugin '%s': %s", entry_point.name, metadata)
                return metadata

        logger.debug("No metadata.json found for plugin '%s'.", entry_point.name)
    except importlib.metadata.PackageNotFoundError:
        logger.debug("Distribution not found for plugin '%s'.", entry_point.name)
    except FileNotFoundError:
        logger.debug("metadata.json not found for plugin '%s'.", entry_point.name)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in metadata.json for plugin '%s': %s", entry_point.name, e)
    except Exception as e:
        logger.exception("Error loading metadata.json for plugin '%s': %s", entry_point.name, e)
    return None


def _register_lazy_plugin_from_metadata(entry_point: EntryPoint, metadata: Dict[str, Any]) -> None:
    """
    Registers a lazy-loaded plugin's type and module in the registries based on metadata.
    Utilizes importlib.util.LazyLoader to defer module loading until accessed.
    """
    try:
        type_name = metadata["type_name"]
        resource_kind = metadata["resource_kind"]

        # Extract module_path and attribute_path from entry_point.value ('module:attr' expected)
        module_path, sep, attr_path = entry_point.value.partition(":")
        if not module_path:
            msg = (
                f"Invalid entry point value '{entry_point.value}' for plugin '{entry_point.name}'. "
                f"Expected format 'module_path:attribute_path' or 'module_path'."
            )
            logger.error(msg)
            raise PluginValidationError(msg)

        resource_path = f"swarmauri.{resource_kind}.{type_name}"

        # Determine classification
        citizenship = "first" if PluginCitizenshipRegistry.is_first_class(entry_point) else "second"
        logger.debug("Plugin '%s' identified as %s-class.", resource_path, citizenship)

        # Register in PluginCitizenshipRegistry with 'lazy' loading strategy
        PluginCitizenshipRegistry.add_to_registry(citizenship, resource_path, module_path)
        logger.info("Registered %s-class plugin '%s' at '%s' [lazy]", citizenship, type_name, resource_path)

        # Prepare LazyLoader module
        spec = importlib.util.find_spec(module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot find loader for module '{module_path}'")
        loader = importlib.util.LazyLoader(spec.loader)
        spec.loader = loader
        module = importlib.util.module_from_spec(spec)
        # Register the module; exec_module configures lazy loading on first attribute access
        sys.modules[module_path] = module
        loader.exec_module(module)

    except KeyError as e:
        logger.error("Missing required metadata field: %s in plugin '%s'", e, entry_point.name)
        raise PluginValidationError(f"Missing required metadata field: {e}") from e
    except Exception as e:
        logger.exception("Failed to register lazy plugin '%s': %s", entry_point.name, e)
        raise PluginValidationError(f"Failed to register lazy plugin '{entry_point.name}': {e}") from e


def is_plugin_class(entry_point: EntryPoint) -> bool:
    """
    Determines if the plugin is a class based on the entry point's object reference.
    """
    object_ref = entry_point.value
    return ":" in object_ref and object_ref.split(":")[1].isidentifier()


def is_plugin_module(entry_point: EntryPoint) -> bool:
    """
    Determines if the plugin is a module based on the entry point's object reference.
    """
    object_ref = entry_point.value
    return ":" not in object_ref


def is_plugin_generic(entry_point: EntryPoint) -> bool:
    """
    Determines if the plugin is generic (neither class nor module) based on the entry point's object reference.
    """
    object_ref = entry_point.value
    return ":" in object_ref and not object_ref.split(":")[1].isidentifier()


def _process_class_plugin(
    entry_point: EntryPoint,
    resource_path: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Processes and registers a class-based plugin.
    """
    try:
        plugin_class = entry_point.load()
        logger.debug("Loaded plugin class '%s' from '%s'", getattr(plugin_class, "__name__", "<?>"), entry_point.name)

        citizenship = determine_plugin_citizenship(entry_point)
        if not citizenship:
            logger.warning("Plugin '%s' has unrecognized citizenship and will not be registered.", entry_point.name)
            return False
        logger.info("Plugin '%s' is classified as %s-class.", entry_point.name, citizenship)

        if citizenship in ["first", "second"]:
            resource_kind = resource_path.split(".")[1]
            interface_class = InterfaceRegistry.get_interface_for_resource(f"swarmauri.{resource_kind}")
            if not issubclass(plugin_class, interface_class):
                msg = f"Plugin '{entry_point.name}' must subclass '{interface_class.__name__}'."
                logger.error(msg)
                raise PluginValidationError(msg)
            logger.info(
                "Validated class-based plugin '%s' against interface '%s'",
                getattr(plugin_class, "__name__", "<?>"), interface_class.__name__,
            )

        module_path = entry_point.value.split(":")[0] if ":" in entry_point.value else entry_point.value
        PluginCitizenshipRegistry.add_to_registry(citizenship, resource_path, module_path)
        logger.info("Registered %s-class plugin '%s' at '%s' in PluginCitizenshipRegistry",
                    citizenship, getattr(plugin_class, "__name__", entry_point.name), resource_path)

        return True

    except PluginValidationError:
        raise
    except Exception as e:
        logger.exception("Failed to process class-based plugin '%s': %s", entry_point.name, e)
        raise PluginValidationError(f"Failed to process class-based plugin '{entry_point.name}': {e}") from e


def _process_module_plugin(
    entry_point: EntryPoint,
    resource_path: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Processes and registers a module-based plugin.
    """
    try:
        plugin_module = entry_point.load()
        logger.debug("Loaded plugin module '%s' from '%s'", getattr(plugin_module, "__name__", "<?>"), entry_point.name)

        module_all = getattr(plugin_module, "__all__", [])
        if not module_all:
            logger.warning("Module '%s' does not define __all__; skipping.", plugin_module.__name__)
            return False

        for attr_name in module_all:
            try:
                attr = getattr(plugin_module, attr_name)
                logger.debug("Processing attribute '%s' in module '%s'", attr_name, plugin_module.__name__)

                if inspect.isclass(attr):
                    class_resource_path = f"swarmauri.{resource_path.split('.')[1]}.{attr_name}"
                    # Synthetic EntryPoint just for classification (name/group only)
                    try:
                        ep_class = EntryPoint(
                            name=attr_name,
                            value=f"{plugin_module.__name__}:{attr_name}",
                            group=entry_point.group,
                            dist=getattr(entry_point, "dist", None),
                        )
                    except TypeError:
                        # If EntryPoint cannot be constructed, use a simple shim-like object
                        ep_class = type("EP", (), {"name": attr_name, "group": entry_point.group})

                    citizenship = determine_plugin_citizenship(ep_class)  # type: ignore[arg-type]
                    if citizenship in ["first", "second"]:
                        resource_kind = resource_path.split(".")[1]  # e.g., 'agents'
                        interface_class = InterfaceRegistry.get_interface_for_resource(f"swarmauri.{resource_kind}")
                        if not issubclass(attr, interface_class):
                            msg = f"Plugin class '{attr_name}' must subclass '{interface_class.__name__}'."
                            logger.error(msg)
                            raise PluginValidationError(msg)

                        PluginCitizenshipRegistry.add_to_registry(
                            citizenship, class_resource_path, plugin_module.__name__
                        )
                        logger.info(
                            "Registered %s-class plugin '%s' at '%s'", citizenship, attr_name, class_resource_path
                        )

                    elif citizenship is None:
                        logger.warning(
                            "Plugin class '%s' has unrecognized citizenship and will not be registered.", attr_name
                        )

                elif inspect.ismodule(attr):
                    # Recursively process the sub-module
                    try:
                        sub_entry_point = EntryPoint(
                            name=attr_name,
                            value=f"{attr.__name__}",
                            group=entry_point.group,
                            dist=getattr(entry_point, "dist", None),
                        )
                    except TypeError:
                        sub_entry_point = type("EP", (), {"name": attr_name, "group": entry_point.group, "value": attr.__name__})
                    logger.debug("Recursively processing sub-module '%s'", getattr(attr, "__name__", attr_name))
                    process_plugin(sub_entry_point)  # type: ignore[arg-type]

                else:
                    # Generic attribute; process as generic plugin
                    generic_resource_path = f"swarmauri.plugins.{attr_name}"
                    try:
                        ep_generic = EntryPoint(
                            name=attr_name,
                            value=f"{plugin_module.__name__}:{attr_name}",
                            group="swarmauri.plugins",
                            dist=getattr(entry_point, "dist", None),
                        )
                    except TypeError:
                        ep_generic = type("EP", (), {"name": attr_name, "group": "swarmauri.plugins", "value": f"{plugin_module.__name__}:{attr_name}"})
                    citizenship = determine_plugin_citizenship(ep_generic)  # type: ignore[arg-type]
                    if citizenship == "third":
                        PluginCitizenshipRegistry.add_to_registry(
                            "third", generic_resource_path, plugin_module.__name__
                        )
                        logger.info(
                            "Registered third-class generic plugin '%s' at '%s'", attr_name, generic_resource_path
                        )
                    else:
                        logger.warning(
                            "Generic plugin '%s' in module '%s' is not classified as third-class; skipping.",
                            attr_name, plugin_module.__name__,
                        )

            except PluginValidationError:
                continue
            except Exception as e:
                logger.exception(
                    "Failed to process attribute '%s' in module '%s': %s", attr_name, plugin_module.__name__, e
                )
                continue

        return True

    except Exception as e:
        logger.error("Failed to process module-based plugin '%s': %s", entry_point.name, e)
        raise PluginValidationError(f"Failed to process module-based plugin '{entry_point.name}': {e}") from e


def _process_generic_plugin(
    entry_point: EntryPoint,
    resource_path: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Processes and registers a generic plugin.
    """
    try:
        citizenship = determine_plugin_citizenship(entry_point)
        if citizenship != "third":
            logger.warning(
                "Generic plugin '%s' is not classified as third-class and cannot be registered under protected namespaces.",
                entry_point.name,
            )
            return False

        PluginCitizenshipRegistry.add_to_registry(
            "third", resource_path, entry_point.value.split(":")[0]
        )
        logger.info("Registered generic plugin '%s' under '%s' for lazy loading.", entry_point.name, resource_path)
        return True

    except Exception as e:
        logger.error("Failed to process generic plugin '%s': %s", entry_point.name, e)
        raise PluginValidationError(f"Failed to process generic plugin '{entry_point.name}': {e}") from e


# --------------------------------------------------------------------------------------
# 4. HELPER FUNCTIONS
# --------------------------------------------------------------------------------------
def determine_plugin_citizenship(entry_point: EntryPoint) -> Optional[str]:
    """
    Determine the citizenship classification of a plugin from its entry point.
    """
    group = getattr(entry_point, "group", "")
    name = getattr(entry_point, "name", "<unknown>")

    logger.debug("Determining citizenship for plugin '%s' with group '%s'.", name, group)

    if group == "swarmauri.plugins":
        logger.debug("Plugin '%s' classified as third-class.", name)
        return "third"

    if group.startswith(_SWARMAURI_PREFIX):
        registered_namespaces = InterfaceRegistry.list_registered_namespaces()
        for ns in registered_namespaces:
            if group.startswith(ns):
                if PluginCitizenshipRegistry.is_first_class(entry_point):
                    logger.debug("Plugin '%s' classified as first-class.", name)
                    return "first"
                logger.debug("Plugin '%s' classified as second-class.", name)
                return "second"

    logger.warning("Plugin '%s' does not match any recognized citizenship classification.", name)
    return None


def _extract_resource_kind_from_group(group: str) -> Optional[str]:
    """
    Extract the resource kind from something like 'swarmauri.chunkers'
    or 'swarmauri.utils'. E.g. 'swarmauri.utils' => 'utils'.
    """
    parts = group.split(".")
    return parts[1] if len(parts) > 1 else None


def discover_and_register_plugins(
    group_prefix: str = _SWARMAURI_PREFIX,
    *,
    collect_stats: bool = False,
    entry_points_override: Optional[GroupedEntryPoints] = None,
) -> Optional[Dict[str, Any]]:
    """
    Discover all plugins via entry points and process them. When collect_stats=True,
    returns a dictionary with timing and counters for perf tests.
    """
    stats: Dict[str, Any] = {}
    try:
        t0 = time.perf_counter()
        grouped_entry_points = entry_points_override if entry_points_override is not None else get_entry_points(group_prefix)
        stats["fetch_seconds"] = time.perf_counter() - t0
        stats["groups"] = {k: len(v) for k, v in grouped_entry_points.items()}

        processed = 0
        succeeded = 0
        failed = 0

        t1 = time.perf_counter()
        for namespace, eps in grouped_entry_points.items():
            for ep in eps:
                processed += 1
                try:
                    ok = process_plugin(ep)
                    if ok:
                        succeeded += 1
                    else:
                        failed += 1
                except (PluginLoadError, PluginValidationError):
                    failed += 1
                    # Error already logged
        stats["process_seconds"] = time.perf_counter() - t1
        stats["processed"] = processed
        stats["succeeded"] = succeeded
        stats["failed"] = failed

    except Exception as e:
        logger.exception("Failed during plugin discovery and registration: %s", e)
        if collect_stats:
            stats["error"] = str(e)

    return stats if collect_stats else None


def get_plugin_type_info(resource_path: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves the plugin's type information from the registries without loading the module.
    """
    for registry in PluginCitizenshipRegistry.total_registry():
        if resource_path in registry:
            module_path = registry[resource_path]
            return {"module_path": module_path}
    return None
