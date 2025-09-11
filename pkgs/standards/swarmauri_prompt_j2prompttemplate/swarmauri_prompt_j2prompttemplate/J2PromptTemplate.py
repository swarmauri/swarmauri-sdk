import os
from typing import Any, Callable, Dict, List, Literal, Optional, Union

from jinja2 import Environment, FileSystemLoader, Template
from pydantic import ConfigDict, FilePath
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.prompt_templates.PromptTemplateBase import PromptTemplateBase


@ComponentBase.register_type(PromptTemplateBase, "J2PromptTemplate")
class J2PromptTemplate(PromptTemplateBase):
    """
    A subclass of PromptTemplateBase that uses Jinja2 for template rendering.

    The `template` attribute supports either a literal string representing the template content
    or a Pydantic FilePath. When a FilePath is provided, the template is loaded using
    `env.get_template()` and stored in `template`.

    Features:
    - Support for multiple template directories with fallback mechanism
    - Built-in filters: split_whitespace, make_singular, make_plural
    - Template caching for performance
    """

    # The template attribute may be a literal string (template content),
    # a FilePath (when provided as input), or a compiled Jinja2 Template (when loaded from file).
    template: Union[str, FilePath, Template] = ""
    variables: Dict[str, Union[str, int, float, Any]] = {}
    # Optional templates_dir attribute (can be a single path or a list of paths)
    templates_dir: Optional[Union[str, List[str]]] = None
    # Whether to enable code generation specific features like linguistic filters

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    type: Literal["J2PromptTemplate"] = "J2PromptTemplate"

    def get_env(self) -> Environment:
        """
        Constructs and returns a Jinja2 Environment.

        If `templates_dir` is provided, a FileSystemLoader is created with that directory (or directories).
        Otherwise, no loader is set.

        The custom filters are added before returning the environment.
        """
        if self.templates_dir:
            if isinstance(self.templates_dir, str):
                loader = FileSystemLoader([self.templates_dir])
            else:
                loader = FileSystemLoader(self.templates_dir)
        else:
            loader = None
        env = Environment(loader=loader, autoescape=False)

        # Add basic filters
        env.filters["split"] = self.split_whitespace
        env.filters["make_singular"] = self.make_singular
        env.filters["make_plural"] = self.make_plural

        return env

    def set_template(self, template: Union[str, FilePath]) -> None:
        """
        Sets or updates the template.

        - If the provided `template` is a literal string, it is stored as-is.
        - If it is a FilePath, the template is loaded via an environment using `get_template()`.
        """
        if type(template) is str:
            self.template = template
        else:
            self._set_template_from_filepath(template)

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
                    rel_template = os.path.relpath(abs_template, abs_dir).replace(
                        os.sep, "/"
                    )
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
                            os.path.join(root, os.path.basename(template_path_str)),
                            abs_dir,
                        ).replace(os.sep, "/")
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
                    self.templates_dir[0]
                    if isinstance(self.templates_dir, list)
                    else self.templates_dir
                )
            else:
                directory = os.getcwd()
        template_name = os.path.basename(template_path_str)
        fallback_env = Environment(
            loader=FileSystemLoader([directory]), autoescape=False
        )
        fallback_env.filters["split"] = self.split_whitespace
        fallback_env.filters["make_singular"] = self.make_singular
        fallback_env.filters["make_plural"] = self.make_plural

        self.template = fallback_env.get_template(template_name)

    def generate_prompt(self, variables: Dict[str, Any] = None) -> str:
        """
        Generates a prompt by rendering the current template with the provided variables.

        - If `template` is a literal string, it is compiled on the fly.
        - If it is already a compiled Template (loaded via FilePath), it is rendered directly.
        """
        variables = variables if variables else self.variables
        return self.fill(variables)

    def __call__(self, variables: Optional[Dict[str, Any]] = None) -> str:
        """
        Allows the instance to be called directly to generate a prompt.
        """
        variables = variables if variables else self.variables
        return self.fill(variables)

    def fill(self, variables: Dict[str, Any] = None) -> str:
        """
        Renders the template with the provided variables.
        """
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
    def make_singular(word: str):
        """
        Converts a plural word to singular form.
        Requires inflect library to be installed.
        """
        try:
            import inflect

            # Initialize the engine
            p = inflect.engine()
            # Return the singular form of the verb
            return p.singular_noun(word) if p.singular_noun(word) else word
        except ImportError:
            # Return the original if inflect is not available
            return word

    @staticmethod
    def make_plural(word: str) -> str:
        """
        Converts a singular word to its plural form.
        Requires inflect library to be installed.
        """
        try:
            import inflect

            p = inflect.engine()
            return p.plural(word) or word
        except ImportError:
            return word

    def add_filter(self, name: str, filter_func: Callable) -> None:
        """
        Adds a custom filter to the Jinja2 environment.

        Parameters:
            name: The name of the filter (used in templates)
            filter_func: The function to be called when the filter is used
        """
        env = self.get_env()
        env.filters[name] = filter_func
