from swarmauri.utils._lazy_import import _lazy_import

# List of chunker names (file names without the ".py" extension) and corresponding class names
chunkers_files = [
    ("swarmauri.chunkers.concrete.DelimiterBasedChunker", "DelimiterBasedChunker"),
    ("swarmauri.chunkers.concrete.FixedLengthChunker", "FixedLengthChunker"),
    ("swarmauri.chunkers.concrete.MdSnippetChunker", "MdSnippetChunker"),
    ("swarmauri.chunkers.concrete.SentenceChunker", "SentenceChunker"),
    ("swarmauri.chunkers.concrete.SlidingWindowChunker", "SlidingWindowChunker"),
]

# Lazy loading of chunker classes, storing them in variables
for module_name, class_name in chunkers_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded chunker classes to __all__
__all__ = [class_name for _, class_name in chunkers_files]
