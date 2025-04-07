#!/usr/bin/env python3
"""
unparser_class.py

This module defines the Unparser class, which converts a configuration dictionary back into
its textual representation according to the custom grammar.
"""

import json

class JMLUnparser:
    def __init__(self, config):
        """
        Initialize the Unparser with a configuration object.
        
        :param config: The configuration data to unparse. This can be a dictionary or an object
                       that wraps the configuration (e.g., a DocumentNode) with a `data` or `value` attribute.
        """
        self.config = config

    def _get_config_data(self):
        """
        Retrieve the underlying configuration dictionary from the config attribute.
        If config is a dict, return it. If config has a 'data' or 'value' attribute, return that.
        """
        if isinstance(self.config, dict):
            return self.config
        elif hasattr(self.config, "data"):
            return self.config.data
        elif hasattr(self.config, "value"):
            return self.config.value
        else:
            raise AttributeError("Configuration object does not have an expected dictionary interface.")

    def format_value(self, value):
        """
        Format a scalar or compound value into a string that conforms to the configuration syntax.
        Leading/trailing whitespace in strings is preserved.
        """
        if isinstance(value, str):
            # Quote strings with double quotes; preserve whitespace.
            return f"\"{value}\""
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif value is None:
            return "null"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            return json.dumps(value)
        elif isinstance(value, dict):
            # Format dictionaries as inline tables: { key = value, ... }
            items = []
            for k, v in value.items():
                items.append(f"{k} = {self.format_value(v)}")
            return "{" + ", ".join(items) + "}"
        else:
            return str(value)

    def unparse_section(self, section_dict, section_path):
        """
        Recursively unparse a section of the configuration.
        
        :param section_dict: The dictionary representing the section.
        :param section_path: A list of section names leading to the current section.
        :return: A string containing the unparsed section.
        """
        output = ""
        # Output the section header if section_path is not empty.
        if section_path:
            output += f"[{'.'.join(section_path)}]\n"

        assignments = {}
        nested_sections = {}

        # Distinguish between assignments and nested sections.
        for key, value in section_dict.items():
            if isinstance(value, dict):
                # If any inner value is a dict, treat this as a nested section.
                if any(isinstance(v, dict) for v in value.values()):
                    nested_sections[key] = value
                else:
                    # Depending on how inline tables are represented, this might need adjustment.
                    nested_sections[key] = value
            else:
                assignments[key] = value

        # Output assignment lines.
        for key, value in assignments.items():
            output += f"{key} = {self.format_value(value)}\n"
        if assignments:
            output += "\n"

        # Recursively process nested sections.
        for key, subsec in nested_sections.items():
            output += self.unparse_section(subsec, section_path + [key])
        return output

    def unparse(self):
        """
        Unparse the entire configuration into its textual representation.
        
        :return: The unparsed configuration as a string.
        """
        output = ""
        config_data = self._get_config_data()

        # Process default assignments (those not contained in any section).
        default_section = config_data.get("__default__", {})
        for key, value in default_section.items():
            output += f"{key} = {self.format_value(value)}\n"
        if default_section:
            output += "\n"

        # Process each top-level section (excluding "__default__").
        for key, section in config_data.items():
            if key == "__default__":
                continue
            output += self.unparse_section(section, [key])
        return output

    def __str__(self):
        return self.unparse()