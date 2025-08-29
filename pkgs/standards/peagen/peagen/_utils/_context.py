from typing import Dict, Any, Optional
from pprint import pformat


def _create_context(
    file_record: Dict[str, Any],
    project_global_attributes: Dict[str, Any],
    logger: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Builds the rendering context for a single file record.
    """
    project_name = file_record.get("PROJECT_NAME")
    package_name = file_record.get("PACKAGE_NAME")
    module_name = file_record.get("MODULE_NAME")

    context: Dict[str, Any] = {}

    if project_name:
        context["PROJ"] = project_global_attributes
        context["PROJ"].setdefault("EXTRAS", {})

    if package_name:
        package = next(
            (
                pkg
                for pkg in project_global_attributes["PACKAGES"]
                if pkg["NAME"] == package_name
            ),
            None,
        )
        if package:
            context["PKG"] = package
            context["PKG"].setdefault("EXTRAS", {})

    if module_name:
        module = None
        pkg = context.get("PKG")
        if pkg:
            module = next(
                (mod for mod in pkg.get("MODULES", []) if mod["NAME"] == module_name),
                None,
            )
        if module:
            context["MOD"] = module
            context["MOD"].setdefault("EXTRAS", {})

    context["FILE"] = file_record

    if logger:
        logger.debug(f"context:\n{pformat(context, indent=2)}")
    return context
