from typing import Dict, List, Union, Optional, Literal
from pydantic import ConfigDict, FilePath
from jinja2 import Environment, FileSystemLoader, Template
import os

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.prompt_templates.PromptTemplateBase import PromptTemplateBase


@ComponentBase.register_type(PromptTemplateBase, "J2PromptTemplate")
class J2PromptTemplate(PromptTemplateBase):
    """
    A subclass of PromptTemplateBase that uses Jinja2 for template rendering.

    The `template` attribute supports either a literal string representing the template content
    or a Pydantic FilePath. When a FilePath is provided, the template is loaded using
    `env.get_template()` and stored in `template`.
    """

    # The template attribute may be a literal string (template content),
    # a FilePath (when provided as input), or a compiled Jinja2 Template (when loaded from file).
    template: Union[str, FilePath, Template] = ""
    variables: Dict[str, Union[str, int, float]] = {}
    # Optional templates_dir attribute (can be a single path or a list of paths)
    templates_dir: Optional[Union[str, List[str]]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
    type: Literal["J2PromptTemplate"] = "J2PromptTemplate"

    def get_env(self) -> Environment:
        """
        Constructs and returns a Jinja2 Environment.

        If `templates_dir` is provided, a FileSystemLoader is created with that directory (or directories).
        Otherwise, no loader is set.

        The custom 'split' filter is added before returning the environment.
        """
        if self.templates_dir:
            if isinstance(self.templates_dir, str):
                loader = FileSystemLoader([self.templates_dir])
            elif isinstance(self.templates_dir, list):
                loader = FileSystemLoader(self.templates_dir)
        else:
            loader = None
        env = Environment(loader=loader, autoescape=False)
        env.filters["split"] = self.split_whitespace
        return env

    def set_template(self, template: Union[str, FilePath]) -> None:
        """
        Sets or updates the template.

        - If the provided `template` is a literal string, it is stored as-is.
        - If it is a FilePath, the template is loaded via an environment using `get_template()`.
        """
        if isinstance(template, str):
            self._set_template_from_str(template)
        else:
            self._set_template_from_filepath(template)

    def _set_template_from_str(self, template_str: str) -> None:
        """
        Sets the template from a literal string.
        """
        self.template = template_str

    def _set_template_from_filepath(self, template_path: FilePath) -> None:
        """
        Loads the template from a file specified by a FilePath.

        If `templates_dir` is provided and the template file is located in one of the directories,
        the relative path is computed so that subdirectories (e.g. 'test2') are preserved.
        If the direct lookup fails, a recursive search is performed over all provided directories.
        Otherwise, it falls back to using the file's own directory.
        """
        env = self.get_env()
        template_path_str = str(template_path)

        if self.templates_dir:
            self.template = self._load_template_from_dirs(env, template_path_str)
        else:
            self.template = self._load_template_from_file(env, template_path_str)

        def _load_template_from_dirs(self, env: Environment, template_path_str: str) -> Template:
            abs_template = os.path.abspath(template_path_str)
            dirs = [self.templates_dir] if isinstance(self.templates_dir, str) else self.templates_dir
    
            for d in dirs:
                abs_dir = os.path.abspath(d)
                if abs_template.startswith(abs_dir):
                    rel_template = os.path.relpath(abs_template, abs_dir).replace(os.sep, "/")
                    try:
                        return env.get_template(rel_template)
                    except Exception:
                        continue
    
            for d in dirs:
                abs_dir = os.path.abspath(d)
                for root, _, files in os.walk(abs_dir):
                    if os.path.basename(template_path_str) in files:
                        rel_template = os.path.relpath(os.path.join(root, os.path.basename(template_path_str)), abs_dir).replace(os.sep, "/")
                        try:
                            return env.get_template(rel_template)
                        except Exception:
                            continue
    
            return self._load_template_from_file(env, template_path_str)
    
        def _load_template_from_file(self, env: Environment, template_path_str: str) -> Template:
            directory = os.path.dirname(template_path_str) or (os.path.abspath(self.templates_dir[0]) if self.templates_dir else os.getcwd())
            template_name = os.path.basename(template_path_str)
            fallback_env = Environment(loader=FileSystemLoader([directory]), autoescape=False)
            fallback_env.filters["split"] = self.split_whitespace
            return fallback_env.get_template(template_name)

    def generate_prompt(self, variables: Dict[str, str] = None) -> str:
        """
        Generates a prompt by rendering the current template with the provided variables.

        - If `template` is a literal string, it is compiled on the fly.
        - If it is already a compiled Template (loaded via FilePath), it is rendered directly.
        """
        variables = variables if variables else self.variables
        return self.fill(variables)

    def __call__(self, variables: Optional[Dict[str, str]] = None) -> str:
        """
        Allows the instance to be called directly to generate a prompt.
        """
        variables = variables if variables else self.variables
        return self.fill(variables)

    def fill(self, variables: Dict[str, str] = None) -> str:
        variables = variables or self.variables
        env = self.get_env()
        if isinstance(self.template, Template):
            tmpl = self.template
        else:
            tmpl = env.from_string(self.template)
        return tmpl.render(**variables)

    @staticmethod
    def split_whitespace(value, delimiter: str = None):
        """
        Splits a string into a list based on whitespace.
        """
        if not isinstance(value, str):
            raise ValueError("Expected a string")
        if delimiter:
            return value.split(delimiter)
        else:
            return value.split()
