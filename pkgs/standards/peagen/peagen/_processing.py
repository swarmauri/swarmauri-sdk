"""
processing.py

This module contains functions for processing file records within a project.
It supports processing each individual file based on its PROCESS_TYPE:
  - For "COPY": It renders the file’s template using the provided context.
  - For "GENERATE": It renders an agent prompt template, calls an external agent to generate content,
    and then saves the generated content.
The module also provides a function to process all file records for a project.
"""

import os
from colorama import Fore, Style
from typing import Dict, Any, List, Optional
from pprint import pformat
from ._config import _config
from ._rendering import _render_copy_template, _render_generate_template
from ._Jinja2PromptTemplate import j2pt


def _save_file(
    content: str,
    filepath: str,
    logger: Optional[Any] = None,
    start_idx: int = 0,
    idx_len: int = 1,
) -> None:
    """
    Saves the given content to the specified file path.
    Creates the target directory if it does not exist.

    Parameters:
      content (str): The file content to save.
      filepath (str): The full path (including file name) where the content should be saved.
    """
    try:
        directory = os.path.dirname(filepath)
        os.makedirs(directory, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"({start_idx + 1}/{idx_len}) File saved: {filepath}")
    except Exception as e:
        logger.error(f"Failed to save file '{filepath}': {e}")


def _create_context(
    file_record: Dict[str, Any],
    project_global_attributes: Dict[str, Any],
    logger: Optional[Any] = None,
):
    project_name = file_record.get("PROJECT_NAME")
    package_name = file_record.get("PACKAGE_NAME")
    module_name = file_record.get("MODULE_NAME")

    # Initialize the context
    context = {}

    # Find the project information
    if project_name:
        project = project_global_attributes  # project_global_attributes contains all the project context
        context["PROJ"] = project
        if "EXTRAS" not in context["PROJ"]:
            context["PROJ"]["EXTRAS"] = {}

    # If a package_name is provided, match it to the correct package
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
            if "EXTRAS" not in context["PKG"]:
                context["PKG"]["EXTRAS"] = {}

    # If a module_name is provided, match it to the correct module within the package
    if module_name:
        module = None
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
                module = next(
                    (mod for mod in package["MODULES"] if mod["NAME"] == module_name),
                    None,
                )
        if module:
            context["MOD"] = module
            if "EXTRAS" not in context["MOD"]:
                context["MOD"]["EXTRAS"] = {}

    context["FILE"] = file_record

    if logger:
        logger.debug(f"contexts:\n{pformat(context, indent=2)}")
    return context


def _process_file(
    file_record: Dict[str, Any],
    global_attrs: Dict[str, Any],
    template_dir: str,
    agent_env: Dict[str, Any],
    logger: Optional[Any] = None,
    start_idx: int = 0,
    idx_len: int = 1,
) -> None:
    """
    Processes a single file record based on its PROCESS_TYPE.

    For a "COPY" process, the function renders the file’s template using the copy environment.
    For a "GENERATE" process, the function renders an agent prompt template and calls an external
    agent to generate content.

    Parameters:
      file_record (dict): The file record containing necessary fields (e.g., FILE_NAME, PROCESS_TYPE).
      global_attrs (dict): The project-level context.
      template_dir (str): The base directory where template files reside.
      agent_env (dict): Configuration for agent operations (used in GENERATE process).
    """
    # Merge the project-level context with file-specific data.
    context = _create_context(file_record, global_attrs, logger)
    # from pprint import pprint

    # print("_process_file: combined context")
    # pprint(context)
    # print('\n\n')

    # Render the file name field (which might still be unresolved) to determine the target file path.
    final_filename = file_record.get("RENDERED_FILE_NAME")

    process_type = file_record.get("PROCESS_TYPE", "COPY").upper()

    if process_type == "COPY":
        content = _render_copy_template(file_record, context, logger)

    elif process_type == "GENERATE":
        if _config["revise"] and "agent_prompt_template_file" not in agent_env:
            agent_env["agent_prompt_template_file"] = "agent_revise.j2"

        if _config["revise"]:
            # Set agent_prompte_template from agent_env and set INJ_CTX.
            agent_prompt_template_name = agent_env["agent_prompt_template_file"]
            context["INJ"] = _config["revision_notes"]
        else:
            # Determine the agent prompt template.
            agent_prompt_template_name = file_record.get(
                "AGENT_PROMPT_TEMPLATE", "agent_default.j2"
            )

        # Set final agent_prompt_template_path
        agent_prompt_template_path = os.path.join(
            template_dir, agent_prompt_template_name
        )

        content = _render_generate_template(
            file_record, context, agent_prompt_template_path, agent_env, logger
        )
    else:
        if logger:
            logger.warning(
                f"Unknown PROCESS_TYPE '{process_type}' for file '{final_filename}'. Skipping."
            )
        return False

    if not content:
        if logger:
            logger.warning(f"No content generated for file '{final_filename}'.")
        return False
    _save_file(content, final_filename, logger, start_idx, idx_len)
    return True


def _process_project_files(
    global_attrs: Dict[str, Any],
    file_records: List[Dict[str, Any]],
    template_dir: str,
    agent_env: Dict[str, Any],
    logger: Optional[Any] = None,
    start_idx: int = 0,
) -> None:
    idx_len = len(file_records) + start_idx
    for file_record in file_records:
        # Decide which template dir to use for the current record:
        # (1) If the file record has a "TEMPLATE_SET", use that;
        # (2) else fall back to the project-level global_attrs["TEMPLATE_SET"].
        new_template_dir = file_record.get("TEMPLATE_SET") or global_attrs.get(
            "TEMPLATE_SET"
        )

        # Update j2pt.templates_dir[0] only if it’s actually changed
        if new_template_dir and (j2pt.templates_dir[0] != new_template_dir):
            if logger:
                logger.debug(
                    "Template dir updated: "
                    f" \033[35m '{j2pt.templates_dir[0]}' "
                    + Style.RESET_ALL
                    + "to"
                    + Fore.YELLOW
                    + f" '{new_template_dir}'"
                    + Style.RESET_ALL
                )
            j2pt.templates_dir[0] = new_template_dir

        # Now process the file
        if not _process_file(
            file_record=file_record,
            global_attrs=global_attrs,
            template_dir=template_dir,
            agent_env=agent_env,
            logger=logger,
            start_idx=start_idx,
            idx_len=idx_len,
        ):
            break
        start_idx += 1
