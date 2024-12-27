# from swarmauri.utils._lazy_import import _lazy_import

# # List of chunker names (file names without the ".py" extension) and corresponding class names
# chunkers_files = [
#     ("swarmauri_standard.chunkers.DelimiterBasedChunker", "DelimiterBasedChunker"),
#     ("swarmauri_standard.chunkers.FixedLengthChunker", "FixedLengthChunker"),
#     ("swarmauri_standard.chunkers.MdSnippetChunker", "MdSnippetChunker"),
#     ("swarmauri_standard.chunkers.SentenceChunker", "SentenceChunker"),
#     ("swarmauri_standard.chunkers.SlidingWindowChunker", "SlidingWindowChunker"),
# ]

# # Lazy loading of chunker classes, storing them in variables
# for module_name, class_name in chunkers_files:
#     globals()[class_name] = _lazy_import(module_name, class_name)

# # Adding the lazy-loaded chunker classes to __all__
# __all__ = [class_name for _, class_name in chunkers_files]

