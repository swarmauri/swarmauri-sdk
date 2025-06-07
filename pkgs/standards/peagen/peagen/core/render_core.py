# peagen/core/render_core.py

import sys
from pathlib import Path
from typing import Any, Dict, Optional

import colorama
from colorama import Fore, Style

from peagen.core._external import call_external_agent

# Initialize colorama for auto-resetting colors
colorama.init(autoreset=True)
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.INFO)

def _render_copy_template(
    file_record: Dict[str, Any],
    context: Dict[str, Any],
    j2_instance: Any,
) -> str:
    """
    Render a COPY‐style template.  
    - file_record["FILE_NAME"] should be a path to the template.  
    - context is a dict of values for Jinja.  
    - j2_instance must provide set_template(path) and fill(context).  
    """
    try:
        template_path = file_record.get("FILE_NAME", "")
        if logger:
            logger.debug(f"Rendering copy template {template_path}")
        # Pass the raw path string or Path to the Jinja2 wrapper
        j2_instance.set_template(str(template_path))
        return j2_instance.fill(context)
    except Exception as e:
        if logger:
            msg = str(e)
            if "not found" in msg:
                parts = msg.split("not found")
                logger.error(
                    f"{Fore.RED}Failed{Style.RESET_ALL} to render copy template '{template_path}':"
                    f"{Fore.YELLOW}{parts[0]}{Style.RESET_ALL} not found{parts[1]}"
                )
            else:
                logger.error(
                    f"{Fore.RED}Failed{Style.RESET_ALL} to render copy template '{template_path}': {e}"
                )
        sys.exit(1)


def _render_generate_template(
    file_record: Dict[str, Any],
    context: Dict[str, Any],
    agent_prompt_template: str,
    j2_instance: Any,
    agent_env: Dict[str, str] = {},
    cfg: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Render a GENERATE‐style template.  
    - agent_prompt_template is a path to the Jinja template for the prompt.  
    - context is a dict of values for Jinja.  
    - j2_instance must provide set_template(path) and fill(context).  
    - agent_env is passed through to call_external_agent.  
    """
    try:
        template_name = Path(agent_prompt_template).name
        if logger:
            logger.debug(f"Rendering generate template {agent_prompt_template}")
        j2_instance.set_template(template_name)

        print('\n\n\nagent_prompt_template', agent_prompt_template)
        print('\n\ncontext', context)
        print('\n\nj2_instance', j2_instance)
        print('\n\n\n')
        rendered_prompt = j2_instance.fill(context)
        print('\n\n\nrendered_prompt', rendered_prompt)
        import inspect
        sig = inspect.signature(call_external_agent)
        if len(sig.parameters) >= 4:
            resp = call_external_agent(rendered_prompt, agent_env, cfg, logger)
        else:
            resp = call_external_agent(rendered_prompt, agent_env, logger=logger)
        print('\n\nresp', resp)
        return resp
    except Exception as e:
        if logger:
            msg = str(e)
            if "not found" in msg:
                parts = msg.split("not found")
                logger.error(
                    f"{Fore.RED}Failed{Style.RESET_ALL} to render generate template '{agent_prompt_template}':"
                    f"{Fore.YELLOW}{parts[0]}{Style.RESET_ALL} not found{parts[1]}"
                )
            else:
                logger.error(
                    f"{Fore.RED}Failed{Style.RESET_ALL} to render generate template '{agent_prompt_template}': {e}"
                )
        sys.exit(1)
