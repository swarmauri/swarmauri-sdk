Below is an example of a comprehensive `README.md` for your unified monorepo management tool:

---

```markdown
# Monorepo Manager

**Monorepo Manager** is a unified command-line tool for managing a Python monorepo that contains multiple standalone packages, each with its own `pyproject.toml`. It consolidates several common tasks—including dependency management, version bumping, remote dependency resolution, test analysis, and project configuration updates—into one robust CLI.

## Features

- **Dependency Management**  
  - **Lock:** Generate a `poetry.lock` file.
  - **Install:** Install dependencies with options for extras and development dependencies.
  - **Show Freeze:** Display installed packages using `pip freeze`.

- **Version Management**  
  - **Version:** Bump (major, minor, patch, finalize) or explicitly set package versions in `pyproject.toml`.

- **Remote Operations**  
  - **Remote Fetch:** Fetch the version from a remote GitHub repository’s `pyproject.toml`.
  - **Remote Update:** Update a local `pyproject.toml` file with version information from remote Git dependencies.

- **Test Analysis**  
  - **Test:** Parse a JSON file with test results, display summary statistics, and evaluate threshold conditions.

- **Pyproject Operations**  
  - **Pyproject:** Extract local (path) and Git-based dependencies from a `pyproject.toml` file and optionally update dependency versions.

## Installation

    ```bash
    pip install monorepo-manager
    ```

_This installs the `monorepo-manager` CLI (provided via the entry point `monorepo-manager`) into your system PATH._

## Usage

Once installed, you can invoke the CLI using:

```bash
monorepo-manager --help
```

This displays the list of available commands.

### Command Examples

#### 1. Lock Dependencies

Generate a `poetry.lock` file for a package by specifying the directory or file path:

```bash
# Lock using a directory containing pyproject.toml:
monorepo-manager lock --directory ./packages/package1

# Lock using an explicit pyproject.toml file:
monorepo-manager lock --file ./packages/package1/pyproject.toml
```

#### 2. Install Dependencies

Install dependencies with various options:

```bash
# Basic installation:
monorepo-manager install --directory ./packages/package1

# Install using an explicit pyproject.toml file:
monorepo-manager install --file ./packages/package1/pyproject.toml

# Install including development dependencies:
monorepo-manager install --directory ./packages/package1 --dev

# Install including extras (e.g., extras named "full"):
monorepo-manager install --directory ./packages/package2 --extras full

# Install including all extras:
monorepo-manager install --directory ./packages/package2 --all-extras
```

#### 3. Version Management

Bump the version or set it explicitly for a given package:

```bash
# Bump the patch version (e.g. from 1.2.3.dev1 to 1.2.3.dev2):
monorepo-manager version ./packages/package1/pyproject.toml --bump patch

# Finalize a development version (remove the ".dev" suffix):
monorepo-manager version ./packages/package1/pyproject.toml --bump finalize

# Set an explicit version:
monorepo-manager version ./packages/package1/pyproject.toml --set 2.0.0.dev1
```

#### 4. Remote Operations

Fetch version information from a remote GitHub repository’s `pyproject.toml` and update your local configuration accordingly.

```bash
# Fetch the remote version:
monorepo-manager remote fetch --git-url https://github.com/YourOrg/YourRepo.git --branch main --subdir "src/"

# Update a local pyproject.toml with versions resolved from remote dependencies.
# (If --output is omitted, the input file is overwritten.)
monorepo-manager remote update --input ./packages/package1/pyproject.toml --output ./packages/package1/pyproject.updated.toml
```

#### 5. Test Analysis

Analyze test results provided in a JSON file, and enforce percentage thresholds for passed and skipped tests:

```bash
# Analyze test results without thresholds:
monorepo-manager test test-results.json

# Analyze test results with thresholds: require that passed tests are greater than 75% and skipped tests are less than 20%:
monorepo-manager test test-results.json --required-passed gt:75 --required-skipped lt:20
```

#### 6. Pyproject Operations

Operate on the `pyproject.toml` file to extract dependency information and optionally update dependency versions:

```bash
# Extract local (path) and Git-based dependencies:
monorepo-manager pyproject --pyproject ./packages/package1/pyproject.toml

# Update local dependency versions to 2.0.0 (updates parent file and, if possible, each dependency's own pyproject.toml):
monorepo-manager pyproject --pyproject ./packages/package1/pyproject.toml --update-version 2.0.0
```

## Development

### Project Structure

```
monorepo_manager/
├── __init__.py
├── cli.py            # Main CLI entry point
├── poetry_ops.py     # Poetry operations (lock, install, build, publish, etc.)
├── version_ops.py    # Version bumping and setting operations
├── remote_ops.py     # Remote Git dependency version fetching/updating
├── test_ops.py       # Test result analysis operations
└── pyproject_ops.py  # pyproject.toml dependency extraction and updates
pyproject.toml        # Package configuration file containing metadata
README.md             # This file
```

### Running Tests

For development purposes, you can use your favorite test runner (such as `pytest`) to run tests for the CLI and modules.

```bash
pytest
```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests for improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

---

This `README.md` provides a detailed overview, installation instructions, and comprehensive usage examples for each command offered by your CLI tool. Feel free to adjust sections or add any additional details specific to your project needs.