import os
import subprocess
import argparse
from pathlib import Path

def create_component(package_name, author_name, author_email, year):
    # Define the path to the Hatch template
    template_path = ".config/hatch/templates/component"

    # Validate the template path
    if not Path(template_path).exists():
        raise FileNotFoundError(f"Hatch template not found at {template_path}")

    # Run the `hatch new` command with placeholders
    output_dir = Path.cwd() / package_name
    subprocess.run([
        "hatch", "new",
        "--template", template_path,
        "--",
        package_name,
        f"--author-name={author_name}",
        f"--author-email={author_email}",
        f"--year={year}"
    ], check=True)

    print(f"Component '{package_name}' created successfully in {output_dir}")


def main():
    # Parse arguments from the workflow
    parser = argparse.ArgumentParser(description="Generate a new Hatch component from a template.")
    parser.add_argument("--package-name", required=True, help="The name of the new package/component.")
    parser.add_argument("--author-name", required=True, help="The name of the author.")
    parser.add_argument("--author-email", required=True, help="The email of the author.")
    parser.add_argument("--year", required=True, help="The current year.")
    args = parser.parse_args()

    # Create the component
    create_component(
        package_name=args.package_name,
        author_name=args.author_name,
        author_email=args.author_email,
        year=args.year
    )


if __name__ == "__main__":
    main()
