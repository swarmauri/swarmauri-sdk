# Contributing to Swarmauri SDK

We welcome contributions from the community to help improve Swarmauri SDK. This document provides guidelines on how to contribute, including submitting PRs, debugging, developing plugins, and following the style guide.

!!! info "Before You Start"
    Make sure you have a GitHub account and are familiar with Git basics, Python development, and the general structure of the Swarmauri SDK.

## Pull Requests (PRs)

### Submitting a PR

1. **Fork the Repository**: Start by forking the Swarmauri SDK repository to your GitHub account.
2. **Clone the Fork**: Clone your forked repository to your local machine.
   ```bash
   git clone https://github.com/your-username/swarmauri-sdk.git
   cd swarmauri-sdk
   ```
3. **Create a Branch**: Create a new branch for your feature or bug fix.
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make Changes**: Implement your changes in the new branch.
5. **Commit Changes**: Commit your changes with a descriptive commit message.
   ```bash
   git add .
   git commit -m "Add feature: your-feature-name"
   ```
6. **Push Changes**: Push your changes to your forked repository.
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a PR**: Open a pull request from your forked repository to the main Swarmauri SDK repository. Provide a clear description of your changes and link any relevant issues.

!!! tip "PR Best Practices" 
    - Keep PRs focused on a single issue or feature 
    - Include tests for your changes 
    - Update documentation if necessary - Respond promptly to review comments

### PR Review Process

- **Code Review**: Your PR will be reviewed by maintainers. They may request changes or provide feedback.
- **CI Checks**: Ensure that all continuous integration (CI) checks pass. This includes tests, linting, and other automated checks.
- **Merge**: Once approved, your PR will be merged into the main repository.

## Debugging

### Setting Up a Debugging Environment

1. **Install Poetry**: Ensure you have Poetry installed. If not, install it using the following command:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
2. **Install Dependencies**: Use Poetry to install the necessary dependencies.
   ```bash
   poetry install
   ```
3. **Activate the Virtual Environment**: Activate the virtual environment created by Poetry.
   ```bash
   poetry shell
   ```
4. **Run Tests**: Run the test suite to ensure everything is working.
   ```bash
   pytest
   ```

!!! warning "Common Setup Issues" 
    - Make sure you're using Python 3.10 or later 
    - If you encounter dependency conflicts, try `poetry update` to resolve them 
    - Ensure you have the necessary permissions to install packages

### Debugging Tips

- **Use Breakpoints**: Insert breakpoints in your code to pause execution and inspect variables.
- **Logging**: Add logging statements to track the flow of execution and identify issues.
- **Interactive Debugging**: Use interactive debugging tools like `pdb` to step through your code.

!!! note "Debugging Tools"
    ```python 
    # Using pdb for debugging
    import pdb; pdb.set_trace()

        # Using logging
        import logging
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        logger.debug("Variable value: %s", variable)
    ```

## Plugin Development

???+ abstract "Plugin System Overview"
    Swarmauri SDK uses a plugin system that allows developers to extend its functionality. Plugins can add new tools, models, agents, and other components to the SDK. The plugin system is based on the `ComponentBase` class, which provides registration and discovery mechanisms.

### Creating a Plugin

1. **Define the Plugin**: Create a new Python file for your plugin and define the necessary classes and functions.
2. **Register the Plugin**: Use the `ComponentBase.register_type` decorator to register your plugin with the Swarmauri SDK.

```python
from swarmauri_core.ComponentBase import ComponentBase

@ComponentBase.register_type(ToolBase, "MyCustomPlugin")
class MyCustomPlugin(ToolBase):
...
```

3. **Implement Functionality**: Implement the functionality of your plugin, ensuring it adheres to the required interfaces and standards.
4. **Update Registries**: Register your new component so it can be discovered.
   - **InterfaceRegistry**: Add the resource kind and its interface mapping.
   - **PluginCitizenshipRegistry**: Map the full resource path of your class to its module path.

!!! tip "Plugin Development" 
    - Study existing plugins to understand the patterns and conventions 
    - Use type hints to ensure your plugin is type-safe 
    - Follow the naming conventions for consistency

### Testing the Plugin

- **Unit Tests**: Write unit tests for your plugin to ensure it works as expected.
- **Integration Tests**: Test your plugin in the context of a larger application to verify its integration.

## Style Guide

### Code Style

- **PEP 8**: Follow the PEP 8 style guide for Python code.
- **Docstrings**: Use docstrings to document your classes and functions.
- **Type Annotations**: Use type annotations to specify the types of function arguments and return values.

!!! info "Code Quality Tools"
    We use several tools to maintain code quality:

    - **Ruff**: For linting and formatting
    - **Mypy**: For static type checking
    - **Pytest**: For testing

### Naming Conventions

- **Classes**: Use CamelCase for class names.
- **Functions and Variables**: Use snake_case for function and variable names.
- **Constants**: Use UPPER_CASE for constants.

### Comments

- **Inline Comments**: Use inline comments to explain complex logic.
- **Block Comments**: Use block comments to provide context for sections of code.

### Linting and Formatting

- **Ruff**: Use Ruff for linting and formatting your code.

  ```bash
  # Install Ruff
  poetry add --dev ruff

  # Run Ruff to check for linting issues
  poetry run ruff check .

  # Run Ruff to automatically fix formatting issues
  poetry run ruff fix .
  ```

### Docstring Conventions

We follow spaCy's docstring style to ensure our documentation is clear and consistent.

???+ example "Docstring Examples"
    #### Overview

    - **Triple Double Quotes**: Use `"""` for all docstrings.
    - **Placement**: Place the docstring immediately after the function, method, class, or module definition.
    - **Imperative Mood**: Write summaries in the imperative mood (e.g., "Return", "Process", "Compute").

    #### Structure

    1. **One-Line Summary**: A concise description of what the function/class/module does.
    2. **Blank Line**: Insert a blank line after the summary if the docstring contains additional detail.
    3. **Extended Description**: Provide any extra information necessary to understand the code's purpose or behavior.
    4. **Parameter Section (Args)**: List each parameter, its type, and a brief description.
    5. **Returns Section**: Describe the return type and the meaning of the returned value.
    6. **Raises Section (if applicable)**: List any exceptions that might be raised by the function.

    #### Example

    Below is an example demonstrating the spaCy docstring style at the method level:

    ```python
    def process_text(text: str) -> Doc:
        """
        Process a text string and return a spaCy Doc object.

        This function tokenizes and annotates the input text using spaCy's NLP pipeline.

        Args:
            text (str): The input text to be processed.

        Returns:
            Doc: The processed spaCy Doc object.

        Raises:
            ValueError: If the input text is empty.
        """
        if not text:
            raise ValueError("Input text must not be empty.")
        # Processing code goes here
    ```

    Below is an example demonstrating the spaCy docstring style at the module level:

    ```python
    """
    text_utils.py

    This module provides utilities for processing text data. It leverages spaCy's NLP
    pipeline to tokenize, annotate, and analyze text, offering helper classes and functions
    to simplify common text processing tasks.
    """

    import spacy
    ```

    Below is an example demonstrating spaCy docstring style at the class level:

    ```python
    class TextProcessor:
        """
        A class for processing and analyzing text data using spaCy.

        This class provides methods to tokenize, lemmatize, and extract named entities from text.
        It utilizes spaCy's NLP pipeline to annotate the text and offers helper methods for
        common text processing tasks.

        Attributes:
            nlp (spacy.language.Language): The spaCy NLP model used for processing text.
        """

        def __init__(self, model: str = "en_core_web_sm"):
            """
            Initialize the TextProcessor with the specified spaCy model.

            Args:
                model (str): The name of the spaCy model to load (default is "en_core_web_sm").
            """
            self.nlp = spacy.load(model)

        def process(self, text: str):
            """
            Process the input text and return the annotated spaCy Doc object.

            Args:
                text (str): The input text to process.

            Returns:
                spacy.tokens.Doc: The processed document with tokens, entities, and annotations.

            Raises:
                ValueError: If the input text is empty.
            """
            if not text:
                raise ValueError("Input text must not be empty.")
            return self.nlp(text)
    ```

---

!!! question "Need Help?"
    Join our [Discord Community](https://discord.gg/swarmauri) or [open an issue](https://github.com/swarmauri/swarmauri-sdk/issues) on GitHub if you have any questions or need assistance with contributing.
