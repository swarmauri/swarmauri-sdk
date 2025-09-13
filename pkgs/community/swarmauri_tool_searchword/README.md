![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_searchword/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_searchword" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/community/swarmauri_tool_searchword">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/community/swarmauri_tool_searchword&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri/swarmauri_tool_searchword">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_searchword" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri/swarmauri_tool_searchword">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_searchword" alt="PyPI - License"/></a>
    <br />
    <a href="https://pypi.org/project/swarmauri/swarmauri_tool_searchword">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_searchword?label=swarmauri_tool_searchword&color=green" alt="PyPI - swarmauri_tool_searchword"/></a>
</p>

---

# `swarmauri_tool_searchword`

A tool for extracting the number of occurances of a word or phrase (case insensitive) within a file. 

## Installation

To install the `swarmauri_tool_searchword` package, you can use pip. Ensure that you have Python 3.10 or newer installed on your system. You can install the package directly from PyPI using the following command:

```bash
pip install swarmauri_tool_searchword
```

If you are using Poetry for dependency management, you can add it to your project by executing:

```bash
poetry add swarmauri_tool_searchword
```

## Usage 

The `swarmauri_tool_searchword` package provides a single class, `SearchWordTool`, to search for specific words or phrases within a file. Below is an example of how to use it.

### Example

```python
from swarmauri_tool_searchword import SearchWordTool

# Create an instance of the SearchWordTool
search_tool = SearchWordTool()

# Specify the file path and the search word
file_path = 'path/to/your/file.txt'
search_word = 'your_search_term'

# Execute the search
result = search_tool(file_path=file_path, search_word=search_word)
print(f"Occurrences of '{search_word}': {result['count']}")
for line in result['lines']:
   print(line)

```

### Functionality

1. **Create an Instance**: Instantiate the `SearchWordTool` class.
2. **Specify Parameters**: Provide the file path and the word or phrase you want to search.
3. **Execute the Search**: Call the instance with the specified parameters to get the occurrences.

This package highlights the occurrences of the search term in the output, making it easy to identify where the term appears in the text.
