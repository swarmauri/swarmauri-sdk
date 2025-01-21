![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div style="text-align: center;">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri)
![](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false) 
![GitHub repo size](https://img.shields.io/github/repo-size/swarmauri/swarmauri-sdk)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri) ![PyPI - License](https://img.shields.io/pypi/l/swarmauri)





![PyPI - Version](https://img.shields.io/pypi/v/swarmauri?label=swarmauri_core&color=green)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri?label=swarmauri&color=green)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri?label=swarmauri_community&color=yellow)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri?label=swarmauri_experimental&color=yellow)



# Monorepo Manager

**Monorepo Manager** is a unified command-line tool for managing a Python monorepo that contains multiple standalone packages—each with its own `pyproject.toml`. It consolidates common tasks such as dependency management, version bumping, remote dependency resolution, test execution and analysis, and project configuration updates into one robust CLI.

## Features

- **Dependency Management**  
  - **Lock:** Generate a `poetry.lock` file.
  - **Install:** Install dependencies with options for extras and development dependencies.
  - **Show Freeze:** (Available as an internal command) Display installed packages using `pip freeze`.

- **Build Operations**  
  - **Build:** Recursively build packages based on local (path) dependencies as specified in your `pyproject.toml` files.

- **Version Management**  
  - **Version:** Bump (major, minor, patch, finalize) or explicitly set package versions in `pyproject.toml`.

- **Remote Operations**  
  - **Remote Fetch:** Fetch the version from a remote GitHub repository’s `pyproject.toml`.
  - **Remote Update:** Update a local `pyproject.toml` file with version information fetched from remote Git dependencies.

- **Testing and Analysis**  
  - **Test:** Run your tests using pytest. Optionally, run tests in parallel (supports [pytest‑xdist](https://pypi.org/project/pytest-xdist/)).
  - **Analyze:** Analyze test results provided in a JSON file by displaying summary statistics and evaluating threshold conditions for passed/skipped tests.

- **Pyproject Operations**  
  - **Pyproject:** Extract both local (path) and Git-based dependencies from a `pyproject.toml` file and, optionally, update dependency versions.

## Installation

Install via pip:

```bash
pip install monorepo-manager
```

_This command installs the `monorepo-manager` CLI, which is provided via the entry point `monorepo-manager`, into your system PATH._

## Usage

After installation, run the following command to see a list of available commands:

```bash
monorepo-manager --help
```

### Command Examples

#### 1. Lock Dependencies

Generate a `poetry.lock` file by specifying either a directory or a file path containing a `pyproject.toml`:

```bash
# Lock using a directory:
monorepo-manager lock --directory ./packages/package1

# Lock using an explicit pyproject.toml file:
monorepo-manager lock --file ./packages/package1/pyproject.toml
```

#### 2. Install Dependencies

Install dependencies with options for extras and including development dependencies:

```bash
# Basic installation:
monorepo-manager install --directory ./packages/package1

# Using an explicit pyproject.toml file:
monorepo-manager install --file ./packages/package1/pyproject.toml

# Install including development dependencies:
monorepo-manager install --directory ./packages/package1 --dev

# Install including extras (e.g., extras named "full"):
monorepo-manager install --directory ./packages/package2 --extras full

# Install including all extras:
monorepo-manager install --directory ./packages/package2 --all-extras
```

#### 3. Build Packages

Recursively build packages based on their local dependency paths defined in their `pyproject.toml` files:

```bash
# Build packages using a directory containing a master pyproject.toml:
monorepo-manager build --directory .

# Build packages using an explicit pyproject.toml file:
monorepo-manager build --file ./packages/package1/pyproject.toml
```

#### 4. Version Management

Bump or explicitly set the version in a package's `pyproject.toml`:

```bash
# Bump the patch version (e.g., from 1.2.3.dev1 to 1.2.3.dev2):
monorepo-manager version ./packages/package1/pyproject.toml --bump patch

# Finalize a development version (remove the .dev suffix):
monorepo-manager version ./packages/package1/pyproject.toml --bump finalize

# Set an explicit version:
monorepo-manager version ./packages/package1/pyproject.toml --set 2.0.0.dev1
```

#### 5. Remote Operations

Fetch remote version information and update your local dependency configuration:

```bash
# Fetch the version from a remote GitHub repository's pyproject.toml:
monorepo-manager remote fetch --git-url https://github.com/YourOrg/YourRepo.git --branch main --subdir "src/"

# Update a local pyproject.toml with remote-resolved versions:
# (If --output is omitted, the input file is overwritten.)
monorepo-manager remote update --input ./packages/package1/pyproject.toml --output ./packages/package1/pyproject.updated.toml
```

#### 6. Testing and Analysis

Run your tests using pytest and analyze test results from a JSON report:

- **Run Tests:**  
  Execute tests within a specified directory. Use the `--num-workers` flag for parallel execution (requires pytest‑xdist):

  ```bash
  # Run tests sequentially:
  monorepo-manager test --directory ./tests
  
  # Run tests in parallel using 4 workers:
  monorepo-manager test --directory ./tests --num-workers 4
  ```

- **Analyze Test Results:**  
  Analyze a JSON test report and enforce thresholds for passed and skipped tests:

  ```bash
  # Analyze test results without thresholds:
  monorepo-manager analyze test-results.json

  # Analyze test results with thresholds (e.g., passed tests > 75% and skipped tests < 20%):
  monorepo-manager analyze test-results.json --required-passed gt:75 --required-skipped lt:20
  ```

#### 7. Pyproject Operations

Extract and update dependency information from a `pyproject.toml` file:

```bash
# Extract local (path) and Git-based dependencies:
monorepo-manager pyproject --pyproject ./packages/package1/pyproject.toml

# Update local dependency versions to 2.0.0 (updates the parent file and, if possible, each dependency's own pyproject.toml):
monorepo-manager pyproject --pyproject ./packages/package1/pyproject.toml --update-version 2.0.0
```

## Workflow Example in GitHub Actions

Here's an example GitHub Actions workflow that uses **monorepo_manager** to lock, build, install, test, bump the patch version, and publish:

```yaml
name: Release Workflow

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install monorepo_manager Tools
        run: pip install "monorepo_manager@git+https://github.com/swarmauri/monorepo_manager.git@master"

      - name: Lock Dependencies
        run: monorepo-manager lock --directory .

      - name: Build Packages
        run: monorepo-manager build --directory .

      - name: Install Dependencies
        run: monorepo-manager install --directory .

      - name: Run Tests
        run: monorepo-manager test --directory ./tests --num-workers 4

      - name: Bump Patch Version
        run: monorepo-manager version ./packages/package1/pyproject.toml --bump patch

      - name: Publish Packages
        env:
          PYPI_USERNAME: ${{ secrets.PYPI_USERNAME }}
          PYPI_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
        run: monorepo-manager publish --directory . --username "$PYPI_USERNAME" --password "$PYPI_PASSWORD"
```

## Development

### Project Structure

```
monorepo_manager/
├── __init__.py
├── cli.py            # Main CLI entry point
├── poetry_ops.py     # Poetry operations (lock, install, build, publish, run tests, etc.)
├── version_ops.py    # Version bumping and setting operations
├── remote_ops.py     # Remote Git dependency version fetching/updating
├── test_ops.py       # Test result analysis operations
└── pyproject_ops.py  # pyproject.toml dependency extraction and updates
pyproject.toml        # Package configuration file containing metadata
README.md             # This file
```

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
