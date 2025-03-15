import os
import pkgutil
import importlib
import inspect
import yaml
import re

HOME_PAGE_MD = "index.md"  # The file name for your home page.


def ensure_home_page(docs_dir: str):
    """
    Ensure there is a docs/index.md for the Home page.
    If it doesn't exist, create a minimal file.
    """
    home_file_path = os.path.join(docs_dir, HOME_PAGE_MD)
    if not os.path.exists(home_file_path):
        os.makedirs(os.path.dirname(home_file_path), exist_ok=True)
        with open(home_file_path, "w", encoding="utf-8") as f:
            f.write("# Welcome\n\nThis is the home page.\n")
        print(f"Created a new home page at {home_file_path}")
    else:
        print(f"Home page already exists at {home_file_path}")


def generate_docs(package_name: str, output_dir: str) -> dict:
    """
    Generate MkDocs-friendly Markdown files for each class in 'package_name',
    storing them under 'output_dir'. Return a dict describing modules -> list of classes.
    This function skips generating module-level documentation files.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Attempt to import the package
    try:
        root_package = importlib.import_module(package_name)
    except ImportError as e:
        raise ImportError(f"Could not import package '{package_name}': {e}")

    # Ensure it's a proper package
    if not hasattr(root_package, "__path__"):
        raise ValueError(
            f"'{package_name}' is not a package or has no __path__ attribute."
        )

    package_path = root_package.__path__

    # This will map "swarmauri_core.module_name" -> ["Class1", "Class2", ...]
    module_classes_map = {}

    for module_info in pkgutil.walk_packages(package_path, prefix=package_name + "."):
        module_name = module_info.name

        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue

        # Convert "swarmauri_core.some_module" -> "swarmauri_core/some_module"
        relative_path = module_name.replace(".", "/")
        module_dir = os.path.join(output_dir, os.path.dirname(relative_path))
        os.makedirs(module_dir, exist_ok=True)

        # Gather all classes actually defined in this module
        classes = [
            (cls_name, cls_obj)
            for cls_name, cls_obj in inspect.getmembers(module, inspect.isclass)
            if cls_obj.__module__ == module_name
        ]
        class_names = [cls_name for cls_name, _ in classes]

        # Skip generating module-level documentation files
        # We only generate class documentation files

        # ---- Write separate files for each class ----
        for cls_name, _ in classes:
            class_file_path = os.path.join(module_dir, f"{cls_name}.md")
            with open(class_file_path, "w", encoding="utf-8") as cls_md_file:
                cls_md_file.write(f"# Class `{module_name}.{cls_name}`\n\n")
                cls_md_file.write(f"::: {module_name}.{cls_name}\n")
                cls_md_file.write("    options.extra:\n")
                cls_md_file.write("      show_inheritance: true\n\n")

        module_classes_map[module_name] = class_names

    return module_classes_map


def build_nav_for_api_docs(
    package_name: str,
    module_classes_map: dict,
    local_output_dir: str,
    top_label: str = "core",
    home_page: str = "index.md",
) -> list:
    """
    Return a nav structure that fits under the API Documentation section:

    - API Documentation:
      - api/index.md
      - Top Label:
        - Home: api/top_label/index.md
        - ClassName: api/top_label/package_name/module_name/ClassName.md
        ...

    This function only includes class entries in the navigation, not module entries.
    """
    # Sort the modules for stable output
    sorted_modules = sorted(module_classes_map.keys())

    # Start with the index page
    top_label_items = [
        {"Home": os.path.join(local_output_dir, top_label.lower(), home_page)}
    ]

    # Process all modules and add only their classes to the navigation
    for module_name in sorted_modules:
        # Create the module path that includes the full package structure
        module_path = os.path.join(
            local_output_dir, top_label.lower(), module_name.replace(".", "/") + ".md"
        )

        # Add classes for this module
        class_names = sorted(module_classes_map[module_name])
        for cls_name in class_names:
            # Create the class path in the same directory as its module
            module_dir = os.path.dirname(module_path)
            class_path = os.path.join(module_dir, f"{cls_name}.md")

            # Add the class to the navigation
            top_label_items.append({cls_name: class_path})

    # Return the structure for this top_label
    return [{top_label: top_label_items}]


def load_mkdocs_yml_safely(mkdocs_yml_path: str):
    """
    Load the mkdocs.yml file safely, handling custom Python tags.
    """
    if not os.path.isfile(mkdocs_yml_path):
        raise FileNotFoundError(f"Could not find mkdocs.yml at '{mkdocs_yml_path}'")

    # Read the file content
    with open(mkdocs_yml_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace Python tags with placeholders
    pattern = r"!!python/name:([^\s]+)"
    placeholders = {}

    def replace_tag(match):
        tag = match.group(0)
        placeholder = f"__PYTHON_TAG_{len(placeholders)}__"
        placeholders[placeholder] = tag
        return placeholder

    modified_content = re.sub(pattern, replace_tag, content)

    # Load the modified content
    config = yaml.safe_load(modified_content)

    return config, placeholders


def save_mkdocs_yml_safely(mkdocs_yml_path: str, config: dict, placeholders: dict):
    """
    Save the mkdocs.yml file, restoring custom Python tags.
    """
    # Convert config to YAML
    content = yaml.safe_dump(config, sort_keys=False)

    # Restore Python tags
    for placeholder, tag in placeholders.items():
        content = content.replace(f"'{placeholder}'", tag)

    # Write the file
    with open(mkdocs_yml_path, "w", encoding="utf-8") as f:
        f.write(content)


def update_api_docs_nav(mkdocs_yml_path: str, new_section: list):
    """
    Update the API Documentation section in mkdocs.yml with the new section.
    If the section already exists, it will be replaced.
    """
    # Load the config safely
    config, placeholders = load_mkdocs_yml_safely(mkdocs_yml_path)

    if "nav" not in config:
        config["nav"] = []

    # Find the API Documentation section
    api_docs_index = None
    for i, section in enumerate(config["nav"]):
        if isinstance(section, dict) and "API Documentation" in section:
            api_docs_index = i
            break

    if api_docs_index is None:
        # If API Documentation section doesn't exist, create it
        config["nav"].append({"API Documentation": ["api/index.md"]})
        api_docs_index = len(config["nav"]) - 1

    # Get the current API Documentation section
    api_docs_section = config["nav"][api_docs_index]["API Documentation"]

    # Check if the top_label already exists in the API Documentation section
    top_label = list(new_section[0].keys())[0]  # Get the top_label from the new section
    top_label_index = None

    for i, item in enumerate(api_docs_section):
        if isinstance(item, dict) and top_label in item:
            top_label_index = i
            break

    if top_label_index is not None:
        # Replace the existing top_label section
        api_docs_section[top_label_index] = new_section[0]
    else:
        # Add the new top_label section
        api_docs_section.append(new_section[0])

    # Update the config
    config["nav"][api_docs_index]["API Documentation"] = api_docs_section

    # Save the config safely
    save_mkdocs_yml_safely(mkdocs_yml_path, config, placeholders)


def generate(
    package_name: str,
    docs_dir: str,
    api_output_dir: str,
    mkdocs_yml_path: str,
    top_label: str,
    home_page: str = "index.md",
):
    """
    1) Ensure there's a Home: index.md for the top_label
    2) Generate doc files for the given package.
    3) Build a nav structure under 'API Documentation' -> 'top_label'
    4) Update the API Documentation section in mkdocs.yml
    """
    # Step 1: Ensure Home page for the top_label
    top_label_dir = os.path.join(docs_dir, api_output_dir, top_label.lower())
    ensure_home_page(top_label_dir)

    # Step 2: Generate doc files
    # Place the package documentation in a subdirectory matching the package name
    output_dir = os.path.join(docs_dir, api_output_dir, top_label.lower())
    module_classes_map = generate_docs(package_name, output_dir)

    # Step 3: Build a nav structure for API Documentation
    new_section = build_nav_for_api_docs(
        package_name, module_classes_map, api_output_dir, top_label, home_page
    )

    # Step 4: Update the API Documentation section in mkdocs.yml
    update_api_docs_nav(mkdocs_yml_path, new_section)

    print(
        f"Documentation for {package_name} has been generated and added to the API Documentation section."
    )


if __name__ == "__main__":
    # Example usage
    generate(
        package_name="swarmauri_embedding_mlm",
        docs_dir="docs/docs",
        api_output_dir="api",
        mkdocs_yml_path="docs/mkdocs.yml",
        top_label="Second_Class",
    )
