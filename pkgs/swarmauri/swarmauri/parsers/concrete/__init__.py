import importlib

# Define a lazy loader function with a warning message if the module is not found
def _lazy_import(module_name, module_description=None):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        # If module is not available, print a warning message
        print(f"Warning: The module '{module_description or module_name}' is not available. "
              f"Please install the necessary dependencies to enable this functionality.")
        return None

# List of parser names (file names without the ".py" extension)
parser_files = [
    "BeautifulSoupElementParser",
    # "BERTEmbeddingParser",
    "CSVParser",
    "EntityRecognitionParser",
    "HTMLTagStripParser",
    "KeywordExtractorParser",
    "Md2HtmlParser",
    "OpenAPISpecParser",
    "PhoneNumberExtractorParser",
    "PythonParser",
    "RegExParser",
    # "TextBlobNounParser",
    # "TextBlobSentenceParser",
    "URLExtractorParser",
    "XMLParser",
]

# Lazy loading of parser modules, storing them in variables
for parser in parser_files:
    globals()[parser] = _lazy_import(f"swarmauri.parsers.concrete.{parser}", parser)

# Adding the lazy-loaded parser modules to __all__
__all__ = parser_files
