from swarmauri.utils._lazy_import import _lazy_import

# List of parsers names (file names without the ".py" extension) and corresponding class names
parsers_files = [
    (
        "swarmauri.parsers.concrete.BeautifulSoupElementParser",
        "BeautifulSoupElementParser",
    ),
    ("swarmauri.parsers.concrete.CSVParser", "CSVParser"),
    ("swarmauri.parsers.concrete.HTMLTagStripParser", "HTMLTagStripParser"),
    ("swarmauri.parsers.concrete.KeywordExtractorParser", "KeywordExtractorParser"),
    ("swarmauri.parsers.concrete.Md2HtmlParser", "Md2HtmlParser"),
    ("swarmauri.parsers.concrete.OpenAPISpecParser", "OpenAPISpecParser"),
    (
        "swarmauri.parsers.concrete.PhoneNumberExtractorParser",
        "PhoneNumberExtractorParser",
    ),
    ("swarmauri.parsers.concrete.PythonParser", "PythonParser"),
    ("swarmauri.parsers.concrete.RegExParser", "RegExParser"),
    ("swarmauri.parsers.concrete.URLExtractorParser", "URLExtractorParser"),
    ("swarmauri.parsers.concrete.XMLParser", "XMLParser"),
]

# Lazy loading of parsers classes, storing them in variables
for module_name, class_name in parsers_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded parsers classes to __all__
__all__ = [class_name for _, class_name in parsers_files]
