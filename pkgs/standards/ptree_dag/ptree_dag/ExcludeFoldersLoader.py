import os
from jinja2 import FileSystemLoader, TemplateNotFound

class ExcludeFoldersLoader(FileSystemLoader):
    """
    A custom Jinja2 loader that can skip loading templates from multiple
    excluded subfolders.
    """
    def __init__(self, searchpath, excluded_folders=None, encoding='utf-8', followlinks=False):
        """
        :param searchpath: Base directory (or list of directories) to search for templates.
        :param excluded_folders: List of folder names (relative to the search path) to exclude.
        """
        super().__init__(searchpath, encoding, followlinks)
        # Normalize each folder path just in case
        self.excluded_folders = [
            os.path.normpath(folder) for folder in (excluded_folders or [])
        ]

    def get_source(self, environment, template):
        # Normalize the template path
        template_path = os.path.normpath(template)

        # Check whether the template falls within any excluded folder
        # For example, if excluded_folders includes "admin", then anything starting with
        # "admin/" (or exactly "admin") should be considered excluded.
        for folder in self.excluded_folders:
            if (template_path.startswith(folder + os.sep) or
                template_path == folder):
                raise TemplateNotFound(template)

        # Otherwise, use the parent method
        return super().get_source(environment, template)
