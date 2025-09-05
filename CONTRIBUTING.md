## Contributing Guidelines

We welcome contributions to improve this project. Please follow these guidelines to ensure a smooth contribution process.

### Code of Conduct
The Code of Conduct for this project will be available soon. Once available, please make sure to review and adhere to it. 

### Reporting Bugs
To report bugs, please follow these steps:

1. **Search Existing Issues:** Before reporting a bug, check the [Issues](https://github.com/swarmauri/swarmauri-sdk/issues) to see if the problem has already been reported or is being addressed.
   
2. **Create a New Bug Report:** If no issue matches, open a new issue using the provided bug report template. Include:
   - Detailed steps to reproduce the bug.
   - The expected and actual behavior.
   - Screenshots, logs, or other helpful information.

### Suggesting New Features
If you have an idea for a new feature, please:

1. **Search Existing Issues:** Review existing issues to see if the feature has already been requested.

2. **Submit a New Feature Request:** If not, create a new issue using the feature request template. Provide:
   - A clear description of the feature.
   - Its potential use cases and benefits to the project.

### Suggesting Enhancements
To suggest improvements to existing features:

1. **Search Existing Issues:** Make sure the enhancement hasn’t already been proposed.

2. **Create an Enhancement Request:** If not, submit an issue with the enhancement request template. Describe:
   - The current functionality.
   - The proposed improvements and how they enhance the project.

### Style Guide
Please follow the [SDK Style Guide](STYLE_GUIDE.md) and the
[Contribution & Extension Guidelines](pkgs/standards/peagen/docs/feature_evolve/15\ \ Contribution\ \&\ Extension\ Guidelines.md).

Code must satisfy the automated checks used in CI:

| Tool           | Command               | Purpose                          |
| -------------- | -------------------- | -------------------------------- |
| **Formatting** | `ruff format`        | Apply consistent formatting      |
| **Linting**    | `ruff check`         | Enforce project rules            |
| **Typing**     | `mypy --strict`      | Ensure all public functions typed |
| **Security**   | `bandit -r src`      | Detect common vulnerabilities     |

Pull requests that fail any of the above will not be merged.

### How to Contribute

1. **Fork the Repository:**
   - Navigate to the [repository](https://github.com/swarmauri/swarmauri-sdk) and fork it to your GitHub account.
   
2. **Star and Watch:**
   - Star the repo and watch for updates to stay informed.

3. **Clone Your Fork:**
   - Clone your fork to your local machine:  
     `git clone https://github.com/your-username/swarmauri-sdk.git`

4. **Create a New Branch:**
   - Create a feature branch to work on:  
     `git checkout -b feature/your-feature-name`

5. **Make Changes:**
   - Implement your changes. Write meaningful and clear commit messages.
   - Stage and commit your changes:  
     `git add .`  
     `git commit -m "Add a meaningful commit message"`

6. **Push to Your Fork:**
   - Push your branch to your fork:  
     `git push origin feature/your-feature-name`

7. **Write Tests:**  
   - Ensure each new feature has an associated test file.
   - Tests should cover:
     1. **Component Type:** Verify the component is of the expected type.
     2. **Resource Handling:** Validate inputs/outputs and dependencies.
     3. **Serialization:** Ensure data is properly serialized and deserialized.
     4. **Access Method:** Test component accessibility within the system.
     5. **Functionality:** Confirm the feature meets the project requirements.

8. **Create a Pull Request:**  
   - Once your changes are ready, create a pull request (PR) to merge your branch into the main repository. 
   - Provide a detailed description, link to related issues, and request a review.

### Developing Swarmauri Packages and Plugins

Swarmauri follows a plugin-based architecture where components can be added via Python's entry point system. Understanding this system is essential for developing new packages.

#### Package Development Setup

1. **Minimal Development Environment:**
   
   For developing a new Swarmauri package, you typically only need to install the core dependencies:

   ```bash
   # Using pip
   pip install -e pkgs/core/
   pip install -e pkgs/base/
   pip install -e pkgs/swarmauri_standard/
   
   # Or using uv (faster)
   uv pip install -e pkgs/core/
   uv pip install -e pkgs/base/
   uv pip install -e pkgs/swarmauri_standard/
   ```
2. **Package Structure:**

A typical Swarmauri plugin package should follow this structure:
```
swarmauri_<resource_kind>_<plugin_name>/
├── LICENSE
├── README.md
├── pyproject.toml
├── swarmauri_<resource_kind>_<plugin_name>/
│   ├── __init__.py
│   └── <PluginName>.py
└── tests/
    └── unit/
        └── <PluginName>_test.py
```

3. **Entry Point Registration:**

Swarmauri uses Python's entry points for plugin discovery. In your pyproject.toml, register your plugin:

```toml
[project.entry-points.'swarmauri.<resource_kind>']
<plugin_name> = "swarmauri_<resource_kind>_<plugin_name>:<PluginClass>"
```
For example, for a vector store plugin:

```toml
[project.entry-points.'swarmauri.vectorstores']
PineconeVectorStore = "swarmauri_vectorstore_pinecone:PineconeVectorStore"
```

**Plugin Citizenship Classes**

Swarmauri has a concept of "citizenship" for plugins, which determines their privileges:

1. **First-Class Plugins:**

    - Pre-registered and maintained by the core team
    - Must implement required interfaces
    - Example: `@ComponentBase.register_type(VectorStoreBase, "PineconeVectorStore")`

2. **Second-Class Plugins:**

    - Community-contributed plugins
    - Must implement the same interfaces as first-class plugins
    - Registered with the same namespace (e.g., swarmauri.vectorstores)

3. **Third-Class Plugins:**

    - Generic plugins with fewer restrictions
    - Registered under swarmauri.plugins namespace
    - Not required to implement specific interfaces

### Creating a New Plugin
1. **Subclass the Appropriate Base Class:**
```python
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.vectorstores.VectorStoreBase import VectorStoreBase

@ComponentBase.register_type(VectorStoreBase, "MyVectorStore")
class MyVectorStore(VectorStoreBase):
    """
    My custom vector store implementation.
    """
    type: Literal["MyVectorStore"] = "MyVectorStore"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Your initialization code

    # Implement required methods from VectorStoreBase
```
2. **Configure Entry Point in pyproject.toml:**
```toml
[project]
name = "swarmauri_vectorstore_myvectorstore"
version = "0.1.0"
description = "My custom vector store for Swarmauri"
license = "Apache-2.0"
authors = [{ name = "Your Name", email = "your.email@example.com" }]
dependencies = [
    "swarmauri_core",
    "swarmauri_base",
    "swarmauri_standard"
]

[project.entry-points.'swarmauri.vectorstores']
MyVectorStore = "swarmauri_vectorstore_myvectorstore:MyVectorStore"
```
4. **Test Your Plugin:**
```sh
# Install your package in development mode
pip install -e path/to/swarmauri_vectorstore_myvectorstore

# Run unit tests
pytest swarmauri_vectorstore_myvectorstore/tests
```

**Accessing Your Plugin**

After registration, your plugin can be accessed in two ways:

1. **Via Namespace (Recommended):**
```python
from swarmauri.vectorstores import MyVectorStore

my_store = MyVectorStore()
```
2. **Direct Package Import:**

```python
from swarmauri_vectorstore_myvectorstore import MyVectorStore

my_store = MyVectorStore()
```

Plugins must declare their licence (Apache-2.0 or MIT preferred) and register
entry points under `[project.entry-points]`. Entry-point names should remain
stable to preserve backwards compatibility. See the
[Contribution & Extension Guidelines](pkgs/standards/peagen/docs/feature_evolve/15\ \ Contribution\ \&\ Extension\ Guidelines.md)
for the complete checklist including tests, metrics and documentation.
Refer to the
[Dependency Matrix & Licences](pkgs/standards/peagen/docs/feature_evolve/16\ \ Dependency\ Matrix\ \&\ Licences.md)
document for a list of approved dependencies and licences.

### Development Setup

1. **Run Tests with GitHub Actions:**
   - GitHub Actions will automatically run tests for your changes. 
   - Check the Actions tab to verify if your changes pass the tests.

2. **Enabling GitHub Actions on Your Fork:**
   - **Check for Workflow Files:** Ensure `.yml` workflow files are present under `.github/workflows` in your fork.
   - **Enable Actions:** 
     - Go to the "**Settings**" tab of your fork.
     - Under "**Actions**" in the left sidebar, ensure Actions are enabled. If not, enable them.

### Licensing
This project is licensed under the [Project License](https://github.com/swarmauri/swarmauri-sdk/blob/master/LICENSE).
Please ensure that your contributions comply with the terms of the license.

Before submitting a pull request run `scripts/license_scan.py` to
generate the dependency licence report. The script fails if any GPL or
AGPL licensed packages are detected and optionally emits an SPDX SBOM
if `trivy` is installed.
