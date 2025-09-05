import importlib
import inspect
import os
import pkgutil
import re

import yaml

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
    home_page: str = "index.md",
) -> list:
    """
    Return a nav structure that fits under the API Documentation section:

    - API Documentation:
      - api/index.md
      - Top Label:
        - Home: api/top_label/index.md
        - Agents:
          - QAAgent: api/top_label/package_name/agents/QAAgent.md
          - RagAgent: api/top_label/package_name/agents/RagAgent.md
        - Chains:
          - CallableChain: api/top_label/package_name/chains/CallableChain.md
        ...

    This function organizes classes by module category (agents, chains, etc.)
    """
    # Start with the index page
    top_label_items = [
        {"Home": os.path.join(local_output_dir, top_label.lower(), home_page)}
    ]

    # Group modules by their category
    category_map = {}

    # First pass: extract all module categories
    for full_module_name in module_classes_map.keys():
        # Skip modules with no classes
        if not module_classes_map[full_module_name]:
            continue

        # Parse the module path to extract the category
        parts = full_module_name.split(".")

        # We need at least package.category format
        if len(parts) < 2:
            continue

        # For modules like "swarmauri_standard.agents.QAAgent", category is "agents"
        # For modules like "swarmauri_standard.agents", category is also "agents"
        if len(parts) == 2:
            category = parts[1]  # package.category
        else:
            # For deeper modules, we want to use the folder name as the category
            # e.g., "swarmauri_standard.agents.submodule" -> "agents"
            category = parts[1]

        # Format the category name nicely
        # Convert snake_case to Title Case (e.g., "tool_llms" -> "Tool Llms")
        display_category = category.replace("_", " ").title()

        # Initialize category if not exists
        if display_category not in category_map:
            category_map[display_category] = []

        # Get the class names for this module
        for class_name in module_classes_map[full_module_name]:
            # In generate_docs, class files are created as:
            # module_dir = os.path.join(output_dir, os.path.dirname(relative_path))
            # class_file_path = os.path.join(module_dir, f"{cls_name}.md")

            # So we need to recreate that path structure
            module_dirname = os.path.dirname(full_module_name.replace(".", "/"))

            # Build the correct path to the class documentation file
            class_path = os.path.join(
                local_output_dir, top_label.lower(), module_dirname, f"{class_name}.md"
            )

            # Add the class and path to the category
            category_map[display_category].append({class_name: class_path})

    # Add each category to the navigation
    for category, items in sorted(category_map.items()):
        # Sort items by class name and deduplicate
        seen_classes = set()
        unique_sorted_items = []

        for item in sorted(items, key=lambda x: list(x.keys())[0]):
            class_name = list(item.keys())[0]
            if class_name not in seen_classes:
                seen_classes.add(class_name)
                unique_sorted_items.append(item)

        top_label_items.append({category: unique_sorted_items})

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


def check_if_importable(package_name):
    """
    Check if a package can be imported without installing it.
    Returns True if the package can be imported, False otherwise.
    """
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Generate documentation for Swarmauri SDK"
    )
    parser.add_argument("--docs-dir", default="docs", help="Documentation directory")
    parser.add_argument("--api-output-dir", default="api", help="API output directory")
    parser.add_argument("--mkdocs-yml", default="mkdocs.yml", help="Path to mkdocs.yml")
    args = parser.parse_args()

    # Common parameters for all documentation generation
    docs_dir = args.docs_dir
    api_output_dir = args.api_output_dir
    mkdocs_yml_path = args.mkdocs_yml

    # Main SDK packages - process individually as before
    main_packages = [
        {"package_name": "swarmauri_standard", "top_label": "Standard"},
        {"package_name": "swarmauri_core", "top_label": "Core"},
        {"package_name": "swarmauri_base", "top_label": "Base"},
    ]

    print("Processing main SDK packages...")
    for pkg in main_packages:
        if check_if_importable(pkg["package_name"]):
            print(f"Generating documentation for {pkg['package_name']}...")
            generate(
                package_name=pkg["package_name"],
                docs_dir=docs_dir,
                api_output_dir=api_output_dir,
                mkdocs_yml_path=mkdocs_yml_path,
                top_label=pkg["top_label"],
            )
        else:
            print(
                f"Package {pkg['package_name']} is not importable, skipping documentation generation."
            )

    # Get the root directory of the SDK
    current_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    # Process standards packages (First_Class) - collect all modules first
    standards_dir = os.path.join(current_dir, "pkgs", "standards")
    if os.path.exists(standards_dir):
        print("Processing standards (First_Class) packages...")
        # For collecting all classes from all First_Class packages
        first_class_module_classes_map = {}

        # First generate docs for all standards packages
        for item in os.listdir(standards_dir):
            item_path = os.path.join(standards_dir, item)
            if os.path.isdir(item_path) and item != "__pycache__":
                package_name = item
                if check_if_importable(package_name):
                    print(f"Generating documentation for {package_name}...")

                    # Generate docs but don't update mkdocs.yml yet
                    top_label_dir = os.path.join(
                        docs_dir, api_output_dir, "first_class"
                    )
                    ensure_home_page(top_label_dir)

                    output_dir = os.path.join(docs_dir, api_output_dir, "first_class")
                    module_map = generate_docs(package_name, output_dir)

                    # Merge with our accumulated map
                    first_class_module_classes_map.update(module_map)
                else:
                    print(
                        f"Package {package_name} is not importable, skipping documentation generation."
                    )

        # Now build the nav structure for all First_Class packages at once
        if first_class_module_classes_map:
            new_section = build_nav_for_api_docs(
                "first_class",
                first_class_module_classes_map,
                api_output_dir,
                "First_Class",
            )
            update_api_docs_nav(mkdocs_yml_path, new_section)
            print("Updated API Documentation with all First_Class packages")
        else:
            print("No First_Class packages were importable, skipping this section.")
    else:
        print(
            f"Standards directory not found at {standards_dir}, skipping First Class packages."
        )

    # Process community packages (Second_Class) - similar approach
    community_dir = os.path.join(current_dir, "pkgs", "community")
    if os.path.exists(community_dir):
        print("Processing community (Second_Class) packages...")
        # For collecting all classes from all Second_Class packages
        second_class_module_classes_map = {}

        # First generate docs for all community packages
        for item in os.listdir(community_dir):
            item_path = os.path.join(community_dir, item)
            if os.path.isdir(item_path) and item != "__pycache__":
                package_name = item
                if check_if_importable(package_name):
                    print(f"Generating documentation for {package_name}...")

                    # Generate docs but don't update mkdocs.yml yet
                    top_label_dir = os.path.join(
                        docs_dir, api_output_dir, "second_class"
                    )
                    ensure_home_page(top_label_dir)

                    output_dir = os.path.join(docs_dir, api_output_dir, "second_class")
                    module_map = generate_docs(package_name, output_dir)

                    # Merge with our accumulated map
                    second_class_module_classes_map.update(module_map)
                else:
                    print(
                        f"Package {package_name} is not importable, skipping documentation generation."
                    )

        # Now build the nav structure for all Second_Class packages at once
        if second_class_module_classes_map:
            new_section = build_nav_for_api_docs(
                "second_class",
                second_class_module_classes_map,
                api_output_dir,
                "Second_Class",
            )
            update_api_docs_nav(mkdocs_yml_path, new_section)
            print("Updated API Documentation with all Second_Class packages")
        else:
            print("No Second_Class packages were importable, skipping this section.")
    else:
        print(
            f"Community directory not found at {community_dir}, skipping Second Class packages."
        )

    print("Documentation generation complete.")
