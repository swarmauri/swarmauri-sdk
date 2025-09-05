"""create_component.py

Generate a component skeleton from Jinja2 templates.

Provide a templates directory, an output path and a list of KEY=VALUE
placeholders. The script renders each template with these placeholders to
produce the component structure.
"""

import argparse
from pathlib import Path
import shutil
from jinja2 import Environment, FileSystemLoader, Template


def render_template(template_path: Path, output_path: Path, placeholders: dict):
    """Render a single template file using Jinja2"""
    env = Environment(loader=FileSystemLoader(str(template_path.parent)))
    template = env.get_template(template_path.name)
    rendered = template.render(**placeholders)

    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(rendered)


def replace_placeholders_in_path(path: Path, placeholders: dict) -> Path:
    """Replace placeholders in the given path string using Jinja2"""
    template = Template(str(path))
    return Path(template.render(**placeholders))


def create_component(templates_dir: Path, output_dir: Path, placeholders: dict):
    """Create component from templates using Jinja2"""
    # Map project_root values to specific subdirectories
    project_root_mapping = {
        "core": "core",
        "base": "base",
        "mixins": "mixins",
        "swarmauri": "component",
        "community": "component",
        "experimental": "component",
    }

    # Adjust the template directory based on project_root
    project_root = placeholders.get("project_root", "").lower()
    if project_root in project_root_mapping:
        templates_dir = templates_dir / project_root_mapping[project_root]

    if not templates_dir.exists():
        raise FileNotFoundError(f"Templates directory not found: {templates_dir}")

    # Walk through the adjusted template directory
    for template_path in templates_dir.rglob("*"):
        if template_path.is_file():
            # Replace placeholders in the file path
            output_path = replace_placeholders_in_path(
                output_dir / template_path.relative_to(templates_dir), placeholders
            )

            if template_path.suffix in [".py", ".md", ".txt", ".yaml", ".json"]:
                render_template(template_path, output_path, placeholders)
            else:
                # Copy binary files directly
                output_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(template_path, output_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--templates_dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--placeholders", nargs="+", required=True)
    args = parser.parse_args()

    # Parse placeholders into a dictionary
    placeholders = {}
    for placeholder in args.placeholders:
        key, value = placeholder.split("=", 1)
        placeholders[key] = value

    # Validate required placeholders
    required_fields = [
        "project_root",
        "package_name",
        "resource_kind",
        "component_name",
    ]
    if not all(key in placeholders for key in required_fields):
        raise ValueError(f"Missing required placeholders: {', '.join(required_fields)}")

    # Process placeholders
    if not placeholders["resource_kind"].endswith("s"):
        placeholders["resource_kind"] = f"{placeholders['resource_kind']}s"

    # Convert to lowercase
    for key in ["project_root", "package_name", "resource_kind"]:
        placeholders[key] = placeholders[key].lower()

    # Generate the project
    try:
        create_component(args.templates_dir, args.output, placeholders)
    except Exception as e:
        print(f"Error creating component: {str(e)}")
        raise


if __name__ == "__main__":
    main()
