# `swarmauri_tool_searchword`

## Installation

To install the `swarmauri_tool_searchword` package, ensure you have Python 3.10 or newer installed on your system. You can use `pip` to install the package along with its dependencies. Open your terminal and run the following command:

```bash
pip install swarmauri_tool_searchword
```

This command will automatically install the package and all required dependencies as specified in the `pyproject.toml` file.

### Dependencies
The `swarmauri_tool_searchword` package requires the following dependencies:
- `pydantic`: A data validation and settings management library.
- `swarmauri_base`: The base package that provides foundational tools.

Make sure these dependencies are installed correctly. If you run into issues, please check your Python and `pip` installation.

## Usage 

Once the package is installed, you can use the `SearchWordTool` class to search for a specific word or phrase in a text file. Below is a detailed example of how to use the tool:

### Example Usage

1. **Import the Tool**
   First, you need to import the `SearchWordTool` from the package:

   ```python
   from swarmauri_tool_searchword import SearchWordTool
   ```

2. **Create an Instance of the Tool**
   Create an instance of `SearchWordTool`:

   ```python
   search_tool = SearchWordTool()
   ```

3. **Call the Tool with Required Parameters**
   Use the `__call__` method of the `SearchWordTool` instance to search for the word or phrase. Provide the file path and the word you want to search:

   ```python
   result = search_tool(file_path='path/to/your/file.txt', search_word='your_search_word')
   ```

4. **Process the Result**
   The `result` will be a dictionary containing the highlighted lines and the count of occurrences:

   ```python
   print(f"Found {result['count']} occurrences.")
   for line in result['highlighted_lines']:
       print(line)
   ```

### Error Handling
The tool has built-in error handling. If you provide an invalid file path or an invalid search word, it will raise appropriate exceptions.

- `FileNotFoundError`: Raised if the specified file does not exist.
- `ValueError`: Raised if the input parameters are invalid.

Make sure to handle these exceptions in your application to ensure a smooth user experience.

### Logging
The tool uses Python's built-in `logging` module to log information about the search process. You can adjust the logging level by configuring the `logging` settings in your application.

```python
import logging

logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for more detailed logs
```

With these steps and considerations, you can effectively integrate and use the `swarmauri_tool_searchword` package in your projects to search and highlight specific terms in text files.