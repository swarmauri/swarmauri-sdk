import os
import pkgutil
import importlib
import inspect
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
    Generate MkDocs-friendly Markdown files for each module and class in 'package_name',
    storing them under 'output_dir'. Return a dict describing modules -> list of classes.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Attempt to import the package
    try:
        root_package = importlib.import_module(package_name)
    except ImportError as e:
        raise ImportError(f"Could not import package '{package_name}': {e}")

    # Ensure it's a proper package
    if not hasattr(root_package, "__path__"):
        raise ValueError(f"'{package_name}' is not a package or has no __path__ attribute.")

    package_path = root_package.__path__

    # This will map "swarmauri_core.module_name" -> ["Class1", "Class2", ...]
    module_classes_map = {}

    for module_info in pkgutil.walk_packages(package_path, prefix=package_name + "."):
        module_name = module_info.name

        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue

        # Convert "swarmauri_core.some_module" -> "swarmauri_core/some_module.md"
        relative_path = module_name.replace(".", "/")
        doc_file_path = os.path.join(output_dir, f"{relative_path}.md")
        os.makedirs(os.path.dirname(doc_file_path), exist_ok=True)

        # Gather all classes actually defined in this module
        classes = [
            (cls_name, cls_obj)
            for cls_name, cls_obj in inspect.getmembers(module, inspect.isclass)
            if cls_obj.__module__ == module_name
        ]
        class_names = [cls_name for cls_name, _ in classes]

        # ---- Write the module Markdown file ----
        with open(doc_file_path, "w", encoding="utf-8") as md_file:
            md_file.write(f"# Documentation for `{module_name}`\n\n")
            md_file.write(f"::: {module_name}\n")
            md_file.write("    options.extra:\n")
            md_file.write("      show_submodules: false\n")
            md_file.write("      show_inheritance: false\n")
            # Exclude children so we don't double-document classes
            md_file.write("      filters:\n")
            md_file.write("        - '!.*'  # exclude everything but the module docstring\n\n")

            if class_names:
                md_file.write("## Classes\n\n")
                for cls_name in class_names:
                    # Link to a separate class doc
                    md_file.write(f"- [`{cls_name}`]({cls_name}.md)\n")
                md_file.write("\n")
        
        # ---- Write separate files for each class ----
        for cls_name, _ in classes:
            class_file_path = os.path.join(os.path.dirname(doc_file_path), f"{cls_name}.md")
            with open(class_file_path, "w", encoding="utf-8") as cls_md_file:
                cls_md_file.write(f"# Class `{module_name}.{cls_name}`\n\n")
                cls_md_file.write(f"::: {module_name}.{cls_name}\n")
                cls_md_file.write("    options.extra:\n")
                cls_md_file.write("      show_inheritance: true\n\n")

        module_classes_map[module_name] = class_names

    return module_classes_map


def build_nav(
    package_name: str,
    module_classes_map: dict,
    docs_dir: str,
    local_output_dir: str,
    top_label: str = "core",
    home_page: str = "index.md"
) -> list:
    """
    Return a nav structure that looks like:

    nav:
      - core:
        - Home: index.md
        - ClassOne: path/to/ClassOne.md
        - ClassTwo: path/to/ClassTwo.md
        ...
    """
    # Sort the modules for stable output
    sorted_modules = sorted(module_classes_map.keys())

    # We'll build a single top-level list containing one dictionary: { core: [...] }.
    # 1) Start with "Home" => index.md
    core_items = [{"Home": os.path.join(
                local_output_dir,
                home_page
            )}]

    # 2) For each module, add each class to the nav at the same level
    for module_name in sorted_modules:
        class_names = sorted(module_classes_map[module_name])
        for cls_name in class_names:
            # E.g. "src/swarmauri_core/ComponentBase/ComponentBase.md"
            class_md_path = os.path.join(
                local_output_dir,
                module_name.replace(".", "/"),
                f"{cls_name}.md"
            )
            core_items.append({cls_name: class_md_path})

    # Wrap everything under the top_label (e.g. "core")
    return [{top_label: core_items}]

def write_nav_to_mkdocs_yml(mkdocs_yml_path: str, new_nav: list, replace_nav: bool = True):
    """
    Load mkdocs.yml and either replace or append to the existing 'nav' key with new_nav.
    :param replace_nav: If True, we replace the entire nav with 'new_nav'.
                       If False, we extend the existing nav by appending 'new_nav'.
    """
    if not os.path.isfile(mkdocs_yml_path):
        raise FileNotFoundError(f"Could not find mkdocs.yml at '{mkdocs_yml_path}'")

    with open(mkdocs_yml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if "nav" not in config:
        config["nav"] = []

    if replace_nav:
        # Overwrite
        config["nav"] = new_nav
    else:
        # Append
        config["nav"].extend(new_nav)

    with open(mkdocs_yml_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False)


def generate(
    package_name: str,
    docs_dir: str,
    local_output_dir: str,
    mkdocs_yml_path: str,
    top_label: str = "core",
    home_page: str = "index.md",
    replace_nav: bool = False,
):
    """
    1) Ensure there's a Home: index.md
    2) Generate doc files for the given package.
    3) Build a nav structure under 'top_label' (e.g., "core"), with "Home" as the first item.
    4) Write that nav into mkdocs.yml (either replacing or appending).
    """
    # Step 1: Ensure Home page
    home_page_dir = os.path.join(docs_dir, package_name)
    home_page_file_path = os.path.join(package_name, home_page)
    ensure_home_page(home_page_dir)
    

    # Step 2: Generate doc files
    module_classes_map = generate_docs(package_name, docs_dir)

    # Step 3: Build a nav structure
    new_nav_structure = build_nav(package_name, module_classes_map, docs_dir, local_output_dir, top_label, home_page_file_path)

    # Step 4: Write to mkdocs.yml
    write_nav_to_mkdocs_yml(mkdocs_yml_path, new_nav_structure, replace_nav=replace_nav)
