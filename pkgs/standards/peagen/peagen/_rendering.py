"""Internal helpers for rendering templates.

Functions here render YAML payloads, generic fields and prompt
templates using Jinja2. They are used by the processing workflow to
generate files or call out to external agents.
"""

from typing import Any, Dict, Optional

import colorama
from colorama import Fore, Style
from pydantic import FilePath
from swarmauri_prompt_j2prompttemplate import j2pt

# Initialize colorama for auto-resetting colors
colorama.init(autoreset=True)


def _render_copy_template(
    file_record: Dict[str, Any],
    context: Dict[str, Any],
    logger: Optional[Any] = None,
) -> str:
    """
    File: _rendering.py
    Function: _render_copy_template

    Renders a file’s COPY template using the provided j2_instance.
    """
    try:
        template_path = file_record.get("FILE_NAME", "NOT_FILE_FOUND")
        j2pt.set_template(FilePath(template_path))
        return j2pt.fill(context)
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
        j2pt.set_template(FilePath(agent_prompt_template))
        rendered_prompt = j2pt.fill(context)
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
