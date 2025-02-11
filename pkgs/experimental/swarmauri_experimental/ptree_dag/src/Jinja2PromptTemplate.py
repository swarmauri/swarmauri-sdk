from typing import Dict, List, Union, Optional, Literal
from pydantic import Field, ConfigDict, FilePath
from jinja2 import Environment, FileSystemLoader, Template
import os

from swarmauri_core.prompts.IPrompt import IPrompt
from swarmauri_core.prompts.ITemplate import ITemplate
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.prompt_templates.PromptTemplateBase import PromptTemplateBase

@ComponentBase.register_type(PromptTemplateBase, 'Jinja2PromptTemplate')
class Jinja2PromptTemplate(PromptTemplateBase):
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
    type: Literal['Jinja2PromptTemplate'] = 'Jinja2PromptTemplate'
    
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
            else:
                loader = FileSystemLoader(self.templates_dir)
        else:
            loader = None
        env = Environment(loader=loader, autoescape=False)
        env.filters['split'] = self.split_whitespace
        env.filters['make_singular'] = self.make_singular
        return env

    def set_template(self, template: Union[str, FilePath]) -> None:
        """
        Sets or updates the template.
        
        - If the provided `template` is a literal string, it is stored as-is.
        - If it is a FilePath, the template is loaded via an environment using `get_template()`.
        """
        if type(template) is str:
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
        abs_template = os.path.abspath(template_path_str)

        # If templates_dir is provided, try to compute a relative path from each candidate directory.
        if self.templates_dir:
            dirs = (
                [self.templates_dir]
                if isinstance(self.templates_dir, str)
                else self.templates_dir
            )
            for d in dirs:
                abs_dir = os.path.abspath(d)
                if abs_template.startswith(abs_dir):
                    # Compute the relative path and normalize to forward slashes.
                    rel_template = os.path.relpath(abs_template, abs_dir).replace(os.sep, '/')
                    try:
                        self.template = env.get_template(rel_template)
                        return
                    except Exception:
                        # If direct lookup fails for this directory, try the next one.
                        continue

            # If direct lookup did not succeed, perform a recursive search in all candidate directories.
            for d in dirs:
                abs_dir = os.path.abspath(d)
                for root, _, files in os.walk(abs_dir):
                    if os.path.basename(template_path_str) in files:
                        rel_template = os.path.relpath(
                            os.path.join(root, os.path.basename(template_path_str)), abs_dir
                        ).replace(os.sep, '/')
                        try:
                            self.template = env.get_template(rel_template)
                            return
                        except Exception:
                            continue

        # Fallback: use the file's own directory.
        directory = os.path.dirname(template_path_str)
        if not directory:
            # If no directory component is provided, use the first entry of templates_dir (if available) or CWD.
            if self.templates_dir:
                directory = os.path.abspath(
                    self.templates_dir[0] if isinstance(self.templates_dir, list) else self.templates_dir
                )
            else:
                directory = os.getcwd()
        template_name = os.path.basename(template_path_str)
        fallback_env = Environment(loader=FileSystemLoader([directory]), autoescape=False)
        fallback_env.filters['split'] = self.split_whitespace
        fallback_env.filters['make_singular'] = self.make_singular
        self.template = fallback_env.get_template(template_name)

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

    @staticmethod
    def make_singular(verb):
        import inflect
        # Initialize the engine
        p = inflect.engine()
        # Return the singular form of the verb
        return p.singular_noun(verb) if p.singular_noun(verb) else verb


j2pt = Jinja2PromptTemplate()
