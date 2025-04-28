#!/usr/bin/env python3

import argparse
from pathlib import Path

import tomlkit


def find_pyproject_files(base_dir):
    """Find all pyproject.toml files in the given directory tree."""
    return list(Path(base_dir).rglob("pyproject.toml"))


def update_toml_file(file_path, dry_run=False):
    """Add performance marker and pytest-benchmark dependency to a pyproject.toml file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse the TOML content
        doc = tomlkit.parse(content)
        modified = False

        # === 1. Add the performance marker ===
        if (
            "tool" in doc
            and "pytest" in doc["tool"]
            and "ini_options" in doc["tool"]["pytest"]
        ):
            pytest_config = doc["tool"]["pytest"]["ini_options"]

            # Check if markers section exists
            if "markers" in pytest_config:
                markers = pytest_config["markers"]

                # Convert to array if it's a string or other non-array type
                if not isinstance(markers, list):
                    markers = [m.strip() for m in str(markers).strip("[]").split(",")]
                    pytest_config["markers"] = markers

                # Check if perf marker already exists
                perf_marker_exists = any(
                    isinstance(m, str) and "perf:" in m for m in markers
                )

                # Add perf marker if it doesn't exist
                if not perf_marker_exists:
                    markers.append(
                        "perf: Performance tests that measure execution time and resource usage"
                    )
                    print(f"✅ Added perf marker to {file_path}")
                    modified = True
                else:
                    print(f"ℹ️ Perf marker already exists in {file_path}")
            else:
                # Add markers section if it doesn't exist
                pytest_config["markers"] = [
                    "perf: Performance tests that measure execution time and resource usage"
                ]
                print(f"✅ Created markers section with perf marker in {file_path}")
                modified = True
        else:
            print(f"⚠️ No pytest configuration found in {file_path}")

        # === 2. Add pytest-benchmark dependency ===
        # Try different dependency section formats
        dependency_section = None

        # Check dependency-groups format
        if "dependency-groups" in doc and "dev" in doc["dependency-groups"]:
            dependency_section = doc["dependency-groups"]["dev"]
        # Check dev-dependencies format
        elif "dev-dependencies" in doc:
            dependency_section = doc["dev-dependencies"]
        # Check Poetry group format
        elif (
            "tool" in doc
            and "poetry" in doc["tool"]
            and "group" in doc["tool"]["poetry"]
            and "dev" in doc["tool"]["poetry"]["group"]
        ):
            dependency_section = doc["tool"]["poetry"]["group"]["dev"]["dependencies"]

        if dependency_section is not None:
            # Check if pytest-benchmark is already in dependencies
            has_benchmark = any(
                isinstance(dep, str) and dep.startswith("pytest-benchmark")
                for dep in dependency_section
            )

            # Add pytest-benchmark if not found
            if not has_benchmark:
                dependency_section.append("pytest-benchmark>=4.0.0")
                print(f"✅ Added pytest-benchmark to dev dependencies in {file_path}")
                modified = True
            else:
                print(f"ℹ️ pytest-benchmark already in dev dependencies in {file_path}")
        else:
            print(f"⚠️ No dev dependencies section found in {file_path}")

        # Save the changes if modified and not in dry run mode
        if modified and not dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(tomlkit.dumps(doc))
            print(f"💾 Updated {file_path}")

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Add performance test marker and benchmark dependency to all pyproject.toml files"
    )
    parser.add_argument(
        "--base-dir",
        default="/Users/michaeldecent/Swarmauri/swarmauri-sdk/pkgs",
        help="Base directory to search for pyproject.toml files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually modify files, just print what would be done",
    )
    args = parser.parse_args()

    files = find_pyproject_files(args.base_dir)
    print(f"🔍 Found {len(files)} pyproject.toml files")

    for file_path in files:
        update_toml_file(file_path, args.dry_run)

    if not args.dry_run:
        print(
            "\n✨ All files processed. You can now write performance tests using the @pytest.mark.perf marker."
        )
        print("📝 Example usage:")
        print("""
@pytest.mark.perf
def test_function_performance(benchmark):
    result = benchmark(my_function, arg1, arg2)
    assert result == expected_result
        """)
    else:
        print("\n🧪 Dry run completed. No files were modified.")


if __name__ == "__main__":
    main()
