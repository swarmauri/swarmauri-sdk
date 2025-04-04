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

from pydantic import FilePath
from typing import Any, Dict, Optional
from ._Jinja2PromptTemplate import j2pt


def _render_copy_template(
    file_record: Dict[str, Any], context: Dict[str, Any], logger: Optional[Any] = None
) -> str:
    """
    Renders a file’s template for a "COPY" operation.
    It assumes that file_record contains a "FILE_NAME" key representing the unrendered template file path.
    The function renders that field to determine the actual template file location, appends ".j2" to it,
    loads the template using a FileSystemLoader, and renders it with the provided context.

    Parameters:
      file_record (dict): The file record (contains an unrendered "FILE_NAME").
      context (dict): The merged context (project, package, module, and file record data).

    Returns:
      str: The rendered file content.
    """
    try:
        template_path = file_record.get("FILE_NAME", "NOT_FILE_FOUND")
        j2pt.set_template(FilePath(template_path))
        rendered_content = j2pt.fill(context)
        return rendered_content
    except Exception as e:
        if logger:
            logger.error(f"Failed to render copy template '{template_path}': {e}")
        return ""


def _render_generate_template(
    file_record: Dict[str, Any],
    context: Dict[str, Any],
    agent_prompt_template: str,
    agent_env: Dict[str, str] = {},
    logger: Optional[Any] = None,
) -> str:
    """
    Renders the agent prompt template for a "GENERATE" operation using the provided context,
    then calls an external agent (e.g., an LLM) to generate file content.

    Parameters:
      file_record (dict): The file record for which content is being generated.
      context (dict): The merged context (project, package, module, and file record data).
      agent_prompt_template (str): The path to the agent prompt template file.

    Returns:
      str: The content generated by the external agent.
    """
    try:
        # Set up a Jinja2 environment with a FileSystemLoader.
        j2pt.set_template(FilePath(agent_prompt_template))
        rendered_prompt = j2pt.fill(context)
        # Call the external agent to generate content.
        # Here we assume a function call_external_agent exists in external.py.
        from ._external import call_external_agent

        rendered_content = call_external_agent(rendered_prompt, agent_env, logger)
        return rendered_content
    except Exception as e:
        if logger:
            logger.error(
                f"Failed to render generate template '{agent_prompt_template}': {e}"
            )
        return ""
