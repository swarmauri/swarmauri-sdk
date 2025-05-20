"""
rendering.py

This module contains internal rendering functions for the file generation workflow.
It includes methods for:
  - Rendering the project’s YAML (from a .yaml.j2 template) into file records.
  - Rendering a generic field (e.g. an unresolved FILE_NAME) using a given context.
  - Rendering a file template for "COPY" operations.
  - Rendering an agent prompt template for "GENERATE" operations, then calling an external agent.

Note:
  - This module uses Jinja2 for template rendering.
  - It assumes that file paths and templates follow a known structure (e.g., that file records contain an unrendered FILE_NAME
    which is later rendered to obtain the correct template file path, with an expected '.j2' extension).
"""

from typing import Any, Dict, Optional

import colorama
from colorama import Fore, Style
from pydantic import FilePath

# Initialize colorama for auto-resetting colors
colorama.init(autoreset=True)


def _render_copy_template(
    file_record: Dict[str, Any],
    context: Dict[str, Any],
    j2_instance: Any,  # <-- new parameter
    logger: Optional[Any] = None,
) -> str:
    """
    File: _rendering.py
    Function: _render_copy_template

    Renders a file’s COPY template using the provided j2_instance.
    """
    try:
        template_path = file_record.get("FILE_NAME", "NOT_FILE_FOUND")
        j2_instance.set_template(FilePath(template_path))
        return j2_instance.fill(context)
    except Exception as e:
        if logger:
            e_split = str(e).split("not found")
            logger.error(
                f"{Fore.RED}Failed{Style.RESET_ALL} to render copy template '{template_path}':"
                f"{Fore.YELLOW}{e_split[0]}{Style.RESET_ALL} not found {e_split[1]}"
            )
        return ""


def _render_generate_template(
    file_record: Dict[str, Any],
    context: Dict[str, Any],
    agent_prompt_template: str,
    j2_instance: Any,  # <-- new parameter
    agent_env: Dict[str, str] = {},
    logger: Optional[Any] = None,
) -> str:
    """
    File: _rendering.py
    Function: _render_generate_template

    Renders the agent prompt for GENERATE using the provided j2_instance,
    then calls out to the external agent.
    """
    try:
        j2_instance.set_template(FilePath(agent_prompt_template))
        rendered_prompt = j2_instance.fill(context)
        from ._external import call_external_agent

        return call_external_agent(rendered_prompt, agent_env, logger)
    except Exception as e:
        if logger:
            e_split = str(e).split("not found")
            logger.error(
                f"{Fore.RED}Failed{Style.RESET_ALL} to render generate template '{agent_prompt_template}':"
                f"{Fore.YELLOW}{e_split[0]}{Style.RESET_ALL} not found in {e_split[1]}"
            )
        return ""
