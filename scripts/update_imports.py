#!/usr/bin/env python3
import os
import re


def update_component_base_imports(start_path):
    """
    Walk through all Python files in the given path, update ComponentBase imports,
    and add deprecation warnings.
    """
    pattern = r"from\s+swarmauri_core\.ComponentBase\s+import\s+ComponentBase"
    replacement = "from swarmauri_base.ComponentBase import ComponentBase"

    deprecation_warning = """
"""

    # To ensure warnings import is present
    warning_import = "import warnings"

    files_updated = 0

    for root, _, files in os.walk(start_path):
        for file_name in files:
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)

                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()

                    # Check if the file contains the old import
                    if re.search(pattern, content):
                        print(f"Processing file: {file_path}")

                        # Replace the old import with the new one
                        updated_content = re.sub(pattern, replacement, content)

                        # Add warnings import if it's not already there
                        if "import warnings" not in updated_content:
                            # Find the first import statement
                            import_match = re.search(
                                r"^import\s+", updated_content, re.MULTILINE
                            )
                            if import_match:
                                position = import_match.start()
                                updated_content = (
                                    updated_content[:position]
                                    + warning_import
                                    + "\n"
                                    + updated_content[position:]
                                )
                            else:
                                # If no import statement found, add at the beginning
                                updated_content = (
                                    warning_import + "\n\n" + updated_content
                                )

                        # Add the deprecation warning after all import statements
                        # Find the last import statement
                        import_lines = re.findall(
                            r"^(?:import|from)\s+.*$", updated_content, re.MULTILINE
                        )
                        if import_lines:
                            last_import = import_lines[-1]
                            last_import_pos = updated_content.rfind(last_import) + len(
                                last_import
                            )
                            updated_content = (
                                updated_content[:last_import_pos]
                                + "\n\n"
                                + deprecation_warning
                                + "\n"
                                + updated_content[last_import_pos:]
                            )

                        # Write the updated content back to the file
                        with open(file_path, "w", encoding="utf-8") as file:
                            file.write(updated_content)

                        files_updated += 1
                        print(f"Updated: {file_path}")

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    print(f"\nTotal files updated: {files_updated}")


if __name__ == "__main__":
    sdk_path = "/Users/michaeldecent/Swarmauri/swarmauri-sdk"
    update_component_base_imports(sdk_path)
