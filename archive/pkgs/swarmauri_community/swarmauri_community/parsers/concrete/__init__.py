from swarmauri.utils._lazy_import import _lazy_import

parsers_files = [
    ("swarmauri_community.parsers.concrete.BERTEmbeddingParser", "BERTEmbeddingParser"),
    ("swarmauri_community.parsers.concrete.EntityRecognitionParser", "EntityRecognitionParser"),
    ("swarmauri_community.parsers.concrete.FitzPdfParser", "FitzPdfParser"),
    ("swarmauri_community.parsers.concrete.PyPDF2Parser", "PyPDF2Parser"),
    ("swarmauri_community.parsers.concrete.PyPDFTKParser", "PyPDFTKParser"),
    ("swarmauri_community.parsers.concrete.TextBlobNounParser", "TextBlobNounParser"),
    ("swarmauri_community.parsers.concrete.TextBlobSentenceParser", "TextBlobSentenceParser"),
]

for module_name, class_name in parsers_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

__all__ = [class_name for _, class_name in parsers_files]
