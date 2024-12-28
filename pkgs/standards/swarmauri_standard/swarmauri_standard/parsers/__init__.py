# from swarmauri.utils._lazy_import import _lazy_import

# # List of parsers names (file names without the ".py" extension) and corresponding class names
# parsers_files = [
#     (
#         "swarmauri_standard.parsers.BeautifulSoupElementParser",
#         "BeautifulSoupElementParser",
#     ),
#     ("swarmauri_standard.parsers.CSVParser", "CSVParser"),
#     ("swarmauri_standard.parsers.HTMLTagStripParser", "HTMLTagStripParser"),
#     ("swarmauri_standard.parsers.KeywordExtractorParser", "KeywordExtractorParser"),
#     ("swarmauri_standard.parsers.Md2HtmlParser", "Md2HtmlParser"),
#     ("swarmauri_standard.parsers.OpenAPISpecParser", "OpenAPISpecParser"),
#     (
#         "swarmauri_standard.parsers.PhoneNumberExtractorParser",
#         "PhoneNumberExtractorParser",
#     ),
#     ("swarmauri_standard.parsers.PythonParser", "PythonParser"),
#     ("swarmauri_standard.parsers.RegExParser", "RegExParser"),
#     ("swarmauri_standard.parsers.URLExtractorParser", "URLExtractorParser"),
#     ("swarmauri_standard.parsers.XMLParser", "XMLParser"),
# ]

# # Lazy loading of parsers classes, storing them in variables
# for module_name, class_name in parsers_files:
#     globals()[class_name] = _lazy_import(module_name, class_name)

# # Adding the lazy-loaded parsers classes to __all__
# __all__ = [class_name for _, class_name in parsers_files]
